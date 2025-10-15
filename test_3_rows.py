import sys
import os
sys.path.insert(0, "src")

import pandas as pd
from src import PipelineBuilder

os.environ["GROQ_API_KEY"] = "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"

print("🥓 Testing with 3 bacon descriptions\n")

# Load 3 sample rows
df = pd.read_excel("tmp/ground_truth.xlsx").head(3)

print("Input data:")
for i, row in df.iterrows():
    print(f"{i+1}. {row['Item_Description_Long']}")

# Your complete transformation prompt
transformation_prompt = """Rewrite the input into a single, concise, professional product description in fluent English—strictly factual, neutral in tone, and optimized for foodservice procurement and semantic consistency.

✅ Include **only** the following attributes, in this exact order, **as a single sentence**:
1. **Preparation**: "raw", "fully cooked", or "frozen"
2. **Special features** (only if stated): honey-cured, sugar-cured, pepper-crusted, organic, gluten-free, nitrate-free, halal, uncured
3. **Smoke/flavor** (only if stated): applewood-smoked, cherrywood-smoked, hickory-smoked, etc.
4. **Type**: sliced bacon, slab bacon, bacon bits, bacon pieces, etc.
5. **Slice detail** (if applicable): [X–Y] slices per pound ([cut])
6. **Layflat** (if L/O, layout, layflat present): append ", layflat"

🚫 **Strictly omit**: pack sizes, weights, brand names, supplier codes, abbreviations (expand them), redundant terms

Input: {Item_Description_Long}

Output only the cleaned description."""

# Your system message
system_message = """You are a careful product copy editor. Clean fragmented product text into a clear, fluent description. Prioritize consistency, brevity, and factual fidelity. Do not invent details or infer missing data."""

# Build and run
pipeline = (
    PipelineBuilder.create()
    .from_dataframe(df, input_columns=["Item_Description_Long"], output_columns=["cleaned_description"])
    .with_prompt(template=transformation_prompt, system_message=system_message)
    .with_llm(provider="groq", model="openai/gpt-oss-120b", temperature=0.0, max_tokens=300)
    .build()
)

print("\n🚀 Processing...")
result = pipeline.execute()

# Save results
result.data.to_excel("tmp/bacon_test_3rows.xlsx", index=False)
result.data.to_csv("tmp/bacon_test_3rows.csv", index=False)

print(f"\n✅ DONE! Processed {result.metrics.processed_rows} rows in {result.duration:.2f}s")
print(f"💰 Cost: ${result.costs.total_cost}")

print("\n" + "="*80)
print("RESULTS:")
print("="*80)
for i, row in result.data.iterrows():
    print(f"\n{i+1}. INPUT:")
    print(f"   {row['Item_Description_Long']}")
    print(f"   OUTPUT:")
    print(f"   {row['cleaned_description']}")

print("\n" + "="*80)
print(f"📄 Results saved to:")
print(f"   - tmp/bacon_test_3rows.xlsx")
print(f"   - tmp/bacon_test_3rows.csv")
print("="*80)
