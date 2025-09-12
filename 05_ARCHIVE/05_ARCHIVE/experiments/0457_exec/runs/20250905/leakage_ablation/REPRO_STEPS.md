# Leakage Ablation Reproduction Steps

## Command Used

```bash
python3 experiments/0457_exec/scripts/run_leakage_ablation.py
```

## Method

1. Run Generic scoring on winner head (normal)
2. Mask anchor positions [21-24], [25-33], [63-73]
3. Run Generic scoring with masked tokens excluded
4. Compare results to verify no anchor dependence

## Expected Result

Both masked and unmasked should pass, confirming no leakage.
