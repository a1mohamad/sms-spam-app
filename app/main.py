from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.startup import (
    create_predictor,
    validate_artifact_paths,
    warmup_predictor,
)


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


app = FastAPI(
    title="SMS Spam Classifier",
    description="API for classifying SMS messages as ham or spam.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)