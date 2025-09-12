# Reproduction Steps: Window Sweep

## Environment
- Python 3.8+
- Seed: 1337
- Date: 2025-09-05

## Steps

```bash
python3 scripts/explore/run_window_sweep.py \
  --candidates experiments/pipeline_v2/data/window_sweep_heads.json \
  --policies experiments/pipeline_v2/policies/explore_window \
  --baseline experiments/pipeline_v2/runs/2025-01-05-explore-breadth/baseline_stats.json \
  --output experiments/pipeline_v2/runs/2025-01-06-explore-window \
  --seed 1337
```
