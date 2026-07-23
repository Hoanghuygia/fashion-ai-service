import logging
import time
import uuid
from collections.abc import MutableMapping

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.error_codes import ErrorCode
from app.core.responses import ErrorResponse

logger = logging.getLogger(__name__)

REQUEST_ID_HEADERS = (b"x-request-id", b"x-correlation-id")
RATE_LIMIT_EXCLUDED_PATHS = {"/health", "/docs", "/redoc", "/openapi.json"}


class RequestLoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)# Call next middleware or app if not an HTTP request
            return

        request_id = _request_id(scope)
        method = scope["method"]
        path = scope["path"]
        query = scope.get("query_string", b"").decode("latin-1")
        client = scope.get("client")
        client_ip = client[0] if client else None
        start = time.perf_counter()
        status_code = 500

        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "query": query,
                "client_ip": client_ip,
            },
        )

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code # indicate the variable is not local in nested function 
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode("latin-1")))
                message["headers"] = headers
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "duration_ms": round(duration_ms, 2),
                },
            )


class InMemoryRateLimitMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self._requests: dict[str, list[float]] = {}

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["path"] in RATE_LIMIT_EXCLUDED_PATHS:
            await self.app(scope, receive, send)
            return

        settings = scope["app"].state.settings
        if not settings.rate_limit_enabled:
            await self.app(scope, receive, send)
            return

        now = time.monotonic()
        window_start = now - settings.rate_limit_window_seconds
        client_key = _client_key(scope)
        timestamps = [
            seen_at for seen_at in self._requests.get(client_key, []) if seen_at > window_start
        ]

        if len(timestamps) >= settings.rate_limit_requests:
            error_code = ErrorCode.RATE_LIMIT_EXCEEDED
            response = JSONResponse(
                status_code=error_code.http_status,
                content=ErrorResponse(
                    message=error_code.default_message,
                    exceptionCode=error_code.code,
                ).model_dump(by_alias=True),
            )
            await response(scope, receive, send)
            return

        timestamps.append(now)
        self._requests[client_key] = timestamps
        await self.app(scope, receive, send)


def configure_middleware(app: FastAPI) -> None:
    settings = app.state.settings
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(InMemoryRateLimitMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )


def _request_id(scope: Scope) -> str:
    headers: MutableMapping[bytes, bytes] = dict(scope.get("headers", []))
    for header in REQUEST_ID_HEADERS:
        value = headers.get(header)
        if value:
            return value.decode("latin-1")
    return str(uuid.uuid4())


def _client_key(scope: Scope) -> str:
    headers: MutableMapping[bytes, bytes] = dict(scope.get("headers", []))
    forwarded_for = headers.get(b"x-forwarded-for")
    if forwarded_for:
        return forwarded_for.decode("latin-1").split(",", 1)[0].strip()
    client = scope.get("client")
    return client[0] if client else "unknown"
