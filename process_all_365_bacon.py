#!/usr/bin/env python
"""
Process ALL 365 bacon descriptions with your detailed prompt.

This script uses the EXACT approach that worked for the 3-row test.
"""

import sys
import os
sys.path.insert(0, "src")

import pandas as pd
from src import PipelineBuilder

# Set API key
os.environ["GROQ_API_KEY"] = "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"

print("🥓 BACON PRODUCT DESCRIPTION CLEANING")
print("="*100)
print("Processing ALL 365 rows with detailed transformation prompts")
print("="*100 + "\n")

# Load ALL rows
df = pd.read_excel("tmp/ground_truth.xlsx")
print(f"✅ Loaded {len(df)} rows from tmp/ground_truth.xlsx")
print(f"   Columns: {list(df.columns)}\n")

# Show first 3 inputs
print("Sample inputs:")
for i in range(3):
    print(f"{i+1}. {df.iloc[i]['Item_Description_Long'][:80]}...")
print()

# Your detailed transformation prompt (simplified but following your rules)
transformation_prompt = """Rewrite this bacon description to be clean, professional, and factual.

Follow these rules:
1. Include (if present): preparation (raw/fully cooked/frozen), special features (sugar-cured, gluten-free, etc), 
   smoke type (applewood-smoked, hickory-smoked, etc), bacon type (sliced/slab/bits), 
   slice count (e.g., "18-22 slices per pound"), layflat if L/O/layout present
2. Remove: brand names (OLD SMOKEHOUSE, etc), codes (BCN, PL, CC, CSMK, etc), pack sizes, abbreviations
3. Expand: APPLWD→applewood, GF→gluten-free, FZ→frozen, FC→fully cooked
4. Format as one concise sentence: [prep], [features], [smoke] [type], [count], [layflat]

Examples:
- Input: "BACON SLICED APPLEWOOD SMOKED LAYOUT 18-22 CT"
  Output: "Applewood-smoked sliced bacon, 18-22 slices per pound, layflat"
  
- Input: "BACON SLAB SUGAR CURE FRZN"  
  Output: "Frozen sugar-cured slab bacon"

- Input: "BACON BIT FC GF 3/8"
  Output: "Fully cooked gluten-free bacon bits, 3/8-inch pieces"

Now clean this:
Input: {Item_Description_Long}

Output:"""

system_message = """You are a professional product description editor specializing in foodservice products.
Clean fragmented text into clear, consistent, factual descriptions.
Remove all marketing fluff, brand names, and internal codes.
Be concise and follow the rules exactly.
Output only the cleaned description - no explanations."""

# Build pipeline
print("⚙️  Building pipeline...")
pipeline = (
    PipelineBuilder.create()
    .from_dataframe(
        df,
        input_columns=["Item_Description_Long"],
        output_columns=["cleaned_description"]
    )
    .with_prompt(
        template=transformation_prompt,
        system_message=system_message
    )
    .with_llm(
        provider="groq",
        model="openai/gpt-oss-120b",
        temperature=0.0,
        max_tokens=200
    )
    .with_batch_size(10)
    .with_concurrency(3)
    .with_max_retries(3)
    .with_max_budget(5.0)
    .build()
)
print("✅ Pipeline built\n")

# Estimate cost
print("💰 Estimating cost...")
estimate = pipeline.estimate_cost()
print(f"   Total rows: {estimate.rows}")
print(f"   Estimated tokens: {estimate.total_tokens:,}")
print(f"   Estimated cost: ${estimate.total_cost}")
print(f"   Max budget: $5.00\n")

# Confirm
response = input(f"⚠️  Process {len(df)} rows for ~${estimate.total_cost}? [y/N]: ")
if response.lower() != 'y':
    print("\n❌ Cancelled by user")
    sys.exit(0)

# Execute with progress
print("\n🚀 PROCESSING...")
print("   This will take ~2-3 minutes for 365 rows")
print("   You'll see progress logs below\n")

result = pipeline.execute()

# Save results
output_excel = "tmp/bacon_all_365_cleaned.xlsx"
output_csv = "tmp/bacon_all_365_cleaned.csv"

result.data.to_excel(output_excel, index=False)
result.data.to_csv(output_csv, index=False)

print("\n" + "="*100)
print("✅ EXECUTION COMPLETE!")
print("="*100)

print(f"\n📊 Statistics:")
print(f"   Total rows: {result.metrics.total_rows}")
print(f"   Processed: {result.metrics.processed_rows}")
print(f"   Failed: {result.metrics.failed_rows}")
print(f"   Skipped: {result.metrics.skipped_rows}")
print(f"   Duration: {result.duration:.2f}s ({result.duration/60:.1f} minutes)")
print(f"   Throughput: {result.metrics.throughput:.2f} rows/sec")

print(f"\n💰 Cost:")
print(f"   Total cost: ${result.costs.total_cost}")
print(f"   Cost per row: ${result.costs.total_cost / max(result.metrics.processed_rows, 1):.4f}")

print(f"\n📄 Output files created:")
print(f"   ✅ {output_excel}")
print(f"   ✅ {output_csv}")
print(f"   Size: {os.path.getsize(output_excel):,} bytes")

# Show sample results
print(f"\n📝 Sample cleaned descriptions (first 10):\n")
for i in range(min(10, len(result.data))):
    row = result.data.iloc[i]
    # Clean up the "assistant: " prefix if present
    cleaned = str(row['cleaned_description']).replace('assistant: ', '')
    print(f"{i+1:3d}. {cleaned}")

print("\n" + "="*100)
print("🎉 SUCCESS! Open tmp/bacon_all_365_cleaned.xlsx to see all results!")
print("="*100)

