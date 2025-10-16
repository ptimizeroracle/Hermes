#!/usr/bin/env python
"""
Test bacon similarity with 3 independent columns.

Demonstrates: ONE input → THREE outputs with independent prompts
"""

import sys
sys.path.insert(0, "src")

from src.api import PipelineComposer

print("🧪 Testing Similarity Analysis with 3 Independent Columns")
print("="*80)
print("\nConfiguration: examples/similarity_independent_columns.yaml")
print("\nThis will generate:")
print("  1. llm_similarity   - Fast scoring (optimized short prompt)")
print("  2. Explanation      - Detailed reasoning (uses similarity score)")
print("  3. swap_risk_score  - Risk assessment (uses both previous columns)")
print("\nDependency chain: similarity → explanation → risk")
print("="*80)

# Load composition config
composer = PipelineComposer.from_yaml("examples/similarity_independent_columns.yaml")

print("\n🚀 Executing composition pipeline...")
print("   This will run 3 separate LLM stages with dependencies")

# Execute
result = composer.execute()

print("\n✅ Composition Complete!")
print(f"   • Total rows: {len(result.data)}")
print(f"   • Output columns: {list(result.data.columns)}")
print(f"   • Total cost: ${result.costs.total_cost:.4f}")
print(f"   • Errors: {len(result.errors)}")

# Show sample
print("\n📊 Sample Results (first 3 rows):")
print("="*80)
for idx in range(min(3, len(result.data))):
    row = result.data.iloc[idx]
    print(f"\nRow {idx + 1}:")
    print(f"  Incumbent: {row['incumbent'][:60]}...")
    print(f"  Portfolio: {row['portfolio'][:60]}...")
    print(f"  ├─ Similarity: {row.get('llm_similarity', 'N/A')}")
    print(f"  ├─ Explanation: {row.get('Explanation', 'N/A')[:80]}...")
    print(f"  └─ Risk: {row.get('swap_risk_score', 'N/A')}")

# Save
output_path = "tmp/similarity_3_columns_independent.xlsx"
result.data.to_excel(output_path, index=False)

print(f"\n💾 Results saved to: {output_path}")
print("\n" + "="*80)
print("✓ Test complete! Each column used its own optimized prompt.")
print("="*80)

