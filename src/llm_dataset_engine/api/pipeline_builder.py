"""
Pipeline Builder - Fluent API for constructing pipelines.

Implements Builder pattern for intuitive pipeline creation.
"""

from decimal import Decimal
from pathlib import Path
from typing import List, Optional

import pandas as pd

from llm_dataset_engine.api.pipeline import Pipeline
from llm_dataset_engine.core.specifications import (
    DatasetSpec,
    DataSourceType,
    LLMProvider,
    LLMSpec,
    MergeStrategy,
    OutputSpec,
    PipelineSpecifications,
    ProcessingSpec,
    PromptSpec,
)
from llm_dataset_engine.orchestration import (
    AsyncExecutor,
    ExecutionStrategy,
    StreamingExecutor,
    SyncExecutor,
)


class PipelineBuilder:
    """
    Fluent builder for constructing pipelines.
    
    Provides an intuitive, chainable API for common use cases.
    
    Example:
        pipeline = (
            PipelineBuilder.create()
            .from_csv("data.csv", input_columns=["text"], output_columns=["result"])
            .with_prompt("Process: {text}")
            .with_llm(provider="openai", model="gpt-4o-mini")
            .build()
        )
    """

    def __init__(self):
        """Initialize builder with None values."""
        self._dataset_spec: Optional[DatasetSpec] = None
        self._prompt_spec: Optional[PromptSpec] = None
        self._llm_spec: Optional[LLMSpec] = None
        self._processing_spec: ProcessingSpec = ProcessingSpec()
        self._output_spec: Optional[OutputSpec] = None
        self._dataframe: Optional[pd.DataFrame] = None
        self._executor: Optional[ExecutionStrategy] = None

    @staticmethod
    def create() -> "PipelineBuilder":
        """
        Start builder chain.

        Returns:
            New PipelineBuilder instance
        """
        return PipelineBuilder()

    def from_csv(
        self,
        path: str,
        input_columns: List[str],
        output_columns: List[str],
        delimiter: str = ",",
        encoding: str = "utf-8",
    ) -> "PipelineBuilder":
        """
        Configure CSV data source.

        Args:
            path: Path to CSV file
            input_columns: Input column names
            output_columns: Output column names
            delimiter: CSV delimiter
            encoding: File encoding

        Returns:
            Self for chaining
        """
        self._dataset_spec = DatasetSpec(
            source_type=DataSourceType.CSV,
            source_path=Path(path),
            input_columns=input_columns,
            output_columns=output_columns,
            delimiter=delimiter,
            encoding=encoding,
        )
        return self

    def from_excel(
        self,
        path: str,
        input_columns: List[str],
        output_columns: List[str],
        sheet_name: str | int = 0,
    ) -> "PipelineBuilder":
        """
        Configure Excel data source.

        Args:
            path: Path to Excel file
            input_columns: Input column names
            output_columns: Output column names
            sheet_name: Sheet name or index

        Returns:
            Self for chaining
        """
        self._dataset_spec = DatasetSpec(
            source_type=DataSourceType.EXCEL,
            source_path=Path(path),
            input_columns=input_columns,
            output_columns=output_columns,
            sheet_name=sheet_name,
        )
        return self

    def from_parquet(
        self,
        path: str,
        input_columns: List[str],
        output_columns: List[str],
    ) -> "PipelineBuilder":
        """
        Configure Parquet data source.

        Args:
            path: Path to Parquet file
            input_columns: Input column names
            output_columns: Output column names

        Returns:
            Self for chaining
        """
        self._dataset_spec = DatasetSpec(
            source_type=DataSourceType.PARQUET,
            source_path=Path(path),
            input_columns=input_columns,
            output_columns=output_columns,
        )
        return self

    def from_dataframe(
        self,
        df: pd.DataFrame,
        input_columns: List[str],
        output_columns: List[str],
    ) -> "PipelineBuilder":
        """
        Configure DataFrame source.

        Args:
            df: Pandas DataFrame
            input_columns: Input column names
            output_columns: Output column names

        Returns:
            Self for chaining
        """
        self._dataset_spec = DatasetSpec(
            source_type=DataSourceType.DATAFRAME,
            input_columns=input_columns,
            output_columns=output_columns,
        )
        self._dataframe = df
        return self

    def with_prompt(
        self,
        template: str,
        system_message: Optional[str] = None,
    ) -> "PipelineBuilder":
        """
        Configure prompt template.

        Args:
            template: Prompt template with {variable} placeholders
            system_message: Optional system message

        Returns:
            Self for chaining
        """
        self._prompt_spec = PromptSpec(
            template=template,
            system_message=system_message,
        )
        return self

    def with_llm(
        self,
        provider: str,
        model: str,
        api_key: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        **kwargs: any,
    ) -> "PipelineBuilder":
        """
        Configure LLM provider.

        Args:
            provider: Provider name (openai, azure_openai, anthropic)
            model: Model identifier
            api_key: API key (or from env)
            temperature: Sampling temperature
            max_tokens: Max output tokens
            **kwargs: Provider-specific parameters

        Returns:
            Self for chaining
        """
        provider_enum = LLMProvider(provider.lower())
        
        self._llm_spec = LLMSpec(
            provider=provider_enum,
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        return self

    def with_batch_size(self, size: int) -> "PipelineBuilder":
        """
        Configure batch size.

        Args:
            size: Rows per batch

        Returns:
            Self for chaining
        """
        self._processing_spec.batch_size = size
        return self

    def with_concurrency(self, threads: int) -> "PipelineBuilder":
        """
        Configure concurrent requests.

        Args:
            threads: Number of concurrent threads

        Returns:
            Self for chaining
        """
        self._processing_spec.concurrency = threads
        return self

    def with_checkpoint_interval(self, rows: int) -> "PipelineBuilder":
        """
        Configure checkpoint frequency.

        Args:
            rows: Rows between checkpoints

        Returns:
            Self for chaining
        """
        self._processing_spec.checkpoint_interval = rows
        return self

    def with_rate_limit(self, rpm: int) -> "PipelineBuilder":
        """
        Configure rate limiting.

        Args:
            rpm: Requests per minute

        Returns:
            Self for chaining
        """
        self._processing_spec.rate_limit_rpm = rpm
        return self

    def with_max_budget(self, budget: float) -> "PipelineBuilder":
        """
        Configure maximum budget.

        Args:
            budget: Maximum budget in USD

        Returns:
            Self for chaining
        """
        self._processing_spec.max_budget = Decimal(str(budget))
        return self

    def with_output(
        self,
        path: str,
        format: str = "csv",
        merge_strategy: str = "replace",
    ) -> "PipelineBuilder":
        """
        Configure output destination.

        Args:
            path: Output file path
            format: Output format (csv, excel, parquet)
            merge_strategy: Merge strategy (replace, append, update)

        Returns:
            Self for chaining
        """
        format_map = {
            "csv": DataSourceType.CSV,
            "excel": DataSourceType.EXCEL,
            "parquet": DataSourceType.PARQUET,
        }
        
        merge_map = {
            "replace": MergeStrategy.REPLACE,
            "append": MergeStrategy.APPEND,
            "update": MergeStrategy.UPDATE,
        }
        
        self._output_spec = OutputSpec(
            destination_type=format_map[format.lower()],
            destination_path=Path(path),
            merge_strategy=merge_map[merge_strategy.lower()],
        )
        return self

    def with_executor(self, executor: ExecutionStrategy) -> "PipelineBuilder":
        """
        Set custom execution strategy.

        Args:
            executor: ExecutionStrategy instance

        Returns:
            Self for chaining
        """
        self._executor = executor
        return self

    def with_async_execution(
        self, max_concurrency: int = 10
    ) -> "PipelineBuilder":
        """
        Use async execution strategy.
        
        Enables async/await for non-blocking execution.
        Ideal for FastAPI, aiohttp, and async frameworks.

        Args:
            max_concurrency: Maximum concurrent async tasks

        Returns:
            Self for chaining
        """
        self._executor = AsyncExecutor(max_concurrency=max_concurrency)
        return self

    def with_streaming(self, chunk_size: int = 1000) -> "PipelineBuilder":
        """
        Use streaming execution strategy.
        
        Processes data in chunks for memory-efficient handling.
        Ideal for large datasets (100K+ rows).

        Args:
            chunk_size: Number of rows per chunk

        Returns:
            Self for chaining
        """
        self._executor = StreamingExecutor(chunk_size=chunk_size)
        return self

    def build(self) -> Pipeline:
        """
        Build final Pipeline.

        Returns:
            Configured Pipeline

        Raises:
            ValueError: If required specifications missing
        """
        # Validate required specs
        if not self._dataset_spec:
            raise ValueError("Dataset specification required")
        if not self._prompt_spec:
            raise ValueError("Prompt specification required")
        if not self._llm_spec:
            raise ValueError("LLM specification required")
        
        # Create specifications bundle
        specifications = PipelineSpecifications(
            dataset=self._dataset_spec,
            prompt=self._prompt_spec,
            llm=self._llm_spec,
            processing=self._processing_spec,
            output=self._output_spec,
        )
        
        # Create and return pipeline
        return Pipeline(
            specifications,
            dataframe=self._dataframe,
            executor=self._executor,
        )

