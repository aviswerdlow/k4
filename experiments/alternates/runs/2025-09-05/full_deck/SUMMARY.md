# Frame Variant: Full Deck with AND

**Frame description**: All routes enabled (GRID + SPOKE + RAILFENCE + HALF) vs GRID-only baseline  
**Policy**: POLICY.seamfree.full_deck.json  
**Date**: 2025-09-05  
**Seed**: 1337  

## Results Table

| Label | Route_ID | AND_pass | Notes |
|-------|----------|----------|-------|
| All candidates | Various | false | Full deck maintains same selectivity |

## Summary

- Candidates tested: 10
- Passing phrase gate: 0
- Passing nulls: 0

**One-line result**: 0 pass gate / 0 pass nulls

## Interpretation

Expanded routes (full deck) maintain the same selectivity as GRID-only when using the AND gate. This suggests the gate logic, not route restriction, drives the filtering.

**Report-only frame variant; published result remains GRID-only + AND + nulls.**