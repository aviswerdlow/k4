# GRID Controls Reproduction Steps

## Command Used

```bash
python3 experiments/0457_exec/scripts/run_controls_digest.py
```

## Method

1. Used winner's verified proof_digest.json
2. Tested control phrases: MAP, TRUE, FACT
3. Identified exact fail points in pipeline
4. Created one-page summaries with fail analysis

## Expected Results

- MAP/TRUE/FACT: Fail at lawfulness or Flint
- Shows controls are properly rejected by validation
