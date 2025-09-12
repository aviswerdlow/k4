# Reproduction Steps

**Date:** 2025-09-05
**Seed:** 1337

```bash
# Generate heads
python3 scripts/explore/generate_heads_registers.py \
  --out experiments/pipeline_v2/data/heads_registers.json --seed 1337

# Run sweep
python3 scripts/explore/run_window_sweep_multi_route.py \
  --candidates experiments/pipeline_v2/data/heads_registers.json \
  --policies experiments/pipeline_v2/policies/explore_window \
  --baseline experiments/pipeline_v2/runs/2025-01-05-explore-breadth/baseline_stats.json \
  --routes GRID_W14_ROWS \
  --out experiments/pipeline_v2/runs/2025-01-06-explore-H \
  --seed 1337
```
