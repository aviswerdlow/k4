# Sensitivity Strip Analysis

**Date**: 2025-09-05
**Seed**: 1337
**Plaintext**: Winner (published)

## Results Matrix

| POS \ Perp | 99.5% | 99.0% | 98.5% |
|------------|-------|-------|-------|
| 0.40 | ✓ PASS | ✓ PASS | ✓ PASS |
| 0.60 | ✓ PASS | ✓ PASS | ✗ FAIL |
| 0.80 | ✗ FAIL | ✗ FAIL | ✗ FAIL |

**Legend**:
- ✓ PASS: Publishable (passes gate AND nulls)
- ○ Gate: Passes gate but not nulls
- ✗ FAIL: Fails phrase gate

## Baseline Configuration
- POS: 0.60
- Perplexity: 99.5%
- Result: **PUBLISHABLE**

## Summary
- Configurations tested: 9
- Passing phrase gate: 5/9
- Publishable: 5/9

**Conclusion**: Winner remains publishable at baseline (0.60, 99.5%) and looser configurations.
Stricter thresholds (POS ≥ 0.80) eliminate the winner, confirming threshold sensitivity.

**Report-only analysis; does not affect published results.**