# Sensitivity Strip Reproduction Steps

## Commands Used

```bash
python3 experiments/0457_exec/scripts/run_sensitivity_digest.py
```

## Method

1. Used winner's verified proof_digest.json (GRID_W14_ROWS)
2. Fixed key schedules from winner's confirmation
3. Varied only the policy thresholds (POS and perplexity)
4. Ran 3 nulls replicates per cell (deterministic reseeding)

## Policy Parameters

| Policy | POS | Perplexity % |
|--------|-----|-------------|
| pos055_pp15 | 0.055 | 1.5% |
| pos055_pp10 | 0.055 | 1.0% |
| pos055_pp05 | 0.055 | 0.5% |
| pos060_pp15 | 0.060 | 1.5% |
| pos060_pp10 | 0.060 | 1.0% |
| pos060_pp05 | 0.060 | 0.5% |
| pos065_pp15 | 0.065 | 1.5% |
| pos065_pp10 | 0.065 | 1.0% |
| pos065_pp05 | 0.065 | 0.5% |
