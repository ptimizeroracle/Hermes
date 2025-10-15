import sys
import os
sys.path.insert(0, "src")

import pandas as pd
from src import PipelineBuilder

os.environ["GROQ_API_KEY"] = "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"

# Just 1 row for debugging
df = pd.read_excel("tmp/ground_truth.xlsx").head(1)

print("Testing with 1 row to debug output parsing\n")
print(f"Input: {df.iloc[0]['Item_Description_Long']}\n")

# Simplified prompt to see raw output
pipeline = (
    PipelineBuilder.create()
    .from_dataframe(df, input_columns=["Item_Description_Long"], output_columns=["output"])
    .with_prompt(
        template="Clean this bacon description: {Item_Description_Long}\n\nCleaned description:",
        system_message="You are a product editor. Output only the cleaned description, nothing else."
    )
    .with_llm(provider="groq", model="openai/gpt-oss-120b", temperature=0.0, max_tokens=100)
    .build()
)

result = pipeline.execute()

print("Result DataFrame columns:", list(result.data.columns))
print("\nResult data:")
print(result.data.to_string())

# Check what we got
if 'output' in result.data.columns:
    output_val = result.data.iloc[0]['output']
    print(f"\nExtracted output value: {output_val}")
    print(f"Type: {type(output_val)}")
else:
    print("\n❌ 'output' column not found!")

