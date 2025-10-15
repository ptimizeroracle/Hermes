#!/usr/bin/env python
"""
Bacon Product Description Cleaning Script

This script demonstrates the complete workflow for cleaning bacon product descriptions
using the LLM Dataset Engine with detailed logging and verification.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd
from src import PipelineBuilder
from src.config import ConfigLoader


def verify_environment():
    """Step 1: Verify environment and API key."""
    print("=" * 80)
    print("STEP 1: Environment Verification")
    print("=" * 80)
    
    # Check API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ ERROR: GROQ_API_KEY not set!")
        print("\nPlease set your API key:")
        print("export GROQ_API_KEY='your-key-here'")
        return False
    
    print(f"✅ GROQ_API_KEY found: {api_key[:20]}...")
    
    # Check input file
    input_file = Path("tmp/ground_truth.xlsx")
    if not input_file.exists():
        print(f"❌ ERROR: Input file not found: {input_file}")
        return False
    
    print(f"✅ Input file exists: {input_file}")
    print(f"   File size: {input_file.stat().st_size:,} bytes")
    
    # Check config
    config_file = Path("bacon_cleaning_config.yaml")
    if not config_file.exists():
        print(f"❌ ERROR: Config file not found: {config_file}")
        return False
    
    print(f"✅ Config file exists: {config_file}")
    
    return True


def load_and_inspect_data():
    """Step 2: Load and inspect input data."""
    print("\n" + "=" * 80)
    print("STEP 2: Load and Inspect Data")
    print("=" * 80)
    
    df = pd.read_excel("tmp/ground_truth.xlsx")
    
    print(f"\n📊 Dataset Info:")
    print(f"   Rows: {len(df)}")
    print(f"   Columns: {list(df.columns)}")
    
    print(f"\n📝 Sample Data (first 5 rows):")
    for i, row in df.head(5).iterrows():
        print(f"\n   Row {i}:")
        print(f"   PK: {row['pk']}")
        print(f"   Description: {row['Item_Description_Long'][:100]}...")
    
    # Check for null values
    null_counts = df.isnull().sum()
    if null_counts.any():
        print(f"\n⚠️  Null values found:")
        print(null_counts[null_counts > 0])
    else:
        print(f"\n✅ No null values")
    
    return df


def load_configuration():
    """Step 3: Load and validate configuration."""
    print("\n" + "=" * 80)
    print("STEP 3: Load Configuration")
    print("=" * 80)
    
    specs = ConfigLoader.from_yaml("bacon_cleaning_config.yaml")
    
    print(f"\n⚙️  Configuration:")
    print(f"   Provider: {specs.llm.provider}")
    print(f"   Model: {specs.llm.model}")
    print(f"   Temperature: {specs.llm.temperature}")
    print(f"   Max tokens: {specs.llm.max_tokens}")
    print(f"   Batch size: {specs.processing.batch_size}")
    print(f"   Concurrency: {specs.processing.concurrency}")
    print(f"   Max budget: ${specs.processing.max_budget}")
    print(f"   Error policy: {specs.processing.error_policy}")
    
    print(f"\n📝 System Message (first 200 chars):")
    print(f"   {specs.prompt.system_message[:200]}...")
    
    print(f"\n📝 Prompt Template (first 150 chars):")
    print(f"   {specs.prompt.template[:150]}...")
    
    return specs


def build_pipeline(specs, df):
    """Step 4: Build pipeline."""
    print("\n" + "=" * 80)
    print("STEP 4: Build Pipeline")
    print("=" * 80)
    
    from src.api import Pipeline
    
    pipeline = Pipeline(specs, dataframe=df)
    
    print(f"\n✅ Pipeline created:")
    print(f"   Pipeline ID: {pipeline.id}")
    print(f"   Input columns: {specs.dataset.input_columns}")
    print(f"   Output columns: {specs.dataset.output_columns}")
    
    return pipeline


def estimate_cost(pipeline):
    """Step 5: Estimate cost before running."""
    print("\n" + "=" * 80)
    print("STEP 5: Cost Estimation")
    print("=" * 80)
    
    estimate = pipeline.estimate_cost()
    
    print(f"\n💰 Cost Estimate:")
    print(f"   Total rows: {estimate.rows}")
    print(f"   Estimated tokens: {estimate.total_tokens:,}")
    print(f"   Input tokens: {estimate.input_tokens:,}")
    print(f"   Output tokens: {estimate.output_tokens:,}")
    print(f"   Estimated cost: ${estimate.total_cost}")
    print(f"   Confidence: {estimate.confidence}")
    
    return estimate


def run_pipeline(pipeline):
    """Step 6: Execute pipeline."""
    print("\n" + "=" * 80)
    print("STEP 6: Execute Pipeline")
    print("=" * 80)
    print("\n🚀 Starting execution...")
    print("   (This may take a few minutes for 365 rows)")
    print()
    
    result = pipeline.execute()
    
    return result


def verify_results(result):
    """Step 7: Verify and inspect results."""
    print("\n" + "=" * 80)
    print("STEP 7: Verify Results")
    print("=" * 80)
    
    print(f"\n✅ Execution completed!")
    print(f"   Success: {result.success}")
    print(f"   Duration: {result.duration:.2f}s")
    print(f"   Total rows: {result.metrics.total_rows}")
    print(f"   Processed: {result.metrics.processed_rows}")
    print(f"   Failed: {result.metrics.failed_rows}")
    print(f"   Skipped: {result.metrics.skipped_rows}")
    print(f"   Total cost: ${result.costs.total_cost}")
    print(f"   Throughput: {result.metrics.throughput:.2f} rows/sec")
    
    # Show sample results
    print(f"\n📝 Sample Results (first 5):")
    for i in range(min(5, len(result.data))):
        row = result.data.iloc[i]
        print(f"\n   Row {i}:")
        if 'Item_Description_Long' in row:
            print(f"   Input:  {row['Item_Description_Long'][:80]}...")
        if 'cleaned_description' in row:
            print(f"   Output: {row['cleaned_description'][:80]}...")
    
    # Check output file
    output_file = Path("tmp/ground_truth_cleaned.xlsx")
    if output_file.exists():
        print(f"\n✅ Output file created: {output_file}")
        print(f"   File size: {output_file.stat().st_size:,} bytes")
    else:
        print(f"\n⚠️  Output file not found: {output_file}")
    
    return result


def main():
    """Main execution flow."""
    print("\n" + "🎯" * 40)
    print(" " * 15 + "BACON PRODUCT DESCRIPTION CLEANING")
    print(" " * 20 + "LLM Dataset Engine v1.0.0")
    print("🎯" * 40 + "\n")
    
    try:
        # Step 1: Verify environment
        if not verify_environment():
            return 1
        
        # Step 2: Load data
        df = load_and_inspect_data()
        
        # Step 3: Load configuration
        specs = load_configuration()
        
        # Step 4: Build pipeline
        pipeline = build_pipeline(specs, df)
        
        # Step 5: Estimate cost
        estimate = estimate_cost(pipeline)
        
        # Confirm before running
        print("\n" + "=" * 80)
        print("READY TO EXECUTE")
        print("=" * 80)
        print(f"\n⚠️  About to process {estimate.rows} rows")
        print(f"   Estimated cost: ${estimate.total_cost}")
        print(f"   Max budget: ${specs.processing.max_budget}")
        
        response = input("\n   Continue? [y/N]: ")
        if response.lower() != 'y':
            print("\n❌ Execution cancelled by user")
            return 0
        
        # Step 6: Run pipeline
        result = run_pipeline(pipeline)
        
        # Step 7: Verify results
        verify_results(result)
        
        print("\n" + "=" * 80)
        print("✅ ALL STEPS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"\n📄 Results saved to: tmp/ground_truth_cleaned.xlsx")
        print(f"📊 {result.metrics.processed_rows} rows processed in {result.duration:.2f}s")
        print(f"💰 Total cost: ${result.costs.total_cost}")
        print()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n❌ Execution interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

