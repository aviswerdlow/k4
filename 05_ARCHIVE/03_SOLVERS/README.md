# 03_SOLVERS - Pipeline Code

This directory contains the solver pipelines that led to the successful K4 solution.

## Active Pipelines

### v5_2_2_B (Winner)
The pipeline that produced HEAD_0020_v522B - our winning solution.
- Boundary tokenizer v2
- Gap composer v2 with per-gap quotas
- Micro-repair capability
- 100% post-anchor pass rate achieved

### v5_2_1
Content+function harmonization attempt.
- Function-rich templates
- Resulted in anchor collisions

### v5_2
The saturated version that identified the content-function paradox.
- All candidates failed near-gate
- Led to the boundary tokenizer innovation

## Key Scripts

### Production Scripts
- `v5_2_2_B/scripts/run_explore_v5_2_2B_production.py` - K=200 production run
- `v5_2_2_B/scripts/run_confirm_v522B.py` - Confirmation script

### Core Components
- `v5_2_2_B/scripts/boundary_tokenizer_v2.py` - Virtual boundary system
- `v5_2_2_B/scripts/gap_composer_v2.py` - Per-gap quota enforcement
- `v5_2_2_B/scripts/gap_aware_generator.py` - Collision-free generation

## Usage

To reproduce the winning solution:
```bash
cd 03_SOLVERS/v5_2_2_B
python scripts/run_explore_v5_2_2B_production.py
```

To confirm a candidate:
```bash
python scripts/run_confirm_v522B.py --candidate HEAD_0020_v522B
```
