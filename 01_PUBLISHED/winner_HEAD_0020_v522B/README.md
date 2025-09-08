# HEAD_0020_v522B - Published Winner

This bundle contains the published K4 solution with lexicon fillers.

## Key Points

- **Plaintext SHA-256**: `4eceb739ab655d6f4ec87753569b8bf04573fe26d01c0caa68d36776dd052d79`
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

## By-Hand Parity

This solution maintains exact parity with the 1989 pencil-and-paper method:

- **Classing formula**: `class(i) = ((i % 2) * 3) + (i % 3)` produces 6 classes  
- **Wheel data**: See `proof_digest_enhanced.json` for complete wheel residues
- **No seam/tail guard**: The tail emerges at indices 74-96 from anchor-forced wheels
- **Tail derivation**: "THEJOYOFANANGLEISTHEARC" decoded cryptographically, not assumed

### Example: Decrypting Index 80 (in the tail)

```
Index: 80
Ciphertext: T (19)
Class: 2 (computed as ((80 % 2) * 3) + (80 % 3) = 2)
Family: beaufort
L: 17, Phase: 0
Slot: 12 (computed as (80 - 0) % 17 = 12)
K: 7 (H)
Decrypt rule: P = K - C = 7 - 19 = -12 ≡ 14 (mod 26)
Plaintext: O (14)
```

This character is part of "JOY" in the tail, which emerges naturally from the anchor-constrained wheels without any assumptions.

## Tail Verification (Derive, Don't Assume)

- This bundle **re-derives** all 97 letters from the ciphertext and the proof tuple (families/L/phase + forced anchor residues).
- The SHA of the derived plaintext equals the bundle plaintext (`pt_sha256_derived == pt_sha256_bundle` in coverage_report.json).
- The tail (74–96) is **decoded**, not assumed; `tail_derivation_verified: true`, and no tail guard is used in decryption (`no_tail_guard: true`).

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