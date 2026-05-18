from fastapi import FastAPI

from app.api.v1.background_routes import router as background_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.include_router(background_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": settings.app_name, "status": "ok"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
