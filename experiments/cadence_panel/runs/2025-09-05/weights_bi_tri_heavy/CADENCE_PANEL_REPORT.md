# Cadence Panel Report

Generated: 2025-09-04T23:25:26.782532

Reference parameters:
- Bootstrap windows: 2000 per K text
- Window size: 75 tokens
- Seed: 1337
- Total reference windows: 6000

## Executive Summary

This panel compares candidate K4 heads to the style of K1-K3 using multiple metrics.
**This is a report-only analysis and does not change any gating decisions.**

## Combined Cadence Scores (CCS)

| Candidate | CCS | J_content | J_content_lev1 | Cosine_Bi | Cosine_Tri | Has_Quirks |
|-----------|-----|-----------|----------------|-----------|------------|------------|
| winner_GRID_W14_ROWS_head | -2.646 | 0.0000 | 0.0236 | 0.6263 | 0.3749 |     No     |
| runner_GRID_W10_NW_head   | -2.977 | 0.0000 | 0.0160 | 0.6314 | 0.3253 |     No     |

## Detailed Metrics (Raw Values)

| Candidate | χ²_WordLen | JS_WordLen | V:C_Ratio | FW_Mean_Gap | FW_CV | X/100 |
|-----------|------------|------------|-----------|-------------|-------|-------|
| winner_GRID_W14_ROWS_head |  0.1689 |  0.3269 |  0.744 |    0.00 | 0.000 |  0.00 |
| runner_GRID_W10_NW_head   |  0.2096 |  0.3658 |  0.542 |    3.00 | 0.000 |  0.00 |

## Z-Scores (Deviation from K1-K3)

| Candidate | z_J_content | z_Cosine_Bi | z_Cosine_Tri | z_χ²_WordLen | z_V:C | z_FW_Gap |
|-----------|-------------|-------------|--------------|--------------|-------|----------|
| winner_GRID_W14_ROWS_head |  +0.000 |  -5.301 |  -4.381 |  +3.961 | +0.000 | -3.213 |
| runner_GRID_W10_NW_head   |  +0.000 |  -5.153 |  -5.313 |  +5.419 | +0.000 | -0.527 |

## Orthographic Quirks Analysis

No K-style orthographic quirks detected in any candidate.

## Combined Cadence Score (CCS) Weights

The CCS is computed as a weighted sum of z-scores:
```
CCS = 0.25*z(J_content) + 0.10*z(J_content_lev1)
    + 0.20*z(cosine_bigram) + 0.15*z(cosine_trigram)
    - 0.10*|z(χ²_wordlen)| - 0.10*|z(V:C_ratio)|
    - 0.05*|z(FW_mean_gap)| - 0.05*|z(FW_CV)|
```

## Notes

1. All metrics computed on head positions 0-74 only (seam excluded)
2. Tokenization uses canonical cuts with no inferred splits
3. Reference distributions from 2000 bootstrap windows per K text
4. Levenshtein-1 tolerance included as secondary metric only
5. This analysis is report-only and does not change gating decisions