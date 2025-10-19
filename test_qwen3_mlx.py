"""
Test Qwen3-1.7B with MLX on Apple Silicon.

This script tests the Qwen3 model using MLX as an inference engine,
then integrates it with Hermes for batch processing.
"""

import time

from mlx_lm import generate, load

print("=" * 60)
print("🧪 TESTING QWEN3-1.7B-FP8 WITH MLX")
print("=" * 60)

# Step 1: Load the model
print("\n📥 Loading Qwen3-1.7B-FP8 model...")
print("   (First run will download from HuggingFace)")
print("   Model: Qwen/Qwen3-1.7B-FP8")
start_time = time.time()

try:
    # Try MLX-optimized version first
    model, tokenizer = load("mlx-community/Qwen3-1.7B-4bit")
    load_time = time.time() - start_time
    print(f"✅ Model loaded in {load_time:.2f} seconds")
    print("   (Using MLX-optimized 4-bit quantized version)")
except Exception as e:
    print(f"❌ Error with mlx-community version: {e}")
    print("\n💡 Trying standard Qwen3-1.7B...")
    try:
        model, tokenizer = load("mlx-community/Qwen3-1.7B")
        load_time = time.time() - start_time
        print(f"✅ Model loaded in {load_time:.2f} seconds")
    except Exception as e2:
        print(f"❌ Error: {e2}")
        exit(1)

# Step 2: Test single inference
print("\n🔬 Testing single inference...")
test_prompt = "What is the capital of France? Answer in one sentence."

start_time = time.time()
response = generate(
    model,
    tokenizer,
    prompt=test_prompt,
    max_tokens=100,
)
inference_time = time.time() - start_time

print(f"\n📝 Prompt: {test_prompt}")
print(f"💬 Response: {response}")
print(f"⏱️  Inference time: {inference_time:.3f} seconds")

# Step 3: Benchmark multiple prompts
print("\n📊 Benchmarking with multiple prompts...")
test_prompts = [
    "What is Python? Answer in one sentence.",
    "Explain machine learning in simple terms.",
    "What is the speed of light?",
    "Who wrote Romeo and Juliet?",
    "What is 2 + 2?",
]

total_start = time.time()
for i, prompt in enumerate(test_prompts, 1):
    start = time.time()
    response = generate(model, tokenizer, prompt=prompt, max_tokens=50)
    duration = time.time() - start
    print(f"{i}. [{duration:.2f}s] {prompt[:40]}...")

total_time = time.time() - total_start
avg_time = total_time / len(test_prompts)

print("\n📈 Benchmark Results:")
print(f"   Total prompts: {len(test_prompts)}")
print(f"   Total time: {total_time:.2f}s")
print(f"   Average time per prompt: {avg_time:.2f}s")
print(f"   Throughput: {len(test_prompts)/total_time:.2f} prompts/sec")

# Step 4: Performance summary
print("\n" + "=" * 60)
print("🎯 QWEN3-1.7B-FP8 PERFORMANCE SUMMARY")
print("=" * 60)
print("Model: Qwen3-1.7B-FP8")
print("Engine: MLX (Apple Silicon optimized)")
print(f"Load time: {load_time:.2f}s")
print(f"Avg inference: {avg_time:.2f}s/prompt")
print(f"Throughput: {len(test_prompts)/total_time:.2f} prompts/sec")
print("\n💡 Next: Integrate with Hermes for batch processing!")
print("=" * 60)
