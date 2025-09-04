# Anchors-Only Tail Forcing Analysis

**Experiment Date**: September 3, 2025  
**Objective**: Determine whether anchors alone algebraically force the tail (positions 75-96) under minimal Sanborn constraints

## Rails Enforced

**Minimal Sanborn constraints only**:
- **Anchors locked**: EAST (21-24), NORTHEAST (25-33), BERLINCLOCK (63-73) as plaintext at 0-indexed positions
- **97-character plaintext** (A-Z only)
- **Pencil-and-paper families**: Vigenère, Beaufort, Variant-Beaufort with single-key classing
- **NA-only permutations**: Routes that fix anchor positions by exclusion from permutation domain

**No additional constraints**: No head lock, no seam guard, no language scoring, no phrase gates

## Route Families Tested

All routes tested fix anchors by NA-only design (anchors excluded from permutation domain):

- **GRID_W14_ROWS**: Grid width-14, row-major reading
- **GRID_W10_NW**: Grid width-10, northwest reading  
- **SPOKE_NE_NF_w1**: Spoke pattern, northeast near-far width-1
- **RAILFENCE_R3_INVERTED**: Rail-fence 3-rail inverted reading

## Methodology

**Algebraic Coverage Test**:
1. For each route, family, period L, and phase φ:
2. Compute residue addresses for all 24 anchor positions: `r = (position + φ) % L`
3. Solve forced key values from anchor equations: `K[r] = solve(C[anchor], P[anchor], family)`
4. Check for **residue collisions** (multiple anchors forcing different K values at same residue)
5. Check for **illegal pass-through** (K=0 for Vigenère/Variant-Beaufort)
6. If feasible, check if all tail residues (75-96) are covered by forced key values
7. If tail forced, decrypt and record implied tail string

## Key Findings

### 1. Systematic Over-Constraint

**Result**: **All 3024 tested models are infeasible** due to anchor residue collisions.

**Root Cause**: With 24 anchor positions and practical periods L=2-22, multiple anchors inevitably map to the same key residue but require different key values, creating mathematical contradictions.

**Collision Analysis**:
```
Period L=10:  10 unique residues forced, 14 collisions among 24 anchors
Period L=16:  16 unique residues forced,  8 collisions among 24 anchors  
Period L=20:  13 unique residues forced, 11 collisions among 24 anchors
Period L=22:  15 unique residues forced,  9 collisions among 24 anchors
```

Even at the longest tested period (L=22), **persistent collisions prevent feasible solutions**.

### 2. Mathematical Impossibility Under Current Constraints

**Conclusion**: The anchors alone **mathematically over-constrain** all tested pencil-and-paper cipher models for the K4 ciphertext.

**Implication**: For anchor-locked decryption to be feasible, **additional degrees of freedom** are required beyond single-key Vigenère-family ciphers with NA-only permutations.

## Tested Parameter Space

- **Routes**: 4 anchor-fixing permutations (GRID, SPOKE, RAILFENCE families)
- **Cipher Families**: Vigenère, Beaufort, Variant-Beaufort  
- **Periods**: L = 2 through 22 (comprehensive pencil-and-paper range)
- **Phases**: All φ = 0 through L-1 for each period
- **Total Tests**: 3,024 model combinations
- **Feasible Models**: 0
- **Tail Forced Cases**: 0

## Decision Rule Applied

**Infeasibility Criteria**:
- **Residue collision**: Multiple anchors require different key values at same residue
- **Illegal pass-through**: K=0 at any residue for Vigenère/Variant-Beaufort families

**Forcing Criterion** (not reached):
- All tail positions 75-96 must have their required key residues covered by anchor-forced values

## Conclusion

**Primary Finding**: **Anchors alone do not force the K4 tail under minimal Sanborn constraints**.

The mathematical over-constraint demonstrates that **additional structural elements beyond anchors** are required for feasible solutions within pencil-and-paper cipher families. This suggests that:

1. **More complex cipher structures** may be needed (multi-key, irregular periods, etc.)
2. **Additional constraints** (head lock, seam structure) may be essential for mathematical feasibility
3. **The tail "OFANANGLEISTHEARC" is not forced by anchors alone** under these tested models

**Scope Limitation**: This analysis covers single-key Vigenère-family ciphers with periods L=2-22. Other cipher families or more complex key structures were not tested.

**Falsification Result**: The anchors-only hypothesis is **falsified** for the tested pencil-and-paper model space.