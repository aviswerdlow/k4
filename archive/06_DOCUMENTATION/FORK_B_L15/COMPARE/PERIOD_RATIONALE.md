# Period Rationale

## Why L=17 Originally?

### Objective Signals from Prior Panels

1. **Co-prime Coverage**: L=17 is prime and creates perfect 1-to-1 mapping with 97 positions
   - gcd(17, 97) = 1
   - Total slots = 6 × 17 = 102 > 97 (no collision)
   - Each position maps to unique (class, slot) pair

2. **Collision Avoidance**: L=17 ensures no anchor conflicts
   - All four anchors seat without slot collisions
   - Option-A constraint satisfied at all anchor positions

3. **"Distinct Slots" Heuristic**: Preference for unique determination
   - Each plaintext position should ideally determine one wheel slot
   - Avoids ambiguity in reconstruction

### What We Don't Have

**No K3 precedent for L=15**: 
- K3 uses 4×7 grid (28 positions)
- L=14 (2×7) has clearer K3 relationship
- L=15 (3×5) has no direct K3 derivation
- L=17 (prime) also lacks K3 connection

## L=15 as "What-If"

L=15 emerged from systematic algebraic testing:
- Achieves complete closure with anchors + tail
- BUT produces different plaintext than canonical
- Tail under L=15: "...IREGXUWJOKQGLICP" (not "THEJOYOFANANGLEISTHEARC")

This shows L=15 is algebraically viable but semantically different.

## Invitation to Community

If you can show a K3→K4 clue that fixes L=15, we'll adopt it.
Current evidence favors L=17 based on:
1. Produces canonical plaintext
2. 1-to-1 mapping property
3. No slot collision issues

## State of Evidence

- **L=17**: Canonical plaintext match, but needs more than tail
- **L=15**: Algebraic closure, but different plaintext
- **Open question**: Is there a prior-panel signal we're missing?
