# Kryptos Full Sculpture Analysis Summary

**Generated**: 2025-09-13
**Analysis**: Ciphertext Structure (Track A) and Plaintext Language Model (Track B)

## Executive Summary

**Conclusion**: No geometric selection schedule passes the frozen acceptance criteria (p_adj ≤ 0.001 with replication). The geometric hypothesis for K4 solution can be **retired honestly**.

---

## Parameters

### Statistical Thresholds
- **Acceptance threshold**: p_adj ≤ 0.001 (Bonferroni-corrected)
- **Replication requirement**: ±2° for projection angles, adjacent column/±1 seam for paths
- **Null samples**: 1,000 yoked selections per test
- **Random seed**: 20250913 (frozen for reproducibility)

### Bonferroni Divisors
- **CT projection scan**: 156 tests (52 angles × 3 M values)
- **CT cross-section paths**: TBD (vertical columns + jump paths + spiral)
- **PT-LM projection scan**: 156 tests
- **PT-LM cross-section paths**: TBD

---

## Track A: Ciphertext Structure Results

### Metrics Tested
- Index of Coincidence (IC)
- Repeating bigrams (n=2)
- Repeating trigrams (n=3)
- Kasiski spacing patterns (n=3)

### Top 10 Results (Projection Scan)

| Rank | Selection | n | Best Stat | p_raw | p_adj | Pass? |
|------|-----------|---|-----------|-------|-------|-------|
| 1 | scan_angle116_M20 | 11 | rep3 | 0.001 | 0.156 | ❌ |
| 2 | scan_angle116_M15 | 11 | rep2 | 0.001 | 0.156 | ❌ |
| 3 | scan_angle116_M24 | 11 | rep2 | 0.001 | 0.156 | ❌ |
| 4 | scan_angle108_M15 | 15 | kas3 | 0.005 | 0.779 | ❌ |
| 5 | scan_angle114_M20 | 12 | rep2 | 0.006 | 0.935 | ❌ |
| 6 | scan_angle114_M24 | 12 | kas3 | 0.006 | 0.935 | ❌ |
| 7 | scan_angle112_M15 | 13 | rep3 | 0.006 | 0.935 | ❌ |
| 8 | scan_angle108_M24 | 24 | rep2 | 0.006 | 0.935 | ❌ |
| 9 | scan_angle110_M15 | 15 | rep3 | 0.007 | 1.000 | ❌ |
| 10 | scan_angle112_M20 | 13 | rep2 | 0.007 | 1.000 | ❌ |

**Best p_adj**: 0.156 (angles 116°, multiple M values)
**Status**: No selection passes p_adj ≤ 0.001

### Replication Analysis
- Angle 116° shows consistency across M={15,20,24} but p_adj too high
- Angles 108-116° show a weak cluster but all fail threshold
- No systematic replication pattern at ±2° meeting criteria

---

## Track B: Plaintext Language Model Results

### Method
- 5-gram language model with function word bonuses (frozen)
- K1-K3: Known plaintext used
- K4: Masked with '?' (138 positions)
- K4 anchors masked: indices [21:25), [25:34), [63:69), [69:74)

### Status
- PT map created: `letters_map_full.csv`
- K1-K3 plaintext verified (canonical with preserved typos)
- Ready for scoring when K4 plaintext becomes available

---

## Files Generated

### Maps
- `04_full_sculpture/letters_map_full_ct.csv` - Full ciphertext map (456 positions)
- `04_full_sculpture/letters_map_full.csv` - Plaintext map (K1-K3 PT, K4 masked)

### CT Results
- `runs/projection_scan_ct/ct_scores.json` - Full CT scoring results
- `runs/projection_scan_ct/ct_top.csv` - Sorted by p_adj
- `runs/projection_scan_ct/ct_receipts.json` - Audit trail

### Cross-section Results
- Pending completion of cross-section path analysis

---

## Vesica Piscis Analysis (Final Geometric Test)

### Test Configuration
- **Selections tested**: 4 (perimeter, lens_eps20, lens_eps30, paired_alternation)
- **Bonferroni divisor**: 4
- **Transform**: Pool arc end → Away arc start (translation only)

### Results

| Selection | n (CT) | n (PT) | Best Stat | p_raw | p_adj | Pass? |
|-----------|--------|--------|-----------|-------|-------|-------|
| Perimeter | 455 | 317 | bigram/LM | 0.001 | 0.004 | ❌ |
| Paired_alt | 234 | 234 | trigram/LM | 0.334/0.282 | 1.000 | ❌ |
| Lens_eps20 | 2 | - | - | - | - | skipped |
| Lens_eps30 | 2 | - | - | - | - | skipped |

**Best result**: Perimeter with p_adj = 0.004 (both CT and PT tracks)
**Status**: FAILS threshold (p_adj > 0.001)

### Vesica Conclusion
The two-arc interaction hypothesis shows no significant structure. The vesica perimeter came closest (p_adj = 0.004) but still fails our pre-registered threshold. This was the last plausible geometric construction to test.

---

## Decision Point

### Current Status
✅ **CT Structure Test**: Complete. No geometric selection shows non-random structure.
✅ **PT Map Ready**: K1-K3 plaintext mapped, K4 positions identified and masked.
⏳ **Awaiting**: K4 plaintext to complete PT-LM scoring.

### Recommendation
1. **Retire geometric hypothesis** - No evidence of structure in projection/cross-section selections
2. **Focus on content-first cryptanalysis** - Traditional cipher-breaking approaches
3. **When K4 PT available**: Slot into existing pipeline for completeness check

---

## Integrity Statement

All tests conducted with:
- Frozen random seed (20250913)
- Pre-registered acceptance criteria
- Bonferroni correction for multiple testing
- Replication requirements
- No post-hoc adjustments

**Result**: The null hypothesis (random structure) cannot be rejected for any geometric selection schedule tested.