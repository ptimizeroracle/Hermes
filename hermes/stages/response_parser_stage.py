"""Response parsing stage for structured output extraction."""

import json
import re
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Dict, List, Optional, Type

import pandas as pd
from pydantic import BaseModel, ValidationError

from hermes.core.models import (
    CostEstimate,
    ResponseBatch,
    ValidationResult,
)
from hermes.stages.pipeline_stage import PipelineStage


class ResponseParser(ABC):
    """Abstract base for response parsers (Strategy pattern)."""

    @abstractmethod
    def parse(self, response: str) -> Dict[str, Any]:
        """Parse response into structured data."""
        pass


class RawTextParser(ResponseParser):
    """Parser that returns raw text."""

    def parse(self, response: str) -> Dict[str, Any]:
        """Return response as-is, after cleaning chat format artifacts."""
        cleaned = response.strip()
        
        # Strip common chat format prefixes (assistant:, user:, system:)
        for prefix in ["assistant:", "user:", "system:"]:
            if cleaned.lower().startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
                break
        
        return {"output": cleaned}


class JSONParser(ResponseParser):
    """Parser that extracts JSON from response."""

    def __init__(self, strict: bool = False):
        """
        Initialize JSON parser.

        Args:
            strict: If True, fail on invalid JSON; if False, try to extract
        """
        self.strict = strict

    def parse(self, response: str) -> Dict[str, Any]:
        """Parse JSON from response."""
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            if self.strict:
                raise
            
            # Try to extract JSON from markdown code blocks
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
                return json.loads(json_str)
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                json_str = response[start:end].strip()
                return json.loads(json_str)
            else:
                # Return as raw text if can't parse
                return {"output": response.strip()}


class PydanticParser(ResponseParser):
    """
    Parser that validates responses against Pydantic models.
    
    Provides type-safe extraction with automatic validation.
    """

    def __init__(
        self, model: Type[BaseModel], strict: bool = True
    ):
        """
        Initialize Pydantic parser.

        Args:
            model: Pydantic model class for validation
            strict: If True, fail on validation errors
        """
        self.model = model
        self.strict = strict

    def parse(self, response: str) -> Dict[str, Any]:
        """Parse and validate response with Pydantic model."""
        try:
            # Try to parse as JSON first
            json_parser = JSONParser(strict=False)
            data = json_parser.parse(response)
            
            # Validate with Pydantic
            validated = self.model(**data)
            return validated.model_dump()
            
        except ValidationError as e:
            if self.strict:
                raise ValueError(f"Pydantic validation failed: {e}")
            else:
                # Return raw data if validation fails
                return {"output": response.strip(), "validation_error": str(e)}


class RegexParser(ResponseParser):
    """
    Parser that extracts data using regex patterns.
    
    Useful for extracting specific fields from structured text.
    """

    def __init__(self, patterns: Dict[str, str]):
        """
        Initialize regex parser.

        Args:
            patterns: Dict mapping field names to regex patterns
        """
        self.patterns = {
            key: re.compile(pattern)
            for key, pattern in patterns.items()
        }

    def parse(self, response: str) -> Dict[str, Any]:
        """Extract fields using regex patterns."""
        result = {}
        
        for field_name, pattern in self.patterns.items():
            match = pattern.search(response)
            if match:
                # Use first group if groups exist, else full match
                if match.groups():
                    result[field_name] = match.group(1)
                else:
                    result[field_name] = match.group(0)
            else:
                result[field_name] = None
        
        return result


class ResponseParserStage(
    PipelineStage[
        tuple[List[ResponseBatch], List[str]], pd.DataFrame
    ]
):
    """
    Parse LLM responses into structured DataFrame.
    
    Responsibilities:
    - Parse responses using configured parser
    - Map parsed data to output columns
    - Handle parse errors gracefully
    - Return DataFrame with results
    """

    def __init__(
        self,
        parser: ResponseParser | None = None,
        output_columns: List[str] | None = None,
    ):
        """
        Initialize response parser stage.

        Args:
            parser: Response parser (default: RawTextParser)
            output_columns: Output column names
        """
        super().__init__("ResponseParser")
        self.parser = parser or RawTextParser()
        self.output_columns = output_columns or ["output"]

    def process(
        self,
        input_data: tuple[List[ResponseBatch], List[str]],
        context: Any,
    ) -> pd.DataFrame:
        """Parse responses into DataFrame."""
        batches, output_cols = input_data
        
        # Initialize result storage
        results: Dict[int, Dict[str, Any]] = {}
        
        # Parse all responses
        for batch in batches:
            for response, metadata in zip(
                batch.responses, batch.metadata
            ):
                try:
                    # Parse response
                    parsed = self.parser.parse(response)
                    
                    # Map to output columns
                    row_data = {}
                    if len(output_cols) == 1:
                        # Single output column
                        if isinstance(parsed, dict) and "output" in parsed:
                            row_data[output_cols[0]] = parsed["output"]
                        elif isinstance(parsed, dict):
                            # Use first value
                            row_data[output_cols[0]] = next(
                                iter(parsed.values())
                            )
                        else:
                            row_data[output_cols[0]] = parsed
                    else:
                        # Multiple output columns
                        for col in output_cols:
                            row_data[col] = parsed.get(col, None)
                    
                    results[metadata.row_index] = row_data
                    
                except Exception as e:
                    self.logger.error(
                        f"Failed to parse response at row "
                        f"{metadata.row_index}: {e}"
                    )
                    # Store None for failed parses
                    results[metadata.row_index] = {
                        col: None for col in output_cols
                    }
        
        # Create DataFrame
        df = pd.DataFrame.from_dict(results, orient="index")
        df.index.name = "row_index"
        
        self.logger.info(f"Parsed {len(results)} responses")
        
        return df

    def validate_input(
        self, input_data: tuple[List[ResponseBatch], List[str]]
    ) -> ValidationResult:
        """Validate response batches."""
        result = ValidationResult(is_valid=True)
        
        batches, output_cols = input_data
        
        if not batches:
            result.add_error("No response batches provided")
        
        if not output_cols:
            result.add_error("No output columns specified")
        
        return result

    def estimate_cost(
        self, input_data: tuple[List[ResponseBatch], List[str]]
    ) -> CostEstimate:
        """Response parsing has no LLM cost."""
        return CostEstimate(
            total_cost=Decimal("0.0"),
            total_tokens=0,
            input_tokens=0,
            output_tokens=0,
            rows=sum(len(b.responses) for b in input_data[0]),
        )

