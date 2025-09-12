# Reproduction Steps - Sensitivity pos065_perp05 Rep2

```bash
python3 scripts/0457_fullbars/run_sensitivity_grid.py \
    --pos 0.65 \
    --perp 0.5 \
    --replicate 2 \
    --policy prereg/sensitivity/POLICY.pos065_perp05.json \
    --output sensitivity_strip/pos065_perp05/rep2
```

## Parameters
- POS threshold: 0.65
- Perplexity percentile: 0.5%
- Replicate: 2

## Results
- Near-gate: FAIL
- Phrase gate: FAIL
- Publishable: NO
