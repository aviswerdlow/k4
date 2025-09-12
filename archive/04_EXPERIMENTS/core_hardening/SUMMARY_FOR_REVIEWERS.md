# Core-Hardening Studies - Summary for Reviewers

## Headline Results

- **Skeleton Uniqueness**: **1/24** feasible (baseline only)
- **Tail Necessity**: **0/550** mutations feasible
- **Anchor Perturbations**: **0/27** feasible

## Method

All three studies use pure algebraic wheel solving with:
- No seam/tail guards anywhere in the logic
- Option-A strictly enforced (K≠0 at anchors for additive families)
- Pure family arithmetic (Vigenère, Beaufort, Variant-Beaufort)
- Deterministic execution with MASTER_SEED=1337

## Direct Links

### Study A - Skeleton Uniqueness
- [RESULTS.csv](skeleton_survey/RESULTS.csv) - 24 skeletons tested
- [Baseline Proof](skeleton_survey/PROOFS/skeleton_S0_BASELINE.json) - Only feasible solution
- [Analysis](skeleton_survey/README.md) - Detailed findings

### Study B - Tail Necessity
- [RESULTS.csv](tail_necessity/RESULTS.csv) - 550 mutations tested
- [Analysis](tail_necessity/README.md) - Zero feasible mutations

### Study C - Anchor Perturbations
- [RESULTS.csv](anchor_perturbations/RESULTS.csv) - 27 scenarios tested
- [Analysis](anchor_perturbations/README.md) - Zero feasible perturbations

## Quick Re-run

```bash
# Run all three studies
make core-harden

# Validate results against schemas
make core-harden-validate
```

## What This Proves

1. **The six-track classing scheme is unique** within the space of periodic patterns tested
2. **The tail is algebraically necessary**, not a post-hoc filter or assumption
3. **The anchor positions are exact**, with no tolerance for shifting

These results materially strengthen the claim that the published K4 solution represents the true, intended plaintext.