# Cadence Panel Sensitivity Analysis Summary

Date: 2025-09-05
Seed: 1337

## Quick Results Table

| Analysis Type | Winner CCS | Runner CCS | Δ | Order Preserved |
|---------------|------------|------------|---|-----------------|
| **Baseline (75 tokens)** | -1.552 | -1.942 | 0.390 | ✓ |
| Character (450 chars) | -4.195 | -4.420 | 0.225 | ✓ |
| Declarative K2 | -0.684 | -0.956 | 0.272 | ✓ |
| Bigram/Trigram Heavy | -2.646 | -2.977 | 0.331 | ✓ |
| Rhythm Heavy | -0.118 | -0.698 | 0.580 | ✓ |
| Uniform Weights | -0.894 | -1.393 | 0.499 | ✓ |

## Key Findings

1. **Robust Ordering**: Winner > Runner maintained across all 6 sensitivity analyses
2. **CCS Range**: -4.420 (worst) to -0.118 (best) across all configurations
3. **Most Sensitive**: Character windows (450 chars) show largest negative CCS
4. **Least Sensitive**: Rhythm-heavy weights show smallest absolute CCS values
5. **Register Effect**: Removing K2 coordinates improves CCS by ~56%

## Files Generated

- 3 reference distributions (token, char, declarative)
- 6 panel analyses with full reports
- 22 total files with SHA-256 hashes

## Conclusion

The winner (GRID_W14_ROWS) consistently outperforms the runner (GRID_W10_NW) across all sensitivity analyses. The cadence panel shows both candidates are stylistically distinct from K1-K3, with no K-style orthographic quirks detected.

**This is a report-only analysis and does not change any gating decisions.**