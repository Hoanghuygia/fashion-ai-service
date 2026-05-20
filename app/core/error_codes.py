from enum import Enum

from starlette import status


class ErrorCode(Enum):
    INTERNAL_SERVER_ERROR = (
        "INTERNAL.001",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "Internal server error",
    )
    VALIDATION_ERROR = (
        "VALIDATION.001",
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "Validation error",
    )
    NOT_FOUND = ("COMMON.404", status.HTTP_404_NOT_FOUND, "Resource not found")
    BAD_REQUEST = ("COMMON.400", status.HTTP_400_BAD_REQUEST, "Bad request")
    RATE_LIMIT_EXCEEDED = (
        "RATE_LIMIT.001",
        status.HTTP_429_TOO_MANY_REQUESTS,
        "Rate limit exceeded",
    )
    UNAUTHORIZED = ("AUTH.401", status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    FORBIDDEN = ("AUTH.403", status.HTTP_403_FORBIDDEN, "Forbidden")

    def __init__(self, code: str, http_status: int, default_message: str) -> None:
        self.code = code
        self.http_status = http_status
        self.default_message = default_message
