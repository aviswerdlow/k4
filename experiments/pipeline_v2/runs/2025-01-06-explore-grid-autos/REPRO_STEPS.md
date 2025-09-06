# Reproduction Steps: Grid Autos Campaign

## Environment
- Python 3.8+
- Seed: 1337
- Date: 2025-01-06

## Steps to Reproduce

1. **Setup**
```bash
cd experiments/pipeline_v2
git checkout pipeline-v2-grid-autos
```

2. **Run Campaign**
```bash
python3 scripts/explore/run_grid_autos.py \
  --seeds data/candidates_breadth.json \
  --policy policies/explore/POLICY.anchor_fixed.json \
  --baseline runs/2025-01-05-explore-breadth/baseline_stats.json \
  --output runs/2025-01-06-explore-grid-autos \
  --seed 1337
```

3. **Verify Results**
```bash
# Check preservation rate
grep "True" runs/2025-01-06-explore-grid-autos/ANCHOR_MODE_MATRIX.csv | wc -l
# Should output: 80

# Check promotions
jq '.promoted' runs/2025-01-06-explore-grid-autos/promotion_queue.json
# Should output: 0
```

4. **Generate Report**
Report is auto-generated as `EXPLORE_REPORT.md`

## Key Files
- Input: `data/candidates_breadth.json` (top 10 used)
- Policy: `policies/explore/POLICY.anchor_fixed.json`
- Baseline: `runs/2025-01-05-explore-breadth/baseline_stats.json`
- Script: `scripts/explore/run_grid_autos.py`

## Validation
- All transforms preserve anchor geometry (100%)
- No candidates pass delta thresholds
- Deterministic with seed 1337