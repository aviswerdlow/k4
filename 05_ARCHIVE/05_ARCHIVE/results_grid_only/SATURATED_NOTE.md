# Saturation Notice - Policy v5

**Date**: 2025-01-07  
**Policy Version**: 5.0.0  
**Status**: SATURATED

## Summary

No candidates from the v4.1.1 K=200 exploration pass the mandatory cadence (style) gate under policy v5.

## Analysis

### Candidates Evaluated
- **Total explored**: 200 heads
- **Passed exploration gates**: 200  
- **Lawful (encrypts_to_ct)**: 1 (HEAD_147_B)
- **Passed cadence**: 0

### Cadence Gate Results

HEAD_147_B metrics (only lawful candidate):
- ❌ cosine_bigram: 0.0 (threshold ≥0.65)
- ❌ cosine_trigram: 0.0 (threshold ≥0.60)
- ❌ fw_gap_mean: 1.36 (threshold 2.8-5.2)
- ✅ fw_gap_cv: 0.47 (threshold 0.4-1.2)
- ✅ wordlen_chi2: 17.1 (threshold ≤95.0)
- ❌ vc_ratio: 0.609 (threshold 0.95-1.15)

**Result**: 2/6 metrics passed - FAILED

## Root Cause

The v4.1.1 generator optimized for:
- High verb robustness
- Function word density
- Coverage maximization

This produced heads with:
- Function-word clustering
- Unnatural word sequences
- Poor bigram/trigram similarity to English
- Abnormal vowel-consonant ratios

## Implications

1. **No publishable winner** under v5 policy
2. **Style gate effective** at eliminating word-salad
3. **New generation needed** with cadence priors

## Next Steps

To find a v5 winner:
1. Implement cadence-aware head generator
2. Add style priors during exploration
3. Balance robustness with naturalness
4. Re-run with v5 requirements

## Policy Integrity

This saturation demonstrates:
- Style requirements successfully filter unnatural text
- No post-hoc threshold manipulation
- Commitment to quality over publishing anything

---
**Conclusion**: Better no winner than word-salad.