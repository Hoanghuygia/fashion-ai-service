from fastapi import APIRouter

from app.api.v1.background_routes import router as background_router

router = APIRouter(prefix="/api/v1")
router.include_router(background_router)
