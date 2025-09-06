# Reproduction Steps - P74=U

```bash
python3 scripts/0457_fullbars/run_p74_strip.py U \
    --seed 1349525672 \
    --ct_sha eea813570c7f1fd3b34674e47b5c3da8948026f5cefee612a0b38ffaa515ceab \
    --policy prereg/POLICY.cadence.json \
    --output p74_strip/U
```

## Seed Recipe
```
CONFIRM_P74|K4|route:GRID_W14_ROWS|P74:U|ct:eea813570c7f1fd3b34674e47b5c3da8948026f5cefee612a0b38ffaa515ceab|cadence_policy:2161a32ee615f34823cb45b917bc51c6d4e0967fd5c2fb40829901adfbb4defc
```

## Results
- Schedule: FOUND
- Near-gate: FAIL
- Phrase gate: FAIL
- Publishable: NO
