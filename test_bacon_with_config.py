import sys
import os
sys.path.insert(0, "src")

import pandas as pd
from src.config import ConfigLoader
from src.api import Pipeline

# Set API key
os.environ["GROQ_API_KEY"] = "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"

# Load just 3 rows for testing with your full prompt
df = pd.read_excel("tmp/ground_truth.xlsx").head(3)
print(f"📊 Loaded {len(df)} rows for testing\n")

print("Sample inputs:")
for i, row in df.iterrows():
    print(f"{i+1}. {row['Item_Description_Long'][:80]}...")

# Load your configuration
print("\n⚙️  Loading configuration from bacon_cleaning_config.yaml...")
specs = ConfigLoader.from_yaml("bacon_cleaning_config.yaml")

print(f"   Provider: {specs.llm.provider}")
print(f"   Model: {specs.llm.model}")
print(f"   Prompt length: {len(specs.prompt.template)} chars")
print(f"   System message length: {len(specs.prompt.system_message)} chars")

# Create pipeline
pipeline = Pipeline(specs, dataframe=df)

print("\n🚀 Running pipeline with YOUR detailed prompts...")
print("   (This will take ~10 seconds for 3 rows)\n")

result = pipeline.execute()

print(f"\n✅ COMPLETE!")
print(f"   Success: {result.success}")
print(f"   Processed: {result.metrics.processed_rows}/{result.metrics.total_rows}")
print(f"   Duration: {result.duration:.2f}s")
print(f"   Cost: ${result.costs.total_cost}")

print("\n" + "="*80)
print("📝 RESULTS WITH YOUR DETAILED PROMPT:")
print("="*80)

for i, row in result.data.iterrows():
    print(f"\n{i+1}. INPUT:")
    print(f"   {row['Item_Description_Long']}")
    print(f"\n   OUTPUT:")
    if 'cleaned_description' in row and pd.notna(row['cleaned_description']):
        output = str(row['cleaned_description'])
        # Show first 300 chars
        if len(output) > 300:
            print(f"   {output[:300]}...")
        else:
            print(f"   {output}")
    else:
        print("   (No output generated)")
    print("-" * 80)

print("\n✅ Test complete! Your prompts are working!")
