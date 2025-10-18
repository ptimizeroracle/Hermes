# Parallelization Guide for Your Laptop + Groq

## Your Current Config
```python
BATCH_SIZE = 10            # Rows per batch
CONCURRENCY = 3            # Parallel requests per batch
```

**Current throughput**: 3 requests running in parallel at any time

---

## Groq Free Tier Limits (Estimated)
- **~30 requests per minute (RPM)**
- **~14,000 tokens per minute (TPM)**
- Model: `openai/gpt-oss-120b`

---

## Safe Configurations

### **Conservative (Current - RECOMMENDED for Free Tier)**
```python
BATCH_SIZE = 10
CONCURRENCY = 3
```
- **Throughput**: ~30-40 requests/min
- **Risk**: ✅ Very low (well under limits)
- **Use when**: You're on free tier or want stable execution

### **Moderate (Better for Paid Tier)**
```python
BATCH_SIZE = 15
CONCURRENCY = 5
```
- **Throughput**: ~60-80 requests/min
- **Risk**: ⚠️ May hit rate limits on free tier
- **Use when**: You have paid tier or good network

### **Aggressive (Paid Tier Only)**
```python
BATCH_SIZE = 20
CONCURRENCY = 10
```
- **Throughput**: ~120-150 requests/min
- **Risk**: ❌ Will hit rate limits on free tier
- **Use when**: You have high RPM quota

---

## Your Laptop Capacity

**M1/M2/M3 MacBook** (Estimated):
- **CPU cores**: 8-10 cores
- **Max safe concurrency**: 10-15 threads
- **Network**: 100-500 Mbps (sufficient for API calls)
- **Bottleneck**: Groq API rate limits, not your laptop

**Intel MacBook**:
- **CPU cores**: 4-8 cores
- **Max safe concurrency**: 6-10 threads
- **Bottleneck**: Groq API rate limits, not your laptop

**Your laptop can easily handle 10+ parallel requests.** The bottleneck is Groq's API rate limits.

---

## How to Test Your Limits

### 1. **Start Conservative** (Current)
```python
CONCURRENCY = 3
```
Run and watch for errors.

### 2. **Gradually Increase**
If no rate limit errors (429), try:
```python
CONCURRENCY = 5
```

### 3. **Watch for These Errors**
```
HTTP 429: Too Many Requests
Error: Rate limit exceeded
```

If you see these, **reduce `CONCURRENCY` by 2**.

---

## Cost Comparison

### Current Config (CONCURRENCY=3)
- **365 rows** → ~3-4 minutes
- **Cost**: ~$0.013

### Aggressive Config (CONCURRENCY=10)
- **365 rows** → ~1-2 minutes
- **Cost**: Same (~$0.013)
- **Risk**: May hit rate limits on free tier

---

## Recommendations

### **If on Free Tier** (RECOMMENDED)
```python
MAX_TOKENS = 400
MAX_RETRIES = 3
BATCH_SIZE = 10
CONCURRENCY = 3          # Stay at 3 - safe for free tier
MAX_BUDGET = 5.0
```

### **If on Paid Tier**
```python
MAX_TOKENS = 400
MAX_RETRIES = 3
BATCH_SIZE = 15
CONCURRENCY = 7          # Increase to 7 for 2x speed
MAX_BUDGET = 5.0
```

### **If You Have High-RPM Quota**
```python
MAX_TOKENS = 400
MAX_RETRIES = 3
BATCH_SIZE = 20
CONCURRENCY = 10         # Max out at 10 for 3x speed
MAX_BUDGET = 10.0
```

---

## Rate Limit Handling (Already Built-in ✅)

Your pipeline already handles rate limits gracefully:
1. **Retries with exponential backoff** (`max_retries=3`)
2. **Error policy**: `skip` (continues on errors)
3. **Rate limiter**: Automatically pauses on 429 errors

So you can safely experiment with higher concurrency - worst case, it'll just slow down.

---

## TL;DR

**Your laptop**: Can handle 10+ parallel requests easily ✅
**Groq free tier**: Limited to ~30 RPM ⚠️
**Current config (3 concurrent)**: Perfect for free tier ✅
**To go faster**: Upgrade to paid tier, then increase to 7-10 concurrent

**Bottom line: Your laptop isn't the bottleneck - Groq's API limits are.**
