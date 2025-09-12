# Reproducibility Steps - Explore v4.1.1

## Prerequisites

1. Pinned weights files:
   - v4.1: `policies/weights.explore_v4_1.json`
   - v4.1.1: `policies/weights.explore_v4_1_1.json`

2. SHA-256 verification:
   ```bash
   shasum -a 256 experiments/pipeline_v4/policies/weights.explore_v4_1_1.json
   # Expected: 457181035efbc666a0babc1c067d48f8c263862447280f21ef0cafd8988f83b6
   ```

## Step 1: Run A/B Pilot

```bash
cd experiments/pipeline_v4/scripts/v4.1
python3 run_ab_pilot_production.py
```

This will:
- Generate 50 heads with v4.1 weights (control)
- Generate 50 heads with v4.1.1 weights (treatment)
- Use MASTER_SEED=1337 for deterministic seeding
- Output to `runs/track_a_l/pilot/`

## Step 2: Check Pilot Results

The pilot will automatically check against pre-registered thresholds:
- Head-gate pass rate (B) ≥ 80%
- Delta pass rate (B) ≥ 25%
- Leakage = 0.000
- Clear improvement over control

Decision rules:
- ✅ All thresholds met → Proceed to K=200
- ⚠️ Delta marginal (20-24%) → Proceed but require ≥10 delta survivors
- ❌ Thresholds failed → STOP, mark v4.1.1 as SATURATED

## Step 3: Run K=200 Production (if pilot passes)

```bash
cd experiments/pipeline_v4/scripts/v4.1
python3 run_explore_v4_1_1_production.py
```

This will:
- Check pilot passed before proceeding
- Generate 200 heads with v4.1.1 weights
- Run full Explore pipeline (placement → repair → head-gate → deltas)
- Run orbit isolation (ε_tie ≤ 0.15)
- Run fast nulls (K=1000, Holm m=2)
- Output to `runs/track_a_l/batch_200_v4_1_1/`

## Integration Points

The production scripts need connection to your actual pipeline at these points:

1. **run_generation_pipeline()** - Call your verb_robust_mcmc.py with weights file
2. **run_orbit_isolation()** - Implement orbit detection logic
3. **run_fast_nulls()** - Implement null hypothesis testing

## Verification

All runs produce:
- `EXPLORE_MATRIX.csv` - Full metrics for all heads
- `DASHBOARD.csv` - Summary statistics
- `promotion_queue.json` - Surviving heads for Confirm phase
- `EXPLORE_REPORT.md` - Complete analysis report
- `MANIFEST.sha256` - File hashes for verification

## Exact Parameters

```python
# Weights v4.1.1
{
  "lambda_ng": 1.0,
  "lambda_fw": 0.8,        # KEY CHANGE from 0.4
  "lambda_cov": 0.2,
  "lambda_pattern": 0.8,
  "lambda_verb": 1.2,
  "lambda_fw_cap": 0.2,     # Adjusted from 0.4
  "lambda_fratio": 0.3      # Adjusted from 0.5
}

# Thresholds
HEAD_GATE = {
  "fw_min": 0.35,
  "verb_min": 3,
  "cov_min": 0.70,
  "pattern_min": 0.60
}
DELTA_THRESHOLD = 0.15
SHUFFLED_THRESHOLD = 0.12
ORBIT_EPSILON = 0.15
NULL_K = 1000
NULL_ALPHA = 0.01 (Holm m=2)

# Seeds
MASTER_SEED = 1337
Per-head seeds derived: SHA256(f"{MASTER_SEED}:{head_id}")[:16] % 2^32
```