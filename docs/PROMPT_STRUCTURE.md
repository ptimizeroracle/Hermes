# 📝 Prompt Structure - What Gets Sent to the LLM

This document shows **exactly** what the LLM receives for each bacon description.

---

## 🎯 **The Complete Prompt Structure**

For each row in your Excel file, the LLM receives:

```
[SYSTEM MESSAGE - Sets Overall Behavior]
You are a careful product copy editor. Clean fragmented product text...
[... full system message ...]

[TRANSFORMATION PROMPT - Detailed Processing Logic]
Rewrite the input into a single, concise, professional product description...
✅ Include **only** the following attributes, in this exact order...
[... all 85 lines of rules, examples, and guidelines ...]

Input: {Item_Description_Long}
```

---

## 📋 **Example: What the LLM Actually Sees**

### **For Row 1:**

```
SYSTEM MESSAGE:
You are a careful product copy editor. Clean fragmented product text into a clear, fluent description and identify key facts only if explicitly present. Prioritize consistency, brevity, and factual fidelity. Do not invent details or infer missing data.

Guidelines:
• Objective: Produce one concise, neutral sentence (two if essential)...
• Scope: Rephrase existing facts; remove marketing fluff...
[... etc ...]

TRANSFORMATION PROMPT:
Rewrite the input into a single, concise, professional product description in fluent English—strictly factual, neutral in tone, and optimized for foodservice procurement and semantic consistency.

✅ Include **only** the following attributes, in this exact order, **as a single sentence**:
1. **Preparation**:
   - "raw", "fully cooked", or "frozen"
   - If frozen and cooked: "frozen, fully cooked"
2. **Special features** (only if explicitly stated; expand to include honey-cured, sugar-cured, pepper-crusted, organic, gluten-free, nitrate-free, halal, or uncured):
   - List comma-separated if multiple
3. **Smoke/flavor** (only if stated):
   - applewood-smoked, cherrywood-smoked, hickory-smoked, pecanwood-smoked, fruitwood-smoked, hardwood-smoked, cold-smoked, or smoked
   - If cold-smoked with wood type → "applewood cold-smoked"
4. **Type**:
   - sliced bacon, slab bacon, bacon bits, bacon pieces, bacon topping, bacon ends, beef bacon, Canadian style bacon, or round bacon
5. **Slice or piece detail** (if applicable):
   - For sliced: "[X–Y] slices per pound ([cut])", where:
     • ≤12 → thick-cut
     • 13–16 → medium-cut
     • ≥17 → thin-cut
   - For bits/pieces: "X-inch pieces", "finely crumbled", or "random"
   - Always include the exact range/size from input alongside the label
6. **Layflat** (if "L/O", "layout", "layflat", "shingle", or "wide shingled" is present):
   - Append: ", layflat"

🚫 **Strictly omit from the sentence**:
- All pack sizes, weights, case counts (e.g., 5#, 150 CT, 32/36)
- Brand names, supplier codes, SKUs (e.g., Hormel, GFS, BCN, PL, FC, CSMK, SYSUP)
- Abbreviations — expand or interpret (e.g., "GF" → "gluten-free", "APPLWD" → "applewood", "FZ" → "frozen")
- Redundant terms: "pork bacon", "real bacon", "premium", "natural", "style", "quality"
- Any phrase not directly grounded in the input

🗣️ **Tone & Style**:
- Cold, professional, and concise
- No storytelling, no adjectives beyond required attributes
- No invented details — if smoke type isn't stated, omit it entirely
- Use natural sentence flow, but prioritize **consistency over style**
- Start with preparation/special features; end with layflat if applicable

🧠 **Key Rules**:
- "10/12", "10–12 CT", "10-12C" → "10–12 slices per pound (thick-cut)"
- "L/O", "layout", "layflat", "shingle" → add ", layflat" at the end
- "Cold smoked" ≠ "smoked" — only use "cold-smoked" if explicitly stated
- "Fully cooked" covers: cooked, pre-cooked, CKD, FC
- If multiple input variants, cross-reference for completeness
- For ambiguities, omit from sentence but note in metadata

✅ **Output Format**:
- First: The cleaned description sentence.
- Then: A 'Metadata' section (bulleted) capturing omitted/raw details, e.g.:
  - Original abbreviations/codes: [list]
  - Omitted sizes/weights: [list]
  - Preserved nuances: [...]
  - Any flagged ambiguities: [...]

✅ **Examples**:
Input:
BCN,PL,SYSUP,APLWD,10-12C,CSMK,GF | BACON 10/12 CT SLICED APPLEWOOD COLD SMOKED
Output:
Gluten-free, applewood cold-smoked sliced bacon, 10–12 slices per pound (thick-cut), layflat.
Metadata:
- Original codes: BCN, PL, SYSUP, CSMK
- Omitted sizes: 10/12 CT
- Preserved nuances: None

Input:
BACON BIT FC 3/8" GF | REAL BACON BITS COOKED GLUTEN FREE
Output:
Fully cooked, gluten-free bacon bits, 3/8-inch pieces.
Metadata:
- Original codes: FC
- Omitted sizes: None
- Preserved nuances: "REAL" implies non-imitation, but omitted per rules

Input:
SLAB BACON RAW CHERRYWOOD SMOKED
Output:
Raw, cherrywood-smoked slab bacon.
Metadata:
- Original codes: None
- Omitted sizes: None
- Preserved nuances: None

Now, rewrite the following input using these guidelines.
Return only the cleaned description and metadata.

Input: OLD SMOKEHOUSE SUGAR CURED HALF SLAB BACON | BACON SLAB CC SUGAR CURE FRZN
```

---

## 🎯 **Key Points**

1. **System Message** - Sets the LLM's overall behavior (consistent, factual, concise)
2. **Transformation Prompt** - Provides detailed rules for THIS specific task
3. **Your Row Data** - The actual bacon description to transform

**Total prompt length**: ~1,500 tokens per row (well within limits)

---

## ✅ **Verification**

You can verify the prompts are loaded correctly by running:

```bash
python run_bacon_cleaning.py
```

Look for **STEP 3** output which shows:
```
📝 System Message (first 200 chars):
   You are a careful product copy editor...

📝 Prompt Template (first 150 chars):
   Rewrite the input into a single, concise...
```

---

## 🎉 **You Now Have BOTH Prompts!**

✅ **System Message** (line 102-133) - Overall guidance  
✅ **Transformation Prompt** (line 15-100) - Detailed processing logic with all your rules!

**Ready to run!** 🚀

