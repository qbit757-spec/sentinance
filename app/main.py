import structlog
from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import setup_middleware
from app.core.events import register_event_handlers
from app.core.rate_limiter import limiter
from app.api.router import api_router

# Setup structured logging before anything else
setup_logging()
logger = structlog.get_logger()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# SlowAPI Rate Limiter mapping
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Setup middleware & event handlers
setup_middleware(app)
register_event_handlers(app)

# Include routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["health"])
async def health_check():
    logger.info("health_check_called")
    return {"status": "ok", "project_name": settings.PROJECT_NAME}
