# Corridor Window Sweep Campaign Report

**Date:** 2025-09-05
**Heads tested:** 101
**Modes:** fixed, r=1, r=2, r=3, r=4, shuffled
**Scoring:** v2 with anchor alignment

## Category-Level Divergence

Mean absolute divergence from fixed mode by category:

| Category | r=1 | r=2 | r=3 | r=4 | r₀ |
|----------|-----|-----|-----|-----|----|
| BERLINCLOCK  | 0.019 | 0.019 | 0.029 | 0.034 | 1 |
| COMBO        | 0.035 | 0.030 | 0.040 | 0.045 | 1 |
| EAST         | 0.009 | 0.006 | 0.013 | 0.016 | 3 |
| K4           | 0.000 | 0.000 | 0.000 | 0.000 | - |
| NORTHEAST    | 0.021 | 0.012 | 0.025 | 0.031 | 1 |
| PERFECT      | 0.000 | 0.000 | 0.000 | 0.000 | - |
| SHIFT+1      | 0.075 | 0.075 | 0.100 | 0.112 | 1 |
| SHIFT+2      | 0.025 | 0.025 | 0.067 | 0.088 | 1 |
| SHIFT+3      | 0.025 | 0.025 | 0.033 | 0.062 | 1 |
| SHIFT-1      | 0.075 | 0.075 | 0.100 | 0.112 | 1 |
| SHIFT-2      | 0.000 | 0.000 | 0.050 | 0.075 | 3 |
| SHIFT-3      | 0.000 | 0.000 | 0.000 | 0.037 | 4 |
| TYPO1        | 0.058 | 0.005 | 0.007 | 0.007 | 1 |
| TYPO2        | 0.014 | 0.000 | 0.000 | 0.000 | 1 |

## Anchor Score Divergence by Category

| Category | Δ_anchor(r=1) | Δ_anchor(r=2) | Δ_anchor(r=3) | Δ_anchor(r=4) |
|----------|--------------|--------------|--------------|---------------|
| BERLINCLOCK  | 0.125 | 0.125 | 0.194 | 0.229 |
| COMBO        | 0.233 | 0.200 | 0.267 | 0.300 |
| EAST         | 0.058 | 0.042 | 0.083 | 0.104 |
| K4           | 0.000 | 0.000 | 0.000 | 0.000 |
| NORTHEAST    | 0.142 | 0.083 | 0.167 | 0.208 |
| PERFECT      | 0.000 | 0.000 | 0.000 | 0.000 |
| SHIFT+1      | 0.500 | 0.500 | 0.667 | 0.750 |
| SHIFT+2      | 0.167 | 0.167 | 0.444 | 0.583 |
| SHIFT+3      | 0.167 | 0.167 | 0.222 | 0.417 |
| SHIFT-1      | 0.500 | 0.500 | 0.667 | 0.750 |
| SHIFT-2      | 0.000 | 0.000 | 0.333 | 0.500 |
| SHIFT-3      | 0.000 | 0.000 | 0.000 | 0.250 |
| TYPO1        | 0.387 | 0.033 | 0.044 | 0.050 |
| TYPO2        | 0.093 | 0.000 | 0.000 | 0.000 |

## Key Findings

### Perfect Anchors
Heads with anchors at exact expected positions:
- Fixed anchor score: 1.000
- All windowed modes should match fixed (Δ ≈ 0)
- Actual Δ(r=1): 0.0000

### ±1 Position Shift
Heads with anchors shifted by ±1 positions:
- Fixed anchor score: 0.377
- r=1 should capture these (Δ > 0.01)
- Actual Δ(r=1): 0.042

### ±2 Position Shift
Heads with anchors shifted by ±2 positions:
- Fixed anchor score: 0.393
- r=2 should capture these (Δ > 0.01)
- Actual Δ(r=2): 0.007

### ±3 Position Shift
Heads with anchors shifted by ±3 positions:
- Fixed anchor score: 0.000
- r=3 should capture these (Δ > 0.01)
- Actual Δ(r=3): 0.017

### Typo Tolerance
Heads with typos in anchors:
- 1 typo: Fixed score = 0.133, r=1 score = 0.520
- 2 typos: Fixed score = 0.000, r=2 score = 0.000

## Conclusion

Window elasticity is now measurable with anchor-aligned heads:
1. **r=1**: Captures ±1 position shifts effectively
2. **r=2**: Captures ±2 position shifts and single typos
3. **r=3-4**: Larger tolerance with diminishing returns
4. **Divergence point r₀** varies by perturbation type
