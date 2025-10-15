"""
LLM client abstractions and implementations.

Provides unified interface for multiple LLM providers following the
Adapter pattern and Dependency Inversion principle.
"""

import os
import time
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Dict, List, Optional

import tiktoken
from llama_index.core.llms import ChatMessage
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.llms.groq import Groq
from llama_index.llms.openai import OpenAI

from llm_dataset_engine.core.models import LLMResponse
from llm_dataset_engine.core.specifications import LLMProvider, LLMSpec


class LLMClient(ABC):
    """
    Abstract base class for LLM clients.
    
    Defines the contract that all LLM provider implementations must follow,
    enabling easy swapping of providers (Strategy pattern).
    """

    def __init__(self, spec: LLMSpec):
        """
        Initialize LLM client.

        Args:
            spec: LLM specification
        """
        self.spec = spec
        self.model = spec.model
        self.temperature = spec.temperature
        self.max_tokens = spec.max_tokens

    @abstractmethod
    def invoke(self, prompt: str, **kwargs: Any) -> LLMResponse:
        """
        Invoke LLM with a single prompt.

        Args:
            prompt: Text prompt
            **kwargs: Additional model parameters

        Returns:
            LLMResponse with result and metadata
        """
        pass

    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        pass

    def batch_invoke(
        self, prompts: List[str], **kwargs: Any
    ) -> List[LLMResponse]:
        """
        Invoke LLM with multiple prompts.

        Default implementation: sequential invocation.
        Subclasses can override for provider-optimized batch processing.

        Args:
            prompts: List of text prompts
            **kwargs: Additional model parameters

        Returns:
            List of LLMResponse objects
        """
        return [self.invoke(prompt, **kwargs) for prompt in prompts]

    def calculate_cost(
        self, tokens_in: int, tokens_out: int
    ) -> Decimal:
        """
        Calculate cost for token usage.

        Args:
            tokens_in: Input tokens
            tokens_out: Output tokens

        Returns:
            Total cost in USD
        """
        input_cost = (
            Decimal(tokens_in) / 1000
        ) * (self.spec.input_cost_per_1k_tokens or Decimal("0.0"))
        output_cost = (
            Decimal(tokens_out) / 1000
        ) * (self.spec.output_cost_per_1k_tokens or Decimal("0.0"))
        return input_cost + output_cost


class OpenAIClient(LLMClient):
    """OpenAI LLM client implementation."""

    def __init__(self, spec: LLMSpec):
        """Initialize OpenAI client."""
        super().__init__(spec)
        
        api_key = spec.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in spec or environment")
        
        self.client = OpenAI(
            model=spec.model,
            api_key=api_key,
            temperature=spec.temperature,
            max_tokens=spec.max_tokens,
        )
        
        # Initialize tokenizer
        try:
            self.tokenizer = tiktoken.encoding_for_model(spec.model)
        except KeyError:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def invoke(self, prompt: str, **kwargs: Any) -> LLMResponse:
        """Invoke OpenAI API."""
        start_time = time.time()
        
        message = ChatMessage(role="user", content=prompt)
        response = self.client.chat([message])
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Extract token usage
        tokens_in = len(self.tokenizer.encode(prompt))
        tokens_out = len(self.tokenizer.encode(str(response)))
        
        cost = self.calculate_cost(tokens_in, tokens_out)
        
        return LLMResponse(
            text=str(response),
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            model=self.model,
            cost=cost,
            latency_ms=latency_ms,
        )

    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens using tiktoken."""
        return len(self.tokenizer.encode(text))


class AzureOpenAIClient(LLMClient):
    """Azure OpenAI LLM client implementation."""

    def __init__(self, spec: LLMSpec):
        """Initialize Azure OpenAI client."""
        super().__init__(spec)
        
        api_key = spec.api_key or os.getenv("AZURE_OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "AZURE_OPENAI_API_KEY not found in spec or environment"
            )
        
        if not spec.azure_endpoint:
            raise ValueError("azure_endpoint required for Azure OpenAI")
        
        if not spec.azure_deployment:
            raise ValueError("azure_deployment required for Azure OpenAI")
        
        self.client = AzureOpenAI(
            model=spec.model,
            deployment_name=spec.azure_deployment,
            api_key=api_key,
            azure_endpoint=spec.azure_endpoint,
            api_version=spec.api_version or "2024-02-15-preview",
            temperature=spec.temperature,
            max_tokens=spec.max_tokens,
        )
        
        # Initialize tokenizer
        try:
            self.tokenizer = tiktoken.encoding_for_model(spec.model)
        except KeyError:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def invoke(self, prompt: str, **kwargs: Any) -> LLMResponse:
        """Invoke Azure OpenAI API."""
        start_time = time.time()
        
        message = ChatMessage(role="user", content=prompt)
        response = self.client.chat([message])
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Extract token usage
        tokens_in = len(self.tokenizer.encode(prompt))
        tokens_out = len(self.tokenizer.encode(str(response)))
        
        cost = self.calculate_cost(tokens_in, tokens_out)
        
        return LLMResponse(
            text=str(response),
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            model=self.model,
            cost=cost,
            latency_ms=latency_ms,
        )

    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens using tiktoken."""
        return len(self.tokenizer.encode(text))


class AnthropicClient(LLMClient):
    """Anthropic Claude LLM client implementation."""

    def __init__(self, spec: LLMSpec):
        """Initialize Anthropic client."""
        super().__init__(spec)
        
        api_key = spec.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found in spec or environment"
            )
        
        self.client = Anthropic(
            model=spec.model,
            api_key=api_key,
            temperature=spec.temperature,
            max_tokens=spec.max_tokens or 1024,
        )
        
        # Anthropic uses approximate token counting
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def invoke(self, prompt: str, **kwargs: Any) -> LLMResponse:
        """Invoke Anthropic API."""
        start_time = time.time()
        
        message = ChatMessage(role="user", content=prompt)
        response = self.client.chat([message])
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Approximate token usage
        tokens_in = len(self.tokenizer.encode(prompt))
        tokens_out = len(self.tokenizer.encode(str(response)))
        
        cost = self.calculate_cost(tokens_in, tokens_out)
        
        return LLMResponse(
            text=str(response),
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            model=self.model,
            cost=cost,
            latency_ms=latency_ms,
        )

    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens (approximate for Anthropic)."""
        return len(self.tokenizer.encode(text))


class GroqClient(LLMClient):
    """Groq LLM client implementation."""

    def __init__(self, spec: LLMSpec):
        """Initialize Groq client."""
        super().__init__(spec)
        
        api_key = spec.api_key or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found in spec or environment"
            )
        
        self.client = Groq(
            model=spec.model,
            api_key=api_key,
            temperature=spec.temperature,
            max_tokens=spec.max_tokens,
        )
        
        # Use tiktoken for token estimation
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def invoke(self, prompt: str, **kwargs: Any) -> LLMResponse:
        """Invoke Groq API."""
        start_time = time.time()
        
        message = ChatMessage(role="user", content=prompt)
        response = self.client.chat([message])
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Extract token usage
        tokens_in = len(self.tokenizer.encode(prompt))
        tokens_out = len(self.tokenizer.encode(str(response)))
        
        cost = self.calculate_cost(tokens_in, tokens_out)
        
        return LLMResponse(
            text=str(response),
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            model=self.model,
            cost=cost,
            latency_ms=latency_ms,
        )

    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens using tiktoken."""
        return len(self.tokenizer.encode(text))


def create_llm_client(spec: LLMSpec) -> LLMClient:
    """
    Factory function to create appropriate LLM client.

    Args:
        spec: LLM specification

    Returns:
        Configured LLM client

    Raises:
        ValueError: If provider not supported
    """
    if spec.provider == LLMProvider.OPENAI:
        return OpenAIClient(spec)
    elif spec.provider == LLMProvider.AZURE_OPENAI:
        return AzureOpenAIClient(spec)
    elif spec.provider == LLMProvider.ANTHROPIC:
        return AnthropicClient(spec)
    elif spec.provider == LLMProvider.GROQ:
        return GroqClient(spec)
    else:
        raise ValueError(f"Unsupported provider: {spec.provider}")

