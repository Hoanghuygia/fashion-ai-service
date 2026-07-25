from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.error_codes import ErrorCode
from app.core.exceptions import AppException
from app.core.responses import BaseResponse, success_response
from app.infrastructure.database.unit_of_work import UnitOfWork
from app.infrastructure.storage.s3_client import StorageClient
from app.modules.background_removal.schemas import (
    BackgroundRemovalRequest,
    BackgroundRemovalResponse,
)
from app.modules.background_removal.service import (
    BackgroundRemovalError,
    BackgroundRemovalService,
)

router = APIRouter(prefix="/background", tags=["Background Removal"])

PROCESSED_PREFIX = "ai-fashion/clothes/processed/"


def get_storage_client() -> StorageClient:
    return StorageClient.build()


def get_unit_of_work() -> UnitOfWork:
    return UnitOfWork()


def get_background_removal_service(
    storage_client: Annotated[StorageClient, Depends(get_storage_client)],
    uow: Annotated[UnitOfWork, Depends(get_unit_of_work)],
) -> BackgroundRemovalService:
    return BackgroundRemovalService(storage_client=storage_client, uow=uow)


@router.post("/remove", response_model=BaseResponse[BackgroundRemovalResponse])
def remove_background(
    request: BackgroundRemovalRequest,
    service: Annotated[BackgroundRemovalService, Depends(get_background_removal_service)],
) -> BaseResponse[BackgroundRemovalResponse]:
    try:
        return success_response(
            service.remove_background(
                image_id=request.image_id,
                processed_prefix=PROCESSED_PREFIX,
            )
        )
    except BackgroundRemovalError as exc:
        if str(exc) == "NOT_FOUND":
            raise AppException(ErrorCode.NOT_FOUND, "Image not found") from exc
        if str(exc) == "IMAGE_TOO_LARGE":
            raise AppException(ErrorCode.BAD_REQUEST, "Image is too large to process") from exc
        raise AppException(
            ErrorCode.INTERNAL_SERVER_ERROR,
            "Background removal failed",
        ) from exc
