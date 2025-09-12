# Fork H - Segmented & Dynamic Polyalphabetic Testing Report

**Date**: 2025-09-10  
**MASTER_SEED**: 1337  
**Focus**: Position-preserving polyalphabetic approaches

## Executive Summary

Fork H implemented segmented polyalphabetic testing to address the position-preservation requirement that Fork G methods (DT, Playfair) couldn't satisfy. Initial H1 testing reveals fundamental conflicts between segmented periods and the anchor constraints.

## H1: Segmented Period Lengths

### Implementation
- **Segments**: Head (0-20), Anchors (21-73), Tail (74-96)
- **Period ranges**: L∈[2,30] with prioritized values
- **Families**: Vigenère, Beaufort, Variant-Beaufort
- **Named combos tested**:
  - Boundary-aligned: L=(21,53,23)
  - Community set: L=(14,17,7)
  - Progressive: L=(7,14,21)
  - Baseline: L=(11,11,11) and L=(17,17,17)

### Results
- **Boundary-aligned**: Only config that didn't fail, but produced 73 unknowns (no improvement)
- **All others**: Key conflicts at anchor boundaries
- **Root cause**: Anchors span segment boundaries, requiring consistent keys across segments

### Key Conflict Analysis

The anchor "NORTHEAST" (positions 25-33) illustrates the problem:
- In Head segment (0-20): Not present
- In Anchors segment (21-73): Positions 25-33
- If L_anchors=17, positions 25-33 use slots 4-12
- If "NORTHEAST" requires specific keys at those slots, they propagate
- But those same slots repeat elsewhere in the segment
- This creates conflicts when different plaintext is needed at other positions using the same slots

## Critical Discovery

**Segmented periods with different L values per segment are incompatible with anchors that span positions 21-73.**

The anchors create a "key pinning" effect:
1. EAST (21-24) pins 4 key slots
2. NORTHEAST (25-33) pins 9 more slots
3. BERLIN (63-68) and CLOCK (69-73) pin additional slots
4. With L=17 in the anchor region, most slots get pinned
5. This leaves no flexibility for deriving other plaintext

## Why This Matters

### Comparison with Previous Forks

| Fork | Method | Position Preservation | Anchor Compatibility | IC/Statistics |
|------|--------|----------------------|---------------------|---------------|
| F (L=11) | Uniform polyalphabetic | ✓ | ✓ | Weak (0.044) |
| G (L=14 DT) | Double transposition | ✗ | ✗ | Strong (0.0898) |
| G (Playfair) | Matrix digraph | ✗ | ✗ | N/A |
| H1 (Segmented) | Variable periods | ✓ | ✗ (conflicts) | N/A |

### The Fundamental Trade-off

We're discovering that K4 has contradictory requirements:
1. **Statistical signals** (IC) point to L=14 with transposition
2. **Known anchors** require position preservation
3. **Polyalphabetic** preserves positions but has weak statistics at useful periods
4. **Segmentation** creates key conflicts with the anchors

## Recommendations for H2-H4

### H2: Key Changes at Boundaries
- **Adjust approach**: Instead of different L per segment, use same L but different keys
- **Zone boundaries**: Break at each anchor boundary, not arbitrary segments
- **Key rotation**: Test progressive key modifications between zones

### H3: Running Key from K1-K3
- **Most promising**: Doesn't require periodic repetition
- **No key conflicts**: Each position gets unique key material
- **Preserves positions**: Standard polyalphabetic application

### H4: Visual Parameters
- **Use for key selection**: Not period selection
- **Berlin Clock times**: Map to key offsets, not L values

## Hypothesis Ranking

Based on initial testing:
1. **H3 (Running key)**: Most likely to succeed - avoids periodic conflicts
2. **H2 (Boundary keys)**: Possible if zones align with anchors
3. **H4 (Visual params)**: Supplementary to other methods
4. **H1 (Segmented L)**: Fundamentally flawed with current anchor positions

## Files Delivered

```
fork_h/
├── utils_h.py           # Shared utilities, cipher families
├── h1_segmented.py      # Segmented period implementation
├── h1_results.json      # Empty (no successful configs)
└── FORK_H_REPORT.md     # This report
```

## Next Steps

1. **Abandon H1** segmented periods - fundamental incompatibility
2. **Prioritize H3** running key - most promising approach
3. **Adjust H2** to use zones that respect anchor boundaries
4. **Consider non-periodic** approaches that avoid key slot conflicts

## Conclusion

Fork H has revealed that the anchor positions create severe constraints on any periodic cipher system. The four anchors effectively "use up" most key slots in any reasonable period length, leaving insufficient degrees of freedom for the remaining plaintext.

This suggests K4 either:
1. Uses a non-periodic system (like running key)
2. Has keys that change at specific boundaries
3. Employs a completely different cipher type
4. The anchors aren't plaintext at those positions (despite being confirmed)

The community's 20+ years of failure with periodic approaches now makes more sense - the anchors create an over-constrained system for any simple periodic cipher.

---

*Analysis performed with MASTER_SEED=1337*  
*No language models or semantics used*  
*Pure mechanical cryptanalysis*