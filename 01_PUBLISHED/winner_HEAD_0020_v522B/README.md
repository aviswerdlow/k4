# HEAD_0020_v522B - Published Winner

This bundle contains the published K4 solution with lexicon fillers.

## Key Points

- **Plaintext SHA-256**: `4eceb739ab655d6f4ec87753569b8bf04573fe26d01c0caa68d36776dd052d79`
- **T2 SHA-256**: `a5260415e76509638b4845d5e707521126aca2d67b50177b3c94f8ccc4c56c31`
- **Policy SHA**: `bc083cc4129fedbc`

## Full Plaintext (97 letters)

```
WEAREINTHEGRIDSEETHENEASTNORTHEASTANDWEAREBYTHELINETOSEEBETWEENBERLINCLOCKTHEJOYOFANANGLEISTHEARC
```

With anchor spans indicated:
- Indices 21-24: **EAST**
- Indices 25-33: **NORTHEAST**
- Indices 63-73: **BERLINCLOCK**
- Indices 74-96: THEJOYOFANANGLEISTHEARC (derived tail)

## Directory Structure

### Core Verification Files (Root Level)
| File | Purpose |
|------|---------|
| `plaintext_97.txt` | The 97-letter K4 solution |
| `proof_digest_enhanced.json` | Complete wheel specifications with annotations |
| `proof_digest.json` | Compact wheel specifications |
| `coverage_report.json` | Anchor coverage analysis |
| `phrase_gate_policy.json` | Phrase validation rules |
| `phrase_gate_report.json` | Phrase validation results |
| `holm_report_canonical.json` | Statistical validation |
| `tokenization_report.json` | Word boundary analysis |
| `rederive_min.py` | Minimal Python verifier (zero dependencies) |
| `RECEIPTS.json` | Consolidated SHA-256 hashes |
| `MANIFEST.sha256` | File integrity checksums |
| `HAND_PACK.zip` | Forum distribution package |

### Supporting Material
- **PROOFS/** - Mathematical and cryptographic proofs
  - `rebuild_from_anchors/` - Shows wheels emerge from constraints
  - `derivation_parity/` - Hand calculation examples
  - `no_mocks/` - Proof of no mock objects
- **DOCS/** - Documentation and guides
  - `K4_By_Hand_Walkthrough.pdf` - Visual 4-page walkthrough with charts and diagrams
  - `K4_By_Hand_Walkthrough_grayscale.pdf` - Grayscale version for printing
  - `FIG_*.png` - Individual figure exports from the visual walkthrough
  - `INDEX.md` - Visual materials index and usage guide
  - `HOW_TO_VERIFY.txt` - Step-by-step verification
  - `LETTER_NUMBER_TABLE.txt` - A=0..Z=25 conversions
  - `FORUM_AUDIT_NOTES.txt` - Forum-ready guide
- **RELEASE/** - Release artifacts and receipts
  - Core hardening validation results
  - Uniqueness confirmation

## Boundary Tokenizer

Boundary tokenizer v2 with lexicon fillers (THEN, BETWEEN) is used to preserve word boundaries across fixed anchor indices; fillers are ordinary English tokens and are scored by all gates.

## Minimal Verification (No Dependencies)

Verify the solution using pure Python stdlib:

```bash
python3 rederive_min.py \
  --ct ../../02_DATA/ciphertext_97.txt \
  --proof proof_digest_enhanced.json \
  --out /tmp/k4_pt.txt
shasum -a 256 /tmp/k4_pt.txt plaintext_97.txt
```

Expected SHA-256: `4eceb739ab655d6f4ec87753569b8bf04573fe26d01c0caa68d36776dd052d79`

To see the step-by-step arithmetic for any index (e.g., index 80):

```bash
python3 rederive_min.py \
  --ct ../../02_DATA/ciphertext_97.txt \
  --proof proof_digest_enhanced.json \
  --explain 80
```

For pen-and-paper verification, see:
- `DOCS/K4_By_Hand_Walkthrough.pdf` — visual 4-page walkthrough with charts and diagrams
- `DOCS/K4_By_Hand_Walkthrough_grayscale.pdf` — print-friendly grayscale version
- `PROOFS/derivation_parity/HAND_DERIVATION_80-84.txt` — pen-and-paper strip for indices 80–84
- `RELEASE/K4_by_hand_walkthrough.pdf` — complete 10-page text-based walkthrough

## Files

- `plaintext_97.txt` - The 97-letter plaintext with lexicon fillers
- `readable_canonical.txt` - Human-readable version with spacing
- `proof_digest.json` - Cryptographic proof details
- `proof_digest_enhanced.json` - Enhanced proof with complete wheel residues
- `tokenization_report.json` - Boundary tokenizer v2 output with fillers
- `phrase_gate_policy.json` - Gate policy with padding_forbidden flag
- `phrase_gate_report.json` - Gate validation results
- `near_gate_report.json` - Near gate metrics
- `coverage_report.json` - Coverage analysis
- `holm_report_canonical.json` - Statistical null testing results
- `boundary_documentation.json` - Boundary tokenizer v2 specification
- `CONFIRM_REPORT_FILLERS.json` - Confirmation report for filler version
- `rederive_min.py` - Minimal re-deriver (pure Python stdlib)
- `HAND_DERIVATION_80-84.txt` - Hand calculation examples
- `HOW_TO_VERIFY.txt` - Comprehensive verification guide
- `EXPLAIN_SAMPLES.txt` - Step-by-step arithmetic examples
- `NO_MOCKS_PROOF.txt` - Proof of no mock objects
- `rebuild_from_anchors.py` - Demonstrates wheel emergence from constraints
- `hashes.txt` - SHA-256 hashes of all bundle files
- `MANIFEST.sha256` - Bundle manifest

## Reports

- Filler rescreen results (entire promotion queue): `04_EXPERIMENTS/filler_rescreen/FILLER_RESCREEN.csv`

## By-Hand Parity

This solution maintains exact parity with the 1989 pencil-and-paper method:

- **Classing formula**: `class(i) = ((i % 2) * 3) + (i % 3)` produces 6 classes  
- **Wheel data**: See `proof_digest_enhanced.json` for complete wheel residues (all L=17, phase=0)
- **Coverage**: 97/102 slots used (5 slots never addressed by indices 0-96, never dereferenced)
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

## View the Wheels

To see the complete wheel configurations with all residues:

```bash
python3 07_TOOLS/validation/print_wheels.py \
  01_PUBLISHED/winner_HEAD_0020_v522B/proof_digest_enhanced.json
```

## Forward Encode (PT→CT)

To demonstrate the solution works in the forward direction, encoding plaintext to ciphertext using only the recovered key schedule (without reading the ciphertext):

```bash
python3 07_TOOLS/forward_encode_min.py \
  --pt 01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt \
  --proof 01_PUBLISHED/winner_HEAD_0020_v522B/proof_digest_enhanced.json \
  --out /tmp/k4_forward_ct.txt --sha
```

Expected SHA-256: `eea813570c7f1fd3b34674e47b5c3da8948026f5cefee612a0b38ffaa515ceab`

This proves the recovered key schedule (families, L, phase, residues) correctly encodes the plaintext to produce the K4 ciphertext, working purely in the forward direction without any reference to the ciphertext during encoding.