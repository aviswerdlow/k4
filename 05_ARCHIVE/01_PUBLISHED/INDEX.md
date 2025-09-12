# 01_PUBLISHED Directory Index

## Start Here

→ [latest/README.md](latest/README.md) - The current winner bundle with complete verification instructions

## Bundles

### Winner Bundle
- **[winner_HEAD_0020_v522B/](winner_HEAD_0020_v522B/)** - The K4 solution with full verification artifacts
  - Plaintext: `WEAREINTHEGRIDSEETHENEASTNORTHEASTANDWEAREBYTHELINETOSEEBETWEENBERLINCLOCKTHEJOYOFANANGLEISTHEARC`
  - SHA-256: `4eceb739ab655d6f4ec87753569b8bf04573fe26d01c0caa68d36776dd052d79`

### Runner-Up Candidates
- **[runner_up_cand_004/](runner_up_cand_004/)** - Alternative solution candidate (historical)

### Previous Winners
- **[previous_winners/](previous_winners/)** - Earlier solution iterations and historical bundles

## What's in a Bundle

Each winner bundle contains:

### Core Verification Files (Root Level)
- `plaintext_97.txt` - The 97-letter solution
- `proof_digest.json` - Compact wheel specifications
- `proof_digest_enhanced.json` - Detailed wheel specs with annotations
- `coverage_report.json` - Anchor coverage analysis
- `phrase_gate_policy.json` - Phrase validation rules
- `phrase_gate_report.json` - Phrase validation results
- `holm_report_canonical.json` - Statistical validation
- `tokenization_report.json` - Word boundary analysis
- `rederive_min.py` - Minimal Python verifier (zero dependencies)
- `RECEIPTS.json` - Consolidated SHA-256 hashes
- `MANIFEST.sha256` - File integrity hashes
- `HAND_PACK.zip` - Forum distribution package

### Supporting Material (Subdirectories)

#### PROOFS/
Mathematical and cryptographic proofs:
- `rebuild_from_anchors/` - Shows wheels emerge from constraints
- `derivation_parity/` - Hand calculation examples
- `no_mocks/` - Proof of no mock objects in code

#### DOCS/
Documentation and guides:
- `HOW_TO_VERIFY.txt` - Step-by-step verification instructions
- `LETTER_NUMBER_TABLE.txt` - A=0..Z=25 conversion table
- `FORUM_AUDIT_NOTES.txt` - Forum-ready verification guide

#### RELEASE/
Release artifacts and receipts:
- `core_hardening_receipt.json` - Core hardening validation
- `core_hardening_v3_receipt.json` - Enhanced hardening results
- `uniqueness_confirm_summary_GRID.json` - Uniqueness validation

## Quick Verification

```bash
# Minimal verification (no setup required)
cd winner_HEAD_0020_v522B
python3 rederive_min.py \
  --ct ../../02_DATA/ciphertext_97.txt \
  --proof proof_digest_enhanced.json \
  --out result.txt

# Check SHA-256
shasum -a 256 result.txt
# Expected: 4eceb739ab655d6f4ec87753569b8bf04573fe26d01c0caa68d36776dd052d79
```

For complete instructions, see [latest/README.md](latest/README.md)