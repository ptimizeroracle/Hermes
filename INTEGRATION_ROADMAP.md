# 🔌 Integration Roadmap - Making LLM Dataset Engine Fully Transportable

## Executive Summary

**Current State**: ✅ **70% Ready for Integration**

The engine is **usable NOW** as a transformation layer in existing pipelines, but lacks some features for seamless enterprise integration.

**Timeline to 100%**: 3 weeks

---

## Current Integration Capabilities

### ✅ What Works TODAY

| Capability | Status | Example |
|-----------|--------|---------|
| **Programmatic API** | ✅ Ready | `from llm_dataset_engine import PipelineBuilder` |
| **DataFrame In/Out** | ✅ Ready | Seamless pandas integration |
| **Configuration Objects** | ✅ Ready | Pass specs programmatically |
| **YAML/JSON Config** | ✅ Ready | `ConfigLoader.from_yaml()` |
| **Error Handling** | ✅ Ready | 4 policies: SKIP, FAIL, RETRY, USE_DEFAULT |
| **Cost Control** | ✅ Ready | Budget limits, estimation |
| **Checkpointing** | ✅ Ready | Resume from failures |
| **Observability** | ✅ Ready | Logs, metrics, progress bars |
| **Multi-Provider** | ✅ Ready | Groq, OpenAI, Anthropic, Azure |

### ⚠️ What's Partially Working

| Capability | Status | Limitation |
|-----------|--------|------------|
| **Streaming** | ⚠️ Partial | Only chunked CSV reading, no true streaming API |
| **Async Support** | ⚠️ Partial | Concurrent threads, but no async/await |
| **Callbacks** | ⚠️ Partial | Observer pattern exists, but limited hooks |
| **Plugin System** | ⚠️ Partial | Can subclass stages, but no registry |

### ❌ What's Missing

| Capability | Impact | Priority |
|-----------|--------|----------|
| **CLI Tool** | Can't use from command line | HIGH |
| **REST API** | Can't deploy as service | HIGH |
| **Streaming API** | Can't process infinite streams | HIGH |
| **Async/Await** | Can't integrate with async frameworks | HIGH |
| **Custom Stage Registry** | Hard to add custom stages | MEDIUM |
| **Health Check API** | Hard to monitor in production | MEDIUM |
| **Metrics Export** | No Prometheus/Grafana integration | MEDIUM |

---

## Integration Scenarios & Solutions

### Scenario 1: Embed in Existing Python Pipeline

**Current State**: ✅ **WORKS**

```python
# Your existing pipeline
def my_data_pipeline():
    df = load_data()
    df = clean_data(df)
    
    # ✅ Add LLM transformation
    from llm_dataset_engine import PipelineBuilder
    
    llm_pipeline = (
        PipelineBuilder.create()
        .from_dataframe(df, input_columns=["text"], output_columns=["result"])
        .with_prompt("Process: {text}")
        .with_llm(provider="groq", model="openai/gpt-oss-120b")
        .build()
    )
    
    result = llm_pipeline.execute()
    enriched_df = result.data
    
    save_data(enriched_df)
```

**What's Missing**: Nothing! This works today.

---

### Scenario 2: Airflow/Prefect/Dagster Integration

**Current State**: ✅ **WORKS** (with minor boilerplate)

```python
# Airflow example
from airflow.operators.python import PythonOperator
from llm_dataset_engine import PipelineBuilder

def llm_task(**context):
    df = context['ti'].xcom_pull(task_ids='previous_task')
    
    pipeline = (
        PipelineBuilder.create()
        .from_dataframe(df, ...)
        .with_llm(...)
        .build()
    )
    
    result = pipeline.execute()
    context['ti'].xcom_push(key='result', value=result.data)

# ✅ Works, but could be easier
```

**What's Missing**:
- Pre-built Airflow operators
- Pre-built Prefect tasks
- Better XCom serialization

**Roadmap**:
```python
# Week 2: Add pre-built operators
from llm_dataset_engine.integrations.airflow import LLMTransformOperator

llm_task = LLMTransformOperator(
    task_id='llm_enrichment',
    config_path='config.yaml',
    input_xcom='previous_task',
    output_xcom='enriched_data',
)
```

---

### Scenario 3: Kedro Integration

**Current State**: ✅ **WORKS** (as a node)

```python
# Kedro pipeline
from kedro.pipeline import node
from llm_dataset_engine import PipelineBuilder

def llm_node(df, params):
    pipeline = PipelineBuilder.create()...build()
    return pipeline.execute().data

# ✅ Works as a regular node
```

**What's Missing**:
- Kedro dataset type for configs
- Better parameter management

**Roadmap**:
```python
# Week 2: Add Kedro dataset
from llm_dataset_engine.integrations.kedro import LLMConfigDataset

# In catalog.yml
llm_config:
  type: llm_dataset_engine.integrations.kedro.LLMConfigDataset
  filepath: conf/llm_config.yaml
```

---

### Scenario 4: Streaming Data (Kafka, Kinesis)

**Current State**: ❌ **DOESN'T WORK**

```python
# ❌ Can't do this yet
from kafka import KafkaConsumer

consumer = KafkaConsumer('input_topic')
for message in consumer:
    # Need to process one record at a time
    # Current engine expects batch/DataFrame
    pass
```

**What's Missing**:
- Single-record processing API
- Streaming iterator support
- Async processing

**Roadmap**:
```python
# Week 1: Add streaming API
from llm_dataset_engine import StreamProcessor

processor = StreamProcessor(
    prompt="Process: {text}",
    llm_config={"provider": "groq", ...},
)

# Process stream
for message in consumer:
    result = await processor.process_one(message.value)
    producer.send('output_topic', result)
```

---

### Scenario 5: FastAPI/Flask Integration

**Current State**: ⚠️ **PARTIALLY WORKS** (synchronous only)

```python
# FastAPI example
from fastapi import FastAPI
from llm_dataset_engine import PipelineBuilder

app = FastAPI()

@app.post("/process")
def process_data(data: dict):
    # ⚠️ Works but blocks the event loop
    df = pd.DataFrame([data])
    pipeline = PipelineBuilder.create()...build()
    result = pipeline.execute()
    return result.data.to_dict()
```

**What's Missing**:
- Async/await support
- Background task processing
- Request queuing

**Roadmap**:
```python
# Week 1: Add async support
@app.post("/process")
async def process_data(data: dict):
    # ✅ Non-blocking
    df = pd.DataFrame([data])
    pipeline = PipelineBuilder.create()...build()
    result = await pipeline.execute_async()
    return result.data.to_dict()

# Week 2: Add background processing
@app.post("/process/batch")
async def process_batch(file: UploadFile, background_tasks: BackgroundTasks):
    job_id = str(uuid4())
    background_tasks.add_task(process_file, file, job_id)
    return {"job_id": job_id, "status": "processing"}
```

---

### Scenario 6: Spark Integration

**Current State**: ❌ **DOESN'T WORK**

```python
# ❌ Can't use with PySpark UDFs yet
from pyspark.sql import functions as F

# Would need to convert to pandas UDF
@pandas_udf(returnType=StringType())
def llm_transform(texts: pd.Series) -> pd.Series:
    # Need batch processing API
    pass
```

**What's Missing**:
- Batch processing function API
- Spark-compatible serialization

**Roadmap**:
```python
# Week 2: Add batch function API
from llm_dataset_engine import create_batch_function

llm_udf = create_batch_function(
    prompt="Process: {text}",
    llm_config={"provider": "groq", ...},
    batch_size=100,
)

# Use in Spark
df = spark_df.withColumn("result", llm_udf(F.col("text")))
```

---

### Scenario 7: CLI/Shell Scripts

**Current State**: ❌ **DOESN'T WORK**

```bash
# ❌ No CLI yet
llm-dataset process --config config.yaml --input data.csv --output result.csv
```

**Roadmap**:
```bash
# Week 2: Full CLI
llm-dataset process \
  --config config.yaml \
  --input data.csv \
  --output result.csv \
  --provider groq \
  --model openai/gpt-oss-120b

# With progress bar
llm-dataset process --config config.yaml --input data.csv --progress

# Estimate cost first
llm-dataset estimate --config config.yaml --input data.csv

# Resume from checkpoint
llm-dataset resume --session-id abc-123

# Serve as API
llm-dataset serve --port 8000 --config config.yaml
```

---

## 3-Week Implementation Plan

### Week 1: Core Integration Features

**Goal**: Make it work with async frameworks and streaming

#### Task 1.1: Async/Await Support (2 days)

```python
# Add async execution
class Pipeline:
    async def execute_async(self) -> ExecutionResult:
        """Execute pipeline asynchronously."""
        # Use asyncio for concurrent LLM calls
        pass

# Add async LLM clients
class AsyncLLMClient(ABC):
    @abstractmethod
    async def invoke_async(self, prompt: str) -> LLMResponse:
        pass
```

**Files to modify**:
- `llm_dataset_engine/api/pipeline.py` - Add `execute_async()`
- `llm_dataset_engine/adapters/llm_client.py` - Add async clients
- `llm_dataset_engine/stages/llm_invocation_stage.py` - Add async processing

#### Task 1.2: Streaming API (2 days)

```python
# Add streaming execution
class Pipeline:
    def execute_stream(self, chunk_size: int = 1000) -> Iterator[pd.DataFrame]:
        """Execute pipeline in streaming mode."""
        for chunk in self._stream_data(chunk_size):
            yield self._process_chunk(chunk)

# Add single-record processor
class StreamProcessor:
    def __init__(self, prompt: str, llm_config: dict):
        pass
    
    async def process_one(self, record: dict) -> dict:
        """Process single record."""
        pass
```

**Files to create**:
- `llm_dataset_engine/api/stream_processor.py`
- `llm_dataset_engine/stages/streaming_stage.py`

#### Task 1.3: Callback System (1 day)

```python
# Add callback hooks
class Pipeline:
    def on_start(self, callback: Callable):
        """Register start callback."""
        pass
    
    def on_batch_complete(self, callback: Callable):
        """Register batch completion callback."""
        pass
    
    def on_error(self, callback: Callable):
        """Register error callback."""
        pass
    
    def on_complete(self, callback: Callable):
        """Register completion callback."""
        pass
```

**Files to modify**:
- `llm_dataset_engine/api/pipeline.py`
- `llm_dataset_engine/orchestration/observers.py`

---

### Week 2: Deployment & Integration Adapters

**Goal**: Make it easy to deploy and integrate

#### Task 2.1: CLI Tool (2 days)

```python
# Create CLI using Click/Typer
import click

@click.group()
def cli():
    """LLM Dataset Engine CLI."""
    pass

@cli.command()
@click.option('--config', required=True)
@click.option('--input', required=True)
@click.option('--output', required=True)
def process(config, input, output):
    """Process dataset using config."""
    pass

@cli.command()
@click.option('--port', default=8000)
def serve(port):
    """Start API server."""
    pass
```

**Files to create**:
- `llm_dataset_engine/cli/__init__.py`
- `llm_dataset_engine/cli/main.py`
- `llm_dataset_engine/cli/commands.py`

#### Task 2.2: REST API Server (2 days)

```python
# Create FastAPI server
from fastapi import FastAPI, UploadFile, BackgroundTasks

app = FastAPI()

@app.post("/process")
async def process_data(config: dict, data: dict):
    """Process single record."""
    pass

@app.post("/process/batch")
async def process_batch(
    file: UploadFile,
    config: UploadFile,
    background_tasks: BackgroundTasks
):
    """Process batch file."""
    pass

@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job status."""
    pass
```

**Files to create**:
- `llm_dataset_engine/server/__init__.py`
- `llm_dataset_engine/server/api.py`
- `llm_dataset_engine/server/models.py`

#### Task 2.3: Integration Adapters (1 day)

```python
# Airflow operator
from airflow.models import BaseOperator

class LLMTransformOperator(BaseOperator):
    def __init__(self, config_path, input_xcom, output_xcom, **kwargs):
        super().__init__(**kwargs)
        self.config_path = config_path
        self.input_xcom = input_xcom
        self.output_xcom = output_xcom
    
    def execute(self, context):
        df = context['ti'].xcom_pull(key=self.input_xcom)
        # Process with LLM engine
        result = ...
        context['ti'].xcom_push(key=self.output_xcom, value=result)

# Kedro dataset
from kedro.io import AbstractDataSet

class LLMConfigDataset(AbstractDataSet):
    def _load(self):
        return ConfigLoader.from_yaml(self._filepath)
    
    def _save(self, data):
        pass
```

**Files to create**:
- `llm_dataset_engine/integrations/airflow.py`
- `llm_dataset_engine/integrations/prefect.py`
- `llm_dataset_engine/integrations/kedro.py`

---

### Week 3: Plugin System & Advanced Features

**Goal**: Make it extensible

#### Task 3.1: Stage Registry (2 days)

```python
# Create stage registry
class StageRegistry:
    _stages = {}
    
    @classmethod
    def register(cls, name: str):
        def decorator(stage_class):
            cls._stages[name] = stage_class
            return stage_class
        return decorator
    
    @classmethod
    def get(cls, name: str):
        return cls._stages[name]

# Use in pipeline builder
@StageRegistry.register("my_custom_stage")
class MyCustomStage(PipelineStage):
    pass

pipeline = (
    PipelineBuilder.create()
    .add_stage("my_custom_stage", config={...})
    .build()
)
```

**Files to create**:
- `llm_dataset_engine/registry/__init__.py`
- `llm_dataset_engine/registry/stage_registry.py`

#### Task 3.2: Plugin System (2 days)

```python
# Create plugin discovery
import importlib
import pkgutil

class PluginManager:
    def discover_plugins(self):
        """Discover plugins in installed packages."""
        for finder, name, ispkg in pkgutil.iter_modules():
            if name.startswith('llm_dataset_engine_'):
                module = importlib.import_module(name)
                self._load_plugin(module)
```

**Files to create**:
- `llm_dataset_engine/plugins/__init__.py`
- `llm_dataset_engine/plugins/manager.py`
- `llm_dataset_engine/plugins/template/` (cookiecutter)

#### Task 3.3: Batch Function API (1 day)

```python
# Create simple batch function API
from llm_dataset_engine import create_batch_function

# Create reusable function
llm_func = create_batch_function(
    prompt="Process: {text}",
    llm_config={"provider": "groq", ...},
    batch_size=100,
)

# Use anywhere
results = llm_func(["text1", "text2", "text3"])

# Use in pandas
df['result'] = llm_func(df['text'].tolist())

# Use in Spark
from pyspark.sql.functions import pandas_udf
spark_udf = pandas_udf(llm_func, returnType=StringType())
```

**Files to create**:
- `llm_dataset_engine/api/batch_function.py`

---

## Testing Strategy

### Integration Tests to Add

```python
# Test async execution
async def test_async_execution():
    pipeline = PipelineBuilder.create()...build()
    result = await pipeline.execute_async()
    assert result.success

# Test streaming
def test_streaming_execution():
    pipeline = PipelineBuilder.create()...build()
    chunks = list(pipeline.execute_stream(chunk_size=100))
    assert len(chunks) > 0

# Test callbacks
def test_callbacks():
    called = []
    pipeline = PipelineBuilder.create()...build()
    pipeline.on_batch_complete(lambda b: called.append(b))
    pipeline.execute()
    assert len(called) > 0

# Test CLI
def test_cli():
    result = subprocess.run([
        "llm-dataset", "process",
        "--config", "config.yaml",
        "--input", "data.csv",
        "--output", "result.csv"
    ])
    assert result.returncode == 0

# Test REST API
async def test_api():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/process", json={...})
        assert response.status_code == 200
```

---

## Documentation to Add

1. **Integration Guide** - How to integrate with popular frameworks
2. **Plugin Development Guide** - How to create custom stages
3. **Deployment Guide** - Docker, Kubernetes, serverless
4. **API Reference** - Complete API documentation
5. **Migration Guide** - Upgrading between versions

---

## Summary: Is It Ready?

### ✅ Ready NOW For:
- Embedded Python pipelines
- Batch processing
- Airflow/Prefect/Kedro (with minor boilerplate)
- Cost-controlled processing
- Error-tolerant workflows

### ⏳ Ready in 1 Week For:
- Async frameworks (FastAPI, aiohttp)
- Streaming data (Kafka, Kinesis)
- Real-time processing

### ⏳ Ready in 2 Weeks For:
- Command-line usage
- Microservice deployment
- Pre-built integrations

### ⏳ Ready in 3 Weeks For:
- Plugin ecosystem
- Spark integration
- Full extensibility

---

## Recommendation

**Start using it NOW** for batch processing in Python pipelines. The core functionality is solid and production-ready.

**Wait 1-2 weeks** if you need:
- Streaming/async support
- CLI tool
- REST API deployment

**Contribute or wait 3 weeks** if you need:
- Custom plugins
- Spark integration
- Advanced extensibility

---

**Questions? Open an issue on GitHub!**

