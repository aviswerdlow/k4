# Pipeline v2 Instrument Status

**Date:** 2025-01-06  
**Status:** OPERATIONAL ✅

## Windowed Scoring Bug → Fixed

**Issue**: Windowed modes were complete no-ops (all Δ = 0)  
**Root Cause**: Anchors blinded before scoring  
**Solution**: Implemented `anchor_score.py` to score anchors BEFORE blinding  
**Validation**: 
- All unit tests pass (`test_anchor_score.py`)
- Synthetic heads confirm proper behavior (`sanity_check.py`)
- Divergence now measurable (r=n captures ±n position shifts)

## Corridor Campaign → Elasticity Confirmed

**Test**: 101 anchor-aligned heads with systematic variations  
**Anchors**: EAST@21, NORTHEAST@25, BERLINCLOCK@63  
**Results**:
- Perfect anchors: No divergence at any radius ✅
- ±1 shift: Detected at r=1 (Δ = 0.075)
- ±2 shift: Detected at r=2-3 (Δ = 0.050)
- ±3 shift: Detected at r=3-4 (Δ = 0.037)
- Monotonic increase with radius confirmed

## Glue Injection → No Promotions

**Test**: 288 heads with 0/1/2 non-narrative glue tokens  
**Impact**:
- 1 token: Δ = -0.0005 (slight degradation)
- 2 tokens: Δ = -0.0016 (more degradation)
- Anchors preserved: 95/96 (1 token), 93/96 (2 tokens)
**Result**: 0 promotions - δ₁ and δ₂ thresholds hold firm

## Two-Lane Pipeline Final Status

### Explore Lane: TRUSTWORTHY ✅
- Falsifiable anchor modes working correctly
- Blinded scoring prevents spurious promotions
- Window elasticity measurable and monotonic
- 0 promotions across all campaigns (correct outcome)
- "Kill fast, learn fast" discipline intact

### Confirm Lane: READY ✅
- Awaiting Explore survivors
- 10k nulls, Holm correction, full gates configured
- No premature promotions to preserve alpha

## Conclusion

The Pipeline v2 instrumentation is **fully operational**. Windowed scoring now behaves as designed, enabling falsifiable hypothesis testing with graduated anchor flexibility. The two-lane system maintains discipline: Explore kills weak hypotheses quickly, Confirm awaits genuine signals.