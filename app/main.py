from fastapi import FastAPI

from app.api.v1 import router as v1_router
from app.config import get_settings
from app.config.settings import Settings
from app.core.exceptions import register_exception_handlers
from app.core.lifespan import lifespan
from app.core.middleware import configure_middleware
from app.core.responses import BaseResponse, success_response

settings = get_settings()


OPENAPI_TAGS = [
    {"name": "Health", "description": "Service health and metadata endpoints."},
    {"name": "AI Metadata", "description": "Clothing metadata extraction endpoints."},
    {"name": "Background Removal", "description": "Image background removal endpoints."},
    {"name": "Outfit Recommendation", "description": "Outfit recommendation endpoints."},
]


def create_app(app_settings: Settings | None = None) -> FastAPI:
    resolved_settings = app_settings or get_settings()
    application = FastAPI(
        title=resolved_settings.app_name,
        description=resolved_settings.app_description,
        version=resolved_settings.app_version,
        debug=resolved_settings.debug,
        docs_url=resolved_settings.docs_url,
        redoc_url=resolved_settings.redoc_url,
        openapi_url=resolved_settings.openapi_url,
        openapi_tags=OPENAPI_TAGS,
        lifespan=lifespan,
    )
    application.state.settings = resolved_settings
    register_exception_handlers(application)
    configure_middleware(application)
    application.include_router(v1_router)
    register_root_routes(application, resolved_settings)
    return application


def register_root_routes(application: FastAPI, app_settings: Settings) -> None:
    @application.get("/", response_model=BaseResponse[dict[str, str]])
    def root() -> BaseResponse[dict[str, str]]:
        return success_response({"service": app_settings.app_name, "status": "ok"})

    @application.get("/health", tags=["Health"], response_model=BaseResponse[dict[str, str]])
    def health() -> BaseResponse[dict[str, str]]:
        return success_response({"status": "ok"})


app = create_app(settings)
