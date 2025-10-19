"""
MLX Integration Example - Qwen3 on Apple Silicon

This example demonstrates using MLX (Apple's ML framework) for fast,
local LLM inference on M-series chips with the Qwen3 model.

Requirements:
- macOS with Apple Silicon (M1/M2/M3/M4)
- pip install hermes[mlx]
- HuggingFace account (for model downloads)

Benefits:
- 100% Free (no API costs)
- Privacy (data never leaves your machine)
- Fast inference on Apple Silicon
- No internet needed after model download

Setup:
1. Install MLX extra:
   pip install hermes[mlx]

2. Set HuggingFace token (for first-time model download):
   export HUGGING_FACE_HUB_TOKEN="your_token_here"

3. Run this example!
"""

import os

# Check if on Mac
import platform

import pandas as pd

from hermes import PipelineBuilder

if platform.system() != "Darwin":
    print("❌ This example requires macOS with Apple Silicon")
    print("   For Linux/Windows, use examples/05_groq_example.py instead")
    exit(1)

# Check for HuggingFace token
if not os.getenv("HUGGING_FACE_HUB_TOKEN"):
    print("⚠️  HuggingFace token not found!")
    print("   Set with: export HUGGING_FACE_HUB_TOKEN='your_token'")
    print("   Get token at: https://huggingface.co/settings/tokens")
    exit(1)

# Create sample data for testing
data = pd.DataFrame(
    {
        "product": [
            "Organic whole grain bread with seeds",
            "Wireless Bluetooth headphones with noise cancellation",
            "Fresh Atlantic salmon fillet",
            "Cotton t-shirt in navy blue",
            "Stainless steel water bottle 32oz",
        ]
    }
)

print("\n" + "=" * 60)
print("🍎 MLX + QWEN3 LOCAL INFERENCE EXAMPLE")
print("=" * 60)

# Build pipeline with MLX
pipeline = (
    PipelineBuilder.create()
    .from_dataframe(
        data,
        input_columns=["product"],
        output_columns=["category", "description"],
    )
    .with_prompt(
        """Analyze this product and provide:
1. Category (Food, Electronics, Clothing, Home, Sports)
2. Brief description (10 words max)

Product: {product}

Return JSON:
{
  "category": "...",
  "description": "..."
}"""
    )
    .with_llm(
        provider="mlx",
        model="mlx-community/Qwen3-1.7B-4bit",  # Fast, small model
        max_tokens=150,
        input_cost_per_1k_tokens=0.0,  # Free!
        output_cost_per_1k_tokens=0.0,
    )
    .with_batch_size(5)
    .with_concurrency(1)  # MLX works best with concurrency=1
    .build()
)

print("\n📊 Pipeline Configuration:")
print("   Provider: MLX (Apple Silicon)")
print("   Model: mlx-community/Qwen3-1.7B-4bit")
print(f"   Rows: {len(data)}")
print("   Cost: $0.00 (local model)")

# First run will download model (~1-2GB)
print("\n⏳ Processing (first run downloads model)...")
print("   This may take 1-2 minutes for initial download")
print("   Subsequent runs will be instant!\n")

result = pipeline.execute()

# Display results
print("\n" + "=" * 60)
print("✅ RESULTS")
print("=" * 60)

for idx, row in result.data.iterrows():
    print(f"\n{idx + 1}. Product: {row['product']}")
    print(f"   Category: {row['category']}")
    print(f"   Description: {row['description']}")

# Show performance metrics
print("\n" + "=" * 60)
print("📈 PERFORMANCE METRICS")
print("=" * 60)
print(f"Rows processed: {result.metrics.processed_rows}")
print(f"Total duration: {result.metrics.total_duration_seconds:.2f}s")
print(f"Throughput: {result.metrics.rows_per_second:.2f} rows/sec")
print(
    f"Avg time per row: {result.metrics.total_duration_seconds / result.metrics.total_rows:.2f}s"
)
print(f"\n💰 Cost: ${result.costs.total_cost} (FREE!)")
print(f"🎯 Total tokens: {result.costs.total_tokens:,}")

print("\n" + "=" * 60)
print("💡 TIPS")
print("=" * 60)
print("1. Model is cached - subsequent runs are instant!")
print("2. Try different Qwen3 models:")
print("   - mlx-community/Qwen3-1.7B-4bit (fast, small)")
print("   - mlx-community/Qwen3-7B-4bit (slower, better quality)")
print("3. Adjust max_tokens for longer/shorter responses")
print("4. Use concurrency=1 for MLX (optimal for M-series)")
print("=" * 60 + "\n")
