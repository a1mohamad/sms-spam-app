from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.error_handlers import register_error_handlers
from app.api.routes import router
from app.core.startup import (
    create_predictor,
    validate_artifact_paths,
    warmup_predictor,
)
from app.middleware.request_id import RequestIDMiddleware


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
    app.state.predictor = predictor

    yield

    del app.state.predictor


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

    application.add_middleware(RequestIDMiddleware)
    register_error_handlers(application)
    application.include_router(router)

    return application


app = create_app()
