import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Application starting")
    app.state.ai_models = None
    app.state.redis = None
    app.state.database = None
    app.state.storage = None
    app.state.worker_resources = None
    logger.info("Application started")
    try:
        yield
    finally:
        logger.info("Application shutting down")
        logger.info("Application shutdown complete")
