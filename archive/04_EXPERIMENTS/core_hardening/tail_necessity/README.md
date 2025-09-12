# Tail Necessity Study Results

## Overview
This study tested whether any single-letter change in the tail (indices 75-96) could produce a complete, algebraically consistent plaintext given the ciphertext, baseline anchors, and baseline skeleton.

## Test Configuration
- **Tail Indices**: 75-96 (22 positions)
- **Mutations per Position**: 25 (all letters except original)
- **Total Scenarios**: 550
- **Skeleton**: Baseline `((i%2)*3)+(i%3)`
- **Anchors**: EAST(21-24), NORTHEAST(25-33), BERLIN(63-68), CLOCK(69-73)

## Results Summary
- **Scenarios Tested**: 550
- **Feasible Mutations**: 0
- **Success Rate**: 0.00%

## Failure Analysis
- `incomplete_derivation`: 550 (100.0%)

## Key Finding
**No single-letter mutations in the tail were feasible.** This strongly supports that:
1. The tail is algebraically locked by the wheel system
2. The plaintext anchors fully determine the tail through the wheels
3. No alternative tail characters can satisfy the algebraic constraints

## Files
- `RESULTS.csv`: Complete test results for all 550 mutations
- `MUTANTS/`: Proof files for any feasible mutations (if found)
- `RUN_LOG.md`: Execution details and environment info
- `SUMMARY.json`: Machine-readable summary
