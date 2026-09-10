"""统一异常处理。

修复前：4 个后端文件里有 154 处宽泛 `except Exception`，其中 71 处直接
`return {"error": str(e)}`，把 SQL 语句、文件路径、库内部信息回传给了浏览器。

现在：真实堆栈只进日志，客户端拿到的是通用文案 + 一个 trace_id，
出问题时用 trace_id 去日志里定位。
"""

import logging
import uuid

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("interview.errors")

GENERIC_MESSAGE = "服务器内部错误，请稍后重试"


def fail(message, trace_id=None, **extra):
    """业务层构造失败响应的统一入口，避免各处自行拼 str(e)。"""
    body = {"success": False, "status": "failed", "detail": message}
    if trace_id:
        body["trace_id"] = trace_id
    body.update(extra)
    return body


def log_exception(where, exc):
    """记录异常并返回 trace_id，供调用方放进响应体。"""
    trace_id = uuid.uuid4().hex[:12]
    logger.exception("[%s] %s: %s", trace_id, where, exc)
    return trace_id


def install_exception_handlers(app):
    @app.exception_handler(HTTPException)
    async def _http_exc(request: Request, exc: HTTPException):
        # 401/403/404 这类是明确的业务语义，原样透出
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "detail": exc.detail},
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_exc(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"success": False, "detail": "请求参数不合法"},
        )

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception):
        trace_id = log_exception("%s %s" % (request.method, request.url.path), exc)
        return JSONResponse(
            status_code=500,
            content={"success": False, "detail": GENERIC_MESSAGE, "trace_id": trace_id},
        )

    return app
