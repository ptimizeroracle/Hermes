"""
Product Similarity Analysis using Multi-Column Composition

This demonstrates using PipelineComposer to generate:
1. Similarity score (independent)
2. Explanation (depends on score)
3. Swap risk assessment (depends on both)
"""

import pandas as pd

from hermes.api import PipelineBuilder, PipelineComposer

# Load data
df = pd.read_excel("ground_truth_clean_columns.xlsx")

print(f"📊 Loaded {len(df)} rows")
print(f"   Columns: {list(df.columns)}")

# Pipeline 1: Similarity Score (independent)
similarity_pipeline = (
    PipelineBuilder.create()
    .from_dataframe(
        df,
        input_columns=["incumbent", "portfolio"],
        output_columns=["llm_similarity"],
    )
    .with_prompt(
        template="""Rate product similarity (0-100%):

**Input**:
Incumbent: {incumbent}
Portfolio: {portfolio}

Focus on: slice count/thickness, form factor, preparation state, handling requirements.

Return only the percentage (e.g., "95%"):""",
        system_message="""You are a Senior Culinary Technologist at Sodexo.
Evaluate product substitutability based on functional equivalence, not just flavor.""",
    )
    .with_llm(
        provider="groq",
        model="moonshotai/kimi-k2-instruct-0905",
        temperature=0.0,
        max_tokens=10,
    )
    .with_batch_size(100)
    .with_concurrency(3)
    .with_max_retries(3)
    .build()
)

# Pipeline 2: Explanation (depends on similarity score)
explanation_pipeline = (
    PipelineBuilder.create()
    .from_dataframe(
        df,
        input_columns=["incumbent", "portfolio", "llm_similarity"],
        output_columns=["Explanation"],
    )
    .with_prompt(
        template="""Explain why these products have a {llm_similarity} similarity score:

Incumbent: {incumbent}
Portfolio: {portfolio}

Provide a detailed technical justification (2-3 sentences):""",
        system_message="""You are a Product Standards Specialist.
Explain product similarity based on slice thickness, form factor, preparation state, and handling.""",
    )
    .with_llm(
        provider="groq",
        model="moonshotai/kimi-k2-instruct-0905",
        temperature=0.3,
        max_tokens=200,
    )
    .with_batch_size(50)
    .with_concurrency(3)
    .with_max_retries(3)
    .build()
)

# Pipeline 3: Swap Risk Score (depends on similarity and explanation)
risk_pipeline = (
    PipelineBuilder.create()
    .from_dataframe(
        df,
        input_columns=["incumbent", "portfolio", "llm_similarity", "Explanation"],
        output_columns=["swap_risk_score"],
    )
    .with_prompt(
        template="""Based on this analysis:

Similarity: {llm_similarity}
Explanation: {Explanation}

Assess operational swap risk (choose one: low, medium, high, critical):
- low = 95%+ similarity, no barriers
- medium = 80-94% similarity, minor differences
- high = <80% similarity, major differences
- critical = Different categories

Risk level:""",
        system_message="""You are a Supply Chain Risk Analyst.
Assess operational risk for product swaps.""",
    )
    .with_llm(
        provider="groq",
        model="moonshotai/kimi-k2-instruct-0905",
        temperature=0.0,
        max_tokens=10,
    )
    .with_batch_size(100)
    .with_concurrency(3)
    .with_max_retries(3)
    .build()
)

# Compose all pipelines
print("\n🔄 Starting multi-column composition...")
composer = PipelineComposer(input_data=df)

result = (
    composer.add_column("llm_similarity", similarity_pipeline)
    .add_column("Explanation", explanation_pipeline, depends_on=["llm_similarity"])
    .add_column(
        "swap_risk_score", risk_pipeline, depends_on=["llm_similarity", "Explanation"]
    )
    .execute()
)

print("\n✅ Processing complete!")
print(f"   Rows processed: {len(result.data)}")
print(
    f"   Generated columns: {[c for c in result.data.columns if c in ['llm_similarity', 'Explanation', 'swap_risk_score']]}"
)
print(f"   Total cost: ${result.costs.total_cost:.4f}")
print(f"   Errors: {len(result.errors)}")

# Save results
output_path = "ground_truth_similarity_results_composition.xlsx"
result.data.to_excel(output_path, index=False)
print(f"\n💾 Results saved to: {output_path}")

# Show sample
print("\n📋 Sample results:")
print(
    result.data[["incumbent", "portfolio", "llm_similarity", "swap_risk_score"]].head(3)
)
