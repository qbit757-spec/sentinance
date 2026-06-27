import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
import structlog
from app.core.config import settings

logger = structlog.get_logger()


async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    logger.info(
        "request_processed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration=f"{duration:.4f}s",
    )
    return response


def setup_middleware(app: FastAPI):
    # Logging Middleware
    app.middleware("http")(logging_middleware)

    # CORS Middleware
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Trusted Host Middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],  # configure strictly in production if needed
    )

    # Proxy Headers Middleware
    app.add_middleware(
        ProxyHeadersMiddleware,
        trusted_hosts=["*"],
    )
