# Skeleton Uniqueness Survey Results

## Overview
This study explored 24 different periodic classing schemes (skeletons) to test whether they could satisfy the four plaintext anchors and re-derive the full plaintext from ciphertext.

## Results Summary
- **Skeletons Tested**: 24
- **Feasible Solutions**: 1
- **Matching Winner PT**: 1
- **Distinct Tails Found**: 1

## Skeleton Types Tested
1. **Baseline**: The 1989 formula `((i%2)*3)+(i%3)`
2. **Mod-T**: Simple modulo operations for T ∈ {2..8}
3. **2D Interleaves**: Patterns like `(i%p) + p*(i%q)`
4. **Affine Mixes**: Patterns like `((i%p)*k + (i%q)) % M`

## Key Findings
- **Only the baseline skeleton successfully re-derived the winner plaintext**
- No alternative skeletons produced valid solutions
- This strongly supports the uniqueness of the algebraic solution

## Files
- `RESULTS.csv`: Complete results for all skeletons tested
- `PROOFS/`: Proof JSON files for all feasible solutions
- `RUN_LOG.md`: Execution details and environment info
- `SUMMARY.json`: Machine-readable summary
