import sys
sys.path.insert(0, "src")

import pandas as pd
from src import PipelineBuilder

# Load just 5 rows for testing
df = pd.read_excel("tmp/ground_truth.xlsx").head(5)
print(f"Loaded {len(df)} rows for testing")
print("\nSample input:")
print(df['Item_Description_Long'].head(3).to_string())

# Build pipeline
pipeline = (
    PipelineBuilder.create()
    .from_dataframe(
        df,
        input_columns=["Item_Description_Long"],
        output_columns=["cleaned_description"]
    )
    .with_prompt(
        template="""Rewrite this bacon description to be clean and professional.

Input: {Item_Description_Long}

Output format: One clean sentence describing the bacon.""",
        system_message="You are a product description editor. Be concise and factual."
    )
    .with_llm(provider="groq", model="openai/gpt-oss-120b", temperature=0.0)
    .with_batch_size(5)
    .with_concurrency(2)
    .build()
)

print("\n🚀 Running pipeline on 5 rows...")
result = pipeline.execute()

print(f"\n✅ Success: {result.success}")
print(f"   Processed: {result.metrics.processed_rows}")
print(f"   Duration: {result.duration:.2f}s")
print(f"   Cost: ${result.costs.total_cost}")

print("\n📝 Results:")
for i, row in result.data.iterrows():
    print(f"\n{i+1}. Input:  {row['Item_Description_Long'][:80]}...")
    print(f"   Output: {row['cleaned_description'][:80]}...")

