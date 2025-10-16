"""
Example: Multi-Column Composition with Independent Prompts

Demonstrates how to generate multiple output columns, each with its own
processing logic, using PipelineComposer.

Use Cases:
1. One-to-Many: Single prompt generates multiple columns (JSON)
2. One-to-One: Each column has independent prompt
3. Dependencies: Column B uses Column A as input

Zen of Code:
- Explicit is better than implicit (clear dependencies)
- Simple is better than complex (compose from simple pipelines)
- Readability counts (fluent API reads like prose)
"""

import pandas as pd

from src.api import Pipeline, PipelineBuilder, PipelineComposer

# Sample data
bacon_data = pd.DataFrame({
    "incumbent": [
        "BACON SLICED APPLEWOOD 14-18 SLICES/LB 10LB",
        "BACON BITS REAL 20LB",
    ],
    "portfolio": [
        "BACON SLICED HICKORY SMOKED 14-18 SLICES/LB 10LB",
        "BACON BITS IMITATION 20LB",
    ],
})


def example_1_python_api():
    """Example 1: Python API (programmatic composition)"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Python API - Programmatic Composition")
    print("="*70)
    
    # Build Pipeline 1: Similarity scoring
    similarity_pipeline = (
        PipelineBuilder.create()
        .from_dataframe(
            bacon_data,
            input_columns=["incumbent", "portfolio"],
            output_columns=["llm_similarity"]
        )
        .with_prompt(
            template="Rate similarity (0-100%): {incumbent} vs {portfolio}",
        )
        .with_llm(
            provider="groq",
            model="llama-3.3-70b-versatile",
            temperature=0.0,
            max_tokens=10,
        )
        .with_batch_size(100)
        .build()
    )
    
    # Build Pipeline 2: Explanation (uses similarity score)
    explanation_pipeline = (
        PipelineBuilder.create()
        .from_dataframe(
            bacon_data,
            input_columns=["incumbent", "portfolio", "llm_similarity"],
            output_columns=["Explanation"]
        )
        .with_prompt(
            template="Explain {llm_similarity}% score for {incumbent} vs {portfolio}",
        )
        .with_llm(
            provider="groq",
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=200,
        )
        .with_batch_size(50)
        .build()
    )
    
    # Compose pipelines
    composer = PipelineComposer(input_data=bacon_data)
    
    result = (
        composer
        .add_column("llm_similarity", similarity_pipeline)
        .add_column("Explanation", explanation_pipeline, depends_on=["llm_similarity"])
        .execute()
    )
    
    print(f"\n✓ Processed {len(result.data)} rows")
    print(f"✓ Generated columns: {list(result.data.columns)}")
    print(f"✓ Total cost: ${result.costs.total_cost:.4f}")
    print(f"✓ Errors: {len(result.errors)}")
    print("\nSample output:")
    print(result.data.head())


def example_2_yaml_api():
    """Example 2: YAML API (declarative composition)"""
    print("\n" + "="*70)
    print("EXAMPLE 2: YAML API - Declarative Composition")
    print("="*70)
    
    # Load composition config
    composer = PipelineComposer.from_yaml("examples/composition_example.yaml")
    
    # Execute
    result = composer.execute()
    
    print(f"\n✓ Processed {len(result.data)} rows")
    print(f"✓ Generated columns: {list(result.data.columns)}")
    print(f"✓ Total cost: ${result.costs.total_cost:.4f}")


def example_3_json_multi_output():
    """Example 3: JSON multi-output (single prompt, multiple columns)"""
    print("\n" + "="*70)
    print("EXAMPLE 3: JSON Multi-Output (1 prompt → 2 columns)")
    print("="*70)
    
    # Single pipeline with JSON output
    pipeline = (
        PipelineBuilder.create()
        .from_dataframe(
            bacon_data,
            input_columns=["incumbent", "portfolio"],
            output_columns=["llm_similarity", "Explanation"]  # Both columns!
        )
        .with_prompt(
            template="""
Rate similarity and explain in JSON format:

Incumbent: {incumbent}
Portfolio: {portfolio}

Return JSON:
{
  "llm_similarity": "95%",
  "Explanation": "Both are applewood-smoked, thick-cut..."
}
""",
        )
        .with_llm(
            provider="groq",
            model="llama-3.3-70b-versatile",
            temperature=0.0,
            max_tokens=300,
        )
        .build()
    )
    
    # Execute single pipeline
    result = pipeline.execute()
    
    print(f"\n✓ Single LLM call generated {len(result.data.columns)} columns")
    print(f"✓ Columns: {list(result.data.columns)}")
    print(f"✓ Cost: ${result.costs.total_cost:.4f}")
    print("\nSample output:")
    print(result.data.head())


def main():
    """Run all examples."""
    print("\n" + "🧘 ZEN OF CODE: Multi-Column Processing Examples 🧘")
    
    # Example 1: Python API
    example_1_python_api()
    
    # Example 2: YAML API
    # example_2_yaml_api()  # Uncomment when composition configs exist
    
    # Example 3: JSON multi-output
    # example_3_json_multi_output()  # Uncomment to test JSON mode
    
    print("\n" + "="*70)
    print("✓ All examples complete!")
    print("="*70)


if __name__ == "__main__":
    main()

