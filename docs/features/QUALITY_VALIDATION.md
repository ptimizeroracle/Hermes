# Automatic Quality Validation

## Overview

Hermes now includes **automatic quality validation** that checks output completeness after every pipeline run. This feature prevents silent failures where the pipeline reports success but outputs are null or empty.

## Problem Solved

Previously, when using `error_policy: skip`, failed LLM requests would:
- ✅ Be counted as "processed" 
- ❌ Produce `null` outputs silently
- ❌ Show 0 failures in metrics
- ❌ Report 100% success when actual success was much lower

**Example**: Pipeline reported "365 processed, 0 failed" but 335 outputs were `null` (92% failure rate).

## Solution

After every execution, Hermes now:
1. **Analyzes output columns** for null/empty values
2. **Calculates actual success rate** (valid outputs / total rows)
3. **Assigns quality score**: excellent, good, poor, or critical
4. **Raises warnings** if success rate < 70%
5. **Detects metrics mismatch** (reported failures vs actual nulls)
6. **Provides actionable recommendations**

## Usage

### CLI (Automatic)

```bash
hermes process --config config.yaml
```

After processing, you'll see:

```
📊 Validating output quality...
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Metric         ┃ Value     ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ Valid Outputs  │ 278/365   │
│ Success Rate   │ 76.2%     │
│ Null Outputs   │ 87        │
│ Empty Outputs  │ 0         │
│ Quality Score  │ GOOD      │
└────────────────┴───────────┘

✅ Output quality is acceptable (76.2% success)
```

If quality is poor:

```
🚨 Issues Detected:
  • ⚠️  LOW SUCCESS RATE: Only 8.2% of outputs are valid (30/365 rows)
  • ⚠️  HIGH NULL RATE: 335 null values found (91.8% of rows)
  • ⚠️  METRICS MISMATCH: Pipeline reported 0 failures but 335 rows have null outputs

Consider:
  • Review your prompt complexity (simpler prompts often work better)
  • Check LLM provider logs for errors
  • Increase max_tokens if outputs are truncated
  • Verify API key and rate limits

❌ Output quality is below acceptable threshold (8.2% < 70%)
```

### SDK (Manual)

```python
from hermes import PipelineBuilder

pipeline = PipelineBuilder.create()...
result = pipeline.execute()

# Validate quality
quality = result.validate_output_quality(['cleaned_description'])

print(f"Success rate: {quality.success_rate:.1f}%")
print(f"Quality score: {quality.quality_score}")
print(f"Acceptable: {quality.is_acceptable}")  # True if >= 70%

if quality.issues:
    for issue in quality.issues:
        print(f"  • {issue}")
```

## Quality Scores

| Score      | Success Rate | Description                    |
|------------|--------------|--------------------------------|
| EXCELLENT  | ≥ 95%        | Outstanding quality            |
| GOOD       | ≥ 80%        | Acceptable for production      |
| POOR       | ≥ 50%        | Needs improvement              |
| CRITICAL   | < 50%        | Unacceptable - investigation required |

## Thresholds

- **Acceptable**: ≥ 70% success rate
- **High null warning**: > 30% null values
- **Empty string warning**: > 10% empty outputs

## What It Checks

1. **Null values** (`None`, `NaN`, `NaT`) in output columns
2. **Empty strings** (only for string columns)
3. **Metrics consistency** (reported failures vs actual nulls)
4. **Success rate** across all output columns

## Recommendations

When quality is poor, Hermes suggests:

1. **Simplify prompts** - Complex prompts with metadata/examples often fail more
2. **Check LLM logs** - Look for authentication errors, rate limits
3. **Increase `max_tokens`** - Prevent truncated outputs
4. **Verify API key** - Ensure valid credentials

## API Reference

### `QualityReport`

```python
@dataclass
class QualityReport:
    total_rows: int
    valid_outputs: int
    null_outputs: int
    empty_outputs: int
    success_rate: float  # Percentage (0-100)
    quality_score: str   # "excellent", "good", "poor", "critical"
    warnings: List[str]
    issues: List[str]
    
    @property
    def is_acceptable(self) -> bool:
        """Returns True if success_rate >= 70%"""
```

### `ExecutionResult.validate_output_quality()`

```python
def validate_output_quality(
    self, 
    output_columns: List[str]
) -> QualityReport:
    """
    Validate the quality of output data.
    
    Args:
        output_columns: List of output column names to check
        
    Returns:
        QualityReport with metrics, warnings, and issues
    """
```

## Example: Detecting Silent Failures

**Before (without validation)**:
```
✅ Processing complete!
Total Rows: 365
Processed: 365
Failed: 0

→ User opens file: 335/365 rows are null! 😱
```

**After (with validation)**:
```
✅ Processing complete!
Total Rows: 365
Processed: 365
Failed: 0

📊 Quality Report:
Valid Outputs: 30/365
Success Rate: 8.2%
Quality Score: CRITICAL

🚨 Issues Detected:
  • ⚠️  METRICS MISMATCH: Pipeline reported 0 failures but 335 rows have null outputs
  
→ User immediately knows there's a problem! 🎯
```

## Integration

Quality validation is:
- ✅ **Automatic** in CLI
- ✅ **Available** in SDK via `result.validate_output_quality()`
- ✅ **Non-blocking** (warnings only, doesn't fail pipeline)
- ✅ **Fast** (uses pandas vectorized operations)
- ✅ **Configurable** (thresholds can be adjusted)

## Future Enhancements

Potential additions:
- Custom quality thresholds in config
- Quality-based auto-retry for failed rows
- Export quality reports to JSON/CSV
- Historical quality tracking
- Per-column quality metrics

