# Confirm Phase Summary

## Winner: HEAD_147_B

Successfully passed all validation gates after 2 attempts.

### Validation Results

- **Near-Gate**: ✅ PASS (coverage=0.895, f_words=10, has_verb=true)
- **Phrase-Gate**: ✅ PASS (accepted by flint_v2 and generic)
- **Null Hypothesis**: ✅ PUBLISHABLE (adj_p_cov=0.0006, adj_p_fw=0.0005)
- **Schema Validation**: ✅ STRICT mode passed

### Plaintext Details

- Length: 97 characters
- Head window: [0:74]
- Anchors:
  - EAST: [21:25]
  - NORTHEAST: [25:34]
  - BERLINCLOCK: [63:74]

### Artifacts

- Bundle: `HEAD_147_B/`
- Manifest: `HEAD_147_B/MANIFEST.sha256`
- Frozen result: `../../results/GRID_ONLY/winner_HEAD_147_B/`

### Batch Processing

| Attempt | Head ID | Result | Reason |
|---------|---------|--------|--------|
| 1 | HEAD_135_B | ❌ FAIL | phrase_gate: content_words < 6 |
| 2 | HEAD_147_B | ✅ PASS | All gates passed |

See `CONFIRM_LEDGER.csv` for full details.
