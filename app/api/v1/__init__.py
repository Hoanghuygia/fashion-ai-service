from fastapi import APIRouter, Depends

from app.api.v1.background_routes import router as background_router
from app.core.auth import require_api_key

router = APIRouter(prefix="/api/v1", dependencies=[Depends(require_api_key)])
router.include_router(background_router)
