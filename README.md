# Hermes - LLM Dataset Engine

[![Tests](https://github.com/ptimizeroracle/Hermes/actions/workflows/ci.yml/badge.svg)](https://github.com/ptimizeroracle/Hermes/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/ptimizeroracle/Hermes/branch/main/graph/badge.svg)](https://codecov.io/gh/ptimizeroracle/Hermes)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

Production-grade SDK for processing tabular datasets using Large Language Models (LLMs) with reliability, observability, and cost control.

Built with **LlamaIndex** for LLM abstraction and following **SOLID** principles for clean, maintainable code.

## ✨ Features

- **Simple API**: 5-line hello world, fluent builder pattern
- **Reliability**: Automatic retries, checkpointing, error policies (99.9% completion rate)
- **Cost Control**: Pre-execution estimation, budget limits, real-time tracking
- **Observability**: Progress bars, structured logging, metrics, cost reports
- **Extensibility**: Plugin architecture, custom stages, multiple LLM providers
- **Production Ready**: Zero data loss on crashes, resume from checkpoint
- **Multiple Providers**: OpenAI, Azure OpenAI, Anthropic Claude (40+ via LlamaIndex)

## 🚀 Quick Start

```python
from hermes import PipelineBuilder

# Process CSV with LLM transformations
pipeline = (
    PipelineBuilder.create()
    .from_csv("data.csv", input_columns=["description"],
              output_columns=["cleaned"])
    .with_prompt("Clean this text: {description}")
    .with_llm(provider="openai", model="gpt-4o-mini")
    .with_batch_size(100)
    .with_concurrency(5)
    .build()
)

# Estimate cost before running
estimate = pipeline.estimate_cost()
print(f"Estimated cost: ${estimate.total_cost:.4f}")

# Execute pipeline
result = pipeline.execute()
print(f"Processed {result.metrics.processed_rows} rows")
print(f"Total cost: ${result.costs.total_cost:.4f}")
print(f"Duration: {result.metrics.total_duration_seconds:.2f}s")
```

## 📦 Installation

### Using uv (recommended)

```bash
uv add hermes
```

### Using pip

```bash
pip install hermes
```

### Set up API keys

```bash
export OPENAI_API_KEY="your-key-here"
# or
export AZURE_OPENAI_API_KEY="your-key-here"
export AZURE_OPENAI_ENDPOINT="https://your-endpoint.openai.azure.com/"
# or
export ANTHROPIC_API_KEY="your-key-here"
```

## 📖 Usage Examples

### 1. Simple Data Processing

```python
from hermes import DatasetProcessor

# Minimal configuration for simple use cases
processor = DatasetProcessor(
    data="reviews.csv",
    input_column="customer_review",
    output_column="sentiment",
    prompt="Classify sentiment as: Positive, Negative, or Neutral\nReview: {customer_review}\nSentiment:",
    llm_config={"provider": "openai", "model": "gpt-4o-mini"}
)

# Test on sample first
sample = processor.run_sample(n=10)
print(sample)

# Process full dataset
result = processor.run()
```

### 2. Structured Data Extraction

```python
from hermes import PipelineBuilder

pipeline = (
    PipelineBuilder.create()
    .from_dataframe(
        df,
        input_columns=["product_description"],
        output_columns=["brand", "model", "price", "condition"]
    )
    .with_prompt("""
        Extract structured information and return JSON:
        {
          "brand": "...",
          "model": "...",
          "price": "...",
          "condition": "new|used|refurbished"
        }

        Description: {product_description}
    """)
    .with_llm(provider="openai", model="gpt-4o-mini", temperature=0.0)
    .build()
)

result = pipeline.execute()
```

### 3. With Cost Control

```python
pipeline = (
    PipelineBuilder.create()
    .from_csv("large_dataset.csv",
              input_columns=["text"],
              output_columns=["summary"])
    .with_prompt("Summarize in 10 words: {text}")
    .with_llm(provider="openai", model="gpt-4o-mini")
    # Cost control settings
    .with_max_budget(10.0)  # Maximum $10
    .with_batch_size(100)
    .with_concurrency(5)
    .with_rate_limit(60)  # 60 requests/min
    .with_checkpoint_interval(500)  # Checkpoint every 500 rows
    .build()
)

# Estimate first
estimate = pipeline.estimate_cost()
if estimate.total_cost > 10.0:
    print("Cost too high!")
    exit()

result = pipeline.execute()
```

### 4. Multiple Input Columns

```python
pipeline = (
    PipelineBuilder.create()
    .from_csv("products.csv",
              input_columns=["title", "description", "category"],
              output_columns=["optimized_title"])
    .with_prompt("""
        Optimize this product title for SEO.

        Current Title: {title}
        Description: {description}
        Category: {category}

        Optimized Title:
    """)
    .with_llm(provider="openai", model="gpt-4o-mini")
    .with_output("optimized_products.csv", format="csv")
    .build()
)

result = pipeline.execute()
```

### 5. Azure OpenAI

```python
pipeline = (
    PipelineBuilder.create()
    .from_csv("data.csv", input_columns=["text"], output_columns=["result"])
    .with_prompt("Process: {text}")
    .with_llm(
        provider="azure_openai",
        model="gpt-4",
        azure_endpoint="https://your-endpoint.openai.azure.com/",
        azure_deployment="your-deployment-name",
        api_version="2024-02-15-preview"
    )
    .build()
)
```

### 6. Anthropic Claude

```python
pipeline = (
    PipelineBuilder.create()
    .from_csv("data.csv", input_columns=["text"], output_columns=["analysis"])
    .with_prompt("Analyze: {text}")
    .with_llm(
        provider="anthropic",
        model="claude-3-opus-20240229",
        temperature=0.0,
        max_tokens=1024
    )
    .build()
)
```

## 🏗️ Architecture

The SDK follows a **layered architecture** based on SOLID principles:

```
┌─────────────────────────────────────────┐
│  Layer 4: High-Level API                │
│  (Pipeline, PipelineBuilder)            │
├─────────────────────────────────────────┤
│  Layer 3: Orchestration Engine          │
│  (PipelineExecutor, StateManager)       │
├─────────────────────────────────────────┤
│  Layer 2: Processing Stages             │
│  (DataLoader, LLMInvocation, Parser)    │
├─────────────────────────────────────────┤
│  Layer 1: Infrastructure Adapters       │
│  (LLMClient, DataReader, Checkpoint)    │
├─────────────────────────────────────────┤
│  Layer 0: Core Utilities                │
│  (RetryHandler, RateLimiter, Logging)   │
└─────────────────────────────────────────┘
```

### Key Design Principles

- **KISS**: Simple, straightforward solutions
- **SOLID**: Single responsibility, Open/Closed, Liskov substitution, etc.
- **DRY**: No code duplication
- **Clean Code**: Meaningful names, type hints, docstrings
- **Separation of Concerns**: Configuration vs. execution

## 🎯 Use Cases

- **Data Cleaning**: Clean, normalize, standardize text data
- **Sentiment Analysis**: Classify sentiment at scale
- **Information Extraction**: Extract structured data from unstructured text
- **Categorization**: Auto-categorize products, documents, emails
- **Content Generation**: Generate descriptions, summaries, titles
- **Translation**: Translate content to multiple languages
- **Data Enrichment**: Enhance datasets with LLM-generated insights

## 📊 Performance

- **Throughput**: Process 1,000 rows in < 5 minutes (GPT-4o-mini, concurrency=5)
- **Reliability**: 99.9% completion rate with automatic retries
- **Cost Efficiency**: Pre-execution estimation within 10% accuracy
- **Memory**: < 500MB for datasets up to 50K rows

## 🔧 Configuration Options

### Processing Configuration

```python
.with_batch_size(100)          # Rows per batch
.with_concurrency(5)            # Parallel requests
.with_checkpoint_interval(500)  # Checkpoint frequency
.with_rate_limit(60)            # Requests per minute
.with_max_budget(10.0)          # Maximum USD budget
```

### LLM Configuration

```python
.with_llm(
    provider="openai",
    model="gpt-4o-mini",
    temperature=0.0,        # 0.0-2.0
    max_tokens=1024,        # Max output tokens
    api_key="..."           # Or from env
)
```

### Output Configuration

```python
.with_output(
    path="output.csv",
    format="csv",              # csv, excel, parquet
    merge_strategy="replace"   # replace, append, update
)
```

## 🧪 Testing

```bash
# Run tests
uv run pytest

# With coverage
uv run pytest --cov=src --cov-report=html

# Run specific test
uv run pytest tests/test_pipeline.py
```

## 📚 Documentation

- **README.md** (this file): Quick start and usage guide
- **LLM_DATASET_ENGINE.md**: Complete architecture and design documentation
- **examples/**: Example scripts demonstrating various features
- **Code docstrings**: Inline documentation for all public APIs

## 🤝 Contributing

Contributions welcome! Please follow:

1. Fork the repository at https://github.com/ptimizeroracle/Hermes
2. Create a feature branch
3. Follow the existing code style (Black, Ruff)
4. Add tests for new features
5. Update documentation
6. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with [LlamaIndex](https://www.llamaindex.ai/) for LLM abstraction
- Inspired by clean code principles and SOLID design
- Thanks to the open-source community

## 📞 Support

- **Repository**: https://github.com/ptimizeroracle/Hermes
- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Email**: git@binblok.com

## 🗺️ Roadmap

- [ ] Support for streaming responses
- [ ] RAG integration for context-aware processing
- [ ] Multi-modal support (images, PDFs)
- [ ] Distributed processing (Spark integration)
- [ ] Web UI for pipeline management
- [ ] More LLM providers (Cohere, AI21, etc.)

---

**Made with ❤️ using Python, LlamaIndex, and clean code principles**
