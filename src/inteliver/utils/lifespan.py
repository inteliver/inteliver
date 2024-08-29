from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from inteliver.database.postgres import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await on_startup(app)
    yield
    await on_shutdown(app)


async def on_startup(app: FastAPI):
    """
    Executes startup tasks for the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    logger.info("Starting up the app...")
    # Register to services that needs to be created on startup
    try:
        await init_db()
    except Exception as e:
        logger.error(f"Error on initializing postgres db. detail: {e}")
    return app


async def on_shutdown(app: FastAPI) -> None:
    """
    Executes shutdown tasks for the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    logger.info("Shutting down gracefully...")
    # Unregister any service that needs to be gracefully shut down
