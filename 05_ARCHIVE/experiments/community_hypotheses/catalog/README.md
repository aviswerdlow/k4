# Community Hypothesis Catalog

This catalog contains curated community hypotheses for K4 decryption, organized by campaign.

## Campaign Structure

Each campaign (C1-C6) tests a specific decryption family through the Explore pipeline:

- **C1**: Quagmire III with scrambled alphabet
- **C2**: Trifid-by-rows & Eight-cube
- **C3**: Morse masking with 3/4-length code
- **C4**: Internal variant bigram & Row/column Polybius
- **C5**: Time-key schedules
- **C6**: Letter-shape classifier filter

## Catalog Organization

```
catalog/
├── README.md (this file)
├── campaign_C1_quagmire.json
├── campaign_C2_trifid_cube.json
├── campaign_C3_morse.json
├── campaign_C4_bigram_polybius.json
├── campaign_C5_time_key.json
└── campaign_C6_letter_shape.json
```

## Falsifiable Testing

All hypotheses are tested through the Explore pipeline with:
- Anchor modes (fixed, windowed, shuffled)
- Blinded scoring (no narrative leakage)
- Hard controls (matched n-gram distributions)
- Delta thresholds (δ₁ > 0.05, δ₂ > 0.10)

## Results

Campaign results are stored in `../runs/` with manifests, scores, and aggregated dashboards.