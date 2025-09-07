# Campaign C: Scorer Ablations Report

**Date:** 2025-09-05
**Configurations tested:** 23
**Candidates tested:** 10

## Top Configurations by Delta Performance

| Config | Weights (N,C,P) | Avg Score | Avg δ_shuffled | Pass Rate |
|--------|-----------------|-----------|----------------|----------|
| ngram_only | (1.0, 0.0, 0.0) | 5.470 | 5.898 | 0.0% |
| ngram_coverage | (0.5, 0.5, 0.0) | 5.184 | 5.876 | 0.0% |
| coverage_only | (0.0, 1.0, 0.0) | 4.898 | 5.854 | 0.0% |
| sweep_0.6_0.3_0.1 | (0.6, 0.3, 0.10000000000000003) | 4.739 | 5.295 | 0.0% |
| ngram_heavy | (0.7, 0.15, 0.15) | 4.546 | 5.006 | 0.0% |
| coverage_heavy | (0.15, 0.7, 0.15) | 4.231 | 4.982 | 0.0% |
| sweep_0.6_0.2_0.2 | (0.6, 0.2, 0.2) | 4.238 | 4.709 | 0.0% |
| sweep_0.5_0.3_0.2 | (0.5, 0.3, 0.2) | 4.180 | 4.705 | 0.0% |
| sweep_0.4_0.4_0.2 | (0.4, 0.4, 0.19999999999999996) | 4.123 | 4.701 | 0.0% |
| sweep_0.5_0.2_0.3 | (0.5, 0.2, 0.3) | 3.679 | 4.120 | 0.0% |

## Threshold Calibration

Best config: ngram_only

| Threshold | Pass Rate | Passers |
|-----------|-----------|----------|
| 0.03 | 0.0% | 0/10 |
| 0.04 | 0.0% | 0/10 |
| 0.05 | 0.0% | 0/10 |
| 0.06 | 0.0% | 0/10 |
| 0.07 | 0.0% | 0/10 |

## Key Findings

1. **Best configuration:** ngram_only
2. **Optimal weights:** (1.0, 0.0, 0.0)
3. **Delta improvement:** 5.898 vs 4.115 (baseline)
4. **Recommended threshold:** Based on calibration results
