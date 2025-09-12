# Community Alternates Intake Protocol

## Submission Requirements

A valid submission must contain the following files in a single directory:

### 1. plaintext_97.txt
- **Format**: Uppercase A-Z only
- **Length**: Exactly 97 characters
- **Encoding**: ASCII/UTF-8

### 2. proof_digest.json
Required fields:
```json
{
  "route_id": "GRID_W14_ROWS",
  "t2_sha256": "sha256_of_permutation",
  "classing": "c6a",
  "per_class": [
    {
      "class_id": 0,
      "family": "vigenere",
      "L": 14,
      "phase": 0
    },
    // ... entries for classes 1-5
  ],
  "forced_anchor_residues": [
    {
      "i": 21,
      "class_id": 3,
      "residue_index": 7,
      "family": "vigenere",
      "K": 15
    }
    // ... additional anchor constraints
  ],
  "seed_recipe": "optional_seed_string",
  "seed_u64": 1337
}
```

### Field Descriptions

- **route_id**: Must be a valid route (e.g., GRID_W14_ROWS, GRID_W10_NW)
- **t2_sha256**: SHA-256 hash of the T₂ permutation used
- **classing**: Either "c6a" or "c6b"
- **per_class**: Array of 6 objects defining cipher parameters per class
  - **family**: One of "vigenere", "variant_beaufort", "beaufort"
  - **L**: Period length (typically 10-22)
  - **phase**: Phase offset (0 to L-1)
- **forced_anchor_residues**: Optional list of anchor constraints (we recompute if omitted)

## Rails Guarantee

All submissions must satisfy:

1. **Anchors plaintext at 0-idx**:
   - EAST: positions 21-24
   - NORTHEAST: positions 25-33
   - BERLINCLOCK: positions 63-73

2. **NA-only permutation**: Permutation must fix anchor indices

3. **Option-A at anchors**:
   - No illegal pass-through for Vigenere/Variant-Beaufort (K≠0)
   - No residue collisions within class
   - Beaufort allows K=0

## Validation Process

1. **Rails validation**: Check anchor constraints and Option-A
2. **Encryption verification**: Confirm plaintext encrypts to expected ciphertext
3. **Phrase gate (AND)**: Apply Flint v2 and Generic criteria to head window [0,74]
4. **Null hypothesis testing**: 10,000 bootstrap nulls with Holm correction (m=2)

## Output

Successful validation produces:
- Mini-bundle with all confirmation artifacts
- INTAKE_RESULT.json with pass/fail status
- Entry in INTAKE_RESULTS.csv

Failed validation produces:
- Error report (rails_fail.json or encrypt_mismatch.json)
- Diagnostic information for debugging

## Example Directory Structure

```
submission_example/
├── plaintext_97.txt
└── proof_digest.json
```

## Testing Your Submission

```bash
python3 experiments/internal_push/scripts/intake_validate.py \
  --submission_dir path/to/your/submission \
  --policy experiments/internal_push/policies/POLICY.decision.and.json \
  --out_dir experiments/internal_push/runs/test/ \
  --seed 1337
```