"""
Core specification models for pipeline configuration.

These Pydantic models define the configuration contracts for all pipeline
components, following the principle of separation between configuration
(what to do) and execution (how to do it).
"""

from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class DataSourceType(str, Enum):
    """Supported data source types."""

    CSV = "csv"
    EXCEL = "excel"
    PARQUET = "parquet"
    DATAFRAME = "dataframe"


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"


class ErrorPolicy(str, Enum):
    """Error handling policies for processing failures."""

    RETRY = "retry"
    SKIP = "skip"
    FAIL = "fail"
    USE_DEFAULT = "use_default"


class MergeStrategy(str, Enum):
    """Output merge strategies."""

    REPLACE = "replace"
    APPEND = "append"
    UPDATE = "update"


class DatasetSpec(BaseModel):
    """Specification for data source configuration."""

    source_type: DataSourceType
    source_path: Optional[Union[str, Path]] = None
    input_columns: List[str] = Field(
        ..., min_length=1, description="Columns to use as input"
    )
    output_columns: List[str] = Field(
        ..., min_length=1, description="Columns to store results"
    )
    filters: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional data filters"
    )
    sheet_name: Optional[Union[str, int]] = Field(
        default=0, description="Sheet name for Excel files"
    )
    delimiter: str = Field(default=",", description="CSV delimiter")
    encoding: str = Field(default="utf-8", description="File encoding")

    @field_validator("source_path")
    @classmethod
    def validate_source_path(
        cls, v: Optional[Union[str, Path]]
    ) -> Optional[Path]:
        """Convert string paths to Path objects."""
        if v is None:
            return None
        return Path(v) if isinstance(v, str) else v

    @field_validator("output_columns")
    @classmethod
    def validate_no_overlap(cls, v: List[str], info: Any) -> List[str]:
        """Ensure output columns don't overlap with input columns."""
        if "input_columns" in info.data:
            input_cols = set(info.data["input_columns"])
            output_cols = set(v)
            overlap = input_cols & output_cols
            if overlap:
                raise ValueError(
                    f"Output columns overlap with input: {overlap}"
                )
        return v


class PromptSpec(BaseModel):
    """Specification for prompt template configuration."""

    template: str = Field(..., min_length=1, description="Prompt template")
    system_message: Optional[str] = Field(
        default=None, description="System message for LLM"
    )
    few_shot_examples: Optional[List[Dict[str, str]]] = Field(
        default=None, description="Few-shot learning examples"
    )
    template_variables: Optional[List[str]] = Field(
        default=None, description="Expected template variables"
    )

    @field_validator("template")
    @classmethod
    def validate_template(cls, v: str) -> str:
        """Validate template has at least one variable."""
        if "{" not in v or "}" not in v:
            raise ValueError(
                "Template must contain at least one variable in {var} format"
            )
        return v


class LLMSpec(BaseModel):
    """Specification for LLM provider configuration."""

    provider: LLMProvider
    model: str = Field(..., min_length=1, description="Model identifier")
    api_key: Optional[str] = Field(
        default=None, description="API key (or from env)"
    )
    temperature: float = Field(
        default=0.0, ge=0.0, le=2.0, description="Sampling temperature"
    )
    max_tokens: Optional[int] = Field(
        default=None, gt=0, description="Max output tokens"
    )
    top_p: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Nucleus sampling"
    )
    
    # Azure-specific
    azure_endpoint: Optional[str] = Field(
        default=None, description="Azure OpenAI endpoint"
    )
    azure_deployment: Optional[str] = Field(
        default=None, description="Azure deployment name"
    )
    api_version: Optional[str] = Field(
        default="2024-02-15-preview", description="Azure API version"
    )
    
    # Cost tracking
    input_cost_per_1k_tokens: Optional[Decimal] = Field(
        default=None, description="Input token cost"
    )
    output_cost_per_1k_tokens: Optional[Decimal] = Field(
        default=None, description="Output token cost"
    )

    @field_validator("azure_endpoint", "azure_deployment")
    @classmethod
    def validate_azure_config(
        cls, v: Optional[str], info: Any
    ) -> Optional[str]:
        """Validate Azure-specific configuration."""
        if info.data.get("provider") == LLMProvider.AZURE_OPENAI:
            if v is None:
                field_name = info.field_name
                raise ValueError(
                    f"{field_name} required for Azure OpenAI provider"
                )
        return v


class ProcessingSpec(BaseModel):
    """Specification for processing parameters."""

    batch_size: int = Field(
        default=100, gt=0, le=1000, description="Rows per batch"
    )
    concurrency: int = Field(
        default=5, gt=0, le=20, description="Parallel requests"
    )
    checkpoint_interval: int = Field(
        default=500, gt=0, description="Checkpoint frequency"
    )
    max_retries: int = Field(
        default=3, ge=0, description="Max retry attempts"
    )
    retry_delay: float = Field(
        default=1.0, ge=0.0, description="Initial retry delay (seconds)"
    )
    error_policy: ErrorPolicy = Field(
        default=ErrorPolicy.SKIP, description="Error handling policy"
    )
    rate_limit_rpm: Optional[int] = Field(
        default=None, gt=0, description="Requests per minute limit"
    )
    max_budget: Optional[Decimal] = Field(
        default=None, gt=0, description="Maximum budget in USD"
    )
    checkpoint_dir: Path = Field(
        default=Path(".checkpoints"), description="Checkpoint directory"
    )

    @field_validator("checkpoint_dir")
    @classmethod
    def validate_checkpoint_dir(cls, v: Union[str, Path]) -> Path:
        """Convert string paths to Path objects."""
        return Path(v) if isinstance(v, str) else v


class OutputSpec(BaseModel):
    """Specification for output configuration."""

    destination_type: DataSourceType
    destination_path: Optional[Path] = None
    merge_strategy: MergeStrategy = Field(
        default=MergeStrategy.REPLACE, description="Output merge strategy"
    )
    atomic_write: bool = Field(
        default=True, description="Use atomic writes"
    )

    @field_validator("destination_path")
    @classmethod
    def validate_destination_path(
        cls, v: Optional[Union[str, Path]]
    ) -> Optional[Path]:
        """Convert string paths to Path objects."""
        if v is None:
            return None
        return Path(v) if isinstance(v, str) else v


class PipelineSpecifications(BaseModel):
    """Container for all pipeline specifications."""

    dataset: DatasetSpec
    prompt: PromptSpec
    llm: LLMSpec
    processing: ProcessingSpec = Field(default_factory=ProcessingSpec)
    output: Optional[OutputSpec] = None
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Custom metadata"
    )

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True
        validate_assignment = True

