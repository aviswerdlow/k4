# K4 Implementation Final Report

## Executive Summary

Implemented the K4 two-layer cryptosystem as specified in the engineer brief but **failed to produce the expected plaintext** with BERLIN at position 63-69 and CLOCK at position 69-74.

## Corrections Applied (Per User Feedback)

### 1. ✅ Fixed Alphabet
- **Changed from**: Drop X alphabet `ABCDEFGHIJKLMNOPQRSTUVWYZ`
- **Changed to**: Drop J alphabet `ABCDEFGHIKLMNOPQRSTUVWXYZ`
- **Result**: CIAX key now valid in ALPH25

### 2. ✅ Fixed Pass-Through Rule
- **Changed from**: Per-bit pass-through when key bit = 0
- **Changed to**: Per-letter pass-through when XOR result = 0
- **Implementation**:
  ```python
  if r == 0:
      return ct_letter  # Pass through
  elif 1 <= r <= 26:
      return from_1_26(r)
  ```

### 3. ❌ Panel Row Keys Issue
- **Attempted**: KRYPTOS tableau rows as specified
  - ROW_X = `XWXZKRYPTOSABCDEFGHIJLMNQUVWXZK`
  - ROW_V = `VWXZKRYPTOSABCDEFGHIJLMNQUVWXZK` (reversed)
  - ROW_T = `TNQUVWXZKRYPTOSABCDEFGHIJLMNQUV`
- **Problem**: XOR produces values 27-31 (invalid range)
- **Also tried**: K1-K3 derived rows (original mistake)
- **Result**: All keystreams fail with out-of-range XOR results

## Test Results

### Configuration Tested
```
Alphabet: ABCDEFGHIKLMNOPQRSTUVWXYZ (drop J)
Mask Key: CIAX
XOR Keys: Various combinations tested
Pass-through: When XOR result = 0
```

### Decryption Results
| Keystream | XOR Errors | BERLIN Found | CLOCK Found |
|-----------|------------|--------------|-------------|
| Tableau X+V_rev+T | 19 invalid | No | No |
| Tableau X+V+T | 18 invalid | No | No |
| K1-K3 rows | 19 invalid | No | No |
| Tolerant mode | Mapped 27-31 | No | No |

## Critical Issues Identified

### 1. XOR Result Range Problem
- **Expected**: XOR should produce only 0-26
- **Actual**: Frequently produces 27-31
- **Implication**: Either wrong keys or wrong XOR interpretation

### 2. Panel Row Uncertainty
- Brief specifies "right-side KRYPTOS-tableau rows"
- Unclear if these are:
  - Actual sculpture text rows
  - Tableau-generated rows
  - Some other transformation

### 3. Round-Trip Failure
- Decrypt → Encrypt does not reproduce original K4
- Indicates fundamental issue with the cryptosystem

## Code Structure

```
libk4/
├── alphabets_fixed.py     # Drop-J alphabet utilities
├── mask_base5_fixed.py    # Base-5 operations with CIAX
├── xor5_fixed.py          # Per-letter pass-through XOR
├── xor5_tolerant.py       # Handles 27-31 results
├── k4_correct.py          # Main implementation
└── k4_tolerant.py         # Tolerant version
```

## Next Steps Required

1. **Clarify Panel Rows**: Get exact 31-character rows from reliable source
2. **Verify XOR Operation**: Confirm the 1-26 coding and XOR rules
3. **Check Layer Order**: Confirm PT → Mask → XOR → CT is correct
4. **Test Known Pairs**: If any PT-CT pairs exist, use for validation

## Diagnostic Summary

The implementation correctly handles:
- ✅ Drop-J alphabet with CIAX key
- ✅ Per-letter pass-through rule
- ✅ Base-5 masking operations
- ✅ 93-character message length

The implementation fails on:
- ❌ Correct panel row keys
- ❌ XOR producing valid range
- ❌ Finding BERLIN/CLOCK anchors
- ❌ Round-trip verification

## Conclusion

The core cryptographic operations are implemented as specified, but the system does not produce the expected plaintext. The most likely issue is incorrect panel row keys, as these consistently produce XOR results outside the valid 1-26 range. Without the correct keys or additional clarification on the XOR operation, the implementation cannot be completed successfully.

## Files for Review

- `test_xor_debug.py` - Shows exactly where XOR fails
- `k4_correct.py` - Implementation with all fixes
- `K4_IMPLEMENTATION_NOTES.md` - Detailed documentation

The implementation is structurally complete but requires correct key material to function properly.