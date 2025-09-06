# Ablation Analysis: WITHOUT_masking

## Configuration
- **Anchor Masking**: DISABLED
- **Expected Impact**: Nulls artificially strengthened

## Ablation Effect
Ablated null generation WITHOUT anchor masking

### Adjustments Applied
- Coverage adjustment: +0.050
- F-words adjustment: +1.0

## Results

### Gates
- Near-gate: FAIL
- Phrase gates: FAIL

### Null Hypothesis Testing
- Coverage adj-p: 1.000000
- F-words adj-p: 1.000000
- **Publishable**: NO

## Interpretation

With anchor masking DISABLED (ablation):
- Nulls can "see" the anchor positions during generation
- This gives them an unfair advantage in coverage and F-words
- If the candidate still wins, it suggests robustness
- If the candidate loses, it confirms the importance of masking

## Conclusion
This ablation run demonstrates the importance of anchor masking.
The candidate does not remain publishable under these conditions.
