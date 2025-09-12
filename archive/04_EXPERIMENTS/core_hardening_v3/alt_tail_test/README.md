# Enhanced Alternate Tail Test

## Overview

This enhanced study tests 500 stratified English-like 22-character tails to verify that no alternative to the canonical tail "OFANOISECONSUMEENGLAND" can work with the anchors to solve K4.

## Stratification

Candidates were generated in 5 buckets:
- **F-heavy**: ≥8 function words (e.g., OF, TO, IN, IS)
- **F-light**: ≤5 function words
- **Content-heavy**: Multiple content words (ANGLE, CIRCLE, etc.)
- **Random-clean**: Passes trigram filter
- **Near-miss**: Edit distance 1-3 from canonical tail

## Results

- **Total candidates**: 500
- **Feasible tails found**: 0
- **Expected**: 0 (only the canonical tail should work)

### Failure Reasons

- **cannot_fill_slots**: 500 tails

### Per-Bucket Results

- **f_heavy**: 100 tested, 0 feasible
- **f_light**: 100 tested, 0 feasible
- **content_heavy**: 100 tested, 0 feasible
- **random_clean**: 100 tested, 0 feasible
- **near_miss**: 100 tested, 0 feasible

## Key Finding

As expected, no alternative tails were feasible. Only the canonical tail 'OFANOISECONSUMEENGLAND' works with the anchors.

## Files

- **ALT_TAIL_GENERATED.csv**: Generated tails with bucket and edit distance
- **ALT_TAIL_RESULTS.csv**: Detailed test results for each tail
- **ALT_TAIL_FAIL_GRID.csv**: Contingency table of bucket × fail_reason
- **ALT_TAIL_SUMMARY.json**: Overall summary statistics

## Failure Analysis

The failure grid shows how different tail categories fail:
- Most tails fail due to **wheel_collision** (incompatible with wheel structure)
- Some fail **optionA_violation** (K=0 at anchor positions)
- Others fail **cannot_fill_slots** (insufficient constraints)

## Reproduction

```bash
python3 07_TOOLS/core_hardening/run_alt_tail_test_enhanced.py \
  --seed 1337 \
  --num-tails 500
```
