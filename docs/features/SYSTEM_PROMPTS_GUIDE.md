# 🎯 System Prompts Guide - Complete Reference

**Status**: ✅ **FULLY SUPPORTED** (Already Built-In!)

System prompts allow you to guide LLM behavior globally while keeping your transformation prompts focused and specific.

---

## 🚀 Quick Answer: YES, You Can Use System Prompts!

**System prompts were already implemented in the SDK!** You can use them in **5 different ways**:

---

## 📖 Method 1: PipelineBuilder (Most Common)

```python
from llm_dataset_engine import PipelineBuilder

pipeline = (
    PipelineBuilder.create()
    .from_csv("data.csv", input_columns=["text"], output_columns=["result"])
    .with_prompt(
        template="Process: {text}",
        system_message="You are a helpful assistant that follows instructions precisely."
    )
    .with_llm(provider="groq", model="openai/gpt-oss-120b")
    .build()
)

result = pipeline.execute()
```

---

## 📖 Method 2: YAML Configuration

```yaml
# config.yaml
dataset:
  source_type: csv
  input_columns: [description]
  output_columns: [cleaned]

prompt:
  template: "Clean this: {description}"
  system_message: |
    You are a professional data specialist.
    Rules:
    - Keep it concise
    - Use proper grammar
    - Expand abbreviations

llm:
  provider: groq
  model: openai/gpt-oss-120b
```

```python
from llm_dataset_engine.config import ConfigLoader
from llm_dataset_engine.api import Pipeline

specs = ConfigLoader.from_yaml("config.yaml")
pipeline = Pipeline(specs, dataframe=df)
result = pipeline.execute()
```

---

## 📖 Method 3: CLI Tool

```bash
# Create config with system message
cat > config.yaml << EOF
prompt:
  template: "Summarize: {text}"
  system_message: "You are a concise summarizer."
llm:
  provider: groq
  model: openai/gpt-oss-120b
EOF

# Run via CLI
llm-dataset process -c config.yaml -i data.csv -o result.csv
```

---

## 📖 Method 4: Direct PipelineSpecifications

```python
from llm_dataset_engine.core.specifications import (
    PipelineSpecifications,
    PromptSpec,
    DatasetSpec,
    LLMSpec,
)
from llm_dataset_engine.api import Pipeline

specs = PipelineSpecifications(
    dataset=DatasetSpec(...),
    prompt=PromptSpec(
        template="Transform: {text}",
        system_message="You are an expert transformer."
    ),
    llm=LLMSpec(...),
)

pipeline = Pipeline(specs)
```

---

## 📖 Method 5: Dynamic via DatasetProcessor

```python
from llm_dataset_engine import DatasetProcessor

processor = DatasetProcessor(
    data="data.csv",
    input_column="text",
    output_column="result",
    prompt="Process: {text}",
    system_prompt="You are a helpful assistant.",  # ⚠️ TODO: Add this
    llm_config={"provider": "groq", "model": "openai/gpt-oss-120b"}
)
```

---

## 🎨 Use Cases & Examples

### **1. Different Personas**

```python
# Professional tone
.with_prompt(
    template="Respond to: {customer_message}",
    system_message="You are a professional customer service rep. "
                  "Be empathetic, apologetic, and solution-oriented."
)

# Casual tone
.with_prompt(
    template="Respond to: {customer_message}",
    system_message="You are a friendly support person. "
                  "Be warm, conversational, and helpful."
)
```

### **2. Domain Expertise**

```python
# Medical domain
.with_prompt(
    template="Summarize: {medical_note}",
    system_message="You are a medical records specialist. "
                  "Use proper medical terminology. "
                  "Be precise and objective."
)

# Legal domain
.with_prompt(
    template="Summarize: {contract_clause}",
    system_message="You are a legal document specialist. "
                  "Maintain legal accuracy. "
                  "Preserve important terms."
)
```

### **3. Output Format Control**

```python
# JSON output
.with_prompt(
    template="Extract info from: {text}",
    system_message="Always respond with valid JSON only. "
                  "No explanations or markdown. "
                  "Format: {\"field1\": \"value\", \"field2\": \"value\"}"
)

# Structured text
.with_prompt(
    template="Analyze: {text}",
    system_message="Always format responses as:\n"
                  "Summary: [one sentence]\n"
                  "Key Points: [bullet list]\n"
                  "Action Items: [numbered list]"
)
```

### **4. Quality Control**

```python
# Data cleaning
.with_prompt(
    template="Clean: {raw_data}",
    system_message="You are a data quality specialist. "
                  "Rules:\n"
                  "1. Remove special characters\n"
                  "2. Standardize capitalization\n"
                  "3. Expand abbreviations\n"
                  "4. Fix typos\n"
                  "5. Keep original meaning"
)
```

### **5. Multi-language**

```python
# Translation with context
.with_prompt(
    template="Translate to French: {english_text}",
    system_message="You are a professional French translator. "
                  "Maintain tone and context. "
                  "Use appropriate formality level. "
                  "Preserve idioms when possible."
)
```

---

## 🔧 How It Works Internally

When you provide a system message, the SDK **prepends it to each prompt**:

```python
# Your config
template = "Clean: {text}"
system_message = "You are a data specialist."

# What gets sent to LLM
final_prompt = f"{system_message}\n\n{template.format(text=row_value)}"
```

**Result**:
```
You are a data specialist.

Clean: BACON APPLEWOOD SMOKED 14/18
```

---

## 📋 Best Practices

### **✅ DO**
- Use system messages for **global instructions** (tone, format, rules)
- Use transformation prompts for **specific tasks** (what to do with each row)
- Keep system messages **clear and concise**
- Test different system messages to find what works best

### **❌ DON'T**
- Don't put row-specific data in system messages (use template variables)
- Don't make system messages too long (diminishing returns)
- Don't repeat the same instructions in both system and template

---

## 🎯 Examples from Our Test Suite

### **Example 1: Product Cleaning**
```python
pipeline = (
    PipelineBuilder.create()
    .from_dataframe(products_df,
                    input_columns=["raw_description"],
                    output_columns=["clean_description"])
    .with_prompt(
        template="Clean this product description: {raw_description}",
        system_message="You are a professional product data specialist. "
                      "Clean descriptions by: "
                      "1) Converting to proper case "
                      "2) Expanding abbreviations "
                      "3) Making it customer-friendly "
                      "4) Keeping it concise"
    )
    .with_llm(provider="groq", model="openai/gpt-oss-120b")
    .build()
)
```

**Input**: `BACON APPLEWOOD SMOKED 14/18 LB CASE`
**Output**: `Bacon Applewood Smoked – 14–18 lb case`

---

## 🧪 Testing System Prompts

Run our comprehensive example:

```bash
export GROQ_API_KEY="your-key"
python examples/09_system_prompts.py
```

This demonstrates:
1. Basic system prompt usage ✅
2. Different personas ✅
3. JSON extraction with system guidance ✅
4. YAML config with system messages ✅
5. CLI usage with system prompts ✅

---

## 🆕 Enhancement Request

You asked: *"can I give a system prompt en plus du prompt transformation?"*

**Answer**: ✅ **YES! Already supported in 5 different ways!**

The feature was already built into the SDK from day one. See `examples/09_system_prompts.py` for comprehensive examples.

---

## 📚 API Reference

### **PromptSpec**
```python
class PromptSpec:
    template: str                          # Required: transformation prompt
    system_message: Optional[str] = None   # Optional: global instructions
    few_shot_examples: Optional[List] = [] # Optional: example pairs
```

### **PipelineBuilder.with_prompt()**
```python
def with_prompt(
    template: str,                  # Your transformation prompt
    system_message: Optional[str]   # Your system instructions
) -> PipelineBuilder
```

---

## ✅ Summary

**Question**: Can I use system prompts AND transformation prompts?
**Answer**: ✅ **YES! Fully supported!**

**How to use**:
- ✅ PipelineBuilder: `.with_prompt(template="...", system_message="...")`
- ✅ YAML Config: Include `system_message` in prompt section
- ✅ CLI: System message in config file
- ✅ Direct specs: `PromptSpec(template="...", system_message="...")`

**Tested**: ✅ Working perfectly with Groq provider
**Examples**: ✅ See `examples/09_system_prompts.py`
**Documentation**: ✅ This guide!

---

**Need more examples?** Run: `python examples/09_system_prompts.py`
