"""
System Prompts Example - Using system messages with transformation prompts.

This example demonstrates how to use system messages to guide LLM behavior
while keeping the transformation prompt separate.
"""

import pandas as pd
from hermes import PipelineBuilder

# Sample product data
data = pd.DataFrame({
    "raw_description": [
        "BACON APPLEWOOD SMOKED 14/18 LB CASE",
        "LETTUCE ROMAINE HEARTS 12CT ORGANIC",
        "CHICKEN BREAST BONELESS SKINLESS 40LB",
        "TOMATOES CHERRY ON VINE 12/1PT",
    ],
})


def example_1_basic_system_prompt():
    """Example 1: Basic system prompt usage."""
    print("=" * 70)
    print("EXAMPLE 1: Basic System Prompt")
    print("=" * 70)
    
    pipeline = (
        PipelineBuilder.create()
        .from_dataframe(
            data,
            input_columns=["raw_description"],
            output_columns=["clean_description"],
        )
        .with_prompt(
            template="Clean this product description: {raw_description}",
            system_message="You are a professional product data specialist. "
                         "Clean product descriptions by: "
                         "1) Converting to proper case "
                         "2) Expanding abbreviations "
                         "3) Making it customer-friendly "
                         "4) Keeping it concise",
        )
        .with_llm(
            provider="groq",
            model="openai/gpt-oss-120b",
            temperature=0.0,
        )
        .build()
    )
    
    print("\nSystem Message:")
    print(pipeline.specifications.prompt.system_message)
    print("\nTransformation Prompt:")
    print(pipeline.specifications.prompt.template)
    
    # Estimate cost first
    estimate = pipeline.estimate_cost()
    print(f"\nEstimated cost: ${estimate.total_cost}")
    print(f"Rows to process: {estimate.rows}")
    
    # Execute
    result = pipeline.execute()
    
    print("\n✅ Results:")
    for i, row in result.data.iterrows():
        print(f"\nOriginal: {row['raw_description']}")
        print(f"Cleaned:  {row['clean_description']}")


def example_2_different_personas():
    """Example 2: Different system prompts for different personas."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Different Personas via System Prompts")
    print("=" * 70)
    
    review = "The product arrived late and the packaging was damaged."
    
    # Professional response
    pipeline_professional = (
        PipelineBuilder.create()
        .from_dataframe(
            pd.DataFrame({"review": [review]}),
            input_columns=["review"],
            output_columns=["response"],
        )
        .with_prompt(
            template="Write a response to this customer review: {review}",
            system_message="You are a professional customer service representative. "
                         "Be empathetic, apologetic, and offer solutions. "
                         "Keep responses concise and actionable.",
        )
        .with_llm(provider="groq", model="openai/gpt-oss-120b", temperature=0.3)
        .build()
    )
    
    # Casual response
    pipeline_casual = (
        PipelineBuilder.create()
        .from_dataframe(
            pd.DataFrame({"review": [review]}),
            input_columns=["review"],
            output_columns=["response"],
        )
        .with_prompt(
            template="Write a response to this customer review: {review}",
            system_message="You are a friendly, casual customer support rep. "
                         "Be warm, understanding, and conversational. "
                         "Use a casual tone but remain helpful.",
        )
        .with_llm(provider="groq", model="openai/gpt-oss-120b", temperature=0.3)
        .build()
    )
    
    print("\nReview:", review)
    print("\n--- PROFESSIONAL PERSONA ---")
    result_pro = pipeline_professional.execute()
    print(result_pro.data.iloc[0]["response"])
    
    print("\n--- CASUAL PERSONA ---")
    result_casual = pipeline_casual.execute()
    print(result_casual.data.iloc[0]["response"])


def example_3_json_extraction_with_system():
    """Example 3: System prompt for structured output."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Structured Output with System Prompt")
    print("=" * 70)
    
    from hermes.stages import JSONParser
    
    products = pd.DataFrame({
        "text": [
            "Organic Fuji Apples, 3lb bag, $5.99",
            "Wild Caught Salmon Fillets, 2lbs, $24.99",
        ]
    })
    
    pipeline = (
        PipelineBuilder.create()
        .from_dataframe(
            products,
            input_columns=["text"],
            output_columns=["product", "quantity", "price"],
        )
        .with_prompt(
            template="Extract product info from: {text}",
            system_message="You are a data extraction specialist. "
                         "Always respond with valid JSON only, no explanations. "
                         "Format: {\"product\": \"name\", \"quantity\": \"amount\", \"price\": \"$X.XX\"}",
        )
        .with_llm(provider="groq", model="openai/gpt-oss-120b", temperature=0.0)
        .with_parser(JSONParser(strict=False))
        .build()
    )
    
    result = pipeline.execute()
    
    print("\n✅ Extracted Data:")
    print(result.data.to_string(index=False))


def example_4_yaml_config_with_system():
    """Example 4: System prompt in YAML configuration."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: System Prompt in YAML Config")
    print("=" * 70)
    
    # Create YAML config with system message
    yaml_config = """
dataset:
  source_type: dataframe
  input_columns: [description]
  output_columns: [category]

prompt:
  template: "Categorize this product: {description}"
  system_message: |
    You are a product categorization expert.
    Categories: Produce, Meat, Dairy, Bakery, Pantry
    Rules:
    - Choose only one category
    - Be consistent
    - Consider the main product type

llm:
  provider: groq
  model: openai/gpt-oss-120b
  temperature: 0.0

processing:
  batch_size: 10
  concurrency: 2
"""
    
    import tempfile
    from hermes.config import ConfigLoader
    
    # Write config to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_config)
        config_path = f.name
    
    # Load from config
    specs = ConfigLoader.from_yaml(config_path)
    
    print("\nLoaded system message from YAML:")
    print(specs.prompt.system_message)
    
    # Use it
    df = pd.DataFrame({
        "description": ["Fresh Bananas", "Ground Beef 80/20", "Sourdough Bread"]
    })
    
    from hermes.api import Pipeline
    pipeline = Pipeline(specs, dataframe=df)
    result = pipeline.execute()
    
    print("\n✅ Categorization Results:")
    for i, row in result.data.iterrows():
        print(f"{row['description']}: {row['category']}")


def example_5_cli_with_system_prompt():
    """Example 5: Using system prompts via CLI."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: System Prompt via CLI")
    print("=" * 70)
    
    print("\nYou can use system prompts in the CLI by including them in your config:")
    print("""
# config.yaml
dataset:
  source_type: csv
  input_columns: [text]
  output_columns: [result]

prompt:
  template: "Process: {text}"
  system_message: "You are a helpful assistant."

llm:
  provider: groq
  model: openai/gpt-oss-120b
""")
    
    print("\nThen run:")
    print("$ llm-dataset process -c config.yaml -i data.csv -o result.csv")
    print("\n✅ The system message will be automatically included!")


# Main execution
if __name__ == "__main__":
    import os
    
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️  Set GROQ_API_KEY environment variable to run examples")
        print("Example: export GROQ_API_KEY='your-key-here'")
        exit(1)
    
    print("🚀 System Prompts Examples - LLM Dataset Engine\n")
    
    # Run examples
    try:
        example_1_basic_system_prompt()
        example_2_different_personas()
        example_3_json_extraction_with_system()
        example_4_yaml_config_with_system()
        example_5_cli_with_system_prompt()
        
        print("\n" + "=" * 70)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

