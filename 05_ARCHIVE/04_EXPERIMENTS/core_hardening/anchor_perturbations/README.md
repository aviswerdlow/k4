# Anchor Perturbation Study Results

## Overview
This study tested the sensitivity of the four plaintext anchors by shifting their indices ±1 and testing both split and combined modes for BERLIN/CLOCK.

## Test Configuration
- **Base Anchors**: EAST(21), NORTHEAST(25), BERLIN(63), CLOCK(69)
- **Perturbations**: ±1 index shifts per anchor
- **Modes**: SPLIT (BERLIN + CLOCK) vs COMBINED (BERLINCLOCK)
- **Skeleton**: Baseline `((i%2)*3)+(i%3)`

## Results Summary
- **Scenarios Tested**: 27
- **Feasible Solutions**: 0
- **Matching Winner PT**: 0
- **Distinct Tails Found**: 0

## Key Findings

## Mode Analysis
- **SPLIT mode feasible**: 0
- **COMBINED mode feasible**: 0

## Files
- `RESULTS.csv`: Complete test results for all perturbation scenarios
- `PROOFS/`: Proof files for feasible perturbations
- `RUN_LOG.md`: Execution details and environment info
- `SUMMARY.json`: Machine-readable summary
