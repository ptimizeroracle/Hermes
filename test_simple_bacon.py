import sys
import os
sys.path.insert(0, "src")

import pandas as pd
from src import PipelineBuilder

os.environ["GROQ_API_KEY"] = "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"

df = pd.read_excel("tmp/ground_truth.xlsx").head(3)

print("🥓 BACON CLEANING WITH CLI - 3 SAMPLES")
print("="*100 + "\n")

# Build with your prompts but output single column
pipeline = (
    PipelineBuilder.create()
    .from_dataframe(df, input_columns=["Item_Description_Long"], output_columns=["cleaned_description"])
    .with_prompt(
        template="{Item_Description_Long}",
        system_message="""You are a bacon product description cleaner. 

For each bacon description:
1. Identify: preparation (raw/cooked/frozen), smoke type (applewood/hickory/etc), bacon type (sliced/slab/bits), count if present
2. Remove: brand names, codes, pack sizes
3. Format as: [preparation], [smoke]-smoked [type] bacon, [count if present], layflat if L/O present
4. Be concise and factual

Example:
Input: BACON SLICED APPLEWOOD SMOKED LAYOUT 18-22 CT
Output: Applewood-smoked sliced bacon, 18-22 slices per pound, layflat

Now clean this bacon description:"""
    )
    .with_llm(provider="groq", model="openai/gpt-oss-120b", temperature=0.0, max_tokens=150)
    .build()
)

print("Processing...")
result = pipeline.execute()

# Save
result.data.to_excel("tmp/bacon_simple_cli.xlsx", index=False)
result.data.to_csv("tmp/bacon_simple_cli.csv", index=False)

print(f"\n✅ Success! {result.metrics.processed_rows} rows in {result.duration:.2f}s")
print(f"\n📄 Results:\n")

for i, row in result.data.iterrows():
    print(f"{i+1}. INPUT:  {row['Item_Description_Long'][:70]}...")
    print(f"   OUTPUT: {row['cleaned_description']}")
    print()

print("="*100)
print("✅ Saved to: tmp/bacon_simple_cli.xlsx and tmp/bacon_simple_cli.csv")
