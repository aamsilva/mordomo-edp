"""
Structured JSON Logging Configuration for Mordomo MAS Gateway
"""

import logging
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from pythonjsonlogger import jsonlogger
from typing import Optional, Dict, Any
import os

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter for structured logging
    Adds timestamp, level, logger_name, request_id, and extra_data fields
    """
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Add ISO timestamp
        log_record['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add logger name
        log_record['logger'] = record.name
        
        # Add request_id if available in the LogRecord
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        else:
            log_record['request_id'] = None
        
        # Move 'extra' data to 'data' field if present
        if hasattr(record, 'data'):
            log_record['data'] = record.data
        
        # Rename 'message' to standard field
        if 'message' in log_record:
            log_record['message'] = log_record['message']


def configure_logging(
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True
) -> None:
    """
    Configure structured JSON logging for the application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
    """
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Create formatter
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(logger)s %(request_id)s %(message)s'
    )
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler
    if log_to_file:
        log_file = LOGS_DIR / "mordomo.log"
        file_handler = logging.FileHandler(str(log_file))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set specific log levels for noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    # Log configuration complete
    logger = logging.getLogger("mordomo")
    logger.info("Logging configured", extra={"data": {"log_level": log_level}})


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the mordomo. prefix
    
    Args:
        name: Logger name (e.g., 'gateway', 'billing_agent')
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(f"mordomo.{name}")


def generate_request_id() -> str:
    """Generate a unique request ID"""
    return f"req_{uuid.uuid4().hex[:12]}"


def generate_error_id() -> str:
    """Generate a unique error ID"""
    return f"err_{uuid.uuid4()}"


class ContextualLogger:
    """
    Wrapper for logger that automatically includes request_id in all log entries
    """
    
    def __init__(self, logger: logging.Logger, request_id: Optional[str] = None):
        self.logger = logger
        self.request_id = request_id or generate_request_id()
    
    def _log(self, level: int, msg: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Internal log method with context"""
        extra = extra or {}
        extra['request_id'] = self.request_id
        
        # Convert kwargs to data field
        if kwargs:
            extra['data'] = kwargs
        
        self.logger.log(level, msg, extra=extra)
    
    def debug(self, msg: str, **kwargs) -> None:
        self._log(logging.DEBUG, msg, **kwargs)
    
    def info(self, msg: str, **kwargs) -> None:
        self._log(logging.INFO, msg, **kwargs)
    
    def warning(self, msg: str, **kwargs) -> None:
        self._log(logging.WARNING, msg, **kwargs)
    
    def error(self, msg: str, **kwargs) -> None:
        self._log(logging.ERROR, msg, **kwargs)
    
    def critical(self, msg: str, **kwargs) -> None:
        self._log(logging.CRITICAL, msg, **kwargs)
    
    def get_request_id(self) -> str:
        return self.request_id


def get_contextual_logger(name: str, request_id: Optional[str] = None) -> ContextualLogger:
    """
    Get a contextual logger with automatic request_id tracking
    
    Args:
        name: Logger name
        request_id: Optional request ID (generated if not provided)
    
    Returns:
        ContextualLogger instance
    """
    logger = get_logger(name)
    return ContextualLogger(logger, request_id)