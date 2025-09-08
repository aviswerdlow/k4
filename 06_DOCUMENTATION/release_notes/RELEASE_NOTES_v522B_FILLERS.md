# Release: HEAD_0020_v522B with Lexicon Fillers

**Tag**: `confirm-HEAD_0020_v522B-fillers-20250107`  
**Date**: January 7, 2025

## Summary

Published K4 solution with clean English presentation. Visual scaffolding (XXXX/YYYYYYY) replaced with lexicon fillers (THEN/BETWEEN) while preserving all cryptographic invariants.

## Key Changes

- **Boundary Tokenizer v2**: Lexicon fillers preserve word boundaries at fixed anchor indices
- **Padding Forbidden**: No padding tokens in published bundles (enforced by CI)
- **Clean English Head**: `WE ARE IN THE GRID SEE THEN EAST NORTHEAST AND WE ARE BY THE LINE TO SEE BETWEEN BERLINCLOCK`

## Receipts

| Field | Value |
|-------|-------|
| **PT SHA-256** | `e2c4daaff4f9ac567032c587085ac6a8290e10f153eb0b41814cfc6235ddc89e` |
| **T2 SHA-256** | `a5260415e76509638b4845d5e707521126aca2d67b50177b3c94f8ccc4c56c31` |
| **Policy SHA** | `bc083cc4129fedbc` |
| **Pre-reg Commit** | `d0b03f4` |

## Verification

```bash
# One-command verification
k4 confirm \
  --ct 02_DATA/ciphertext_97.txt \
  --pt 01_PUBLISHED/latest/plaintext_97.txt \
  --proof 01_PUBLISHED/latest/proof_digest.json \
  --perm 02_DATA/permutations/GRID_W14_ROWS.json \
  --cuts 02_DATA/constraints/canonical_cuts.json \
  --policy 01_PUBLISHED/latest/phrase_gate_policy.json \
  --out /tmp/k4_verify

# Bundle validation
python 07_TOOLS/validation/validate_bundle.py 01_PUBLISHED/latest --mode strict

# Padding check
python tests/test_no_padding_in_published.py
```

## Promotion Queue Rescreen

Full v5.2.2-B promotion queue (67 candidates) rescreened with fillers:
- **Unchanged**: 64 (95.5%)
- **Improved**: 3 (4.5%)
- **Degraded**: 0 (0%)

See: `04_EXPERIMENTS/filler_rescreen/FILLER_RESCREEN.csv`

## Bundle Contents

- `01_PUBLISHED/winner_HEAD_0020_v522B/` - Complete winner bundle
- `01_PUBLISHED/winner_HEAD_0020_v522B/RECEIPTS.json` - Single-source verification
- `01_PUBLISHED/uniqueness_confirm_summary_GRID.json` - Uniqueness analysis
- `01_PUBLISHED/previous_winners/HEAD_0020_v522B_padding_sentinel/` - Archived sentinel version

## CI/Validation

- ✅ **Bundle**: Strict mode passing
- ✅ **Padding**: Forbidden and enforced
- ✅ **Tests**: All validation passing
- ✅ **Hashes**: All files signed

## Notes

Boundary tokenizer v2 with lexicon fillers (THEN, BETWEEN) preserves word boundaries at fixed anchor indices. Fillers are ordinary English tokens scored by all gates (near-gate, phrase, cadence, context). No padding tokens present in published bundles.

---

**Repository**: https://github.com/aviswerdlow/k4  
**Commit**: `5da50c4`