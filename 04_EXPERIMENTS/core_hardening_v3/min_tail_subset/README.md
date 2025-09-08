# Minimum Tail Subset Study

## Overview

This study identifies the smallest subset of tail indices (positions 75-96) that, combined with the four anchors, uniquely determines the full K4 plaintext.

## Results

- **Tail range tested**: Positions 75-96 (22 possible indices)
- **Subset sizes tested**: 10 to 21
- **Minimal subset size**: Not found
- **Seed**: 1337

## Key Finding

No feasible subset found in the tested range.

## Files

- **MTS_RESULTS.csv**: All tested subset sizes and outcomes
- **MTS_MIN_PROOF.json**: The minimal subset with uniqueness certificate
- **PROOFS/**: Detailed wheel configurations for feasible subsets

## Reproduction

```bash
python3 07_TOOLS/core_hardening/run_min_tail_subset.py \
  --seed 1337 \
  --kmin 10 \
  --kmax 22 \
  --samples-per-k 500
```
