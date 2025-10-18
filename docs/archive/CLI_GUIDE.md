# 🖥️ CLI User Guide - LLM Dataset Engine

**Command**: `llm-dataset`  
**Version**: 1.0.0  
**Status**: ✅ Fully Functional

---

## 📋 Quick Reference

```bash
# Process dataset
llm-dataset process -c config.yaml -i data.csv -o result.csv

# Estimate cost
llm-dataset estimate -c config.yaml -i data.csv

# Validate config
llm-dataset validate -c config.yaml

# Inspect data file
llm-dataset inspect -i data.csv

# List checkpoints
llm-dataset list-checkpoints

# Resume from checkpoint
llm-dataset resume -s session-id
```

---

## 🚀 Installation

```bash
# Install the package
pip install llm-dataset-engine

# Or with uv
uv add llm-dataset-engine

# Verify installation
llm-dataset --version
```

---

## 📖 Commands

### **1. `process` - Process Dataset**

**Purpose**: Transform dataset using LLM according to configuration

**Usage**:
```bash
llm-dataset process [OPTIONS]
```

**Required Options**:
- `-c, --config PATH` - Configuration file (YAML/JSON)
- `-i, --input PATH` - Input data file (CSV, Excel, Parquet)
- `-o, --output PATH` - Output file path

**Optional Options**:
- `--provider [openai|azure_openai|anthropic|groq]` - Override LLM provider
- `--model TEXT` - Override model name
- `--max-budget FLOAT` - Override maximum budget (USD)
- `--batch-size INTEGER` - Override batch size
- `--concurrency INTEGER` - Override concurrency
- `--checkpoint-dir PATH` - Override checkpoint directory
- `--dry-run` - Validate and estimate only, don't execute
- `-v, --verbose` - Enable verbose logging

**Examples**:

```bash
# Basic usage
llm-dataset process -c config.yaml -i products.csv -o products_cleaned.csv

# Override provider and model
llm-dataset process -c config.yaml -i data.csv -o result.csv \
    --provider groq --model openai/gpt-oss-120b

# Set budget limit
llm-dataset process -c config.yaml -i data.csv -o result.csv \
    --max-budget 10.0

# Dry run (estimate only)
llm-dataset process -c config.yaml -i data.csv -o result.csv --dry-run

# With custom settings
llm-dataset process -c config.yaml -i data.csv -o result.csv \
    --batch-size 50 \
    --concurrency 10 \
    --checkpoint-dir /tmp/checkpoints \
    --verbose
```

**Output**:
```
Loading configuration from config.yaml...
Creating pipeline...
Validating pipeline...
✅ Validation passed

Estimating cost...
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Metric        ┃ Value    ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Total Cost    │ $0.0245  │
│ Total Tokens  │ 1,234    │
│ Rows          │ 100      │
└───────────────┴──────────┘

Processing dataset...
✅ Processing complete!

┏━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Metric        ┃ Value    ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Rows Processed│ 100      │
│ Successful    │ 98       │
│ Failed        │ 2        │
│ Duration      │ 45.23s   │
│ Total Cost    │ $0.0243  │
└───────────────┴──────────┘

Output written to: result.csv
```

---

### **2. `estimate` - Cost Estimation**

**Purpose**: Estimate processing cost without executing

**Usage**:
```bash
llm-dataset estimate [OPTIONS]
```

**Required Options**:
- `-c, --config PATH` - Configuration file
- `-i, --input PATH` - Input data file

**Optional Options**:
- `--provider` - Override LLM provider
- `--model` - Override model name

**Examples**:

```bash
# Estimate cost
llm-dataset estimate -c config.yaml -i data.csv

# Estimate with different model
llm-dataset estimate -c config.yaml -i data.csv --model gpt-4o

# Estimate with different provider
llm-dataset estimate -c config.yaml -i data.csv \
    --provider anthropic --model claude-3-haiku-20240307
```

**Output**:
```
Loading configuration from config.yaml...
Estimating cost...

┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Metric           ┃ Value        ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ Total Cost       │ $12.45       │
│ Total Tokens     │ 125,000      │
│ Input Tokens     │ 75,000       │
│ Output Tokens    │ 50,000       │
│ Rows to Process  │ 10,000       │
│ Confidence       │ sample-based │
└──────────────────┴──────────────┘

Cost per row: $0.001245

⚠️  Warning: Estimated cost ($12.45) exceeds $10
```

---

### **3. `validate` - Validate Configuration**

**Purpose**: Check configuration file for errors

**Usage**:
```bash
llm-dataset validate [OPTIONS]
```

**Required Options**:
- `-c, --config PATH` - Configuration file

**Optional Options**:
- `-v, --verbose` - Show detailed configuration

**Examples**:

```bash
# Validate configuration
llm-dataset validate -c config.yaml

# Verbose validation (show config details)
llm-dataset validate -c config.yaml --verbose
```

**Output (Success)**:
```
Loading configuration from config.yaml...
✅ Configuration loaded successfully

Validating pipeline...
✅ Pipeline configuration is valid
```

**Output (Failure)**:
```
Loading configuration from config.yaml...
✅ Configuration loaded successfully

Validating pipeline...
❌ Pipeline configuration is invalid

Errors:
  • Missing required column: 'description'
  • Invalid LLM model: 'gpt-5'
  • Batch size must be between 1 and 1000
```

---

### **4. `inspect` - Inspect Data File**

**Purpose**: Preview data file structure and contents

**Usage**:
```bash
llm-dataset inspect [OPTIONS]
```

**Required Options**:
- `-i, --input PATH` - Input file to inspect

**Optional Options**:
- `--head INTEGER` - Number of rows to show (default: 5)

**Examples**:

```bash
# Inspect CSV file
llm-dataset inspect -i data.csv

# Show first 10 rows
llm-dataset inspect -i data.csv --head 10

# Inspect Excel file
llm-dataset inspect -i products.xlsx

# Inspect Parquet file
llm-dataset inspect -i large_dataset.parquet
```

**Output**:
```
Inspecting data.csv...

      File Information       
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Property      ┃ Value    ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ File Path     │ data.csv │
│ File Type     │ CSV      │
│ Total Rows    │ 10,523   │
│ Total Columns │ 8        │
│ Memory Usage  │ 2.45 MB  │
└───────────────┴──────────┘

Columns:
  • id (int64) - 0 nulls
  • description (object) - 15 nulls
  • category (object) - 0 nulls
  • price (float64) - 3 nulls

First 5 rows:
   id                    description  category  price
0   1  Apple iPhone 13 Pro 256GB  Electronics  999.0
1   2  Samsung Galaxy S22 Ultra   Electronics  899.0
...
```

---

### **5. `list-checkpoints` - List Checkpoints**

**Purpose**: Show available checkpoints for recovery

**Usage**:
```bash
llm-dataset list-checkpoints [OPTIONS]
```

**Optional Options**:
- `--checkpoint-dir PATH` - Checkpoint directory (default: .checkpoints)

**Examples**:

```bash
# List checkpoints
llm-dataset list-checkpoints

# List from custom directory
llm-dataset list-checkpoints --checkpoint-dir /tmp/checkpoints
```

**Output**:
```
Scanning .checkpoints for checkpoints...

        Checkpoints in .checkpoints         
┏━━━━━━━━━━━━┳━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Session ID ┃ Row ┃ Stage ┃ Timestamp           ┃ Size     ┃
┡━━━━━━━━━━━━╇━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ abc123...  │ 500 │ 2     │ 2025-10-15 10:30:00 │ 1,234 KB │
│ def456...  │ 750 │ 3     │ 2025-10-15 11:15:00 │ 2,456 KB │
└────────────┴─────┴───────┴─────────────────────┴──────────┘

Total checkpoints: 2
```

---

### **6. `resume` - Resume from Checkpoint**

**Purpose**: Continue processing from saved checkpoint

**Usage**:
```bash
llm-dataset resume [OPTIONS]
```

**Required Options**:
- `-s, --session-id TEXT` - Session ID to resume (UUID)

**Optional Options**:
- `--checkpoint-dir PATH` - Checkpoint directory (default: .checkpoints)
- `-o, --output PATH` - Override output path

**Examples**:

```bash
# Resume from checkpoint
llm-dataset resume -s abc-123-def-456

# Resume with custom checkpoint directory
llm-dataset resume -s abc-123 --checkpoint-dir /tmp/checkpoints

# Resume and override output
llm-dataset resume -s abc-123 -o new_output.csv
```

**Output**:
```
Looking for checkpoint in .checkpoints...
✅ Found checkpoint at row 5,000

        Checkpoint Information         
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Property       ┃ Value                ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ Session ID     │ abc-123-def-456      │
│ Last Row       │ 5,000                │
│ Last Stage     │ 2                    │
│ Timestamp      │ 2025-10-15 10:30:00  │
└────────────────┴──────────────────────┘

⚠️  Full resume functionality requires the original pipeline configuration
Please use Pipeline.execute(resume_from=session_id) in Python code
```

---

## 🎯 Common Workflows

### **Workflow 1: Process with Cost Check**

```bash
# Step 1: Validate configuration
llm-dataset validate -c config.yaml

# Step 2: Inspect input data
llm-dataset inspect -i data.csv

# Step 3: Estimate cost
llm-dataset estimate -c config.yaml -i data.csv

# Step 4: If cost acceptable, process
llm-dataset process -c config.yaml -i data.csv -o result.csv
```

---

### **Workflow 2: Safe Processing with Budget**

```bash
# Process with budget limit and dry-run first
llm-dataset process -c config.yaml -i data.csv -o result.csv \
    --max-budget 10.0 \
    --dry-run

# If estimate looks good, run for real
llm-dataset process -c config.yaml -i data.csv -o result.csv \
    --max-budget 10.0
```

---

### **Workflow 3: Batch Processing in Shell Script**

```bash
#!/bin/bash
# process_daily.sh

DATE=$(date +%Y%m%d)
INPUT="data/daily_${DATE}.csv"
OUTPUT="results/processed_${DATE}.csv"
CONFIG="configs/daily_enrichment.yaml"

echo "Processing data for $DATE..."

# Estimate first
llm-dataset estimate -c $CONFIG -i $INPUT

# Ask for confirmation
read -p "Proceed with processing? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Process
    llm-dataset process -c $CONFIG -i $INPUT -o $OUTPUT \
        --max-budget 50.0 \
        --verbose
    
    if [ $? -eq 0 ]; then
        echo "✅ Processing successful"
        # Trigger downstream jobs
        ./load_to_warehouse.sh $OUTPUT
    else
        echo "❌ Processing failed"
        exit 1
    fi
fi
```

---

### **Workflow 4: Cron Job**

```bash
# Add to crontab
# Process data every day at 2 AM
0 2 * * * cd /path/to/project && llm-dataset process -c config.yaml -i daily.csv -o result.csv >> logs/llm-$(date +\%Y\%m\%d).log 2>&1
```

---

## ⚙️ Configuration File

**Example config.yaml**:
```yaml
# Dataset configuration
dataset:
  source_type: csv
  input_columns: [description, category]
  output_columns: [cleaned_description, sentiment]
  delimiter: ","
  encoding: utf-8

# Prompt configuration
prompt:
  template: |
    Clean and analyze this product:
    Description: {description}
    Category: {category}
    
    Return JSON: {{"cleaned_description": "...", "sentiment": "..."}}
  system_message: "You are a data processing assistant."

# LLM configuration
llm:
  provider: groq
  model: openai/gpt-oss-120b
  temperature: 0.0
  max_tokens: 200

# Processing configuration
processing:
  batch_size: 50
  concurrency: 5
  max_retries: 3
  error_policy: skip
  rate_limit_rpm: 100
  max_budget: 10.0
  checkpoint_interval: 500

# Output configuration
output:
  format: csv
  merge_strategy: replace
```

---

## 🔑 Environment Variables

```bash
# LLM Provider API Keys
export GROQ_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"
export AZURE_OPENAI_API_KEY="your-key-here"
export AZURE_OPENAI_ENDPOINT="https://your-endpoint.openai.azure.com/"

# Optional: Override defaults
export LLM_DATASET_CHECKPOINT_DIR="/tmp/checkpoints"
export LLM_DATASET_LOG_LEVEL="INFO"
```

---

## 🐛 Troubleshooting

### **Issue: Command not found**

```bash
$ llm-dataset --help
-bash: llm-dataset: command not found
```

**Solution**:
```bash
# Reinstall package
pip install --force-reinstall llm-dataset-engine

# Or with uv
uv sync
```

---

### **Issue: Config validation fails**

```bash
❌ Pipeline configuration is invalid
Errors:
  • Missing required column: 'description'
```

**Solution**:
1. Check your config file has correct `input_columns`
2. Inspect your data: `llm-dataset inspect -i data.csv`
3. Ensure column names match exactly (case-sensitive)

---

### **Issue: High cost estimate**

```bash
⚠️  Warning: Estimated cost ($125.45) exceeds $10
```

**Solution**:
```bash
# Use cheaper model
llm-dataset process -c config.yaml -i data.csv -o result.csv \
    --model gpt-4o-mini  # Cheaper than gpt-4o

# Or reduce max_tokens in config
llm:
  max_tokens: 100  # Reduce from 500

# Or process subset first
head -100 data.csv > sample.csv
llm-dataset process -c config.yaml -i sample.csv -o result.csv
```

---

## 📊 Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Validation error or execution failure |
| 2 | Configuration error |
| 130 | Interrupted by user (Ctrl+C) |

**Usage in scripts**:
```bash
llm-dataset process -c config.yaml -i data.csv -o result.csv

if [ $? -eq 0 ]; then
    echo "Success!"
else
    echo "Failed!"
    exit 1
fi
```

---

## 🎨 Output Formatting

The CLI uses **Rich** for beautiful terminal output:
- ✅ Colored output (green=success, red=error, yellow=warning)
- 📊 Tables for structured data
- 📈 Progress indicators
- 🎯 Clear status messages

**Disable colors** (for logging):
```bash
NO_COLOR=1 llm-dataset process -c config.yaml -i data.csv -o result.csv
```

---

## 🔗 Integration with Other Tools

### **With Make**

```makefile
# Makefile
process-data:
\t@echo "Processing data..."
\tllm-dataset process -c config.yaml -i data.csv -o result.csv

estimate:
\t@echo "Estimating cost..."
\tllm-dataset estimate -c config.yaml -i data.csv

validate:
\t@echo "Validating config..."
\tllm-dataset validate -c config.yaml

.PHONY: process-data estimate validate
```

```bash
# Usage
make estimate
make process-data
```

---

### **With Docker**

```dockerfile
FROM python:3.10-slim

# Install CLI
RUN pip install llm-dataset-engine

# Copy configs
COPY configs/ /app/configs/
COPY data/ /app/data/

WORKDIR /app

# Set API key
ENV GROQ_API_KEY=${GROQ_API_KEY}

# Run processing
CMD ["llm-dataset", "process", "-c", "configs/config.yaml", "-i", "data/input.csv", "-o", "data/output.csv"]
```

```bash
# Build and run
docker build -t llm-processor .
docker run -e GROQ_API_KEY=$GROQ_API_KEY -v $(pwd)/data:/app/data llm-processor
```

---

### **With GitHub Actions**

```yaml
# .github/workflows/process-data.yml
name: Process Data

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  process:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install CLI
        run: pip install llm-dataset-engine
      
      - name: Process data
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
        run: |
          llm-dataset process \
            -c config.yaml \
            -i data/input.csv \
            -o data/output.csv \
            --max-budget 10.0
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: processed-data
          path: data/output.csv
```

---

## 📚 Advanced Usage

### **Override Multiple Settings**

```bash
llm-dataset process \
    -c config.yaml \
    -i data.csv \
    -o result.csv \
    --provider groq \
    --model openai/gpt-oss-120b \
    --max-budget 5.0 \
    --batch-size 100 \
    --concurrency 10 \
    --checkpoint-dir /tmp/checkpoints \
    --verbose
```

### **Process Multiple Files**

```bash
#!/bin/bash
# process_all.sh

for file in data/*.csv; do
    basename=$(basename "$file" .csv)
    echo "Processing $basename..."
    
    llm-dataset process \
        -c config.yaml \
        -i "$file" \
        -o "results/${basename}_processed.csv" \
        --max-budget 5.0
    
    if [ $? -ne 0 ]; then
        echo "Failed: $basename"
        exit 1
    fi
done

echo "✅ All files processed"
```

### **Conditional Processing**

```bash
#!/bin/bash
# smart_process.sh

# Estimate first
COST=$(llm-dataset estimate -c config.yaml -i data.csv | grep "Total Cost" | awk '{print $3}' | tr -d '$')

# Check if cost is acceptable
if (( $(echo "$COST < 10.0" | bc -l) )); then
    echo "Cost $COST is acceptable, processing..."
    llm-dataset process -c config.yaml -i data.csv -o result.csv
else
    echo "Cost $COST too high, skipping..."
    exit 1
fi
```

---

## 🎓 Tips & Best Practices

### **1. Always Estimate First**
```bash
# Good practice
llm-dataset estimate -c config.yaml -i data.csv
# Review cost, then:
llm-dataset process -c config.yaml -i data.csv -o result.csv
```

### **2. Use Dry Run for Testing**
```bash
# Test configuration without spending money
llm-dataset process -c config.yaml -i data.csv -o result.csv --dry-run
```

### **3. Set Budget Limits**
```bash
# Prevent runaway costs
llm-dataset process -c config.yaml -i data.csv -o result.csv --max-budget 10.0
```

### **4. Inspect Data First**
```bash
# Understand your data before processing
llm-dataset inspect -i data.csv
```

### **5. Use Checkpoints for Large Files**
```bash
# For large datasets, checkpoints save progress
# If interrupted, resume with:
llm-dataset resume -s <session-id>
```

---

## 📞 Support

- **Documentation**: See `ONBOARDING.md` for SDK usage
- **Examples**: See `examples/` directory
- **Issues**: GitHub Issues
- **Help**: `llm-dataset COMMAND --help`

---

**Happy Processing! 🚀**

