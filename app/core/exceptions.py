import traceback
from collections.abc import Awaitable, Callable
from typing import Any, cast

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.error_codes import ErrorCode
from app.core.responses import ErrorResponse

ExceptionHandler = Callable[[Request, Exception], Awaitable[Response]]


class AppException(Exception):
    def __init__(
        self,
        error_code: ErrorCode,
        message: str | None = None,
        details: Any | None = None,
    ) -> None:
        self.error_code = error_code
        self.message = message or error_code.default_message
        self.details = details
        super().__init__(self.message)


def _is_debug(request: Request) -> bool:
    settings = getattr(request.app.state, "settings", None)
    return bool(getattr(settings, "debug", False))


def _stack_trace(exc: Exception, debug: bool) -> str | None:
    if not debug:
        return None
    return "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))


def _error_payload(
    *,
    message: str,
    exception_code: str,
    stack_trace: str | None,
) -> dict[str, object]:
    return ErrorResponse(
        message=message,
        stackTrace=stack_trace,
        exceptionCode=exception_code,
    ).model_dump(by_alias=True)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.error_code.http_status,
        content=_error_payload(
            message=exc.message,
            exception_code=exc.error_code.code,
            stack_trace=_stack_trace(exc, _is_debug(request)),
        ),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    error_code = ErrorCode.VALIDATION_ERROR
    return JSONResponse(
        status_code=error_code.http_status,
        content=_error_payload(
            message=error_code.default_message,
            exception_code=error_code.code,
            stack_trace=_stack_trace(exc, _is_debug(request)),
        ),
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    error_code = _error_code_for_status(exc.status_code)
    detail = exc.detail if isinstance(exc.detail, str) else error_code.default_message
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(
            message=detail,
            exception_code=error_code.code,
            stack_trace=_stack_trace(exc, _is_debug(request)),
        ),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    error_code = ErrorCode.INTERNAL_SERVER_ERROR
    debug = _is_debug(request)
    return JSONResponse(
        status_code=error_code.http_status,
        content=_error_payload(
            message=str(exc) if debug else error_code.default_message,
            exception_code=error_code.code,
            stack_trace=_stack_trace(exc, debug),
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, cast(ExceptionHandler, app_exception_handler))
    app.add_exception_handler(
        RequestValidationError,
        cast(ExceptionHandler, validation_exception_handler),
    )
    app.add_exception_handler(
        StarletteHTTPException,
        cast(ExceptionHandler, http_exception_handler),
    )
    app.add_exception_handler(Exception, generic_exception_handler)


def _error_code_for_status(status_code: int) -> ErrorCode:
    return {
        400: ErrorCode.BAD_REQUEST,
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.NOT_FOUND,
        429: ErrorCode.RATE_LIMIT_EXCEEDED,
    }.get(status_code, ErrorCode.INTERNAL_SERVER_ERROR)
