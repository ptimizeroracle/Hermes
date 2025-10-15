"""
Quickstart Example - Basic pipeline usage.

This example demonstrates the simplest way to process a dataset
using the LLM Dataset Engine.
"""

import pandas as pd
from llm_dataset_engine import PipelineBuilder

# Create sample data
data = pd.DataFrame({
    "product_name": [
        "Apple iPhone 13 Pro Max 256GB",
        "Samsung Galaxy S22 Ultra 512GB",
        "MacBook Pro 16\" M2 32GB RAM",
    ],
    "description": [
        "Latest iPhone with advanced camera system",
        "Premium Android flagship with S Pen",
        "Powerful laptop for professionals",
    ],
})

# Build pipeline with fluent API
pipeline = (
    PipelineBuilder.create()
    .from_dataframe(
        data,
        input_columns=["product_name", "description"],
        output_columns=["category"],
    )
    .with_prompt(
        """Categorize this product into ONE of these categories:
        - Electronics > Smartphones
        - Electronics > Laptops
        - Electronics > Accessories
        
        Product: {product_name}
        Description: {description}
        
        Category:"""
    )
    .with_llm(
        provider="openai",
        model="gpt-4o-mini",
        temperature=0.0,
    )
    .with_batch_size(10)
    .with_concurrency(3)
    .build()
)

# Estimate cost before running
print("Estimating cost...")
estimate = pipeline.estimate_cost()
print(f"Estimated cost: ${estimate.total_cost:.4f}")
print(f"Estimated tokens: {estimate.total_tokens}")

# Execute pipeline
print("\nProcessing data...")
result = pipeline.execute()

# Display results
print("\nResults:")
print(result.data[["product_name", "category"]])

# Show metrics
print(f"\nMetrics:")
print(f"  Processed rows: {result.metrics.processed_rows}")
print(f"  Duration: {result.metrics.total_duration_seconds:.2f}s")
print(f"  Total cost: ${result.costs.total_cost:.4f}")
print(f"  Cost per row: ${float(result.costs.total_cost) / result.metrics.total_rows:.6f}")

