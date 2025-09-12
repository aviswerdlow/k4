# Reproduction Steps - Sensitivity pos055_perp15 Rep1

```bash
python3 scripts/0457_fullbars/run_sensitivity_grid.py \
    --pos 0.55 \
    --perp 1.5 \
    --replicate 1 \
    --policy prereg/sensitivity/POLICY.pos055_perp15.json \
    --output sensitivity_strip/pos055_perp15/rep1
```

## Parameters
- POS threshold: 0.55
- Perplexity percentile: 1.5%
- Replicate: 1

## Results
- Near-gate: FAIL
- Phrase gate: FAIL
- Publishable: NO
