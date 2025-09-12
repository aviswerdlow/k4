# Leakage Ablation Report

## Summary

This ablation tests whether the Generic track's pass is driven by anchor tokens 
leaking into the head scoring window. We mask tokens at anchor positions 
(EAST, NORTHEAST, BERLINCLOCK) and re-score the Generic track.

## Results

```json
{
  "generic_unmasked": {
    "perplexity_percentile": 0.8,
    "pos_score": 0.65,
    "pass": true
  },
  "generic_masked": {
    "perplexity_percentile": 0.9,
    "pos_score": 0.63,
    "pass": true
  },
  "mask_spans_0idx": [
    [
      21,
      24
    ],
    [
      25,
      33
    ],
    [
      63,
      73
    ]
  ],
  "accepted_by_and_gate": true,
  "notes": "Flint unchanged; nulls unchanged; decision policy unchanged."
}
```

## Conclusion

Unmasked Generic: PASS
Masked Generic: PASS

The Generic track performance is not dependent on anchor token leakage. 
Both masked and unmasked versions pass the thresholds, confirming that 
the head quality is intrinsic and not an artifact of anchor presence.