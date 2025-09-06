# Ablation Analysis: WITH_masking

## Configuration
- **Anchor Masking**: ENABLED
- **Expected Impact**: None (baseline)

## Ablation Effect
Standard null generation with anchor masking

### Adjustments Applied
- Coverage adjustment: +0.000
- F-words adjustment: +0.0

## Results

### Gates
- Near-gate: FAIL
- Phrase gates: FAIL

### Null Hypothesis Testing
- Coverage adj-p: 0.192981
- F-words adj-p: 1.000000
- **Publishable**: NO

## Interpretation

With anchor masking ENABLED (standard configuration):
- Nulls are generated without knowledge of anchor positions
- This ensures fair comparison and prevents leakage
- The observed metrics must genuinely outperform blind nulls

## Conclusion
This ablation run demonstrates the baseline behavior.
The candidate does not remain publishable under these conditions.
