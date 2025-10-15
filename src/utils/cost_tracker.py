"""
Cost tracking for LLM API calls.

Provides accurate cost tracking with thread safety and detailed breakdowns.
"""

import threading
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, Optional

from src.core.models import CostEstimate


@dataclass
class CostEntry:
    """Single cost tracking entry."""

    tokens_in: int
    tokens_out: int
    cost: Decimal
    model: str
    timestamp: float


class CostTracker:
    """
    Thread-safe cost tracker for LLM API usage.
    
    Follows single responsibility principle for cost accounting.
    """

    def __init__(
        self,
        input_cost_per_1k: Optional[Decimal] = None,
        output_cost_per_1k: Optional[Decimal] = None,
    ):
        """
        Initialize cost tracker.

        Args:
            input_cost_per_1k: Input token cost per 1K tokens
            output_cost_per_1k: Output token cost per 1K tokens
        """
        self.input_cost_per_1k = input_cost_per_1k or Decimal("0.0")
        self.output_cost_per_1k = output_cost_per_1k or Decimal("0.0")
        
        self._total_input_tokens = 0
        self._total_output_tokens = 0
        self._total_cost = Decimal("0.0")
        self._entries: list[CostEntry] = []
        self._stage_costs: Dict[str, Decimal] = {}
        self._lock = threading.Lock()

    def add(
        self,
        tokens_in: int,
        tokens_out: int,
        model: str,
        timestamp: float,
        stage: Optional[str] = None,
    ) -> Decimal:
        """
        Add cost entry.

        Args:
            tokens_in: Input tokens used
            tokens_out: Output tokens used
            model: Model identifier
            timestamp: Timestamp of request
            stage: Optional stage name

        Returns:
            Cost for this entry
        """
        cost = self.calculate_cost(tokens_in, tokens_out)
        
        with self._lock:
            entry = CostEntry(
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost=cost,
                model=model,
                timestamp=timestamp,
            )
            self._entries.append(entry)
            
            self._total_input_tokens += tokens_in
            self._total_output_tokens += tokens_out
            self._total_cost += cost
            
            if stage:
                self._stage_costs[stage] = (
                    self._stage_costs.get(stage, Decimal("0.0")) + cost
                )

        return cost

    def calculate_cost(self, tokens_in: int, tokens_out: int) -> Decimal:
        """
        Calculate cost for given token counts.

        Args:
            tokens_in: Input tokens
            tokens_out: Output tokens

        Returns:
            Total cost
        """
        input_cost = (Decimal(tokens_in) / 1000) * self.input_cost_per_1k
        output_cost = (Decimal(tokens_out) / 1000) * self.output_cost_per_1k
        return input_cost + output_cost

    @property
    def total_cost(self) -> Decimal:
        """Get total accumulated cost."""
        with self._lock:
            return self._total_cost

    @property
    def total_tokens(self) -> int:
        """Get total token count."""
        with self._lock:
            return self._total_input_tokens + self._total_output_tokens

    @property
    def input_tokens(self) -> int:
        """Get total input tokens."""
        with self._lock:
            return self._total_input_tokens

    @property
    def output_tokens(self) -> int:
        """Get total output tokens."""
        with self._lock:
            return self._total_output_tokens

    def get_estimate(self, rows: int = 0) -> CostEstimate:
        """
        Get cost estimate.

        Args:
            rows: Number of rows processed

        Returns:
            CostEstimate object
        """
        with self._lock:
            total_tokens = self._total_input_tokens + self._total_output_tokens
            return CostEstimate(
                total_cost=self._total_cost,
                total_tokens=total_tokens,
                input_tokens=self._total_input_tokens,
                output_tokens=self._total_output_tokens,
                rows=rows,
                breakdown_by_stage=dict(self._stage_costs),
                confidence="actual",
            )

    def reset(self) -> None:
        """Reset all tracking."""
        with self._lock:
            self._total_input_tokens = 0
            self._total_output_tokens = 0
            self._total_cost = Decimal("0.0")
            self._entries.clear()
            self._stage_costs.clear()

    def get_stage_costs(self) -> Dict[str, Decimal]:
        """Get costs breakdown by stage."""
        with self._lock:
            return dict(self._stage_costs)

