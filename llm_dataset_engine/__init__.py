"""
LLM Dataset Processing Engine.

A production-grade SDK for processing tabular datasets using Large Language
Models with reliability, observability, and cost control.
"""

__version__ = "1.0.0"

# Layer 4: High-Level API
from llm_dataset_engine.api.pipeline import Pipeline
from llm_dataset_engine.api.pipeline_builder import PipelineBuilder
from llm_dataset_engine.api.dataset_processor import DatasetProcessor

# Core configuration models
from llm_dataset_engine.core.specifications import (
    DatasetSpec,
    PromptSpec,
    LLMSpec,
    ProcessingSpec,
    PipelineSpecifications,
)

__all__ = [
    "__version__",
    "Pipeline",
    "PipelineBuilder",
    "DatasetProcessor",
    "DatasetSpec",
    "PromptSpec",
    "LLMSpec",
    "ProcessingSpec",
    "PipelineSpecifications",
]

