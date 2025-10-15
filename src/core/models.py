"""
Core data models for execution results and metadata.

These models represent the outputs and state information from pipeline
execution, following clean code principles with type safety.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

import pandas as pd


@dataclass
class LLMResponse:
    """Response from a single LLM invocation."""

    text: str
    tokens_in: int
    tokens_out: int
    model: str
    cost: Decimal
    latency_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CostEstimate:
    """Cost estimation for pipeline execution."""

    total_cost: Decimal
    total_tokens: int
    input_tokens: int
    output_tokens: int
    rows: int
    breakdown_by_stage: Dict[str, Decimal] = field(default_factory=dict)
    confidence: str = "estimate"  # estimate, sample-based, actual


@dataclass
class ProcessingStats:
    """Statistics from pipeline execution."""

    total_rows: int
    processed_rows: int
    failed_rows: int
    skipped_rows: int
    rows_per_second: float
    total_duration_seconds: float
    stage_durations: Dict[str, float] = field(default_factory=dict)


@dataclass
class ErrorInfo:
    """Information about an error during processing."""

    row_index: int
    stage_name: str
    error_type: str
    error_message: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Complete result from pipeline execution."""

    data: pd.DataFrame
    metrics: ProcessingStats
    costs: CostEstimate
    errors: List[ErrorInfo] = field(default_factory=list)
    execution_id: UUID = field(default_factory=uuid4)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    success: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        """Get execution duration in seconds."""
        if self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time).total_seconds()

    @property
    def error_rate(self) -> float:
        """Get error rate as percentage."""
        if self.metrics.total_rows == 0:
            return 0.0
        return (
            self.metrics.failed_rows / self.metrics.total_rows
        ) * 100


@dataclass
class ValidationResult:
    """Result from validation checks."""

    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)


@dataclass
class WriteConfirmation:
    """Confirmation of successful data write."""

    path: str
    rows_written: int
    success: bool
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CheckpointInfo:
    """Information about a checkpoint."""

    session_id: UUID
    checkpoint_path: str
    row_index: int
    stage_index: int
    timestamp: datetime
    size_bytes: int


@dataclass
class RowMetadata:
    """Metadata for a single row during processing."""

    row_index: int
    row_id: Optional[Any] = None
    batch_id: Optional[int] = None
    attempt: int = 1
    custom: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PromptBatch:
    """Batch of prompts for processing."""

    prompts: List[str]
    metadata: List[RowMetadata]
    batch_id: int


@dataclass
class ResponseBatch:
    """Batch of responses from LLM."""

    responses: List[str]
    metadata: List[RowMetadata]
    tokens_used: int
    cost: Decimal
    batch_id: int
    latencies_ms: List[float] = field(default_factory=list)

