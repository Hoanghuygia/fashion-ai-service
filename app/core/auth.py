import secrets
from typing import Annotated

from fastapi import Depends, Header

from app.config import Settings, get_settings
from app.core.error_codes import ErrorCode
from app.core.exceptions import AppException

API_KEY_HEADER = "X-API-Key"


def require_api_key(
    settings: Annotated[Settings, Depends(get_settings)],
    x_api_key: Annotated[str | None, Header(alias=API_KEY_HEADER)] = None,
) -> None:
    """Guard for internal service-to-service calls.

    The Main Backend is the only trusted caller, so a single shared static key
    is sufficient. Compared in constant time to avoid timing oracles.
    """
    if x_api_key is None or not secrets.compare_digest(x_api_key, settings.internal_api_key):
        raise AppException(ErrorCode.UNAUTHORIZED, "Invalid or missing API key")
