"""鉴权与授权。

设计说明：本项目定位为课程/毕业设计的本地演示，因此不引入 pyjwt / passlib /
bcrypt —— 全部用 Python 标准库实现：

- 密码：PBKDF2-HMAC-SHA256（见 data/database.py 的 hash_password）
- 令牌：base64url(payload) + "." + base64url(HMAC-SHA256)，含 exp，
  语义等价于精简版 JWT

修复前的状态：登录接口不下发任何凭证，前端把登录结果塞进 localStorage，
后续请求靠 URL 参数 user_id 表明身份；管理员判定是拿用户名跟
{"admin", "administrator", "管理员"} 做字符串比对，注册一个叫 admin 的
账号即可获得管理员角色。
"""

import base64
import hashlib
import hmac
import json
import os
import time

from fastapi import Header, HTTPException

TOKEN_TTL_SECONDS = 7 * 24 * 3600


class ConfigError(RuntimeError):
    pass


def _secret():
    """读取签名密钥。缺失时直接报错，不允许静默退化为默认值。"""
    key = os.environ.get("APP_SECRET_KEY", "").strip()
    if not key:
        raise ConfigError(
            "APP_SECRET_KEY 未配置。请在 backend/.env 中设置一个随机字符串，"
            "例如用 python -c \"import secrets;print(secrets.token_hex(32))\" 生成。"
        )
    if len(key) < 32:
        raise ConfigError("APP_SECRET_KEY 过短（至少 32 字符），当前长度 %d" % len(key))
    return key.encode("utf-8")


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64d(text: str) -> bytes:
    padding = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + padding)


def _sign(payload_b64: str) -> str:
    return _b64e(hmac.new(_secret(), payload_b64.encode("ascii"), hashlib.sha256).digest())


def create_token(user: dict, ttl=TOKEN_TTL_SECONDS) -> str:
    """为已通过密码校验的用户签发令牌。"""
    payload = {
        "uid": int(user["id"]),
        "username": user.get("username"),
        "role": user.get("role") or "user",
        "exp": int(time.time()) + int(ttl),
    }
    payload_b64 = _b64e(json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    return "%s.%s" % (payload_b64, _sign(payload_b64))


def verify_token(token: str):
    """校验令牌，返回 payload；无效或过期返回 None。"""
    if not token or "." not in token:
        return None
    payload_b64, _, signature = token.rpartition(".")
    try:
        expected = _sign(payload_b64)
    except ConfigError:
        raise
    if not hmac.compare_digest(expected, signature):
        return None
    try:
        payload = json.loads(_b64d(payload_b64))
    except (ValueError, TypeError):
        return None
    if not isinstance(payload, dict) or "uid" not in payload:
        return None
    if int(payload.get("exp", 0)) < int(time.time()):
        return None
    return payload


def _extract(authorization):
    if not authorization:
        return None
    parts = authorization.split(None, 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return authorization.strip()


async def get_current_user(authorization: str = Header(default=None)):
    """FastAPI 依赖：要求携带有效令牌，否则 401。"""
    payload = verify_token(_extract(authorization))
    if not payload:
        raise HTTPException(status_code=401, detail="未登录或登录已过期")
    return payload


async def get_optional_user(authorization: str = Header(default=None)):
    """FastAPI 依赖：有令牌就解析，没有也放行（用于可匿名浏览的接口）。"""
    return verify_token(_extract(authorization))


async def require_admin(authorization: str = Header(default=None)):
    """FastAPI 依赖：要求管理员。无令牌 401，非管理员 403。

    角色来自数据库 users.role 列，不再由用户名现算。
    """
    payload = verify_token(_extract(authorization))
    if not payload:
        raise HTTPException(status_code=401, detail="未登录或登录已过期")
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return payload


def current_user_id(user: dict) -> int:
    return int(user["uid"])


def assert_interview_owner(db, interview_id, user):
    """确认该面试属于当前用户，否则 404/403。返回面试记录以便复用。

    修复前 /api/interview/detail 等 9 个端点完全不校验归属，
    换个 interview_id 就能读到他人的面试全文、简历原文与评估报告。
    """
    interview = db.get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")
    if user.get("role") == "admin":
        return interview
    if int(interview.get("user_id") or 0) != current_user_id(user):
        raise HTTPException(status_code=403, detail="无权访问此面试记录")
    return interview
