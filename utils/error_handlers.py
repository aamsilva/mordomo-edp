"""
FastAPI Exception Handlers for Mordomo MAS Gateway
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Type, Dict, Any
import logging

from .exceptions import (
    MordomoError,
    AgentNotFoundError,
    LLMError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    AgentProcessingError,
    RateLimitError,
    ExternalServiceError
)
from .logging_config import generate_error_id

logger = logging.getLogger("mordomo.error_handler")


def generate_error_response(
    error_code: str,
    message: str,
    status_code: int,
    error_id: str = None,
    details: Dict[str, Any] = None
) -> JSONResponse:
    """
    Generate standardized error response
    
    Args:
        error_code: Machine-readable error code
        message: Human-readable error message
        status_code: HTTP status code
        error_id: Unique error identifier
        details: Additional error details
    
    Returns:
        JSONResponse with standardized error format
    """
    error_id = error_id or generate_error_id()
    
    content = {
        "error": {
            "code": error_code,
            "message": message,
            "error_id": error_id
        }
    }
    
    if details:
        content["error"]["details"] = details
    
    return JSONResponse(
        status_code=status_code,
        content=content
    )


# Exception handlers

async def mordomo_exception_handler(request: Request, exc: MordomoError) -> JSONResponse:
    """Handler for all MordomoError subclasses"""
    
    error_id = exc.error_id or generate_error_id()
    
    # Log the error with context
    logger.error(
        f"MordomoError: {exc.error_code} - {exc.message}",
        extra={
            "data": {
                "error_code": exc.error_code,
                "error_id": error_id,
                "status_code": exc.status_code,
                "path": str(request.url.path),
                "method": request.method,
                "details": exc.details
            }
        }
    )
    
    return generate_error_response(
        error_code=exc.error_code,
        message=exc.message,
        status_code=exc.status_code,
        error_id=error_id,
        details=exc.details
    )


async def agent_not_found_handler(request: Request, exc: AgentNotFoundError) -> JSONResponse:
    """Handler for AgentNotFoundError"""
    return await mordomo_exception_handler(request, exc)


async def llm_error_handler(request: Request, exc: LLMError) -> JSONResponse:
    """Handler for LLMError"""
    return await mordomo_exception_handler(request, exc)


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handler for ValidationError"""
    return await mordomo_exception_handler(request, exc)


async def authentication_error_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
    """Handler for AuthenticationError"""
    return await mordomo_exception_handler(request, exc)


async def authorization_error_handler(request: Request, exc: AuthorizationError) -> JSONResponse:
    """Handler for AuthorizationError"""
    return await mordomo_exception_handler(request, exc)


async def agent_processing_error_handler(request: Request, exc: AgentProcessingError) -> JSONResponse:
    """Handler for AgentProcessingError"""
    return await mordomo_exception_handler(request, exc)


async def rate_limit_error_handler(request: Request, exc: RateLimitError) -> JSONResponse:
    """Handler for RateLimitError"""
    error_id = exc.error_id or generate_error_id()
    
    headers = {}
    if exc.details and "retry_after_seconds" in exc.details:
        headers["Retry-After"] = str(exc.details["retry_after_seconds"])
    
    logger.warning(
        f"RateLimitError: {exc.message}",
        extra={
            "data": {
                "error_id": error_id,
                "path": str(request.url.path),
                "method": request.method
            }
        }
    )
    
    response = generate_error_response(
        error_code=exc.error_code,
        message=exc.message,
        status_code=exc.status_code,
        error_id=error_id,
        details=exc.details
    )
    
    if headers:
        response.headers.update(headers)
    
    return response


async def external_service_error_handler(request: Request, exc: ExternalServiceError) -> JSONResponse:
    """Handler for ExternalServiceError"""
    return await mordomo_exception_handler(request, exc)


async def fastapi_validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handler for FastAPI's RequestValidationError (Pydantic validation)"""
    
    error_id = generate_error_id()
    
    # Extract field errors from Pydantic validation error
    field_errors = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error.get("loc", []))
        field_errors[field] = error.get("msg", "Invalid value")
    
    logger.warning(
        f"ValidationError: {len(field_errors)} field(s) invalid",
        extra={
            "data": {
                "error_id": error_id,
                "path": str(request.url.path),
                "method": request.method,
                "field_errors": field_errors
            }
        }
    )
    
    return generate_error_response(
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_id=error_id,
        details={"field_errors": field_errors}
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler for unhandled exceptions"""
    
    error_id = generate_error_id()
    
    logger.exception(
        f"Unhandled exception: {str(exc)}",
        extra={
            "data": {
                "error_id": error_id,
                "path": str(request.url.path),
                "method": request.method,
                "exception_type": type(exc).__name__
            }
        }
    )
    
    return generate_error_response(
        error_code="INTERNAL_ERROR",
        message="An unexpected error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_id=error_id
    )


def register_exception_handlers(app):
    """
    Register all exception handlers with a FastAPI application
    
    Args:
        app: FastAPI application instance
    """
    
    # Register custom exception handlers
    app.add_exception_handler(AgentNotFoundError, agent_not_found_handler)
    app.add_exception_handler(LLMError, llm_error_handler)
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(AuthenticationError, authentication_error_handler)
    app.add_exception_handler(AuthorizationError, authorization_error_handler)
    app.add_exception_handler(AgentProcessingError, agent_processing_error_handler)
    app.add_exception_handler(RateLimitError, rate_limit_error_handler)
    app.add_exception_handler(ExternalServiceError, external_service_error_handler)
    
    # Register base MordomoError handler (catches any unregistered subclass)
    app.add_exception_handler(MordomoError, mordomo_exception_handler)
    
    # Register FastAPI/Pydantic validation error handler
    app.add_exception_handler(RequestValidationError, fastapi_validation_handler)
    
    # Register catch-all for unhandled exceptions
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("Exception handlers registered")