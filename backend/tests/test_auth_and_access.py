"""鉴权与越权访问的回归测试。

每条用例对应一个修复前可复现的真实漏洞，注释里写明了修复前的行为。
"""

import sqlite3

from conftest import login


# ---------- 密码存储 ----------

def test_密码不再明文存储(app_env):
    """修复前：users.password 存明文，login 用 WHERE password = ? 直接比对。"""
    conn = sqlite3.connect(app_env["db_path"])
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT username, password, password_hash, password_salt FROM users").fetchall()
    conn.close()

    assert rows, "库里应有种子用户"
    for row in rows:
        assert not row["password"], "%s 仍存有明文密码" % row["username"]
        assert row["password_hash"] and len(row["password_hash"]) == 64
        assert row["password_salt"]


def test_正确密码可登录_错误密码被拒(client):
    headers, data = login(client, "alice", "alice-pw-123")
    assert data["role"] == "user"

    bad = client.post("/api/auth/login", json={"username": "alice", "password": "wrong-pw"})
    assert bad.json()["success"] is False


def test_接口不回传口令字段(client, alice_auth):
    """修复前：get_user_by_id 用 SELECT *，/api/user/info 把 password 一起返回。"""
    resp = client.post("/api/user/info", headers=alice_auth)
    assert resp.status_code == 200
    assert not any("password" in key for key in resp.json())


# ---------- 角色 ----------

def test_用户名叫admin不再等于管理员(client):
    """修复前：role = "admin" if username.lower() in {"admin","administrator","管理员"}。"""
    resp = client.post(
        "/api/auth/register",
        json={"username": "administrator", "password": "pw-123456", "email": "adm@test.local"},
    )
    assert resp.status_code == 200
    assert resp.json()["role"] == "user"


def test_注册接口不接受角色参数(client):
    resp = client.post(
        "/api/auth/register",
        json={"username": "wannabe", "password": "pw-123456", "email": "w@test.local", "role": "admin"},
    )
    assert resp.json()["role"] == "user"


# ---------- 管理端鉴权 ----------

def test_管理端接口无令牌返回401(client):
    """修复前：16 个 /api/admin/* 全部零鉴权，curl 即可拉全部用户、删号。"""
    for path in ("/api/admin/users", "/api/admin/stats", "/api/admin/interviews"):
        assert client.get(path).status_code == 401, path


def test_管理端接口普通用户返回403(client, alice_auth):
    assert client.get("/api/admin/users", headers=alice_auth).status_code == 403


def test_管理员可正常访问(client, admin_auth):
    resp = client.get("/api/admin/users", headers=admin_auth)
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_管理端用户搜索带关键词不再报错(client, admin_auth):
    """修复前：COUNT 查询拼了 2 个占位符却没传参，必抛 ProgrammingError。"""
    resp = client.get("/api/admin/users?keyword=ali", headers=admin_auth)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True, body
    assert body["total"] >= 1


# ---------- 越权 ----------

def test_不能读他人面试(client, alice_auth, app_env):
    """修复前：/api/interview/detail 完全不校验归属，换个 id 就能读全文。"""
    bob_interview = app_env["seed"]["interviews"]["bob"]
    resp = client.get("/api/interview/detail?interview_id=%d" % bob_interview, headers=alice_auth)
    assert resp.status_code == 403


def test_无令牌不能读面试(client, app_env):
    bob_interview = app_env["seed"]["interviews"]["bob"]
    assert client.get("/api/interview/detail?interview_id=%d" % bob_interview).status_code == 401


def test_可以读自己的面试(client, alice_auth, app_env):
    mine = app_env["seed"]["interviews"]["alice"]
    assert client.get("/api/interview/detail?interview_id=%d" % mine, headers=alice_auth).status_code == 200


def test_伪造user_id无效(client, alice_auth, app_env):
    """修复前：身份靠 URL 参数 user_id 自称，改成别人的 id 即可读他人历史。"""
    bob_id = app_env["seed"]["bob"]
    resp = client.get("/api/interview/history?user_id=%d" % bob_id, headers=alice_auth)
    assert resp.status_code == 200
    returned = resp.json()["interviews"]
    assert all(item.get("user_id") in (None, app_env["seed"]["alice"]) for item in returned), returned


def test_不能删他人面试(client, alice_auth, app_env):
    bob_interview = app_env["seed"]["interviews"]["bob"]
    bob_id = app_env["seed"]["bob"]
    resp = client.delete(
        "/api/interview/delete?interview_id=%d&user_id=%d" % (bob_interview, bob_id),
        headers=alice_auth,
    )
    assert resp.status_code == 403


# ---------- 能力画像端点拆分 ----------

def test_普通用户可看自己的能力画像(client, alice_auth):
    assert client.get("/api/user/ability-profile", headers=alice_auth).status_code == 200


def test_普通用户不能走管理端看他人画像(client, alice_auth):
    """修复前：前端「个人能力画像」页直接调管理端接口，且改 id 可读他人。"""
    assert client.get("/api/admin/user/1/ability-profile", headers=alice_auth).status_code == 403


def test_能力画像无令牌返回401(client):
    assert client.get("/api/user/ability-profile").status_code == 401


# ---------- 删除返回值 ----------

def test_删除面试返回结构化结果(client, alice_auth, app_env):
    """修复前：函数算完 success 就结束，没有 return，接口返回字面量 null。"""
    mine = app_env["seed"]["interviews"]["alice"]
    resp = client.delete(
        "/api/interview/delete?interview_id=%d&user_id=%d" % (mine, app_env["seed"]["alice"]),
        headers=alice_auth,
    )
    assert resp.status_code == 200
    assert resp.json().get("success") is True


# ---------- 异常不外泄内部信息 ----------

def test_错误响应不包含内部细节(client, alice_auth):
    resp = client.get("/api/interview/detail?interview_id=999999", headers=alice_auth)
    body = resp.text
    for leak in ("Traceback", "sqlite3", "SELECT ", "D:\\\\", "site-packages"):
        assert leak not in body, "响应疑似外泄内部信息: %s" % body[:200]
