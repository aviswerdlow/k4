# Skeleton Survey v3 - Extended

## Overview

This extended study tests 50 different periodic classing schemes to verify that only the baseline skeleton formula produces a valid K4 solution.

## Pattern Families Tested

- **Modular**: Simple modular patterns (i mod a)
- **Sum**: Sum of moduli (i mod a) + (i mod b)
- **Weighted**: Weighted sums c*(i mod a) + d*(i mod b)
- **Product**: Products (i mod a) * (i mod b)
- **XOR**: Bitwise XOR combinations
- **Affine**: Affine transformations (a*i + b) mod c
- **Phase**: Phase-shifted versions of baseline
- **Complex**: Fibonacci, triangular, digital root, Collatz-based
- **Random**: Randomly generated periodic sequences

## Results

- **Total patterns tested**: 50
- **Feasible patterns found**: 1
- **Expected**: 1 (baseline only)

### Feasible Patterns

- BASELINE: (i mod 2)*3 + (i mod 3)

## Key Finding

As expected, only the baseline skeleton formula is feasible.

## Files

- **RESULTS.csv**: Test results for all patterns
- **SUMMARY.json**: Overall statistics
- **PROOFS/**: JSON proof files for feasible patterns

## Pattern Details

The baseline formula is:
```
class(i) = (i mod 2) * 3 + (i mod 3)
```

This creates a 6-class periodic pattern with period lcm(2,3) = 6.

## Reproduction

```bash
python3 07_TOOLS/core_hardening/run_skeleton_survey_v3.py \
  --seed 1337 \
  --max-patterns 50
```
