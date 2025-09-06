# Grid Autos Campaign Report

**Date:** 2025-01-06  
**Campaign ID:** PV2-EXPLORE-GRID-AUTOS-001  
**Status:** Complete

## Executive Summary

Tested 80 anchor-constrained GRID transformations that preserve spatial relationships. All transformations successfully maintained anchor geometry, but none achieved promotion due to delta thresholds.

## Results

| Metric | Value |
|--------|-------|
| Total tests | 80 |
| Anchors preserved | 80 (100%) |
| Delta passers | 0 |
| Promoted to Confirm | 0 |
| Best fixed score | 0.58 |
| Best δ_shuffled | 0.00 |

## Key Findings

### 1. Anchor Preservation Success
- All 8 transformation types successfully preserved anchor relationships
- EAST→NORTHEAST adjacency maintained
- BERLINCLOCK stayed in NA-domain
- Spatial geometry respected throughout

### 2. Delta Problem Persists
- **All δ_windowed = 0**: Windowed mode still behaving identically to fixed
- **All δ_shuffled = 0**: Even with preserved anchors, no separation from controls
- This suggests the ±1 window is fundamentally too narrow

### 3. Best Performing Transforms
Top scores (all from GRID_CONJUGATE_1):
- B0008: 0.585
- B0006: 0.556
- B0027: 0.467
- B0002: 0.267

### 4. Transform Performance Patterns
- **GRID_CONJUGATE_1**: Block transpose, highest scores
- **GRID_10x10_FIXED**: Moderate scores, stable
- **GRID_10x10_ROW_PERM**: High variance, some negative scores
- **GRID_CONJUGATE_3**: Diagonal read, consistently negative

## Technical Analysis

### Anchor Preservation Algorithm
Successfully verified:
1. EAST positions map to contiguous locations
2. NORTHEAST maintains adjacency with EAST
3. BERLINCLOCK stays in latter half of text
4. Relative offsets preserved within tolerance

### Why Deltas Still Zero
Even with perfect anchor preservation:
1. Windowed mode with ±1 is too restrictive
2. Shuffled control may be benefiting from same anchor positions
3. Blinding removes the anchor words themselves from scoring

## Comparison to Previous Campaigns

| Campaign | Tests | Anchors OK | Best δ_shuffled | Promotions |
|----------|-------|------------|-----------------|------------|
| Breadth | 70 | N/A | 3.91 | 0 |
| Route | 780 | No | 0.00 | 0 |
| Ablations | 230 | N/A | 5.90* | 0 |
| **Grid Autos** | **80** | **Yes** | **0.00** | **0** |

*Using different scoring weights

## Conclusions

1. **Anchor preservation alone insufficient**: Maintaining geometry doesn't overcome delta thresholds
2. **Window too narrow**: ±1 flexibility acts identical to fixed positioning
3. **Need different approach**: Either wider windows or different falsification strategy

## Recommendations

1. **Run window sweep campaign**: Test r ∈ {2,3,4} to find where elasticity matters
2. **Try lexicon injection**: Add high-frequency glue tokens for better n-gram scores
3. **Test known winner**: Validate that pipeline can pass legitimate solution
4. **Consider relaxing δ thresholds**: Current 0.05 may be too conservative

## Files Generated

- `ANCHOR_MODE_MATRIX.csv`: Full results matrix (80 rows)
- `promotion_queue.json`: Empty queue (0 promotions)
- `MANIFEST.sha256`: File integrity hashes
- This report: `EXPLORE_REPORT.md`

## One-Liner Summary

N=10 seeds, M=8 transforms, K=80 tests, L=80 preserved, Q=0 promoted

---
*Campaign completed: 2025-01-06*