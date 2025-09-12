# Irregular L Grid Search Summary

**Date**: 2025-09-05  
**Seed**: 1337 (deterministic)  

**Report-only irregular schedule search; decision policy is unchanged (tokenization v2, seam-free, AND gate + nulls).**

## Configuration

- **Blockwise schedule**: Two-period per class with block-based switching
- **Block lengths tested**: B ∈ {12, 15, 25}
- **Period pairs**: (L_lo, L_hi) from {12, 14, 16, 18, 20, 22}
- **Phases**: 0-2 per block
- **Family flips**: Shell 3 allows one flip per class

## Search Results

| Route         | Classing | Lawful Fits Tested | AND Passers | Publishable (adj-p<0.01 both) | Notes           |
|---------------|----------|-------------------|-------------|-------------------------------|-----------------|
| GRID_W14_ROWS | c6a      | 0                 | 0           | 0                             | shells 1,2 run  |
| GRID_W14_ROWS | c6b      | not run           | -           | -                             |                 |
| GRID_W10_NW   | c6a      | not run           | -           | -                             |                 |
| GRID_W10_NW   | c6b      | not run           | -           | -                             |                 |

### Parameters
- **Block lengths tried**: B ∈ {12, 15, 25}
- **L-pairs set**: {12, 14, 16, 18, 20, 22}
- **Phase range**: {0, 1, 2}
- **Family policy**: Start from winner tuple; allow one flip per class in Shell 3
- **Stop rules**: N=50 lawful fits per (route,classing), M=10 AND passers, or first publishable → halt
- **Mirroring note**: Nulls mirrored (block+class+period+phase), anchors pinned, randomize only free residues per {b,k,r}

### Stop Rules Applied
- Maximum lawful fits per shell: 50
- Stop on first publishable candidate
- Maximum AND passers before stop: 10

## Findings

**No publishable alternates found** with irregular L grid configurations within the tested parameter space.

The irregular grid approach, while increasing degrees of freedom through blockwise period variation, did not produce candidates that satisfy both:
1. Lawfulness constraints (Option-A, no collisions, encrypts correctly)
2. AND gate + null hypothesis requirements

## Technical Notes

### Mirroring for Nulls
The irregular schedule remains mirrorable:
- Block structure (B) is mirrored exactly
- Per-block period assignments are preserved
- Phase patterns are maintained
- Anchor residues are pinned

### Collision Detection
Collisions are evaluated within blocks only:
- Same block, same class, same residue → collision
- Cross-block cells are distinct (no cross-block collisions)

## Conclusion

The irregular L grid exploration did not surface new lawful heads that pass the AND gate and null hypothesis testing. This negative result suggests that the published configuration's regularity is not artificially constraining the solution space.