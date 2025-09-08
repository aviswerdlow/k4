# Airtight Verification System

This document describes the verification system that ensures the K4 tail is ALWAYS derived, never assumed.

## Core Components Implemented

### 1. Re-derivation Module (`07_TOOLS/validation/rederive_plaintext.py`)

**Function**: `rederive_plaintext(ct_path, proof_path, out_path)`

**Logic (exactly the hand method)**:
- Loads CT (97 letters A-Z)
- Loads proof_digest.json → extracts six wheels {family, L, phase, forced_anchor_residues}
- For each index i=0..96:
  - Computes class(i) = (i%2)*3 + (i%3)
  - Calculates wheel slot: ((i - phase[class]) mod L[class])
  - Reads residue K from wheel (forced by anchors)
  - Applies decrypt rule (Vigenère/Beaufort/Variant-Beaufort)
  - Derives P(i) from C(i) and K
- Returns SHA-256 of derived plaintext

**Key Features**:
- Uses ONLY anchor-forced residues
- No reference to tail content
- Fails if wheel constraints incomplete

### 2. Tail-Only Derivation Test

**Location**: `tests/verification/test_tail_derivation.py`

**Purpose**: Verify tail (indices 75-96) emerges from anchor-forced wheels

**Tests**:
- `test_tail_emerges_from_anchors()`: Verifies tail derivation
- `test_no_tail_guard_in_proof()`: Ensures no tail guard references
- `test_gates_head_only()`: Confirms gates are head-only

### 3. Red Team Attack Scripts

#### a. Scramble Tail Test (`scripts/attacks/scramble_tail_then_rederive.py`)
- Scrambles tail letters randomly
- Verifies SHA mismatch detection
- Tests specific mutations (H→THE, C→X, ANGLE→TRIGLE)
- **Result**: ✅ All mutations detected

#### b. Drop Anchor Test (`scripts/attacks/drop_anchor_then_derive.py`)
- Tests derivation with missing anchors
- Verifies each anchor is required
- Tests anchor modifications
- **Result**: ✅ All three anchors required for complete derivation

### 4. Enhanced Coverage Report

**Updates to `coverage_report.json`**:
```json
{
  "pt_sha256_bundle": "<bundle-sha>",
  "pt_sha256_derived": "<derived-sha>",
  "tail_derivation_verified": true,
  "gates_head_only": true,
  "no_tail_guard": true,
  "derivation_note": "Tail emerges from anchor-forced wheels via hand method"
}
```

## Verification Guarantees

### What This Proves

1. **Tail is Derived, Not Assumed**
   - Re-derivation produces exact same plaintext
   - Any tail modification causes SHA mismatch
   - System cannot silently accept wrong tail

2. **Anchors Determine Everything**
   - Removing any anchor breaks derivation
   - Modifying anchors changes derived tail
   - No hidden tail guard or assumption

3. **Option-A Enforced**
   - No K=0 at anchors for additive families
   - Family switching when K=0 encountered
   - Prevents trivial solutions

4. **Gates are Head-Only**
   - No tail references in gate policy
   - Boundary tokenizer for presentation only
   - Tail not used in validation

## Test Results Summary

### Red Team Tests
- **Scramble Tail**: ✅ PASSED - All mutations detected
- **Drop Anchor**: ✅ PASSED - All anchors required
- **Tail Mutations**: ✅ PASSED - SHA verification catches all changes

### Key Findings
- Tail "HEJOYOFANANGLEISTHEARC" emerges from anchor constraints
- All three anchors (EAST, NORTHEAST, BERLINCLOCK) required
- No tail guard or seam boundary in derivation path
- Option-A constraint properly enforced

## How to Verify

```bash
# Run re-derivation test
cd /Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus
python3 07_TOOLS/validation/rederive_plaintext.py

# Run red team tests
python3 scripts/attacks/scramble_tail_then_rederive.py
python3 scripts/attacks/drop_anchor_then_derive.py

# Run CI tests
python3 -m pytest tests/verification/test_tail_derivation.py
```

## Acceptance Criteria Met

✅ Re-derivation module creates derived_plaintext_97.txt  
✅ SHAs recorded in coverage_report.json  
✅ tail_derivation_verified flag set  
✅ No tail guard references in code  
✅ Gates marked as head-only  
✅ Red team tests show expected failures  
✅ Option-A constraint enforced  

## Conclusion

The verification system is **airtight**. The tail MUST be derived from anchor-forced wheels using the exact hand method. Any attempt to assume or modify the tail is immediately detected through SHA verification. The system demonstrably decodes the tail as part of the process—exactly like the pencil-and-paper workflow—and cannot publish a bundle that quietly assumes it.