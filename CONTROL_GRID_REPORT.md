# Control Grid Report

## Executive Summary
The control-mode grid tests revealed that the current zone_runner implementation does not support the advanced control-mode features (schedule changes, family toggles, mask switches). Only R4 with its specially aligned key produces BERLINCLOCK.

## Test Results

### Control Grid Manifests (S1-S4)
All failed to produce BERLINCLOCK due to missing feature support:

| Manifest | Control Text | Round-trip | Function Words | Score |
|----------|-------------|------------|----------------|-------|
| S1_vig_ABSCISSA_period5 | VGPVSBKRNXK | ✅ | 0 | 0.025 |
| S1_beau_LATLONG_diag12 | HTZMBXKSFPK | ❌ | 0 | 0.012 |
| S2_toggle_mid | FHPDFIGROPS | ✅ | 0 | 0.012 |
| S3_switch_mask | NYPVTTMZFPK | ❌ | 0 | 0.012 |
| S4_serpentine_flip | JUSFKVKTCLT | ❌ | 0 | 0.000 |

### R4 Baseline
- **Control text**: BERLINCLOCK ✅
- **Round-trip**: PASS ✅
- **Function words outside control**: 0
- **Score excluding control**: 0.012

## Key Findings

### 1. Implementation Gap
The zone_runner.py lacks support for:
- `schedule: "rotate_on_control"` - Key rotation at control indices
- `family_overrides` - Cipher family toggling  
- `mask_overrides` - Mask switching at indices
- `route_overrides` - Route direction flipping

### 2. No Natural BERLINCLOCK
Without the specially aligned key from R4, no standard dictionary words produce BERLINCLOCK at positions 63-73.

### 3. Low English Content
Even with masks applied (period5, period7, diag_weave), the English content remains very low (scores < 0.03).

### 4. Function Word Analysis
**Zero function words found outside control span** in all tested manifests, indicating the solution space hasn't been found yet.

## Files and Paths

### Top 2 Manifests (by score)
1. **S1_vig_ABSCISSA_period5.json**
   - Path: `/04_EXPERIMENTS/phase3_zone/configs/control_grid/S1_vig_ABSCISSA_period5.json`
   - Best English score but no BERLINCLOCK

2. **R4 (baseline)**
   - Path: `/01_PUBLISHED/candidates/zone_mask_v1_R4/manifest.json`
   - Only manifest producing BERLINCLOCK

### Summary Report Output
```
======================================================================
TOP CANDIDATES:
1. S1_vig_ABSCISSA_period5 - Score 0.025, No BERLINCLOCK
2. R4 - Score 0.012, BERLINCLOCK ✅

FUNCTION WORDS OUTSIDE CONTROL: 0 for all manifests
======================================================================
```

## Recommendations

### Immediate Actions
1. **Implement control-mode features** in zone_runner.py:
   - Add key rotation at indices
   - Add cipher family switching
   - Add mask/route overrides

2. **Expand key search** with the current working framework:
   - Test TANGENT, SECANT, RADIAN, DEGREE
   - Test compound keys like BERLINCLOCKABSCISSA
   - Implement key phase scanning

3. **Zone edge adjustments**:
   - Test MID 35-73 and 34-72
   - May help align keys naturally

### Decision
**No candidates pass the criteria** for promotion:
- ❌ No manifests produce both BERLINCLOCK and function words
- ❌ All fail null hypothesis tests (p = 1.0)
- ✅ R4 remains as calibration artifact only

## Next Steps

Since the control-mode features aren't implemented, the best path forward is:

1. **Focus on key discovery** with existing features
2. **Implement key phase scanning** to find natural alignments
3. **Test zone edge variations** (MID 35-73 vs 34-72)
4. **Add the missing control-mode features** to zone_runner.py

The framework is correct (zones fixed, indices proper) but needs:
- Better keys
- Control-mode feature implementation
- Or a different approach to producing BERLINCLOCK naturally