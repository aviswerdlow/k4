# Reproduction Steps - Internal Push Program

**Date**: 2025-09-05  
**Global Seed**: 1337  
**Repository Root**: `/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus`

## 1. Boundary v2.1 Analysis (Report-Only)

Analyze the published winner with boundary-aware tokenization:

```bash
python3 experiments/internal_push/scripts/report_boundary_tie_break.py \
  --pt results/GRID_ONLY/cand_005/plaintext_97.txt \
  --cuts experiments/internal_push/data/canonical_cuts.json \
  --fwords experiments/internal_push/data/function_words.txt \
  --out experiments/internal_push/runs/2025-09-05/boundary_v21/winner/
```

**Result**: 
- v2 (decision): 0 function words in head
- v2.1 (report): 1 function word in head ('THE' from split 'THEJOY')
- Delta: +1 function word

**Important**: This v2.1 tokenization is **never** used in the AND gate or nulls; it's purely informational for tie-break reporting.

## 2. Irregular L Grid Search

Test blockwise two-period schedules:

```bash
# GRID_W14_ROWS with c6a
python3 experiments/internal_push/scripts/generate_irregular_grid.py \
  --route GRID_W14_ROWS \
  --classing c6a \
  --shells 1,2,3 \
  --max_lawful 50 \
  --seed 1337 \
  --out experiments/internal_push/runs/2025-09-05/irregular/GRID_W14_ROWS/c6a/

# For each lawful candidate (if any), run confirmation:
python3 experiments/internal_push/scripts/confirm_and_nulls.py \
  --policy experiments/internal_push/policies/POLICY.decision.and.json \
  --pt <plaintext_97.txt> \
  --proof_digest <proof_digest_irregular.json> \
  --out <fit_out_dir> \
  --seed 1337
```

**Stop Rules**:
- N=50 maximum lawful fits per shell
- M=10 maximum AND passers
- Stop on first publishable (adj-p < 0.01 for both metrics)

## 3. Community Alternates Intake

Validate external submissions:

```bash
# Example submission validation
python3 experiments/internal_push/scripts/intake_validate.py \
  --submission_dir experiments/internal_push/data/intake/example_submission/ \
  --policy experiments/internal_push/policies/POLICY.decision.and.json \
  --out_dir experiments/internal_push/runs/2025-09-05/intake/example/ \
  --seed 1337
```

**Pipeline**:
1. Rails validation (anchors, NA-only, Option-A)
2. Encryption verification
3. Phrase gate (AND) with tokenization v2
4. Nulls (10k, Holm m=2)

## 4. Nulls Mirroring Details

### Standard Schedule
```python
seed_recipe = "CONFIRM_AND|K4|route:<ROUTE>|classing:<C>|digest_sha:<SHA>"
seed_u64 = lo64(SHA256(seed_recipe))
seed_worker = lo64(SHA256(seed_recipe + "|" + label + "|worker:" + worker_id))
```

### Irregular Schedule
- Mirror exact block structure (B)
- Mirror per-block period assignments
- Mirror phase patterns
- Pin all anchor residue slots
- Randomize only free residues

## Expected Outputs

### Boundary v2.1
- `boundary_v21/winner/BOUNDARY_TIE_BREAK.md`
- `boundary_v21/winner/head_tokens_v2.json`
- `boundary_v21/winner/head_tokens_v21.json`
- `boundary_v21/winner/boundary_tie_break.json`

### Irregular Grid
- `irregular/IRREGULAR_SUMMARY.md`
- `irregular/IRREGULAR_SUMMARY.csv`
- Per-fit mini-bundles (if any publishable found)

### Intake
- `intake/INTAKE_RESULTS.csv`
- Per-submission mini-bundles
- `intake/<label>/INTAKE_RESULT.json`

## Verification

All calibration files referenced in policies should have SHA-256 hashes recorded.
All outputs include deterministic seeds for reproducibility.