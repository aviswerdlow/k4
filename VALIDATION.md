# K4 GRID-only Uniqueness Validation Guide

Step-by-step instructions for external reviewers to reproduce and validate the GRID-only AND gate uniqueness result.

## Prerequisites

1. **Clone Repository**:
   ```bash
   git clone https://github.com/aviswerdlow/k4.git
   cd k4
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Repository Structure**:
   ```bash
   ls -la  # Should show: README.md, POLICY.json, VALIDATION.md, k4cli/, data/, results/, scripts/
   ```

## Step 1: Verify File Integrity

Check that all files match their expected SHA-256 hashes:

```bash
python scripts/make_manifest.py --check results/ results/MANIFEST.sha256
python scripts/make_manifest.py --check data/ data/MANIFEST.sha256
```

**Expected Result**: `✅ All files verified successfully` for both directories.

## Step 2: Validate the Winner (cand_005)

Run the complete confirmation pipeline on the winner:

```bash
k4 confirm \
  --ct data/ciphertext_97.txt \
  --pt results/GRID_ONLY/cand_005/plaintext_97.txt \
  --proof results/GRID_ONLY/cand_005/proof_digest.json \
  --perm data/permutations/GRID_W14_ROWS.json \
  --cuts data/canonical_cuts.json \
  --fwords data/function_words.txt \
  --calib data/calibration/calib_97_perplexity.json \
  --pos-trigrams data/calibration/pos_trigrams.json \
  --pos-threshold data/calibration/pos_threshold.txt \
  --policy POLICY.json \
  --out /tmp/k4_validate_cand_005
```

**Expected Results**:
- Rails Validation: All checks PASS (format, anchors, head_lock, seam_guard)
- Near Gate: Coverage ≥0.8, function words ≥6, has verb = true → PASS  
- Phrase Gate: Both Flint v2 AND Generic tracks → PASS
- AND Gate: accepted_by = ["flint_v2", "generic"] → PASS
- Overall: `✅ CANDIDATE CONFIRMED - ALL GATES PASSED`

**Validation Bundle**: Check generated files in `/tmp/k4_validate_cand_005/` match the reference bundle in `results/GRID_ONLY/cand_005/`.

## Step 3: Validate Tie-breaker Logic

Compare the winner against the runner-up using the GRID-only uniqueness validator:

```bash
k4 grid-unique \
  --winner results/GRID_ONLY/cand_005 \
  --runner-up results/GRID_ONLY/cand_004 \
  --summary results/GRID_ONLY/uniqueness_confirm_summary_GRID.json
```

**Expected Results**:
```
=== Tie-breaker Analysis ===
1. Holm adj_p_min: TIE (both ~9.999e-05)
2. Perplexity percentile: TIE (both 0.1%)  
3. Coverage (decisive): WINNER (0.923077 > 0.884615)

✅ UNIQUENESS CONFIRMED
Winner: cand_005 (GRID_W14_ROWS)
Decisive metric: Coverage (0.923077 vs 0.884615)
Method: Pre-registered tie-breakers under GRID-only restriction
```

## Step 4: Verify Bundle Integrity

Quick integrity check on the winner bundle:

```bash
k4 verify --bundle results/GRID_ONLY/cand_005 --policy POLICY.json
```

**Expected Results**:
- Required Files: PASS (all present)
- Rails Validation: PASS (format, anchors, head lock, seam)
- Policy Compliance: PASS (AND gate, tracks passed)  
- Encryption Check: PASS (PT encrypts to CT)
- Nulls Validation: PASS (p_cov < 0.01, p_fw < 0.01)
- Overall: `✅ BUNDLE VERIFICATION PASSED`

## Step 5: Generate Summary (Optional)

Regenerate the GRID-only uniqueness summary to verify consistency:

```bash
k4 summarize --grid-only \
  --winner results/GRID_ONLY/cand_005 \
  --runner-up results/GRID_ONLY/cand_004 \
  --output /tmp/uniqueness_summary_regenerated.json
```

Compare with the reference:
```bash
diff results/GRID_ONLY/uniqueness_confirm_summary_GRID.json /tmp/uniqueness_summary_regenerated.json
```

**Expected Result**: No differences (or only trivial formatting differences).

## Optional: Seam-Free Verification

You can independently confirm tail behavior without the seam guard:

```bash
python experiments/seam_free/scripts/seam_free_confirm.py \
  --ct data/ciphertext_97.txt \
  --pt results/GRID_ONLY/cand_005/plaintext_97.txt \
  --proof results/GRID_ONLY/cand_005/proof_digest.json \
  --perm data/permutations/GRID_W14_ROWS.json \
  --cuts data/canonical_cuts.json \
  --fwords data/function_words.txt \
  --calib data/calibration/calib_97_perplexity.json \
  --pos-trigrams data/calibration/pos_trigrams.json \
  --pos-threshold data/calibration/pos_threshold.txt \
  --policy experiments/seam_free/POLICY.seamfree.json \
  --out /tmp/k4_seamfree_cand_005
```

The tool writes a standard confirm bundle **plus** `tail_75_96.txt` (observed tail letters). See the seam-free summary table in:

```
experiments/seam_free/runs/20250903/FINAL_SUMMARY.md
```

## Acceptance Criteria

For validation to be considered successful, **ALL** of the following must be true:

### ✅ Core Validation
- [ ] File integrity checks pass (Step 1)
- [ ] Winner confirmation passes all gates (Step 2): rails, near-gate, phrase-gate (AND), nulls  
- [ ] `encrypts_to_ct: true` in coverage report
- [ ] `accepted_by: ["flint_v2", "generic"]` in phrase gate report
- [ ] Holm adjusted p-values < 0.01 for both coverage and f_words metrics

### ✅ Uniqueness Validation  
- [ ] Tie-breaker sequence operates correctly (Step 3)
- [ ] Coverage separates candidates: cand_005 (0.923) > cand_004 (0.885)
- [ ] Summary reports `"unique": true` and `"winner": "cand_005"`

### ✅ Technical Compliance
- [ ] Bundle verification passes (Step 4)
- [ ] SHA-256 hashes match expected values
- [ ] Permutation SHA matches: `a5260415e76509638b4845d5e707521126aca2d67b50177b3c94f8ccc4c56c31`
- [ ] Plaintext SHA matches: `595673454befe63b02053f311d1a966e3f08ce232d5d744d3afbc2ea04d3d769`

## Quick Sanity Checks

### Plaintext Verification
```bash
cat results/GRID_ONLY/cand_005/plaintext_97.txt
# Expected: WECANSEETHETEXTISCODEEASTNORTHEASTWESETTHECOURSETRUEREADTHENSEEBERLINCLOCKTHEJOYOFANANGLEISTHEARC
```

### Policy Verification  
```bash
grep -A 5 '"combine"' POLICY.json
# Expected: "combine": "AND"

grep -A 3 '"pos_threshold"' POLICY.json  
# Expected: "pos_threshold": 0.60
```

### Route Verification
```bash
grep '"route_id"' results/GRID_ONLY/cand_005/proof_digest.json
# Expected: "route_id": "GRID_W14_ROWS"
```

## Troubleshooting

**File Not Found Errors**: Ensure you're running from the repository root directory.

**Command Not Found (`k4`)**: Install the CLI with `pip install -e .` or use `python -m k4cli.cli` instead of `k4`.

**Hash Mismatches**: Repository may be corrupted or tampered with. Re-clone from GitHub.

**CLI Import Errors**: Ensure all dependencies are installed: `pip install -r requirements.txt`.

## Expected Runtime

- Step 1 (Hash verification): ~5 seconds
- Step 2 (Winner confirmation): ~10 seconds  
- Step 3 (Uniqueness validation): ~2 seconds
- Step 4 (Bundle verification): ~2 seconds
- Step 5 (Summary generation): ~3 seconds

**Total validation time**: Under 30 seconds on modern hardware.

## Conclusion

Upon successful completion of all validation steps, you will have independently verified:

1. **Mathematical Uniqueness**: cand_005 is the unique GRID-only AND gate winner
2. **Cryptographic Validity**: The solution satisfies all rail, gate, and null hypothesis requirements  
3. **Reproducible Evidence**: All results are deterministic and backed by SHA-256 integrity
4. **Audit Trail**: Complete provenance from input data to final uniqueness verdict

This constitutes a complete, independent validation of the K4 GRID-only uniqueness claim.