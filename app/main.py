from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import AppConfig
from app.db.session import database
from app.security.message_cipher import MessageCipher
from app.api.error_handlers import register_error_handlers
from app.api.routes import router
from app.core.startup import (
    create_predictor,
    validate_artifact_paths,
    warmup_predictor,
)
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.request_body_limit import RequestBodyLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown.

    Args:
        app: FastAPI application instance.

    Yields:
        Control while the application serves requests.
    """
    validate_artifact_paths()

    predictor = create_predictor()
    warmup_predictor(predictor)

    # Validate the encryption key during startup instead of failing on
    # the first prediction request.
    message_cipher = MessageCipher(
        AppConfig.get_message_encryption_key()
    )

    app.state.predictor = predictor
    app.state.message_cipher = message_cipher

    try:
        yield
    finally:
        del app.state.predictor
        del app.state.message_cipher

        # Close pooled database connections during application shutdown.
        database.dispose()

def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured application with lifecycle management, middleware,
        exception handlers, and API routes registered.
    """
    application = FastAPI(
        title="SMS Spam Classifier",
        description="API for classifying SMS messages as ham or spam.",
        version="1.0.0",
        lifespan=lifespan,
    )

    # The request-ID layer remains outermost so even size-limit failures carry
    # the same correlation ID in their response body and header.
    application.add_middleware(
        RequestBodyLimitMiddleware,
        max_body_bytes=AppConfig.MAX_REQUEST_BODY_BYTES,
    )
    application.add_middleware(RequestIDMiddleware)
    register_error_handlers(application)
    application.include_router(router)

    return application


app = create_app()
