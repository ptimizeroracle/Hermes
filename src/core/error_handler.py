"""
Error handling system with configurable policies.

Implements Strategy pattern for different error handling approaches.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional

from src.core.specifications import ErrorPolicy
from src.utils import get_logger

logger = get_logger(__name__)


class ErrorAction(str, Enum):
    """Actions to take on errors."""

    RETRY = "retry"
    SKIP = "skip"
    FAIL = "fail"
    USE_DEFAULT = "use_default"


@dataclass
class ErrorDecision:
    """Decision on how to handle an error."""

    action: ErrorAction
    default_value: Any = None
    retry_count: int = 0
    context: dict[str, Any] | None = None


class ErrorHandler:
    """
    Handles errors according to configured policies.
    
    Follows Strategy pattern for pluggable error handling logic.
    """

    def __init__(
        self,
        policy: ErrorPolicy = ErrorPolicy.SKIP,
        max_retries: int = 3,
        default_value_factory: Optional[Callable[[], Any]] = None,
    ):
        """
        Initialize error handler.

        Args:
            policy: Error handling policy
            max_retries: Maximum retry attempts
            default_value_factory: Function to generate default values
        """
        self.policy = policy
        self.max_retries = max_retries
        self.default_value_factory = default_value_factory or (
            lambda: None
        )

    def handle_error(
        self,
        error: Exception,
        context: dict[str, Any],
        attempt: int = 1,
    ) -> ErrorDecision:
        """
        Decide how to handle an error.

        Args:
            error: The exception that occurred
            context: Error context (row_index, stage, etc.)
            attempt: Current attempt number

        Returns:
            ErrorDecision with action to take
        """
        row_index = context.get("row_index", "unknown")
        stage = context.get("stage", "unknown")
        
        # Log the error
        logger.error(
            f"Error in {stage} at row {row_index}: {error}",
            exc_info=True,
        )

        # Apply policy
        if self.policy == ErrorPolicy.RETRY:
            if attempt < self.max_retries:
                logger.info(
                    f"Retrying (attempt {attempt + 1}/{self.max_retries})"
                )
                return ErrorDecision(
                    action=ErrorAction.RETRY,
                    retry_count=attempt + 1,
                    context=context,
                )
            else:
                logger.warning(
                    f"Max retries ({self.max_retries}) exceeded, skipping"
                )
                return ErrorDecision(
                    action=ErrorAction.SKIP,
                    context=context,
                )

        elif self.policy == ErrorPolicy.SKIP:
            logger.info(f"Skipping row {row_index} due to error")
            return ErrorDecision(
                action=ErrorAction.SKIP,
                context=context,
            )

        elif self.policy == ErrorPolicy.USE_DEFAULT:
            default = self.default_value_factory()
            logger.info(
                f"Using default value for row {row_index}: {default}"
            )
            return ErrorDecision(
                action=ErrorAction.USE_DEFAULT,
                default_value=default,
                context=context,
            )

        elif self.policy == ErrorPolicy.FAIL:
            logger.error("Failing pipeline due to error")
            return ErrorDecision(
                action=ErrorAction.FAIL,
                context=context,
            )

        else:
            # Unknown policy, default to fail
            return ErrorDecision(
                action=ErrorAction.FAIL,
                context=context,
            )

    def should_retry(self, error: Exception) -> bool:
        """
        Determine if error should be retried.

        Args:
            error: The exception

        Returns:
            True if retriable
        """
        retriable_keywords = [
            "rate limit",
            "timeout",
            "network",
            "connection",
            "503",
            "502",
            "429",
        ]
        
        error_str = str(error).lower()
        return any(keyword in error_str for keyword in retriable_keywords)

