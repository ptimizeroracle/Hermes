# 🚀 LLM Dataset Engine - User Onboarding Guide

Welcome! This guide will help you understand and use the LLM Dataset Engine effectively.

---

## 📋 Table of Contents

1. [What is This?](#what-is-this)
2. [Quick Start (5 Minutes)](#quick-start-5-minutes)
3. [Core Concepts](#core-concepts)
4. [Usage Patterns](#usage-patterns)
5. [Integration Guide](#integration-guide)
6. [Configuration](#configuration)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)

---

## What is This?

**LLM Dataset Engine** is a production-ready SDK for processing tabular datasets (CSV, Excel, Parquet) using Large Language Models with:

✅ **Reliability**: Automatic retries, checkpointing, error handling  
✅ **Cost Control**: Budget limits, cost estimation, real-time tracking  
✅ **Observability**: Progress bars, structured logging, metrics  
✅ **Flexibility**: Multiple LLM providers, custom parsers, plugin architecture  

### Real-World Use Cases

- **Data Cleaning**: Clean messy product descriptions, normalize addresses
- **Classification**: Categorize customer reviews, tag support tickets
- **Extraction**: Extract structured data from unstructured text
- **Enrichment**: Add sentiment scores, generate summaries
- **Translation**: Translate datasets across languages
- **Validation**: Check data quality, flag anomalies

---

## Quick Start (5 Minutes)

### Installation

```bash
# Using uv (recommended)
uv add llm-dataset-engine

# Or using pip
pip install llm-dataset-engine
```

### Your First Pipeline (3 Lines!)

```python
from llm_dataset_engine import PipelineBuilder

# Process CSV with LLM
pipeline = (
    PipelineBuilder.create()
    .from_csv("data.csv", input_columns=["text"], output_columns=["result"])
    .with_prompt("Clean this text: {text}")
    .with_llm(provider="groq", model="openai/gpt-oss-120b")
    .to_csv("output.csv")
    .build()
)

result = pipeline.execute()
print(f"✅ Processed {result.metrics.total_rows} rows in {result.duration:.2f}s")
```

### Set Your API Key

```bash
# Groq (fast & affordable)
export GROQ_API_KEY="your-key-here"

# Or OpenAI
export OPENAI_API_KEY="your-key-here"

# Or Anthropic
export ANTHROPIC_API_KEY="your-key-here"
```

---

## Core Concepts

### 1. **Pipeline Architecture**

The engine follows a **5-stage pipeline**:

```
Data Source → Prompt Formatting → LLM Invocation → Response Parsing → Output
```

Each stage is:
- **Independent**: Can be customized or replaced
- **Testable**: Isolated unit tests
- **Observable**: Logs and metrics at each step

### 2. **Configuration-Driven**

Everything is configured through **specifications**:

```python
from llm_dataset_engine.core.specifications import (
    DatasetSpec,
    PromptSpec,
    LLMSpec,
    ProcessingSpec,
)

# Define what to process
dataset_spec = DatasetSpec(
    source_type="csv",
    source_path="data.csv",
    input_columns=["description"],
    output_columns=["cleaned"],
)

# Define how to prompt
prompt_spec = PromptSpec(
    template="Clean: {description}",
    system_message="You are a data cleaning assistant.",
)

# Define which LLM
llm_spec = LLMSpec(
    provider="groq",
    model="openai/gpt-oss-120b",
    temperature=0.0,
)

# Define processing behavior
processing_spec = ProcessingSpec(
    batch_size=50,
    concurrency=5,
    max_retries=3,
    error_policy="skip",
)
```

### 3. **Builder Pattern (Recommended)**

For convenience, use the fluent builder API:

```python
pipeline = (
    PipelineBuilder.create()
    .from_csv("data.csv", input_columns=["text"], output_columns=["result"])
    .with_prompt("Process: {text}")
    .with_llm(provider="groq", model="openai/gpt-oss-120b")
    .with_batch_size(50)
    .with_concurrency(5)
    .with_max_retries(3)
    .with_error_policy("skip")
    .to_csv("output.csv")
    .build()
)
```

---

## Usage Patterns

### Pattern 1: Simple Transformation

**Use Case**: Transform each row independently

```python
import pandas as pd
from llm_dataset_engine import PipelineBuilder

df = pd.DataFrame({
    "product": ["APPLE IPHONE 13", "SAMSUNG GALAXY S22"],
})

pipeline = (
    PipelineBuilder.create()
    .from_dataframe(df, input_columns=["product"], output_columns=["cleaned"])
    .with_prompt("Clean product name: {product}")
    .with_llm(provider="groq", model="openai/gpt-oss-120b")
    .build()
)

result = pipeline.execute()
print(result.data)
```

### Pattern 2: Structured Extraction

**Use Case**: Extract structured data (JSON)

```python
from llm_dataset_engine.stages import JSONParser

pipeline = (
    PipelineBuilder.create()
    .from_csv("products.csv", 
              input_columns=["description"], 
              output_columns=["brand", "model", "price"])
    .with_prompt("""
Extract product details as JSON:
{description}

Return JSON with keys: brand, model, price
""")
    .with_llm(provider="groq", model="openai/gpt-oss-120b")
    .with_parser(JSONParser(strict=False))
    .to_csv("extracted.csv")
    .build()
)

result = pipeline.execute()
```

### Pattern 3: Type-Safe Extraction (Pydantic)

**Use Case**: Validate extracted data against schema

```python
from pydantic import BaseModel
from llm_dataset_engine.stages import PydanticParser

class Product(BaseModel):
    brand: str
    model: str
    price: float

pipeline = (
    PipelineBuilder.create()
    .from_csv("products.csv", 
              input_columns=["description"],
              output_columns=["brand", "model", "price"])
    .with_prompt("Extract: {description}\n\nJSON:")
    .with_llm(provider="groq", model="openai/gpt-oss-120b")
    .with_parser(PydanticParser(Product, strict=True))
    .build()
)
```

### Pattern 4: Configuration File

**Use Case**: Version control your pipelines

```yaml
# config.yaml
dataset:
  source_type: csv
  source_path: data.csv
  input_columns: [text]
  output_columns: [result]

prompt:
  template: "Process: {text}"
  system_message: "You are a helpful assistant."

llm:
  provider: groq
  model: openai/gpt-oss-120b
  temperature: 0.0

processing:
  batch_size: 50
  concurrency: 5
  max_retries: 3
  error_policy: skip
```

```python
from llm_dataset_engine.config import ConfigLoader
from llm_dataset_engine.api import Pipeline

# Load from YAML
specs = ConfigLoader.from_yaml("config.yaml")
pipeline = Pipeline(specs)
result = pipeline.execute()
```

### Pattern 5: Cost Estimation

**Use Case**: Estimate costs before running

```python
pipeline = PipelineBuilder.create()...build()

# Estimate first
estimate = pipeline.estimate_cost()
print(f"Estimated cost: ${estimate.total_cost}")
print(f"Estimated tokens: {estimate.total_tokens}")

# Ask for approval
if input("Proceed? (y/n): ").lower() == 'y':
    result = pipeline.execute()
```

---

## Integration Guide

### 🎯 Current Integration Capabilities

The engine is **READY** for integration as a transformation layer! Here's how:

#### ✅ What Works NOW

1. **Programmatic API** - Import and use in your code
2. **Configuration-Driven** - Pass configs dynamically
3. **DataFrame In/Out** - Seamless pandas integration
4. **Chainable** - Fits into data pipelines
5. **Observable** - Hooks for monitoring

#### 🔧 Integration Methods

### Method 1: Direct Import (Simplest)

```python
# In your existing pipeline
from llm_dataset_engine import PipelineBuilder

def my_data_pipeline():
    # Your existing code
    df = load_data()
    df = clean_data(df)
    
    # Add LLM transformation layer
    llm_pipeline = (
        PipelineBuilder.create()
        .from_dataframe(df, 
                       input_columns=["text"], 
                       output_columns=["enriched"])
        .with_prompt("Enrich: {text}")
        .with_llm(provider="groq", model="openai/gpt-oss-120b")
        .build()
    )
    
    result = llm_pipeline.execute()
    enriched_df = result.data
    
    # Continue your pipeline
    save_data(enriched_df)
```

### Method 2: As a Transform Function

```python
from llm_dataset_engine import PipelineBuilder
import pandas as pd

def llm_transform(
    df: pd.DataFrame,
    input_cols: list[str],
    output_cols: list[str],
    prompt: str,
    llm_config: dict
) -> pd.DataFrame:
    """Reusable LLM transformation function."""
    pipeline = (
        PipelineBuilder.create()
        .from_dataframe(df, 
                       input_columns=input_cols, 
                       output_columns=output_cols)
        .with_prompt(prompt)
        .with_llm(**llm_config)
        .build()
    )
    
    result = pipeline.execute()
    return result.data

# Use in your pipeline
df = pd.read_csv("data.csv")
df = llm_transform(
    df,
    input_cols=["description"],
    output_cols=["category"],
    prompt="Categorize: {description}",
    llm_config={"provider": "groq", "model": "openai/gpt-oss-120b"}
)
```

### Method 3: With External Config

```python
import yaml
from llm_dataset_engine.config import ConfigLoader
from llm_dataset_engine.api import Pipeline

def process_with_config(df, config_path):
    """Process DataFrame using external config."""
    # Load config
    specs = ConfigLoader.from_yaml(config_path)
    
    # Override dataset with runtime DataFrame
    specs.dataset.source_type = "dataframe"
    
    # Create pipeline
    pipeline = Pipeline(specs)
    pipeline._dataframe = df  # Inject DataFrame
    
    result = pipeline.execute()
    return result.data

# Usage
df = pd.read_csv("data.csv")
enriched = process_with_config(df, "llm_config.yaml")
```

### Method 4: Airflow/Prefect Integration

```python
# Airflow DAG
from airflow import DAG
from airflow.operators.python import PythonOperator
from llm_dataset_engine import PipelineBuilder

def llm_enrichment_task(**context):
    """Airflow task for LLM enrichment."""
    df = context['task_instance'].xcom_pull(task_ids='load_data')
    
    pipeline = (
        PipelineBuilder.create()
        .from_dataframe(df, input_columns=["text"], output_columns=["result"])
        .with_prompt("Process: {text}")
        .with_llm(provider="groq", model="openai/gpt-oss-120b")
        .with_max_budget(10.0)  # Cost control
        .build()
    )
    
    result = pipeline.execute()
    
    # Push to next task
    context['task_instance'].xcom_push(key='enriched_data', value=result.data)
    
    # Log metrics
    print(f"Cost: ${result.costs.total_cost}")
    print(f"Duration: {result.duration}s")

with DAG('data_pipeline', ...) as dag:
    load = PythonOperator(task_id='load_data', ...)
    enrich = PythonOperator(task_id='llm_enrichment', python_callable=llm_enrichment_task)
    save = PythonOperator(task_id='save_data', ...)
    
    load >> enrich >> save
```

### Method 5: Kedro Integration

```python
# In your Kedro pipeline
from kedro.pipeline import Pipeline, node
from llm_dataset_engine import PipelineBuilder

def llm_enrichment_node(df, params):
    """Kedro node for LLM processing."""
    pipeline = (
        PipelineBuilder.create()
        .from_dataframe(df, 
                       input_columns=params["input_cols"],
                       output_columns=params["output_cols"])
        .with_prompt(params["prompt"])
        .with_llm(**params["llm_config"])
        .build()
    )
    
    result = pipeline.execute()
    return result.data

def create_pipeline(**kwargs):
    return Pipeline([
        node(
            func=llm_enrichment_node,
            inputs=["raw_data", "params:llm_enrichment"],
            outputs="enriched_data",
            name="llm_enrichment",
        ),
    ])
```

---

## ⚠️ Current Limitations & Roadmap

### What's Missing for Full Integration

| Feature | Status | Priority | ETA |
|---------|--------|----------|-----|
| **Streaming API** | ❌ Not implemented | HIGH | Week 1 |
| **Async/Await Support** | ❌ Not implemented | HIGH | Week 1 |
| **CLI Tool** | ❌ Not implemented | MEDIUM | Week 2 |
| **REST API Server** | ❌ Not implemented | MEDIUM | Week 2 |
| **Callback Hooks** | ⚠️ Partial (observers) | MEDIUM | Week 2 |
| **Custom Stage Registry** | ❌ Not implemented | LOW | Week 3 |
| **Plugin System** | ⚠️ Partial | LOW | Week 3 |

### Roadmap to Production-Ready Integration

#### Phase 1: Core Integration Features (Week 1)

**Goal**: Make it easy to embed in existing pipelines

```python
# 1. Streaming API for large datasets
async def process_stream():
    async for batch in pipeline.execute_stream(chunk_size=1000):
        await downstream_processor(batch)

# 2. Async support
result = await pipeline.execute_async()

# 3. Callback hooks
pipeline.on_batch_complete(lambda batch: log_metrics(batch))
pipeline.on_error(lambda error: alert_team(error))
```

**Implementation Plan**:
- [ ] Add `execute_stream()` method returning iterator
- [ ] Add `execute_async()` with asyncio support
- [ ] Add callback system (on_start, on_batch, on_complete, on_error)
- [ ] Add progress callback for custom progress bars

#### Phase 2: Deployment Features (Week 2)

**Goal**: Deploy as a service

```bash
# CLI tool
llm-dataset process --config config.yaml --input data.csv --output result.csv

# REST API server
llm-dataset serve --port 8000

# Then call via HTTP
curl -X POST http://localhost:8000/process \
  -F "file=@data.csv" \
  -F "config=@config.yaml"
```

**Implementation Plan**:
- [ ] Create CLI with `click` or `typer`
- [ ] Add FastAPI REST server
- [ ] Add Docker support
- [ ] Add Kubernetes manifests

#### Phase 3: Advanced Integration (Week 3)

**Goal**: Plugin ecosystem

```python
# Custom stage registration
from llm_dataset_engine import StageRegistry

@StageRegistry.register("my_custom_stage")
class MyCustomStage(PipelineStage):
    def process(self, data, context):
        # Custom logic
        return transformed_data

# Use in pipeline
pipeline = (
    PipelineBuilder.create()
    .add_stage("my_custom_stage", config={...})
    .build()
)
```

**Implementation Plan**:
- [ ] Create stage registry system
- [ ] Add plugin discovery mechanism
- [ ] Create plugin template/cookiecutter
- [ ] Add plugin marketplace/docs

---

## Configuration

### Environment Variables

```bash
# LLM Provider Keys
export GROQ_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export AZURE_OPENAI_API_KEY="your-key"

# Optional: Logging
export LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR
export LOG_FORMAT="json"  # json or console

# Optional: Monitoring
export PROMETHEUS_PORT="9090"
```

### YAML Configuration

```yaml
# Full configuration example
name: "my_pipeline"
version: "1.0"

dataset:
  source_type: csv
  source_path: data.csv
  input_columns: [description, category]
  output_columns: [cleaned_description, sentiment]
  delimiter: ","
  encoding: utf-8

prompt:
  template: |
    Clean and analyze:
    Description: {description}
    Category: {category}
    
    Return JSON with: cleaned_description, sentiment
  system_message: "You are a data processing assistant."
  few_shot_examples:
    - input: "BACON APPLEWOOD 14/18"
      output: '{"cleaned_description": "Applewood Bacon 14-18oz", "sentiment": "neutral"}'

llm:
  provider: groq
  model: openai/gpt-oss-120b
  temperature: 0.0
  max_tokens: 200
  input_cost_per_1k_tokens: "0.00005"
  output_cost_per_1k_tokens: "0.00008"

processing:
  batch_size: 50
  concurrency: 5
  max_retries: 3
  retry_delay: 1.0
  error_policy: skip  # skip, fail, retry, use_default
  rate_limit_rpm: 100
  max_budget: 10.0
  checkpoint_interval: 500

output:
  path: output.csv
  format: csv
  merge_strategy: replace
```

---

## Advanced Features

### 1. Error Handling Policies

```python
# SKIP: Skip failed rows, continue processing
pipeline.with_error_policy("skip")

# FAIL: Stop pipeline on first error
pipeline.with_error_policy("fail")

# USE_DEFAULT: Use default value for failed rows
pipeline.with_error_policy("use_default", default_value="N/A")
```

### 2. Checkpointing & Resume

```python
# Enable checkpointing
pipeline = (
    PipelineBuilder.create()
    .from_csv("large_file.csv", ...)
    .with_checkpoint_dir("./checkpoints")
    .with_checkpoint_interval(500)  # Save every 500 rows
    .build()
)

# If it crashes, resume from checkpoint
result = pipeline.execute(resume_from=session_id)
```

### 3. Cost Control

```python
# Set budget limit
pipeline.with_max_budget(10.0)  # Max $10

# Get warnings at thresholds
pipeline.with_budget_warnings(at_75=True, at_90=True)

# Estimate before running
estimate = pipeline.estimate_cost()
if estimate.total_cost > 5.0:
    print("Too expensive!")
```

### 4. Custom Parsers

```python
from llm_dataset_engine.stages import ResponseParser

class MyCustomParser(ResponseParser):
    def parse(self, response: str) -> dict:
        # Your custom parsing logic
        return {"result": response.strip().upper()}

pipeline.with_parser(MyCustomParser())
```

### 5. Monitoring & Observability

```python
# Add custom observers
from llm_dataset_engine.orchestration import ExecutionObserver

class MetricsObserver(ExecutionObserver):
    def on_stage_complete(self, stage, result, context):
        # Send metrics to your monitoring system
        send_to_datadog({
            "stage": stage.name,
            "duration": result.duration,
            "cost": result.cost,
        })

pipeline.add_observer(MetricsObserver())
```

---

## Troubleshooting

### Issue: "Rate limit exceeded"

**Solution**: Add rate limiting

```python
pipeline.with_rate_limit(requests_per_minute=60)
```

### Issue: "Out of memory with large files"

**Solution**: Use streaming (coming in Week 1)

```python
# Current workaround: Process in chunks
for chunk in pd.read_csv("large.csv", chunksize=1000):
    result = process_chunk(chunk)
    save_chunk(result)
```

### Issue: "Responses don't match input order"

**Solution**: ✅ Fixed in v1.0.0! Concurrent execution now maintains order.

### Issue: "Costs too high"

**Solutions**:
1. Use cheaper model: `model="openai/gpt-oss-120b"` (Groq)
2. Reduce max_tokens: `max_tokens=100`
3. Set budget limit: `with_max_budget(5.0)`
4. Estimate first: `pipeline.estimate_cost()`

### Issue: "Pipeline hangs"

**Solutions**:
1. Check API key is valid
2. Reduce concurrency: `with_concurrency(1)`
3. Add timeout: `with_timeout(30)`
4. Check logs: `export LOG_LEVEL=DEBUG`

---

## Next Steps

1. **Try the examples**: `cd examples && python 01_quickstart.py`
2. **Read the architecture doc**: `LLM_DATASET_ENGINE.md`
3. **Check the tests**: `uv run pytest tests/`
4. **Join the community**: [GitHub Issues](https://github.com/...)

---

## Support

- **Documentation**: See `LLM_DATASET_ENGINE.md`
- **Examples**: See `examples/` directory
- **Issues**: GitHub Issues
- **Questions**: GitHub Discussions

---

**Happy Processing! 🚀**

