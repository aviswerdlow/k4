# Reproduction Steps - Sensitivity pos065_perp10 Rep3

```bash
python3 scripts/0457_fullbars/run_sensitivity_grid.py \
    --pos 0.65 \
    --perp 1.0 \
    --replicate 3 \
    --policy prereg/sensitivity/POLICY.pos065_perp10.json \
    --output sensitivity_strip/pos065_perp10/rep3
```

## Parameters
- POS threshold: 0.65
- Perplexity percentile: 1.0%
- Replicate: 3

## Results
- Near-gate: FAIL
- Phrase gate: FAIL
- Publishable: NO
