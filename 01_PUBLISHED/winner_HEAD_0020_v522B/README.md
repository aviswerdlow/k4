# HEAD_0020_v522B - Published Winner

This bundle contains the published K4 solution with lexicon fillers.

## Key Points

- **Plaintext SHA-256**: `e2c4daaff4f9ac567032c587085ac6a8290e10f153eb0b41814cfc6235ddc89e`
- **T2 SHA-256**: `a5260415e76509638b4845d5e707521126aca2d67b50177b3c94f8ccc4c56c31`
- **Policy SHA**: `bc083cc4129fedbc`

## Boundary Tokenizer

Boundary tokenizer v2 with lexicon fillers (THEN, BETWEEN) is used to preserve word boundaries across fixed anchor indices; fillers are ordinary English tokens and are scored by all gates.

## Files

- `plaintext_97.txt` - The 97-letter plaintext with lexicon fillers
- `readable_canonical.txt` - Human-readable version with spacing
- `proof_digest.json` - Cryptographic proof details
- `tokenization_report.json` - Boundary tokenizer v2 output with fillers
- `phrase_gate_policy.json` - Gate policy with padding_forbidden flag
- `phrase_gate_report.json` - Gate validation results
- `near_gate_report.json` - Near gate metrics
- `coverage_report.json` - Coverage analysis
- `holm_report_canonical.json` - Statistical null testing results
- `boundary_documentation.json` - Boundary tokenizer v2 specification
- `CONFIRM_REPORT_FILLERS.json` - Confirmation report for filler version
- `hashes.txt` - SHA-256 hashes of all bundle files
- `MANIFEST.sha256` - Bundle manifest

## Reports

- Filler rescreen results (entire promotion queue): `04_EXPERIMENTS/filler_rescreen/FILLER_RESCREEN.csv`

## Verification

```bash
k4 confirm \
  --ct 02_DATA/ciphertext_97.txt \
  --pt 01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt \
  --proof 01_PUBLISHED/winner_HEAD_0020_v522B/proof_digest.json \
  --perm 02_DATA/permutations/GRID_W14_ROWS.json \
  --cuts 02_DATA/canonical_cuts.json \
  --fwords 02_DATA/function_words.txt \
  --policy 01_PUBLISHED/winner_HEAD_0020_v522B/phrase_gate_policy.json \
  --out /tmp/k4_verify
```