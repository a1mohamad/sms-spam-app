"""Centralized exception logging and safe HTTP error responses."""

import logging
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.errors import (
    DatabaseUnavailableError,
    PersistenceError,
    PredictionError,
)


logger = logging.getLogger(__name__)


def _error_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    message: str,
) -> JSONResponse:
    """Build the standard API error response.

    Args:
        request: Request whose correlation ID should be included.
        status_code: HTTP status code returned to the client.
        code: Stable, machine-readable error identifier.
        message: Safe, human-readable explanation of the failure.

    Returns:
        JSON response containing the error details and correlation ID.
    """
    # The middleware normally supplies this ID; the fallback keeps the helper
    # safe when it is used without that middleware, such as in an isolated test.
    request_id = getattr(request.state, "request_id", None) or str(uuid4())
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": request_id,
            }
        },
        headers={"X-Request-ID": request_id},
    )


async def prediction_error_handler(
    request: Request,
    exc: PredictionError,
) -> JSONResponse:
    """Handle a known model inference failure.

    Args:
        request: Request being processed when inference failed.
        exc: Application-level prediction exception to log.

    Returns:
        Retryable HTTP 503 response without internal exception details.
    """
    # Preserve the traceback in server logs while keeping it out of the client
    # response. The request ID connects that response to this log record.
    logger.warning(
        "Prediction failed",
        exc_info=(type(exc), exc, exc.__traceback__),
        extra={"request_id": request.state.request_id},
    )
    return _error_response(
        request,
        status_code=503,
        code="prediction_unavailable",
        message="Prediction is temporarily unavailable. Please try again.",
    )


async def persistence_error_handler(
    request: Request,
    exc: PersistenceError,
) -> JSONResponse:
    """Handle a known prediction-storage failure.

    Args:
        request: Request being processed when persistence failed.
        exc: Application-level persistence exception to log.

    Returns:
        Retryable HTTP 503 response without database details.
    """
    logger.error(
        "Prediction persistence failed",
        exc_info=(type(exc), exc, exc.__traceback__),
        extra={"request_id": request.state.request_id},
    )
    return _error_response(
        request,
        status_code=503,
        code="persistence_unavailable",
        message=(
            "Prediction storage is temporarily unavailable. "
            "Please try again."
        ),
    )


async def database_unavailable_error_handler(
    request: Request,
    exc: DatabaseUnavailableError,
) -> JSONResponse:
    """Handle a failed readiness check without exposing connection details."""
    logger.error(
        "Database readiness check failed",
        exc_info=(type(exc), exc, exc.__traceback__),
        extra={"request_id": request.state.request_id},
    )
    return _error_response(
        request,
        status_code=503,
        code="database_unavailable",
        message="The database is temporarily unavailable.",
    )


async def unexpected_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle an unexpected exception that escaped request processing.

    Args:
        request: Request being processed when the exception occurred.
        exc: Unhandled exception to record for investigation.

    Returns:
        Generic HTTP 500 response that does not expose sensitive details.
    """
    # Unknown failures need the full traceback for diagnosis, but clients
    # receive only a stable error code and a safe generic message.
    logger.error(
        "Unhandled request error",
        exc_info=(type(exc), exc, exc.__traceback__),
        extra={"request_id": request.state.request_id},
    )
    return _error_response(
        request,
        status_code=500,
        code="internal_error",
        message="An unexpected error occurred.",
    )


def register_error_handlers(app: FastAPI) -> None:
    """Register the application's centralized exception handlers.

    Args:
        app: FastAPI application on which to register the handlers.
    """
    # FastAPI selects the specific handler before falling back to Exception.
    app.add_exception_handler(PredictionError, prediction_error_handler)
    app.add_exception_handler(PersistenceError, persistence_error_handler)
    app.add_exception_handler(
        DatabaseUnavailableError,
        database_unavailable_error_handler,
    )
    app.add_exception_handler(Exception, unexpected_error_handler)
