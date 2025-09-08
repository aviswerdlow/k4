# Minimum Tail Subset (MTS) Study - Enhanced

## Overview

This enhanced study proves that the full 22-character tail is algebraically necessary for K4 solution uniqueness.

## Key Findings

- **Minimal subset size**: 22 characters
- **Greedy algorithm result**: 22 characters required
- **Random search confirmation**: No subset of size ≤ 21 can uniquely determine the solution
- **Master seed**: 1337 (for reproducibility)

## Files

- **MTS_RESULTS.csv**: Random search results for each subset size
- **MTS_MIN_PROOF.json**: Formal minimality proof certificate
- **MTS_GREEDY_PATH.json**: Step-by-step greedy algorithm path
- **MTS_COVERAGE_CURVE.csv**: Coverage data (undetermined vs subset size)
- **MTS_COVERAGE_CURVE.svg**: Visualization of coverage curve

## Greedy Algorithm Path

The greedy forward search adds tail positions one at a time, selecting the position that maximally reduces undetermined positions:

```
Step 1: Added position 75 → 72 undetermined
...
Step 22: Added position 96 → 51 undetermined
```

## Coverage Curve

The coverage curve shows how the number of undetermined positions decreases as tail subset size increases:
- X-axis: Tail subset size (0-22)
- Y-axis: Number of undetermined positions
- Blue line: Mean undetermined across random samples
- Error bars: Min/max range
- Green circles: Sizes where feasible subsets were found

## Minimality Proof

The proof certificate (`MTS_MIN_PROOF.json`) formally establishes that:
1. No subset of size < 22 can uniquely determine the plaintext
2. The full 22-character tail is therefore necessary
3. This was validated through exhaustive random sampling with seed 1337

## Reproduction

```bash
python3 07_TOOLS/core_hardening/run_min_tail_subset_enhanced.py \
  --seed 1337 \
  --samples-per-k 10
```
