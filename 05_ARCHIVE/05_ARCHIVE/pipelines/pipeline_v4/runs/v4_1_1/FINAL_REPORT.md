# v4.1.1 Exploration and Confirm Report

## Summary

The v4.1.1 exploration with diversified weights successfully broke through the saturation observed in the fw=0.4 run.

### Key Results

1. **Pilot Phase**: 50 A/B heads generated and validated
   - Path: `experiments/pipeline_v4/runs/v4_1_1/pilot/`
   - Files: HEAD_GATE_MATRIX.csv, PILOT_REPORT.md

2. **K=200 Production**: 200 heads generated, ALL passed exploration gates
   - Path: `experiments/pipeline_v4/runs/v4_1_1/k200/`
   - Dashboard: 200/200 passed all gates (100% success rate)
   - Promotion queue: 200 candidates available for Confirm

3. **Confirm Phase**: Initiated with deterministic selection
   - Selected: HEAD_135_B (top ranked by 8-part key)
   - Status: Failed near-gate (f_words=9, needs 10)
   - Next candidate: HEAD_66_B ready for testing

### Weight Distributions (K=200)

Function word weights (fw_post):
- fw=9: 2 heads
- fw=10: 4 heads
- fw=11: 8 heads
- fw=12: 10 heads
- fw=13: 16 heads
- fw=14: 22 heads
- fw=15: 26 heads
- fw=16: 24 heads
- fw=17: 22 heads
- fw=18: 20 heads
- fw=19: 18 heads
- fw=20: 16 heads
- fw=21: 12 heads

Verb weights:
- verb=2: 134 heads
- verb=3: 66 heads

### Files Generated

#### Exploration
- `EXPLORE_MATRIX.csv` - Raw results for all 200 heads
- `DASHBOARD.csv` - Funnel summary statistics
- `promotion_queue.json` - 200 candidates with metrics
- `MANIFEST.sha256` - Complete file hashes
- `README.md` - Quick start guide

#### Confirm (partial)
- `CONFIRM_SELECTION.json` - Deterministic selection algorithm
- `runs/confirm/HEAD_135_B/` - First attempt (failed near-gate)
- `runs/confirm/rejects.json` - Rejection log

### Validation Status

✅ Pilot batch validates against schemas
✅ K=200 batch validates against schemas
✅ CI remains green (pytest -q passes)
✅ Manifest complete with 202 files

### Next Steps

1. Continue Confirm testing with HEAD_66_B
2. Iterate through ranked candidates until one passes all gates
3. Complete full Confirm bundle with lawfulness proof and null testing

## Comparison to Saturated Run

The previous fw=0.4 run resulted in complete saturation (0 promoted heads).
This v4.1.1 run with diversified weights (fw 9-21, verb 2-3) successfully
generated 200 viable candidates, demonstrating the value of the weight
exploration strategy.

## Technical Notes

- Weights SHA-256: d2b426b77c965c3ecd804c8d25c48ab45f0635db18275f68827cd48fa0d98be0
- Commit: 6f65f3a (main branch)
- Rails: GRID-only
- Gates: Near (head-only) + Phrase (AND: flint_v2 + generic)
- Nulls: 10,000 mirrored with Holm m=2 correction