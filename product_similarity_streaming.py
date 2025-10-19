"""
Product Similarity Analysis with Streaming

Uses StreamingExecutor for memory-efficient processing of large Excel files.
Generates 3 columns (similarity, explanation, risk) via JSON in one LLM call per row.

This is the streaming version of bacon_similarity_config.yaml - same logic,
but processes data in chunks for better memory efficiency on large files.
"""

import pandas as pd

from hermes.api import PipelineBuilder
from hermes.stages import JSONParser

print("Product Similarity Analysis (Streaming Mode)")

# Load data
df = pd.read_excel("ground_truth_clean_columns.xlsx")
print(f"Loaded {len(df)} rows")

# Build pipeline (same as YAML config, but in Python)
pipeline = (
    PipelineBuilder.create()
    .from_dataframe(
        df,
        input_columns=["incumbent", "portfolio"],
        output_columns=["llm_similarity", "Explanation", "swap_risk_score"],
    )
    .with_prompt(
        template="""Given two bacon product descriptions — an **Incumbent** (current standard) and a **Portfolio** candidate — evaluate their **technical substitutability** in a large-scale foodservice environment like Sodexo.

Focus on these critical dimensions:
- **Slice count per pound** (used to infer cut thickness: 18–22 = thin, 14–18 = standard, 10–12 = thick, etc.)
- **Form factor** (e.g., layflat, shingled, diced, bits, slab, etc.)
- **Preparation state** (raw vs. fully cooked, etc.)
- **Handling requirements** (frozen vs. refrigerated vs. ambient, etc.)
- **Portioning consistency** (must use comparable units—e.g., slices/lb vs. slices/lb, not vs. grams or "portions" without context)

Assign a **similarity percentage (0–100%)** that reflects **true functional equivalence**—not just textual or flavor similarity. A high score requires alignment in **thickness, form, state, and operational handling**. Mismatches in any of these drastically reduce usability, even if flavor descriptors match.

**Input**:
Incumbent: {incumbent}
Portfolio: {portfolio}

**Output format**: Return ONLY valid JSON with exactly these THREE fields:
{{
  "llm_similarity": "95%",
  "Explanation": "Detailed technical justification explaining the similarity score based on the 5 dimensions above",
  "swap_risk_score": "low"
}}

For swap_risk_score, assess operational risk:
- "low" = High confidence swap (95%+ similarity, no operational barriers)
- "medium" = Moderate risk (80-94% similarity, minor differences in form/prep)
- "high" = Significant risk (<80% similarity, major operational differences)
- "critical" = Do not swap (different product categories or safety concerns)""",
        system_message="""You are a Senior Culinary Technologist and Product Standards Specialist at Sodexo, with 15+ years of experience in large-scale foodservice procurement, menu engineering, and supply chain innovation.

You master the following domains with precision:
- **Culinary Science**: Sensory attributes, cooking behavior, yield, and functional performance of proteins—especially bacon and cooked cured meats.
- **Food Specifications & Compliance**: USDA/FDA labeling, ingredient declarations, allergen control, halal/kosher/gluten-free claims, and clean-label trends.
- **Operational Feasibility**: Kitchen workflow impact, labor requirements, storage (frozen/refrigerated), thawing protocols, and portioning formats.
- **Supply Chain & Cost-in-Use Analysis**: Case configuration, pack size compatibility, supplier reliability, and true cost per edible portion—not just per case.
- **Data-Driven Product Matching**: Interpretation of similarity scores, taxonomy alignment, size-unit harmonization (e.g., PORTIONS vs. grams vs. slice count), and tolerance thresholds (±10% for high-confidence swaps).

You evaluate every proposed product swap using Sodexo's 5-Pillar Swap Framework:
1. **Functional Equivalence** – Can it be used identically in recipes without retraining or retooling?
2. **Sensory & Quality Parity** – Does it deliver the same taste, texture, appearance, and consumer satisfaction?
3. **Compliance & Safety** – Is it nutritionally, legally, and ethically substitutable (e.g., pork vs. beef, raw vs. precooked)?
4. **Operational Viability** – Does it fit existing storage, prep, and service workflows across Sodexo segments (corporate, healthcare, education)?
5. **Commercial Sustainability** – Is the alternative scalable, cost-effective, and available across Sodexo's national distribution network?

You communicate with clarity, authority, and actionable insight—never guessing. If data is ambiguous (e.g., undefined units, missing prep state), you explicitly call out the risk and recommend human validation.

Your goal: Ensure every approved swap maintains Sodexo's brand promise of consistent, safe, high-quality food experiences across 100,000+ daily servings.

**CRITICAL**: Return ONLY valid JSON. No markdown, no code blocks, no additional text. Just the raw JSON object with the three required fields.""",
    )
    .with_llm(
        provider="groq",
        model="moonshotai/kimi-k2-instruct-0905",
        temperature=0.0,
        max_tokens=500,  # Increased for 3 fields
    )
    .with_parser(JSONParser(strict=False))  # Parse JSON response
    .with_batch_size(100)
    .with_concurrency(3)
    .with_max_retries(3)
    .with_preprocessing(enabled=True, max_length=500)
    .with_streaming(chunk_size=1000)  # Process 1000 rows at a time (memory-efficient)
    .build()
)

# Estimate cost first
print("\n💰 Estimating cost...")
estimate = pipeline.estimate_cost()
print(f"   Estimated rows: {estimate.rows}")
print(f"   Estimated cost: ${estimate.total_cost:.2f}")
print(f"   Estimated tokens: {estimate.total_tokens:,}")

# Execute with streaming
print("\n🔄 Processing with streaming (memory-efficient)...")
result = pipeline.execute()

print("\n✅ Complete!")
print(f"   Rows processed: {result.metrics.processed_rows}")
print(f"   Failed rows: {result.metrics.failed_rows}")
print(f"   Total cost: ${result.costs.total_cost:.4f}")
print(f"   Duration: {result.metrics.total_duration_seconds:.2f}s")
print(f"   Throughput: {result.metrics.rows_per_second:.2f} rows/sec")

# Save results
output_path = "ground_truth_similarity_results_streaming.xlsx"
result.data.to_excel(output_path, index=False)
print(f"\n💾 Results saved to: {output_path}")

# Show sample
print("\n📋 Sample results:")
sample_cols = ["incumbent", "portfolio", "llm_similarity", "swap_risk_score"]
available_cols = [c for c in sample_cols if c in result.data.columns]
if available_cols:
    print(result.data[available_cols].head(3))
