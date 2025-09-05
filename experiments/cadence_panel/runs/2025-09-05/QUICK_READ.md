Cadence panel (report-only). Winner > Runner across 6 sensitivity variants.

- Token windows (75 tokens): Winner CCS -1.552; Runner -1.942 → Δ=0.390
- Character windows (450 chars): Winner -4.195; Runner -4.420 → Δ=0.225
- Declarative reference (K2 coords removed): Winner -0.684; Runner -0.956 → Δ=0.272
- Bigram/Trigram-heavy: Winner -2.646; Runner -2.977 → Δ=0.331
- Rhythm-heavy: Winner -0.118; Runner -0.698 → Δ=0.580
- Uniform weights: Winner -0.894; Runner -1.393 → Δ=0.499

Interpretation:
- Ordering is robust to window choice and weights; Winner > Runner always.
- Character windows show the largest absolute divergence (more negative CCS).
- Declarative reference reduces divergence (coordinate block in K2 skews baselines).
- Panel is report-only; no gating/published result changed.
- Claim boundary applies (GRID-only + AND + nulls).