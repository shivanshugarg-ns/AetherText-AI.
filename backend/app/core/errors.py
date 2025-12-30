import logging
from typing import Optional

from fastapi import HTTPException, status
from pydantic import ValidationError

from app.models.responses import ErrorInfo, ErrorResponse

logger = logging.getLogger(__name__)


class OpenAIFallbackError(Exception):
    def __init__(self, message: str = "Both primary and fallback models failed."):
        super().__init__(message)
        self.message = message


def map_exception(exc: Exception) -> HTTPException:
    # Validation from Pydantic
    if isinstance(exc, ValidationError):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ErrorResponse(
                error=ErrorInfo(
                    type="validation_error",
                    message="Validation failed",
                    detail=str(exc),
                    retryable=False,
                )
            ).dict(),
        )

    if isinstance(exc, HTTPException):
        return exc

    if isinstance(exc, OpenAIFallbackError):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ErrorResponse(
                error=ErrorInfo(
                    type="openai_fallback_failed",
                    message=exc.message,
                    retryable=True,
                )
            ).dict(),
        )

    # Default catch-all
    logger.exception("Unhandled exception", exc_info=exc)
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=ErrorResponse(
            error=ErrorInfo(
                type="internal_error",
                message="Unexpected server error",
                retryable=True,
                detail=str(exc),
            )
        ).dict(),
    )
