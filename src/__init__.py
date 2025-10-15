"""
LLM Dataset Processing Engine.

A production-grade SDK for processing tabular datasets using Large Language
Models with reliability, observability, and cost control.
"""

import os
import warnings
import logging

# Suppress transformers warnings about missing deep learning frameworks
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")

# Suppress common dependency warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
warnings.filterwarnings("ignore", message=".*PyTorch.*TensorFlow.*Flax.*")

# Suppress HTTP request logs from httpx/httpcore (used by llama_index)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

__version__ = "1.0.0"

# Layer 4: High-Level API
from src.api.pipeline import Pipeline
from src.api.pipeline_builder import PipelineBuilder
from src.api.dataset_processor import DatasetProcessor

# Core configuration models
from src.core.specifications import (
    DatasetSpec,
    PromptSpec,
    LLMSpec,
    ProcessingSpec,
    PipelineSpecifications,
)

# Core result models
from src.core.models import (
    ExecutionResult,
    QualityReport,
    ProcessingStats,
    CostEstimate,
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
    "ExecutionResult",
    "QualityReport",
    "ProcessingStats",
    "CostEstimate",
]

