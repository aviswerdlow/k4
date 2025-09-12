# 04:57 Sensitivity and P[74] Strips – Conceptual Only

**Status**: CONCEPTUAL (no new execution)
**Date**: 2025-09-05

## Overview

This folder contains conceptual summaries based on prior empirical runs. No new computations were performed for these analyses.

## Expected Behavior (Based on Prior Work)

### P[74] Strip

**Expected Result**: P[74] is editorial under our publication bar
- All 26 letters (A-Z) at position 74 pass the phrase gate equally
- All 26 letters achieve identical statistical significance under null hypothesis testing
- The choice of 'K' (creating "HIAKTHEJOY") is editorial for readability
- No single letter at position 74 is cryptographically forced

**Evidence Base**: Previous P[74] sweeps documented in `experiments/p74/runs/20250903_final_corrected/`

### Sensitivity Strip

**Expected Result**: Winner remains robust across reasonable threshold variations
- Baseline configuration (POS=0.60, perplexity top-1%) yields publishable result
- Looser thresholds (POS<0.60) maintain publishability
- Extremely strict thresholds (POS≥0.80) would likely eliminate all candidates
- The solution is stable within a reasonable parameter range

**Evidence Base**: Parameter selection studies and threshold calibration

### GRID Controls

**Expected Result**: Control imperatives fail under GRID+AND+nulls
- "IS A MAP" - Expected to fail GRID transposition
- "IS TRUE" - Expected to produce gibberish
- "IS FACT" - Expected to fail encryption match

**Evidence Base**: GRID method selectivity observed in all prior runs

## Why Conceptual Only?

During the 04:57 action packet implementation, mock scripts were initially created that generated simulated results without running actual cryptographic tests. In the interest of transparency and accuracy, these have been quarantined and replaced with this conceptual summary based on our established empirical findings.

## References

- Published results: `results/GRID_ONLY/`
- P[74] analysis: See README.md Section "P[74] Analysis (Editorial Choice)"
- Policy specification: `experiments/policy_prereg/docs/POLICY_PREREG.md`

## Status

These statements are grounded in earlier executed ladders. For actual empirical results, refer to the referenced experiments.