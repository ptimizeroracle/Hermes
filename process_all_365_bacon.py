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

# ========================================
# CONFIGURATION - Adjust these as needed
# ========================================
MAX_TOKENS = 400           # Groq recommended: 400-800 for detailed outputs
MAX_RETRIES = 3            # Number of retries on API errors
BATCH_SIZE = 10            # Rows per batch
CONCURRENCY = 3            # Parallel requests per batch
MAX_BUDGET = 5.0           # Maximum spend in USD

# Groq Pricing (as of 2024)
GROQ_INPUT_COST_PER_1K = 0.00005   # $0.05 per 1M input tokens
GROQ_OUTPUT_COST_PER_1K = 0.00008  # $0.08 per 1M output tokens

print("🥓 BACON PRODUCT DESCRIPTION CLEANING")
print("="*100)
print(f"Processing ALL 365 rows with detailed transformation prompts")
print(f"Config: max_tokens={MAX_TOKENS}, max_retries={MAX_RETRIES}, concurrency={CONCURRENCY}")
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

**CRITICAL: Always return a valid description. Never return "None" or empty text.**

Follow these rules:
1. Include (if present): preparation (raw/fully cooked/frozen), special features (sugar-cured, gluten-free, etc), 
   smoke type (applewood-smoked, hickory-smoked, etc), bacon type (sliced/slab/bits), 
   slice count (e.g., "18-22 slices per pound"), layflat if L/O/layout present
2. Remove: brand names (OLD SMOKEHOUSE, HORMEL, etc), codes (BCN, PL, CC, CSMK, etc), pack sizes, abbreviations
3. Expand: APPLWD→applewood, GF→gluten-free, FZ→frozen, FC/CKD→fully cooked, AWS→applewood
4. Format as one concise sentence: [prep], [features], [smoke] [type], [count], [layflat]
5. **If unsure, make best effort** - extract what you can identify and write partial description

Now clean this:
Input: {Item_Description_Long}

Output:"""

system_message = """You are a professional product description editor specializing in foodservice products.
Clean fragmented text into clear, consistent, factual descriptions.
Remove all marketing fluff, brand names, and internal codes.
Be concise and follow the rules exactly.
Output only the cleaned description - no explanations.
NEVER return "None" or empty output - always provide your best effort description."""

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
        max_tokens=MAX_TOKENS,
        input_cost_per_1k_tokens=GROQ_INPUT_COST_PER_1K,
        output_cost_per_1k_tokens=GROQ_OUTPUT_COST_PER_1K
    )
    .with_batch_size(BATCH_SIZE)
    .with_concurrency(CONCURRENCY)
    .with_max_retries(MAX_RETRIES)
    .with_max_budget(MAX_BUDGET)
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
print(f"   Duration: {result.metrics.total_duration_seconds:.2f}s ({result.metrics.total_duration_seconds/60:.1f} minutes)")
print(f"   Throughput: {result.metrics.rows_per_second:.2f} rows/sec")

print(f"\n💰 Cost:")
print(f"   Total cost: ${result.costs.total_cost}")
print(f"   Cost per row: ${result.costs.total_cost / max(result.metrics.processed_rows, 1):.4f}")

# Validate output quality
print(f"\n🔍 Quality Validation:")
quality = result.validate_output_quality(["cleaned_description"])
print(f"   Valid outputs: {quality.valid_outputs}/{quality.total_rows}")
print(f"   Success rate: {quality.success_rate:.1f}%")
print(f"   Null outputs: {quality.null_outputs}")
print(f"   Quality score: {quality.quality_score.upper()}")

if quality.warnings:
    print(f"\n⚠️  Warnings:")
    for warning in quality.warnings:
        print(f"   • {warning}")

if quality.issues:
    print(f"\n🚨 Issues Detected:")
    for issue in quality.issues:
        print(f"   • {issue}")
    print(f"\n💡 Consider:")
    print(f"   • Review your prompt complexity (simpler prompts often work better)")
    print(f"   • Check LLM provider logs for errors")
    print(f"   • Increase max_tokens if outputs are truncated")
    print(f"   • Verify API key and rate limits")

if quality.is_acceptable:
    print(f"\n✅ Output quality is ACCEPTABLE ({quality.success_rate:.1f}% success)")
else:
    print(f"\n❌ Output quality is BELOW ACCEPTABLE THRESHOLD ({quality.success_rate:.1f}% < 70%)")

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

