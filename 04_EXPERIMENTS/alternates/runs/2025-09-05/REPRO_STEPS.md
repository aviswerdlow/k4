# Reproduction Steps - Alternates Exploration

**Date**: 2025-09-05  
**Seed**: 1337 (deterministic across all runs)  
**Repository root**: `/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus`  

## Null Hypothesis Testing Parameters

- **Bootstrap nulls**: K=10,000
- **Correction**: Holm m=2  
- **Metrics**: coverage, f_words
- **Threshold**: adj-p < 0.01 for both metrics
- **Add-one correction**: Right-tail p-values
- **Per-worker seeding**: Deterministic derivation
  ```python
  seed_worker = lo64(SHA256(seed_recipe + "|" + label + "|worker:" + worker_id))
  rng = random.Random(seed_worker)
  ```

## 1. Within-Frame Analysis (GRID-only + AND)

Test surveying-equivalent imperatives within the published frame:

```bash
# Generate and test alternates
python3 experiments/alternates/scripts/scan_within_frame.py \
  --policy experiments/alternates/policies/POLICY.seamfree.and.json \
  --output_dir experiments/alternates/runs/2025-09-05/within_frame/ \
  --seed 1337
```

**Output structure**:
- `within_frame/candidates.txt` - Generated alternate heads  
- `within_frame/confirmations.json` - Gate and null test results
- `within_frame/ALTERNATES_SUMMARY.md` - Detailed summary
- `within_frame/within_frame.csv` - Tabular results
- `within_frame/MANIFEST.sha256` - File verification

## 2. Adjacent Frame Testing

Test frames outside the claim boundary:

```bash
# Test all frame variants
python3 experiments/alternates/scripts/run_frame_variant.py \
  --all \
  --output_dir experiments/alternates/runs/2025-09-05/ \
  --seed 1337

# Or test individual variants:
# AND + POS 0.80
python3 experiments/alternates/scripts/run_frame_variant.py \
  --variant pos080 \
  --output_dir experiments/alternates/runs/2025-09-05/ \
  --seed 1337

# Full deck + AND  
python3 experiments/alternates/scripts/run_frame_variant.py \
  --variant full_deck \
  --output_dir experiments/alternates/runs/2025-09-05/ \
  --seed 1337

# OR + strict Generic
python3 experiments/alternates/scripts/run_frame_variant.py \
  --variant or_strict \
  --output_dir experiments/alternates/runs/2025-09-05/ \
  --seed 1337
```

**Output per frame**:
- `{frame}/candidates.txt` - Generated candidates
- `{frame}/confirmations.json` - Results  
- `{frame}/SUMMARY.md` - Frame-specific summary
- `{frame}/MANIFEST.sha256` - Verification

## 3. Mini-Bundle Structure (if produced)

Each passing candidate would generate a mini-bundle mirroring the confirm bundle:
- `plaintext_97.txt` - Candidate plaintext
- `proof_digest.json` - Cryptographic parameters
- `phrase_gate_policy.json` - Gate configuration
- `phrase_gate_report.json` - Gate evaluation
- `near_gate_report.json` - Distance metrics
- `holm_report_canonical.json` - Null hypothesis results
- `coverage_report.json` - Coverage metrics with seeds
- `hashes.txt` - SHA-256 verification

## 4. Generate Manifests

```bash
# Create SHA-256 manifests for verification
python3 experiments/alternates/scripts/make_manifest.py \
  experiments/alternates/runs/2025-09-05/
```

## Expected Results

### Within-Frame
- Candidates generated: 10 (5 imperatives × 2 anchor positions)
- Passing gate: 0
- Passing nulls: 0
- **Conclusion**: No alternates within published frame

### Adjacent Frames  
| Frame | Gate Passes | Null Passes |
|-------|-------------|-------------|
| AND + POS 0.80 | 0 | 0 |
| Full deck + AND | 0 | 0 |
| OR + strict | 6 | 0 |

## Verification

All results include:
- Deterministic seed (1337)
- Policy SHA-256 hashes
- Ciphertext SHA: `eea813570c7f1fd3b34674e47b5c3da8948026f5cefee612a0b38ffaa515ceab`
- Calibration file hashes (placeholder_sha256 in policies)
- Per-worker seed derivation scheme