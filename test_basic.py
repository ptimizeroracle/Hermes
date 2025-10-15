"""
Quick test to verify basic package functionality.
"""

import pandas as pd
from llm_dataset_engine import PipelineBuilder

def test_basic_import():
    """Test that package imports correctly."""
    print("✅ Test 1: Package imports successfully")

def test_builder_creation():
    """Test that PipelineBuilder can be created."""
    builder = PipelineBuilder.create()
    print("✅ Test 2: PipelineBuilder created successfully")

def test_pipeline_construction():
    """Test that a pipeline can be constructed."""
    # Create sample data
    df = pd.DataFrame({
        "text": ["Hello world", "This is a test"],
    })
    
    # Build pipeline (without executing)
    pipeline = (
        PipelineBuilder.create()
        .from_dataframe(
            df,
            input_columns=["text"],
            output_columns=["result"]
        )
        .with_prompt("Echo: {text}")
        .with_llm(
            provider="openai",
            model="gpt-4o-mini",
            temperature=0.0
        )
        .build()
    )
    
    print("✅ Test 3: Pipeline constructed successfully")
    print(f"   Pipeline ID: {pipeline.id}")
    print(f"   Input columns: {pipeline.specifications.dataset.input_columns}")
    print(f"   Output columns: {pipeline.specifications.dataset.output_columns}")

def test_validation():
    """Test that pipeline validation works."""
    df = pd.DataFrame({"text": ["test"]})
    
    pipeline = (
        PipelineBuilder.create()
        .from_dataframe(df, input_columns=["text"], output_columns=["result"])
        .with_prompt("Process: {text}")
        .with_llm(provider="openai", model="gpt-4o-mini")
        .build()
    )
    
    validation = pipeline.validate()
    print("✅ Test 4: Pipeline validation successful")
    print(f"   Valid: {validation.is_valid}")
    print(f"   Errors: {validation.errors}")
    print(f"   Warnings: {validation.warnings}")

if __name__ == "__main__":
    print("=" * 60)
    print("LLM Dataset Engine - Basic Functionality Tests")
    print("=" * 60)
    print()
    
    test_basic_import()
    test_builder_creation()
    test_pipeline_construction()
    test_validation()
    
    print()
    print("=" * 60)
    print("✅ All basic tests passed!")
    print("=" * 60)
    print()
    print("NOTE: These tests don't execute LLM calls (no API key required).")
    print("To test full execution, set OPENAI_API_KEY and run examples.")

