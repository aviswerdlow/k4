# P[74] Strip Reproduction Steps

## Command Used

```bash
python3 experiments/0457_exec/scripts/run_p74_digest.py
```

## Method

1. Used winner's verified proof_digest.json (fixed schedule)
2. For each letter A-Z, replaced P[74] with that letter
3. Ran confirm with publication policy
4. Recorded lawfulness (encrypts_to_ct) and gate results

## Expected Result

Only P[74]='T' should be lawful with winner's schedule.
Other letters fail lawfulness, confirming editorial choice.
