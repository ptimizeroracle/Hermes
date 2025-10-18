# 🪽 HERMES CLI - Bacon Cleaning Guide

## Beautiful CLI with ASCII Art! 🎨

The CLI now features a stunning ASCII art banner:

```
    ╦ ╦╔═╗╦═╗╔╦╗╔═╗╔═╗
    ╠═╣║╣ ╠╦╝║║║║╣ ╚═╗
    ╩ ╩╚═╝╩╚═╩ ╩╚═╝╚═╝
    The LLM Dataset Engine
━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Quick Start: Clean 365 Bacon Rows with CLI

### **Step 1: Set Your API Key**
```bash
export GROQ_API_KEY="your-groq-api-key-here"
```

### **Step 2: Validate Your Config** (Optional)
```bash
llm-dataset validate --config bacon_cleaning_config.yaml
```

**Output:**
```
    ╦ ╦╔═╗╦═╗╔╦╗╔═╗╔═╗
    ╠═╣║╣ ╠╦╝║║║║╣ ╚═╗
    ╩ ╩╚═╝╩╚═╩ ╩╚═╝╚═╝
    The LLM Dataset Engine
━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Configuration is valid!
```

### **Step 3: Estimate Cost** (Recommended)
```bash
llm-dataset estimate --config bacon_cleaning_config.yaml
```

**Output:**
```
    ╦ ╦╔═╗╦═╗╔╦╗╔═╗╔═╗
    ╠═╣║╣ ╠╦╝║║║║╣ ╚═╗
    ╩ ╩╚═╝╩╚═╩ ╩╚═╝╚═╝
    The LLM Dataset Engine
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Cost Estimation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Rows:                365
Estimated Tokens:    216,810
Estimated Cost:      $0.0130
Input Cost:          $0.0043
Output Cost:         $0.0087
Confidence:          sample-based
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### **Step 4: Process the Dataset** 🚀
```bash
llm-dataset process --config bacon_cleaning_config.yaml
```

**Output:**
```
    ╦ ╦╔═╗╦═╗╔╦╗╔═╗╔═╗
    ╠═╣║╣ ╠╦╝║║║║╣ ╚═╗
    ╩ ╩╚═╝╩╚═╩ ╩╚═╝╚═╝
    The LLM Dataset Engine
━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚙️  Processing dataset...
2025-10-15 17:27:34 [INFO] Pipeline execution started (session: abc-123)
2025-10-15 17:27:34 [INFO] Starting stage: DataLoader (progress: 0.0%)
2025-10-15 17:27:34 [INFO] Loaded 365 rows from dataframe
2025-10-15 17:27:34 [INFO] Starting stage: LLMInvocation (progress: 0.0%)
2025-10-15 17:27:34 [INFO] Processing batch 0 (10 prompts)
2025-10-15 17:27:37 [INFO] ━━━━━━ PROGRESS: 10/365 rows (2.7%) | Cost: $0.0003 ━━━━━━
2025-10-15 17:27:40 [INFO] ━━━━━━ PROGRESS: 20/365 rows (5.5%) | Cost: $0.0008 ━━━━━━
...
2025-10-15 17:30:45 [INFO] ━━━━━━ PROGRESS: 365/365 rows (100.0%) | Cost: $0.0130 ━━━━━━

✅ Processing complete!

📊 Results
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Rows:          365
Processed:           365
Failed:              0
Skipped:             0
Duration:            197.23s
Cost:                $0.0130
Output:              tmp/ground_truth_cleaned.xlsx
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## All CLI Commands

### **1. Process Dataset**
```bash
llm-dataset process --config bacon_cleaning_config.yaml
```
Runs the full pipeline and saves results to the configured output path.

### **2. Estimate Cost**
```bash
llm-dataset estimate --config bacon_cleaning_config.yaml
```
Estimates cost before processing (uses 10-row sample).

### **3. Validate Config**
```bash
llm-dataset validate --config bacon_cleaning_config.yaml
```
Checks if your YAML configuration is valid.

### **4. Resume from Checkpoint**
```bash
llm-dataset resume --session-id abc-123-def-456
```
Resume a previously interrupted run.

### **5. List Checkpoints**
```bash
llm-dataset list-checkpoints
```
Show all available checkpoints.

### **6. Inspect Dataset**
```bash
llm-dataset inspect --input tmp/ground_truth.xlsx
```
Show dataset schema and sample rows.

### **7. Get Help**
```bash
llm-dataset --help
llm-dataset process --help
```

---

## Your Config File: `bacon_cleaning_config.yaml`

The CLI reads everything from your YAML config:

```yaml
dataset:
  source_type: excel
  source_path: "tmp/ground_truth.xlsx"
  input_columns:
    - Item_Description_Long
  output_columns:
    - cleaned_description

prompt:
  template: |
    Rewrite this bacon description to be clean, professional, and factual.
    ...
  system_message: |
    You are a professional product description editor...

llm:
  provider: groq
  model: openai/gpt-oss-120b
  temperature: 0.0
  max_tokens: 400
  input_cost_per_1k_tokens: 0.00005
  output_cost_per_1k_tokens: 0.00008

processing:
  batch_size: 10
  concurrency: 3
  max_retries: 3
  max_budget: 5.0

output:
  destination_type: excel
  destination_path: "tmp/ground_truth_cleaned.xlsx"
  merge_strategy: replace
```

---

## Comparison: CLI vs SDK Script

### **CLI Approach** (Recommended for production)
```bash
# Configuration in YAML
llm-dataset process --config bacon_cleaning_config.yaml
```

**Pros:**
- ✅ Beautiful ASCII art banner
- ✅ Clean, professional output
- ✅ Easy to version control config
- ✅ No Python code needed
- ✅ Automatic progress bars
- ✅ Built-in validation

### **SDK Script Approach** (For custom logic)
```python
# Configuration in Python
python process_all_365_bacon.py
```

**Pros:**
- ✅ Full Python control
- ✅ Custom pre/post processing
- ✅ Programmatic configuration
- ✅ Easy to integrate into pipelines

---

## Tips & Tricks

### **1. Dry Run (Estimate First)**
Always estimate before processing:
```bash
llm-dataset estimate --config bacon_cleaning_config.yaml
# If cost looks good:
llm-dataset process --config bacon_cleaning_config.yaml
```

### **2. Watch Progress in Real-Time**
The CLI shows beautiful progress indicators:
```
━━━━━━ PROGRESS: 100/365 rows (27.4%) | Cost: $0.0035 ━━━━━━
```

### **3. Resume if Interrupted**
If interrupted (Ctrl+C), resume later:
```bash
# Note the session ID from logs
llm-dataset resume --session-id abc-123-def-456
```

### **4. Test with Small Sample First**
Edit your YAML to process just 10 rows:
```yaml
dataset:
  source_path: "tmp/ground_truth.xlsx"
  # Add filter to limit rows
  filters:
    limit: 10
```

Then run:
```bash
llm-dataset process --config bacon_cleaning_config.yaml
```

---

## What You Get

### **Input:** `tmp/ground_truth.xlsx`
```
pk, Item_Description_Long
1045543_5128206, OLD SMOKEHOUSE SUGAR CURED HALF SLAB BACON | BACON SLAB CC SUGAR CURE FRZN
...
```

### **Output:** `tmp/ground_truth_cleaned.xlsx`
```
pk, Item_Description_Long, cleaned_description
1045543_5128206, OLD SMOKEHOUSE SUGAR CURED HALF SLAB BACON | BACON SLAB CC SUGAR CURE FRZN, Frozen sugar-cured half-slab bacon
...
```

**No more:**
- ❌ "assistant:" prefix
- ❌ "None" outputs
- ❌ Truncated descriptions
- ❌ Brand names and codes

---

## Troubleshooting

### **Issue: "Configuration file not found"**
```bash
# Check path
ls bacon_cleaning_config.yaml

# Use absolute path if needed
llm-dataset process --config /full/path/to/bacon_cleaning_config.yaml
```

### **Issue: "API key not found"**
```bash
# Set environment variable
export GROQ_API_KEY="your-key-here"

# Or add to config
llm:
  api_key: "your-key-here"  # Not recommended for security
```

### **Issue: Rate limits (429 errors)**
Reduce concurrency in your YAML:
```yaml
processing:
  concurrency: 2  # Reduce from 3 to 2
```

---

## Next Steps

1. **Run the CLI:**
   ```bash
   export GROQ_API_KEY="your-key"
   llm-dataset process --config bacon_cleaning_config.yaml
   ```

2. **Check results:**
   ```bash
   open tmp/ground_truth_cleaned.xlsx
   ```

3. **Adjust config if needed** and re-run!

---

## Summary

**The CLI is now beautiful and production-ready!** 🎉

- 🎨 **Stunning ASCII art banner**
- 📊 **Clear progress indicators**
- 🚀 **Simple commands**
- ⚙️  **YAML configuration**
- 🔧 **Built-in validation**

**No more Python scripts needed - just run:**
```bash
llm-dataset process --config bacon_cleaning_config.yaml
```
