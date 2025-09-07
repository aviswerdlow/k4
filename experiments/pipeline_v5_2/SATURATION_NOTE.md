# v5.2 SATURATION NOTE

**Date**: 2025-01-07  
**Status**: **SATURATED**  
**Tag**: v5.2-SATURATED

## Saturation Cause

**Primary constraint violation**: f_words < 8 on ALL 85 promoted candidates

The v5.2 content-aware generation successfully eliminated word-salad heads but reached saturation due to incompatible constraints:

1. **Near-gate requirement**: f_words ≥ 8
2. **Actual achievement**: Maximum f_words = 7 (only 4/85 candidates)
3. **Most common**: f_words = 6 (58/85 candidates)

## Function Word Distribution (85 promoted candidates)
```
f_words | Count | Percentage
--------|-------|------------
   5    |  23   |  27.1%
   6    |  58   |  68.2%
   7    |   4   |   4.7%
   8+   |   0   |   0.0%  ← Required threshold
```

## Root Cause Analysis

The content-aware generation creates a **content-function paradox**:

- **Content enforcement** (≥35% content words) reduces available slots for function words
- **Surveying vocabulary** creates meaningful but content-heavy phrases
- **74-char limit** provides insufficient space for both rich content AND 8+ function words

### Example: HEAD_008_v52
```
Text: "FOLLOW THE DIAL TOWARD THE MERIDIAN THEN READ THE COURSE AND READ"
Content words: 7 (58.3%)
Function words: 5 (fails ≥8 requirement)
```

## Artifacts

- **Triage CSV**: `runs/confirm_strict/TRIAGE.csv` - Complete analysis of all 85 candidates
- **Promotion Queue**: `runs/k200/promotion_queue.json` - Original promoted candidates
- **Explore Matrix**: `runs/k200/EXPLORE_MATRIX.csv` - Full generation metrics

## Outcome

v5.2 achieved its primary goal of semantic meaningfulness but cannot meet the pre-registered near-gate threshold of f_words ≥ 8 within the 74-character constraint.

**Decision**: Campaign frozen as SATURATED. No post-hoc gate adjustments. Proceeding to v5.2.1 with generation improvements.

---
**Frozen**: 2025-01-07  
**Next**: v5.2.1 with content+function harmonization