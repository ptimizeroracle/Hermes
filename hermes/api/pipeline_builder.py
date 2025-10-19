"""
Pipeline Builder - Fluent API for constructing pipelines.

Implements Builder pattern for intuitive pipeline creation.
"""

from decimal import Decimal
from pathlib import Path

import pandas as pd

from hermes.api.pipeline import Pipeline
from hermes.core.specifications import (
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
from hermes.orchestration import (
    AsyncExecutor,
    ExecutionStrategy,
    StreamingExecutor,
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
        self._dataset_spec: DatasetSpec | None = None
        self._prompt_spec: PromptSpec | None = None
        self._llm_spec: LLMSpec | None = None
        self._processing_spec: ProcessingSpec = ProcessingSpec()
        self._output_spec: OutputSpec | None = None
        self._dataframe: pd.DataFrame | None = None
        self._executor: ExecutionStrategy | None = None
        self._custom_parser: any | None = None
        self._custom_llm_client: any | None = None

    @staticmethod
    def create() -> "PipelineBuilder":
        """
        Start builder chain.

        Returns:
            New PipelineBuilder instance
        """
        return PipelineBuilder()

    @staticmethod
    def from_specifications(specs: PipelineSpecifications) -> "PipelineBuilder":
        """
        Create builder from existing specifications.

        Useful for loading from YAML and modifying programmatically.

        Args:
            specs: Complete pipeline specifications

        Returns:
            PipelineBuilder pre-configured with specs

        Example:
            specs = load_pipeline_config("config.yaml")
            builder = PipelineBuilder.from_specifications(specs)
            pipeline = builder.build()
        """
        builder = PipelineBuilder()
        builder._dataset_spec = specs.dataset
        builder._prompt_spec = specs.prompt
        builder._llm_spec = specs.llm
        builder._processing_spec = specs.processing
        builder._output_spec = specs.output
        return builder

    def from_csv(
        self,
        path: str,
        input_columns: list[str],
        output_columns: list[str],
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
        input_columns: list[str],
        output_columns: list[str],
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
        input_columns: list[str],
        output_columns: list[str],
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
        input_columns: list[str],
        output_columns: list[str],
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
        system_message: str | None = None,
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
        api_key: str | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
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

    def with_custom_llm_client(self, client: any) -> "PipelineBuilder":
        """
        Provide a custom LLM client instance directly.

        This allows advanced users to create their own LLM client implementations
        by extending the LLMClient base class. The custom client will be used
        instead of the factory-created client.

        Args:
            client: Custom LLM client instance (must inherit from LLMClient)

        Returns:
            Self for chaining

        Example:
            class MyCustomClient(LLMClient):
                def invoke(self, prompt: str, **kwargs) -> LLMResponse:
                    # Custom implementation
                    ...

            pipeline = (
                PipelineBuilder.create()
                .from_dataframe(df, ...)
                .with_prompt("...")
                .with_custom_llm_client(MyCustomClient(spec))
                .build()
            )
        """
        from hermes.adapters.llm_client import LLMClient

        if not isinstance(client, LLMClient):
            raise TypeError(
                f"Custom client must inherit from LLMClient, got {type(client).__name__}"
            )

        self._custom_llm_client = client
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

    def with_max_retries(self, retries: int) -> "PipelineBuilder":
        """
        Configure maximum retry attempts.

        Args:
            retries: Maximum number of retry attempts

        Returns:
            Self for chaining
        """
        self._processing_spec.max_retries = retries
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

    def with_error_policy(self, policy: str) -> "PipelineBuilder":
        """
        Configure error handling policy.

        Args:
            policy: Error policy ('skip', 'fail', 'retry', 'use_default')

        Returns:
            Self for chaining
        """
        from hermes.core.specifications import ErrorPolicy

        self._processing_spec.error_policy = ErrorPolicy(policy.lower())
        return self

    def with_checkpoint_dir(self, directory: str) -> "PipelineBuilder":
        """
        Configure checkpoint directory.

        Args:
            directory: Path to checkpoint directory

        Returns:
            Self for chaining
        """
        self._processing_spec.checkpoint_dir = Path(directory)
        return self

    def with_parser(self, parser: any) -> "PipelineBuilder":
        """
        Configure response parser.

        This method allows setting a custom parser. The parser type
        determines the response_format in the prompt spec.

        Args:
            parser: Parser instance (JSONParser, RegexParser, PydanticParser, etc.)

        Returns:
            Self for chaining
        """
        # Store the parser for later use in the pipeline
        # We'll configure response_format based on parser type
        if hasattr(parser, "__class__"):
            parser_name = parser.__class__.__name__
            if "JSON" in parser_name:
                if not self._prompt_spec:
                    raise ValueError(
                        "with_prompt() must be called before with_parser()"
                    )
                # Update the existing prompt spec's response_format
                self._prompt_spec.response_format = "json"
            elif "Regex" in parser_name:
                if not self._prompt_spec:
                    raise ValueError(
                        "with_prompt() must be called before with_parser()"
                    )
                self._prompt_spec.response_format = "regex"
                if hasattr(parser, "patterns"):
                    self._prompt_spec.regex_patterns = parser.patterns

        # Store the parser instance in metadata for the pipeline to use
        if not hasattr(self, "_custom_parser"):
            self._custom_parser = parser

        return self

    def to_csv(self, path: str) -> "PipelineBuilder":
        """
        Configure CSV output destination.

        Alias for with_output(path, format='csv').

        Args:
            path: Output CSV file path

        Returns:
            Self for chaining
        """
        return self.with_output(path, format="csv")

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

    def with_async_execution(self, max_concurrency: int = 10) -> "PipelineBuilder":
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

        # LLM spec is optional if custom client is provided
        if not self._llm_spec and not self._custom_llm_client:
            raise ValueError("Either LLM specification or custom LLM client required")

        # Prepare metadata with custom parser and/or custom client if provided
        metadata = {}
        if self._custom_parser is not None:
            metadata["custom_parser"] = self._custom_parser
        if self._custom_llm_client is not None:
            metadata["custom_llm_client"] = self._custom_llm_client

        # Create specifications bundle
        # If custom client provided but no llm_spec, create a dummy spec
        llm_spec = self._llm_spec
        if llm_spec is None and self._custom_llm_client is not None:
            # Create minimal spec using custom client's attributes
            llm_spec = LLMSpec(
                provider=LLMProvider.OPENAI,  # Dummy provider
                model=self._custom_llm_client.model,
                temperature=self._custom_llm_client.temperature,
                max_tokens=self._custom_llm_client.max_tokens,
            )

        specifications = PipelineSpecifications(
            dataset=self._dataset_spec,
            prompt=self._prompt_spec,
            llm=llm_spec,
            processing=self._processing_spec,
            output=self._output_spec,
            metadata=metadata,
        )

        # Create and return pipeline
        return Pipeline(
            specifications,
            dataframe=self._dataframe,
            executor=self._executor,
        )
