"""
Main Pipeline class - the Facade for the entire system.

This is the primary entry point that users interact with.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Iterator, List
from uuid import UUID, uuid4

import pandas as pd

from src.adapters import (
    LocalFileCheckpointStorage,
    create_llm_client,
)
from src.core.models import (
    CostEstimate,
    ExecutionResult,
    ValidationResult,
)
from src.core.specifications import (
    DatasetSpec,
    LLMSpec,
    OutputSpec,
    PipelineSpecifications,
    ProcessingSpec,
    PromptSpec,
)
from src.orchestration import (
    AsyncExecutor,
    CostTrackingObserver,
    ExecutionContext,
    ExecutionObserver,
    ExecutionStrategy,
    LoggingObserver,
    ProgressBarObserver,
    StateManager,
    StreamingExecutor,
    SyncExecutor,
)
from src.stages import (
    DataLoaderStage,
    LLMInvocationStage,
    PromptFormatterStage,
    RawTextParser,
    ResponseParserStage,
    ResultWriterStage,
)
from src.utils import RateLimiter, RetryHandler, get_logger

logger = get_logger(__name__)


class Pipeline:
    """
    Main pipeline class - Facade for dataset processing.
    
    Provides high-level interface for building and executing
    LLM-powered data transformations.
    
    Example:
        pipeline = Pipeline(specifications)
        result = pipeline.execute()
    """

    def __init__(
        self,
        specifications: PipelineSpecifications,
        dataframe: pd.DataFrame | None = None,
        executor: ExecutionStrategy | None = None,
    ):
        """
        Initialize pipeline with specifications.

        Args:
            specifications: Complete pipeline configuration
            dataframe: Optional pre-loaded DataFrame
            executor: Optional execution strategy (default: SyncExecutor)
        """
        self.id = uuid4()
        self.specifications = specifications
        self.dataframe = dataframe
        self.executor = executor or SyncExecutor()
        self.observers: List[ExecutionObserver] = []
        self.logger = get_logger(f"{__name__}.{self.id}")

    def add_observer(self, observer: ExecutionObserver) -> "Pipeline":
        """
        Add execution observer.

        Args:
            observer: Observer to add

        Returns:
            Self for chaining
        """
        self.observers.append(observer)
        return self

    def validate(self) -> ValidationResult:
        """
        Validate pipeline configuration.

        Returns:
            ValidationResult with any errors/warnings
        """
        result = ValidationResult(is_valid=True)
        
        # Validate dataset spec
        if not self.specifications.dataset.input_columns:
            result.add_error("No input columns specified")
        
        if not self.specifications.dataset.output_columns:
            result.add_error("No output columns specified")
        
        # Validate prompt spec
        if not self.specifications.prompt.template:
            result.add_error("No prompt template specified")
        
        # Validate LLM spec
        if not self.specifications.llm.model:
            result.add_error("No LLM model specified")
        
        return result

    def estimate_cost(self) -> CostEstimate:
        """
        Estimate total processing cost.

        Returns:
            Cost estimate
        """
        # Create stages
        loader = DataLoaderStage(self.dataframe)
        
        # Load first few rows for estimation
        df = loader.process(self.specifications.dataset, ExecutionContext())
        sample_size = min(10, len(df))
        sample_df = df.head(sample_size)
        
        # Create formatter and get prompts
        formatter = PromptFormatterStage(
            self.specifications.processing.batch_size
        )
        batches = formatter.process(
            (sample_df, self.specifications.prompt), ExecutionContext()
        )
        
        # Create LLM client and estimate
        llm_client = create_llm_client(self.specifications.llm)
        llm_stage = LLMInvocationStage(llm_client)
        
        sample_estimate = llm_stage.estimate_cost(batches)
        
        # Scale to full dataset
        scale_factor = Decimal(len(df)) / Decimal(sample_size)
        
        return CostEstimate(
            total_cost=sample_estimate.total_cost * scale_factor,
            total_tokens=int(sample_estimate.total_tokens * float(scale_factor)),
            input_tokens=int(sample_estimate.input_tokens * float(scale_factor)),
            output_tokens=int(sample_estimate.output_tokens * float(scale_factor)),
            rows=len(df),
            confidence="sample-based",
        )

    def execute(
        self, resume_from: UUID | None = None
    ) -> ExecutionResult:
        """
        Execute pipeline end-to-end.

        Args:
            resume_from: Optional session ID to resume from checkpoint

        Returns:
            ExecutionResult with data and metrics
        """
        # Validate first
        validation = self.validate()
        if not validation.is_valid:
            raise ValueError(f"Pipeline validation failed: {validation.errors}")
        
        # Create or restore execution context
        state_manager = StateManager(
            storage=LocalFileCheckpointStorage(
                self.specifications.processing.checkpoint_dir
            ),
            checkpoint_interval=self.specifications.processing.checkpoint_interval,
        )
        
        if resume_from:
            # Resume from checkpoint
            context = state_manager.load_checkpoint(resume_from)
            if not context:
                raise ValueError(
                    f"No checkpoint found for session {resume_from}"
                )
            self.logger.info(
                f"Resuming from checkpoint at row {context.last_processed_row}"
            )
        else:
            # Create new context
            context = ExecutionContext(pipeline_id=self.id)
        
        # Add default observers if none specified
        if not self.observers:
            self.observers = [
                ProgressBarObserver(),
                LoggingObserver(),
                CostTrackingObserver(),
            ]
        
        # Notify observers of start
        for observer in self.observers:
            observer.on_pipeline_start(self, context)
        
        try:
            # Execute stages
            result_df = self._execute_stages(context, state_manager)
            
            # Mark completion
            context.end_time = datetime.now()
            
            # Create execution result
            result = ExecutionResult(
                data=result_df,
                metrics=context.get_stats(),
                costs=CostEstimate(
                    total_cost=context.accumulated_cost,
                    total_tokens=context.accumulated_tokens,
                    input_tokens=0,
                    output_tokens=0,
                    rows=context.total_rows,
                    confidence="actual",
                ),
                execution_id=context.session_id,
                start_time=context.start_time,
                end_time=context.end_time,
                success=True,
            )
            
            # Cleanup checkpoints on success
            state_manager.cleanup_checkpoints(context.session_id)
            
            # Notify observers of completion
            for observer in self.observers:
                observer.on_pipeline_complete(context, result)
            
            return result
            
        except Exception as e:
            # Save checkpoint on error
            state_manager.save_checkpoint(context)
            self.logger.error(
                f"Pipeline failed. Checkpoint saved. "
                f"Resume with: pipeline.execute(resume_from=UUID('{context.session_id}'))"
            )
            
            # Notify observers of error
            for observer in self.observers:
                observer.on_pipeline_error(context, e)
            raise

    def _execute_stages(
        self, context: ExecutionContext, state_manager: StateManager
    ) -> pd.DataFrame:
        """Execute all pipeline stages with checkpointing."""
        specs = self.specifications
        
        # Create budget controller if max_budget specified
        budget_controller = None
        if specs.processing.max_budget:
            from src.utils import BudgetController
            
            budget_controller = BudgetController(
                max_budget=specs.processing.max_budget,
                warn_at_75=True,
                warn_at_90=True,
                fail_on_exceed=True,
            )
        
        # Stage 1: Load data
        loader = DataLoaderStage(self.dataframe)
        self._execute_stage(loader, specs.dataset, context)
        df = context.intermediate_data["loaded_data"] = (
            loader.process(specs.dataset, context)
        )
        
        # Stage 2: Format prompts
        formatter = PromptFormatterStage(specs.processing.batch_size)
        self._execute_stage(formatter, (df, specs.prompt), context)
        batches = context.intermediate_data["prompt_batches"] = (
            formatter.process((df, specs.prompt), context)
        )
        
        # Stage 3: Invoke LLM
        llm_client = create_llm_client(specs.llm)
        rate_limiter = (
            RateLimiter(specs.processing.rate_limit_rpm)
            if specs.processing.rate_limit_rpm
            else None
        )
        retry_handler = RetryHandler(
            max_attempts=specs.processing.max_retries,
            initial_delay=specs.processing.retry_delay,
        )
        
        llm_stage = LLMInvocationStage(
            llm_client,
            concurrency=specs.processing.concurrency,
            rate_limiter=rate_limiter,
            retry_handler=retry_handler,
            error_policy=specs.processing.error_policy,
            max_retries=specs.processing.max_retries,
        )
        self._execute_stage(llm_stage, batches, context)
        response_batches = context.intermediate_data["response_batches"] = (
            llm_stage.process(batches, context)
        )
        
        # Check budget after LLM invocation
        if budget_controller:
            budget_controller.check_budget(context.accumulated_cost)
        
        # Save checkpoint after expensive LLM stage
        if state_manager.should_checkpoint(context.last_processed_row):
            state_manager.save_checkpoint(context)
        
        # Stage 4: Parse responses
        parser_stage = ResponseParserStage(
            parser=RawTextParser(),
            output_columns=specs.dataset.output_columns,
        )
        self._execute_stage(
            parser_stage,
            (response_batches, specs.dataset.output_columns),
            context,
        )
        results_df = parser_stage.process(
            (response_batches, specs.dataset.output_columns), context
        )
        
        # Stage 5: Write results (if output spec provided)
        if specs.output:
            writer = ResultWriterStage()
            self._execute_stage(
                writer, (df, results_df, specs.output), context
            )
            final_df = writer.process((df, results_df, specs.output), context)
            return final_df
        else:
            # Merge results with original
            for col in results_df.columns:
                df[col] = results_df[col]
            return df

    async def execute_async(
        self, resume_from: UUID | None = None
    ) -> ExecutionResult:
        """
        Execute pipeline asynchronously.
        
        Uses AsyncExecutor for non-blocking execution. Ideal for integration
        with FastAPI, aiohttp, and other async frameworks.

        Args:
            resume_from: Optional session ID to resume from checkpoint

        Returns:
            ExecutionResult with data and metrics
            
        Raises:
            ValueError: If executor doesn't support async
        """
        if not self.executor.supports_async():
            raise ValueError(
                "Current executor doesn't support async. "
                "Use AsyncExecutor: Pipeline(specs, executor=AsyncExecutor())"
            )
        
        # Use executor's async execute method
        return await self.executor.execute([], ExecutionContext())

    def execute_stream(
        self, chunk_size: int = 1000
    ) -> Iterator[pd.DataFrame]:
        """
        Execute pipeline in streaming mode.
        
        Processes data in chunks for memory-efficient handling of large datasets.
        Ideal for datasets that don't fit in memory.

        Args:
            chunk_size: Number of rows per chunk

        Yields:
            DataFrames with processed chunks
            
        Raises:
            ValueError: If executor doesn't support streaming
        """
        if not self.executor.supports_streaming():
            raise ValueError(
                "Current executor doesn't support streaming. "
                f"Use StreamingExecutor: Pipeline(specs, executor=StreamingExecutor({chunk_size}))"
            )
        
        # Use executor's streaming execute method
        return self.executor.execute([], ExecutionContext())

    def _execute_stage(
        self, stage: Any, input_data: Any, context: ExecutionContext
    ) -> None:
        """Execute a single stage with observer notifications."""
        # Notify observers of stage start
        for observer in self.observers:
            observer.on_stage_start(stage, context)
        
        try:
            # Execute stage
            result = stage.execute(input_data, context)
            
            # Notify observers of completion
            for observer in self.observers:
                observer.on_stage_complete(stage, context, result)
                
        except Exception as e:
            # Notify observers of error
            for observer in self.observers:
                observer.on_stage_error(stage, context, e)
            raise

