import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    logger.info("Application starting")
    logger.info("Application started")

    try:
        yield
    finally:
        logger.info("Application shutting down")
        logger.info("Application shutdown complete")
