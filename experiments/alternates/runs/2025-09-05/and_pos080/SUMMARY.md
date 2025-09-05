# Frame Variant: AND with POS 0.80

**Frame description**: Stricter Generic threshold (0.80 vs 0.60) compared to baseline AND gate  
**Policy**: POLICY.seamfree.and_pos080.json  
**Date**: 2025-09-05  
**Seed**: 1337  

## Results Table

| Label | AND_pos080_pass | Notes |
|-------|-----------------|-------|
| All candidates | false | Stricter POS threshold eliminates all |

## Summary

- Candidates tested: 10
- Passing phrase gate: 0
- Passing nulls: 0

**One-line result**: 0 pass gate / 0 pass nulls

## Interpretation

Stricter thresholds (POS ≥ 0.80) eliminate all candidates, including potential alternates. This confirms that the published threshold (0.60) is necessary for any candidates to pass.

**Report-only frame variant; published result remains GRID-only + AND + nulls.**