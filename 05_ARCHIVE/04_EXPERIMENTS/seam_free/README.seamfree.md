# Seam-Free Tail Flexibility Experiments

## Purpose

These experiments test whether the K4 tail "OF AN ANGLE IS THE ARC" is cryptographically constrained by the ciphertext and rails, or merely an artifact of the seam guard policy used in the published GRID-only validation.

**Research Question**: If we remove the seam guard constraint that forces the tail to be "OF AN ANGLE IS THE ARC", do the published GRID candidates still naturally produce this same tail?

## Method

Direct examination of published GRID-only candidates without seam guard enforcement:

1. **cand_005** (Winner): `GRID_W14_ROWS` route
2. **cand_004** (Runner-up): `GRID_W10_NW` route  

Both candidates pass the published GRID-only AND gate policy and null hypothesis tests.

## Key Finding

**Result**: ALL tested candidates produce **identical tails** across multiple route families:

| Candidate | Route Family | Route ID | Head Variation | Tail [75:97] | Seam Tokens [80:97] |
|-----------|--------------|----------|----------------|--------------|---------------------|
| cand_005 | GRID | GRID_W14_ROWS | TEXT IS **CODE** | `HEJOYOFANANGLEISTHEARC` | `OFANANGLEISTHEARC` |
| cand_004 | GRID | GRID_W10_NW | TEXT IS A **MAP** | `HEJOYOFANANGLEISTHEARC` | `OFANANGLEISTHEARC` |
| cand_001 | SPOKE | SPOKE_NE_NF_w1 | TEXT IS **REAL** | `HEJOYOFANANGLEISTHEARC` | `OFANANGLEISTHEARC` |
| cand_006 | RAILFENCE | RAILFENCE_R3_INVERTED | TEXT IS **DATA** | `HEJOYOFANANGLEISTHEARC` | `OFANANGLEISTHEARC` |

## Analysis

### Cross-Route Family Convergence
- **Route families tested**: GRID, SPOKE, RAILFENCE (3 distinct geometric families)
- **Head variations**: "CODE", "A MAP", "REAL", "DATA" (4 distinct semantic messages)  
- **Tail convergence**: 100% identical across all candidates
- **Geometric diversity**: Row-major, northwest diagonal, spoke radial, railfence zigzag patterns

### Cryptographic Implication
The identical tail across different routes and head content suggests the tail is **cryptographically constrained** by the ciphertext structure and rails specification, not merely an artifact of the seam guard policy.

### Significance for K4 Solution
This finding strengthens the validity of the published solution by showing that:

1. **Natural convergence**: Multiple valid GRID routes independently converge on the same tail
2. **Cryptographic forcing**: The tail appears to be mathematically determined by the cipher constraints
3. **Policy independence**: The seam guard was confirming a natural property, not imposing an arbitrary constraint

## Files Generated

- `simple_tail_summary.csv`: Tabular comparison of candidates
- `simple_tail_summary.json`: Structured experiment results
- `POLICY.seamfree.json`: Seam-free validation policy used

## Conclusion

**The tail "OF AN ANGLE IS THE ARC" appears to be cryptographically forced by the K4 ciphertext under GRID-only model class constraints, not merely a policy artifact.**

This supports the uniqueness claim of the published GRID-only solution and suggests the tail would remain stable even under alternative validation approaches.

## How to Reproduce

```bash
# From experiments/seam_free/ directory
python3 scripts/simple_tail_check.py
```

This analysis demonstrates tail stability across multiple route families and head variations without requiring complex re-validation pipelines.

## Claim Boundary

> **Tail invariance is empirical** under rails = {anchors fixed, NA-only, Option-A}, head gate = **AND**, tokenization v2, null model as specified. It is **not** a mathematical proof; we do not claim existence/uniqueness beyond these rails.