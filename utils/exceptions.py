"""
Custom Exceptions for Mordomo MAS Gateway
"""

from typing import Optional, Dict, Any
import traceback


class MordomoError(Exception):
    """
    Base exception for all Mordomo errors
    """
    
    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"
    
    def __init__(
        self,
        message: str,
        error_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_id = error_id
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to JSON-serializable dict"""
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "error_id": self.error_id,
                "details": self.details if self.details else None
            }
        }


class AgentNotFoundError(MordomoError):
    """
    Raised when requested agent is not found
    HTTP 404
    """
    
    status_code = 404
    error_code = "AGENT_NOT_FOUND"
    
    def __init__(self, agent_name: str, error_id: Optional[str] = None):
        super().__init__(
            message=f"Agent '{agent_name}' not found",
            error_id=error_id,
            details={"requested_agent": agent_name}
        )


class LLMError(MordomoError):
    """
    Raised when LLM service fails
    HTTP 502
    """
    
    status_code = 502
    error_code = "LLM_ERROR"
    
    def __init__(
        self,
        message: str = "LLM service error",
        error_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_id=error_id,
            details=details
        )


class ValidationError(MordomoError):
    """
    Raised when request validation fails
    HTTP 422
    """
    
    status_code = 422
    error_code = "VALIDATION_ERROR"
    
    def __init__(
        self,
        message: str = "Validation error",
        error_id: Optional[str] = None,
        field_errors: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            message=message,
            error_id=error_id,
            details={"field_errors": field_errors} if field_errors else None
        )


class AuthenticationError(MordomoError):
    """
    Raised when authentication fails
    HTTP 401
    """
    
    status_code = 401
    error_code = "AUTHENTICATION_ERROR"
    
    def __init__(
        self,
        message: str = "Authentication failed",
        error_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_id=error_id,
            details=details
        )


class AuthorizationError(MordomoError):
    """
    Raised when user lacks permission
    HTTP 403
    """
    
    status_code = 403
    error_code = "AUTHORIZATION_ERROR"
    
    def __init__(
        self,
        message: str = "Access denied",
        error_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_id=error_id,
            details=details
        )


class AgentProcessingError(MordomoError):
    """
    Raised when agent fails to process a request
    HTTP 500
    """
    
    status_code = 500
    error_code = "AGENT_PROCESSING_ERROR"
    
    def __init__(
        self,
        agent_name: str,
        message: str = "Agent processing failed",
        error_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details["agent"] = agent_name
        super().__init__(
            message=message,
            error_id=error_id,
            details=details
        )


class RateLimitError(MordomoError):
    """
    Raised when rate limit is exceeded
    HTTP 429
    """
    
    status_code = 429
    error_code = "RATE_LIMIT_EXCEEDED"
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        error_id: Optional[str] = None,
        retry_after: Optional[int] = None
    ):
        details = {}
        if retry_after:
            details["retry_after_seconds"] = retry_after
        super().__init__(
            message=message,
            error_id=error_id,
            details=details if details else None
        )


class ExternalServiceError(MordomoError):
    """
    Raised when external service (EDP API, etc.) fails
    HTTP 503
    """
    
    status_code = 503
    error_code = "EXTERNAL_SERVICE_ERROR"
    
    def __init__(
        self,
        service_name: str,
        message: str = "External service error",
        error_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details["service"] = service_name
        super().__init__(
            message=message,
            error_id=error_id,
            details=details
        )