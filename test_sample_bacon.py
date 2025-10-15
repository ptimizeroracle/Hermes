import sys
import os
sys.path.insert(0, "src")

import pandas as pd
from src.config import ConfigLoader
from src.api import Pipeline

# Set API key
os.environ["GROQ_API_KEY"] = "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"

print("🥓 BACON CLEANING TEST - 3 SAMPLE ROWS")
print("="*80 + "\n")

# Load just 3 rows for testing
df_full = pd.read_excel("tmp/ground_truth.xlsx")
df_sample = df_full.head(3).copy()
print(f"✅ Loaded 3 sample rows from {len(df_full)} total rows\n")

print("Sample inputs:")
for i, row in df_sample.iterrows():
    print(f"{i+1}. {row['Item_Description_Long']}")

# Load your configuration
print("\n⚙️  Loading your detailed configuration...")
specs = ConfigLoader.from_yaml("bacon_cleaning_config.yaml")

print(f"   Provider: {specs.llm.provider}")
print(f"   Model: {specs.llm.model}")
print(f"   Prompt: {len(specs.prompt.template)} chars")
print(f"   System: {len(specs.prompt.system_message)} chars")

# Override to use our 3-row sample
specs.dataset.source_path = None  # Don't reload from file

# Create pipeline with our sample
pipeline = Pipeline(specs, dataframe=df_sample)

print("\n🚀 Processing 3 rows with YOUR detailed prompts...\n")

result = pipeline.execute()

print(f"\n✅ EXECUTION COMPLETE!")
print(f"   Success: {result.success}")
print(f"   Processed: {result.metrics.processed_rows}/{result.metrics.total_rows}")
print(f"   Duration: {result.duration:.2f}s")
print(f"   Cost: ${result.costs.total_cost}")

# Save results
output_file = "tmp/bacon_sample_results.xlsx"
result.data.to_excel(output_file, index=False)
print(f"\n✅ Results saved to: {output_file}")

# Also save as CSV for easy viewing
csv_file = "tmp/bacon_sample_results.csv"
result.data.to_csv(csv_file, index=False)
print(f"✅ Also saved as CSV: {csv_file}")

print("\n" + "="*80)
print("📝 RESULTS:")
print("="*80 + "\n")

for i, row in result.data.iterrows():
    print(f"ROW {i+1}:")
    print(f"  INPUT:  {row['Item_Description_Long']}")
    print(f"  OUTPUT: {row['cleaned_description']}")
    if 'metadata' in row and pd.notna(row['metadata']):
        print(f"  META:   {row['metadata'][:100]}...")
    print()

print("="*80)
print(f"✅ Open {output_file} or {csv_file} to see full results!")
print("="*80)
