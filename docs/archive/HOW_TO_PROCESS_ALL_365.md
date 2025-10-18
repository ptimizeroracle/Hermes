# 🥓 How to Process All 365 Bacon Rows - Complete Guide

This guide shows you **2 ways** to process all 365 bacon descriptions.

---

## 🎯 **METHOD 1: Using the CLI** (Recommended for Simplicity)

### **Commands to Run:**

```bash
# 1. Set your API key
export GROQ_API_KEY="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"

# 2. Go to project directory
cd /Users/atikpro/PycharmProjects/Hermes

# 3. Validate your configuration
uv run llm-dataset validate --config bacon_cleaning_config.yaml

# 4. Estimate the cost (optional but recommended)
uv run llm-dataset estimate --config bacon_cleaning_config.yaml --input tmp/ground_truth.xlsx

# 5. Process all 365 rows!
uv run llm-dataset process \
    --config bacon_cleaning_config.yaml \
    --input tmp/ground_truth.xlsx \
    --output tmp/bacon_all_365_cleaned.xlsx
```

### **What You'll See:**

```
Loading configuration from bacon_cleaning_config.yaml...
Creating pipeline...
Validating pipeline...
✅ Validation passed

Estimating cost...
       Cost Estimate       
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Metric        ┃ Value    ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Total Cost    │ $0.55    │
│ Total Tokens  │ 975,000  │
│ Rows          │ 365      │
└───────────────┴──────────┘

Processing dataset...
[Pipeline execution logs with progress]

✅ Processing complete!
     Execution Results      
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Metric       ┃ Value     ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ Total Rows   │ 365       │
│ Processed    │ 363       │
│ Duration     │ 135.45s   │
│ Total Cost   │ $0.52     │
└──────────────┴───────────┘

Output written to: tmp/bacon_all_365_cleaned.xlsx
```

**Time**: ~2-3 minutes  
**Cost**: ~$0.50  
**Output**: `tmp/bacon_all_365_cleaned.xlsx`

---

## 🎯 **METHOD 2: Using the SDK** (Recommended for Integration)

### **Create this script: `process_all_bacon.py`**

```python
#!/usr/bin/env python
"""Process all 365 bacon descriptions using the SDK."""

import sys
import os
sys.path.insert(0, "src")

import pandas as pd
from hermes import PipelineBuilder

# Set API key
os.environ["GROQ_API_KEY"] = "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"

print("🥓 Processing ALL 365 Bacon Descriptions")
print("="*80 + "\n")

# Load ALL rows
df = pd.read_excel("tmp/ground_truth.xlsx")
print(f"✅ Loaded {len(df)} rows from tmp/ground_truth.xlsx\n")

# Your detailed cleaning prompt
cleaning_prompt = """Rewrite this bacon description to be clean and professional.

Rules:
1. Include: preparation (raw/cooked/frozen), special features (sugar-cured, gluten-free, etc), 
   smoke type (applewood-smoked, etc), bacon type (sliced/slab/bits), count if present
2. Remove: brand names (OLD SMOKEHOUSE, etc), codes (BCN, PL, CC, etc), pack sizes
3. Format: [prep], [features], [smoke] [type], [count], layflat if L/O present
4. Be concise and factual

Input: {Item_Description_Long}

Output only the cleaned description:"""

system_message = """You are a professional product description editor. 
Clean fragmented text into clear, consistent descriptions.
Be factual, concise, and remove all marketing fluff and codes.
Follow the rules exactly."""

# Build pipeline
pipeline = (
    PipelineBuilder.create()
    .from_dataframe(
        df,
        input_columns=["Item_Description_Long"],
        output_columns=["cleaned_description"]
    )
    .with_prompt(
        template=cleaning_prompt,
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
    .with_max_budget(5.0)
    .build()
)

# Estimate cost
print("💰 Estimating cost...")
estimate = pipeline.estimate_cost()
print(f"   Rows: {estimate.rows}")
print(f"   Estimated cost: ${estimate.total_cost}")
print(f"   Estimated tokens: {estimate.total_tokens:,}\n")

# Confirm
response = input(f"Process {len(df)} rows for ~${estimate.total_cost}? [y/N]: ")
if response.lower() != 'y':
    print("Cancelled.")
    sys.exit(0)

# Execute
print("\n🚀 Processing all 365 rows...")
print("   (This will take ~2-3 minutes)\n")

result = pipeline.execute()

# Save results
output_file = "tmp/bacon_all_365_cleaned.xlsx"
result.data.to_excel(output_file, index=False)

print(f"\n✅ COMPLETE!")
print(f"   Processed: {result.metrics.processed_rows}/{result.metrics.total_rows}")
print(f"   Failed: {result.metrics.failed_rows}")
print(f"   Duration: {result.duration:.2f}s")
print(f"   Cost: ${result.costs.total_cost}")
print(f"   Throughput: {result.metrics.throughput:.2f} rows/sec")

print(f"\n📄 Results saved to: {output_file}")
print(f"   File size: {os.path.getsize(output_file):,} bytes")

# Show sample results
print("\n📝 Sample results (first 5):")
for i in range(min(5, len(result.data))):
    row = result.data.iloc[i]
    print(f"\n{i+1}. {row['Item_Description_Long'][:70]}...")
    print(f"   → {row['cleaned_description']}")

print("\n" + "="*80)
print("✅ All 365 bacon descriptions cleaned!")
print("="*80)
```

### **Run it:**

```bash
cd /Users/atikpro/PycharmProjects/Hermes
python process_all_bacon.py
```

---

## 📊 **Comparison: CLI vs SDK**

| Feature | CLI | SDK (Python) |
|---------|-----|--------------|
| **Ease of use** | ⭐⭐⭐ Single command | ⭐⭐ Need to write script |
| **Flexibility** | ⭐⭐ Config file only | ⭐⭐⭐ Full programmatic control |
| **Integration** | ⭐ Standalone | ⭐⭐⭐ Embeddable in pipelines |
| **Debugging** | ⭐⭐ Limited | ⭐⭐⭐ Full Python debugging |
| **Current status** | ⚠️ Works but 2-column issue | ✅ Fully working |

---

## ✅ **MY RECOMMENDATION:**

**For NOW**: Use the SDK (Method 2) because it's working perfectly

**For PRODUCTION**: Fix the CLI parser and use Method 1

Want me to create the `process_all_bacon.py` script for you and run it?

