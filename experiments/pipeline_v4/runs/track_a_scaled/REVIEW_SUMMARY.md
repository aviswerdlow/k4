# GO-A Track A Scaled Review - First 25 Heads

**Date:** 2025-01-06  
**Seed:** 1337  
**Parameters:** GO-A frozen (α=0.7, β=0.3, γ=0.15)  

## Summary

Generated and processed 25 heads through scaled Track A pipeline with 4-stage annealing MCMC.

### Key Statistics

- **Heads generated:** 42 total (from 2 chains × 4 stages)
- **Heads processed:** Top 25 by blinded score
- **Score range:** 2.470 (best) to 1.767 (worst)
- **Repair improvements:** 0.0 to 0.609 (mean: 0.238)
- **Delta performance:** 0/25 pass thresholds
- **Within ε=0.10:** 25/25 (100%)

### Files Delivered

1. **EXPLORE_MATRIX.csv** - Full scoring results for 25 heads
2. **SALIENCY_EXEMPLAR.json** - Detailed saliency analysis for BLINDED_CH00_S1_I004
3. **processed_heads_review.json** - Complete processing data
4. **blinded_heads_scaled_review.json** - Raw generated heads

## Analysis

### Strengths
- **Blinded generation working**: Heads achieve scores 1.767-2.470 in blinded space
- **Saliency mapping effective**: Successfully identifies low-impact positions
- **Pareto placement functional**: All heads placed anchors at fixed positions
- **Neutral repair effective**: Mean improvement 0.238, max 0.609

### Challenges
- **Delta thresholds not met**: All heads score 0.0 on both deltas
- **Z-scores zero**: Indicates scoring pipeline may need adjustment
- **No promotion candidates**: 0/25 pass delta thresholds

## Exemplar Analysis

**Head:** BLINDED_CH00_S1_I004
- **Original S_blind:** 2.470
- **After anchors:** 2.463 (drop: 0.007)
- **After repair:** 2.463 (improvement: 0.0)
- **Anchor placement:** Fixed (positions 21, 25, 63)

Saliency map shows mostly zero values with peaks at positions 2, 11, 14 - confirming anchors placed in low-sensitivity regions.

## Recommendations

1. **Continue to K=200**: Initial 25 heads show promise but need larger sample
2. **Investigate delta scoring**: Zero deltas suggest possible scoring issue
3. **Consider parameter tuning**: May need to adjust MCMC temperature schedule
4. **Examine blinding interaction**: Verify anchors scored BEFORE blinding

## Next Steps

Per GO-A specification:
1. Generate remaining heads to reach K=200
2. Run orbit analysis on any near-threshold candidates
3. Execute 1k nulls on orbit survivors
4. Proceed to GO-B (Track B Pareto MCMC) in parallel