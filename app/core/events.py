import structlog
from fastapi import FastAPI
from app.db.init_db import init_db

logger = structlog.get_logger()


def register_event_handlers(app: FastAPI):
    @app.on_event("startup")
    async def startup_event():
        logger.info("application_startup")
        await init_db()

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("application_shutdown")
