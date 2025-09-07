# Stylistic Note

This plaintext formally passes all registered cryptographic and statistical gates within the GRID-only + AND + nulls frame:
- Lawfulness: Valid GRID_W14_ROWS encryption
- Near-gate: coverage=0.895, f_words=10, has_verb=true  
- Phrase-gate: Passed both Flint v2 and Generic tracks
- Null hypothesis: Publishable (adj_p < 0.01 for both metrics)

However, the text reads as unnatural prose with function-word clustering:

```
ON THEN READ THE THIS AND A EAST NORTHEAST THERE THE WOULD AS 
OUR THIS YOUR WHE BERLIN CLOCK ERE THAT BE THEM THE FOLLOW WI
```

## Cadence Metrics (Report-Only)

The stylistic analysis shows significant deviation from natural English patterns:
- Cosine similarity (bigram): 0.42 (threshold ≥0.65)
- Cosine similarity (trigram): 0.38 (threshold ≥0.60)
- Function-word rhythm: High clustering
- Word-length χ²: 145.2 (threshold ≤95)
- Vowel-consonant ratio: 0.89 (normal band: 0.95-1.15)
- Repeated "THE": 4 occurrences in 74 chars

These metrics are provided for transparency. Cadence was kept report-only for this publication per pre-registration, not used as a gate. Future iterations may promote style checks to hard requirements.

## Flint v2 Evidence Details

While Flint v2 passed, the evidence comes from sparse pattern matches:
- Declination expressions: "READ" [7:11], "FOLLOW" [94:100]
- Instrument verb: "READ" [7:11]  
- Directions: "EAST" [25:29], "NORTHEAST" [29:38]
- Instrument noun: "CLOCK" [68:73]

Note: No coherent phrase like "SET THE COURSE TRUE" or navigational sentence structure. The tokens satisfy requirements but lack semantic coherence.
