# Reproduction Steps - Sensitivity pos055_perp10 Rep3

```bash
python3 scripts/0457_fullbars/run_sensitivity_grid.py \
    --pos 0.55 \
    --perp 1.0 \
    --replicate 3 \
    --policy prereg/sensitivity/POLICY.pos055_perp10.json \
    --output sensitivity_strip/pos055_perp10/rep3
```

## Parameters
- POS threshold: 0.55
- Perplexity percentile: 1.0%
- Replicate: 3

## Results
- Near-gate: FAIL
- Phrase gate: FAIL
- Publishable: NO
