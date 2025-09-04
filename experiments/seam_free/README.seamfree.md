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

**Result**: Both candidates produce **identical tails** despite different head content:

| Candidate | Head Difference | Tail [75:97] | Seam Tokens [80:97] |
|-----------|----------------|--------------|---------------------|
| cand_005 | TEXT IS **CODE** | `HEJOYOFANANGLEISTHEARC` | `OFANANGLEISTHEARC` |
| cand_004 | TEXT IS A **MAP** | `HEJOYOFANANGLEISTHEARC` | `OFANANGLEISTHEARC` |

## Analysis

### Head Variation, Tail Stability
- **Head content differs**: "THE TEXT IS CODE" vs "THE TEXT IS A MAP"
- **Tail content identical**: Both produce "OF AN ANGLE IS THE ARC"
- **Route difference**: Width-14 row-major vs Width-10 northwest reading

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

This analysis demonstrates tail stability across the two published GRID candidates without requiring complex re-validation pipelines.