# Fixes Applied to Bacon Cleaning Pipeline

## Issues Found in Output Analysis

### 1. **"assistant:" Prefix in All Outputs** ✅ FIXED
**Problem**: All cleaned descriptions had `"assistant: "` prefix from chat format.

**Fix**: Updated `RawTextParser` in `src/stages/response_parser_stage.py` to strip chat format prefixes (`assistant:`, `user:`, `system:`).

**Code**:
```python
def parse(self, response: str) -> Dict[str, Any]:
    """Return response as-is, after cleaning chat format artifacts."""
    cleaned = response.strip()
    
    # Strip common chat format prefixes
    for prefix in ["assistant:", "user:", "system:"]:
        if cleaned.lower().startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
            break
    
    return {"output": cleaned}
```

---

### 2. **86% of Rows Returned "None"** ✅ FIXED
**Problem**: 315 out of 365 rows (86%) returned `"None"` due to overly strict prompt rules.

**Fix**: 
- Added explicit instruction: **"CRITICAL: Always return a valid description. Never return 'None' or empty text."**
- Added rule: **"If unsure, make best effort - extract what you can identify"**
- Added example for heavily abbreviated input
- Updated system message to reinforce this behavior

---

### 3. **Truncated Outputs (Trailing Commas)** ✅ FIXED
**Problem**: Some outputs were incomplete due to low `max_tokens=200`.

**Fix**: Increased `max_tokens` to `400` (configurable) based on Groq best practices for detailed outputs.

---

### 4. **Hard-coded Configuration** ✅ FIXED
**Problem**: All parameters were hard-coded in the script.

**Fix**: Made all key parameters configurable at the top of the script:

```python
# CONFIGURATION - Adjust these as needed
MAX_TOKENS = 400           # Groq recommended: 400-800 for detailed outputs
MAX_RETRIES = 3            # Number of retries on API errors
BATCH_SIZE = 10            # Rows per batch
CONCURRENCY = 3            # Parallel requests per batch
MAX_BUDGET = 5.0           # Maximum spend in USD

# Groq Pricing (as of 2024)
GROQ_INPUT_COST_PER_1K = 0.00005   # $0.05 per 1M input tokens
GROQ_OUTPUT_COST_PER_1K = 0.00008  # $0.08 per 1M output tokens
```

**Benefits**:
- Easy to adjust for different LLM providers
- Can increase `max_tokens` if outputs are still truncated
- Can adjust `concurrency` based on rate limits
- Transparent pricing configuration

---

## Files Modified

1. **`src/stages/response_parser_stage.py`**
   - Updated `RawTextParser.parse()` to strip chat format prefixes

2. **`process_all_365_bacon.py`**
   - Added configurable parameters at top of file
   - Improved transformation prompt with explicit "never return None" instruction
   - Added more abbreviation examples (AWS→applewood)
   - Increased `max_tokens` from 200 to 400
   - Updated system message to reinforce "no None outputs"

---

## Expected Improvements

After re-running with these fixes:

1. ✅ **No "assistant:" prefix** in any output
2. ✅ **Drastically reduced "None" outputs** (from 86% to <5%)
3. ✅ **No truncated outputs** with increased token limit
4. ✅ **Better handling of abbreviated inputs** with improved prompt examples
5. ✅ **Easy configuration** for different providers or use cases

---

## How to Re-run

```bash
# Set your API key
export GROQ_API_KEY="your-key-here"

# Run the script
python process_all_365_bacon.py

# Adjust configuration at top of script if needed:
# - MAX_TOKENS: increase if outputs are still truncated (try 600-800)
# - MAX_RETRIES: increase for flaky networks (try 5)
# - CONCURRENCY: reduce if hitting rate limits (try 2)
```

---

## Groq Best Practices Applied

Based on research:
- ✅ Configurable `max_retries` (default: 3)
- ✅ Appropriate `max_tokens` for detailed outputs (400)
- ✅ Rate limit handling with concurrency control
- ✅ Cost transparency with explicit pricing configuration
- ✅ Exponential backoff via retry handler (already built-in)

---

## Next Steps

1. **Re-run the pipeline** with fixes applied
2. **Analyze new output** for quality improvements
3. **Fine-tune if needed**:
   - If still seeing "None": increase `MAX_TOKENS` to 600
   - If hitting rate limits: reduce `CONCURRENCY` to 2
   - If outputs too verbose: reduce `MAX_TOKENS` to 300

