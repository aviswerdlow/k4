# Alternate Tail Test

## Overview

This study generates and tests 50 English-like 22-character tails to determine if any alternative to the canonical tail can work with the anchors to solve K4.

## Generation Constraints

- Length: Exactly 22 characters
- Alphabet: A-Z only
- Patterns avoided: Anchor words (EAST, NORTHEAST, BERLIN, CLOCK)
- Generation strategies:
  1. Geometric/angle themed phrases
  2. Bigram-constrained random text
  3. Function word combinations

## Results

- **Tails generated**: 50
- **Feasible tails found**: 0
- **Expected**: 0 (only the canonical tail should work)

## Key Finding

As expected, no alternative tails were feasible. Only the canonical tail 'OFANOISECONSUMEENGLAND' works with the anchors.

## Files

- **ALT_TAIL_GENERATED.csv**: Generated tails with linguistic statistics
- **ALT_TAIL_RESULTS.csv**: Feasibility test results for each tail

## Reproduction

```bash
python3 07_TOOLS/core_hardening/run_alt_tail_test.py \
  --seed 1337 \
  --num-tails 50
```
