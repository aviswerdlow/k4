# How to Verify K4 Solution

This document explains how to independently verify a K4 solution candidate.

## Prerequisites

- Python 3.7 or higher
- Basic command line knowledge
- This repository cloned locally

## Quick Verification (5 minutes)

```bash
# 1. Navigate to repository root
cd k4_cli_plus

# 2. Verify round-trip with provided manifest
make verify-rt MANIFEST=01_PUBLISHED/candidates/zone_mask_v1_<tag>/manifest.json

# 3. Check output for:
#    ✅ VERIFICATION SUCCESSFUL
#    ✓ All checks passed!
```

## Detailed Verification Steps

### Step 1: Verify Round-Trip

The solution must encrypt back to the exact original ciphertext:

```bash
python3 03_SOLVERS/zone_mask_v1/scripts/verifier.py \
    --manifest 01_PUBLISHED/candidates/zone_mask_v1_<tag>/manifest.json \
    --ct 02_DATA/ciphertext_97.txt \
    --verbose
```

Expected output:
- `Round-trip valid: True`
- `BERLINCLOCK verified: True`
- All checks should pass

### Step 2: Verify Null Controls

The solution must significantly beat random baselines:

```bash
# Test against random keys
python3 07_TOOLS/nulls/key_scramble.py \
    --manifest 01_PUBLISHED/candidates/zone_mask_v1_<tag>/manifest.json \
    --iterations 100

# Test against shuffled segments
python3 07_TOOLS/nulls/segment_shuffle.py \
    --manifest 01_PUBLISHED/candidates/zone_mask_v1_<tag>/manifest.json \
    --iterations 100
```

Expected output:
- P-value < 0.01 for both tests
- Z-score > 3 (strong effect)

### Step 3: Verify Human Readability

Check that the solution can be done by hand:

```bash
# Generate notecard
python3 03_SOLVERS/zone_mask_v1/scripts/notecard.py \
    --manifest 01_PUBLISHED/candidates/zone_mask_v1_<tag>/manifest.json \
    --out notecard_test.md

# View notecard
cat notecard_test.md
```

The notecard should:
- Fit on one page
- Use only simple operations (no complex math)
- Be understandable without computer assistance

### Step 4: Verify Antipodes Mode

The solution should work with Antipodes reordering:

```bash
python3 04_EXPERIMENTS/antipodes_check/reorder_to_antipodes.py \
    --ct 02_DATA/ciphertext_97.txt \
    --layout 02_DATA/antipodes_layout.json \
    --manifest 01_PUBLISHED/candidates/zone_mask_v1_<tag>/manifest.json
```

Expected output:
- `✓ Reordering is invertible`
- Manifest should process successfully

### Step 5: Check K5 Gate

Verify the plaintext is ready for K5 analysis:

```bash
python3 04_EXPERIMENTS/k5_gate/post_plaintext_gate.py \
    --plaintext 01_PUBLISHED/candidates/zone_mask_v1_<tag>/plaintext_97.txt \
    --verbose
```

Expected output:
- K5 Ready: ✓
- Score > 50/100

## Manual Verification

To manually verify the solution:

1. **Read the notecard**: Open `notecard.md` and follow the steps by hand
2. **Check the math**: Verify cipher operations with pen and paper
3. **Test a small section**: Try the first 10 characters manually

## Acceptance Criteria

A solution is valid if and only if ALL of the following are true:

- [ ] Deterministic round-trip to exact ciphertext
- [ ] BERLINCLOCK appears at positions 64-73
- [ ] P-value < 0.01 on null controls (Holm corrected)
- [ ] Operations are paper-doable (one-page notecard)
- [ ] Works with Antipodes reordering
- [ ] K5 gate score > 50

## Troubleshooting

### "Verification failed"
- Check manifest.json is valid JSON
- Ensure ciphertext file hasn't been modified
- Verify Python dependencies are installed

### "BERLINCLOCK not found"
- Check control indices in manifest
- Verify zone boundaries are correct
- Ensure cipher keys are uppercase

### "Null test failed"
- Run more iterations (--iterations 1000)
- Check that solution isn't trivial
- Verify English-like properties in plaintext

## Contact

For questions about verification:
- Open an issue on GitHub
- Include your manifest.json and error messages
- Specify which verification step failed

---

Remember: A valid K4 solution must pass ALL verification steps, not just some.