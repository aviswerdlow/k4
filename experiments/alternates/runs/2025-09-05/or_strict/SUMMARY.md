# Frame Variant: OR with Strict Generic

**Frame description**: OR gate logic (Flint v2 ∨ Generic) with top-0.5% perplexity threshold  
**Policy**: POLICY.seamfree.or_strict.json  
**Date**: 2025-09-05  
**Seed**: 1337  

## Results Table

| Label | OR_pass | Notes |
|-------|---------|-------|
| 6 candidates | true | OR admits more through gate |
| After nulls | false | Nulls filter all candidates |

## Summary

- Candidates tested: 10
- Passing phrase gate: 6
- Passing nulls: 0

**One-line result**: 6 OR passers; 0 pass nulls

## Interpretation

OR gate allows more candidates through initial screening (6 vs 0) compared to AND gate, but null hypothesis testing still filters all. This demonstrates that nulls provide a strong final filter regardless of gate logic.

**Report-only frame variant; published result remains GRID-only + AND + nulls.**