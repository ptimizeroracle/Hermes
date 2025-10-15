"""
Structured logging utilities.

Provides consistent logging configuration across the SDK using structlog.
"""

import logging
import sys
from typing import Any, Dict, Optional

import structlog


def configure_logging(
    level: str = "INFO",
    json_format: bool = False,
    include_timestamp: bool = True,
) -> None:
    """
    Configure structured logging for the SDK.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON output format
        include_timestamp: Include timestamps in logs
    """
    # Set stdlib logging level
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )

    # Configure structlog processors
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
    ]

    if include_timestamp:
        processors.append(structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"))

    if json_format:
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Use ConsoleRenderer without padding
        processors.append(
            structlog.dev.ConsoleRenderer(
                pad_event=0,  # No padding on log levels
                colors=True,
            )
        )

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def sanitize_for_logging(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize sensitive data for logging.

    Args:
        data: Dictionary potentially containing sensitive data

    Returns:
        Sanitized dictionary
    """
    sensitive_keys = {
        "api_key",
        "password",
        "secret",
        "token",
        "authorization",
        "credential",
    }
    
    sanitized = {}
    for key, value in data.items():
        key_lower = key.lower()
        if any(sensitive in key_lower for sensitive in sensitive_keys):
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_for_logging(value)
        else:
            sanitized[key] = value
    
    return sanitized

