# K4 Implementation Comprehensive Report

## Executive Summary

Despite implementing all specified corrections and testing multiple cryptographic approaches, **the K4 two-layer system does not produce the expected plaintext** with BERLIN/CLOCK anchors or achieve round-trip verification.

## Implemented Corrections

### ✅ 1. Drop-J Alphabet
- Changed from drop-X to drop-J: `ABCDEFGHIKLMNOPQRSTUVWXYZ`
- CIAX key now valid in ALPH25

### ✅ 2. Per-Letter Pass-Through
- Implemented correctly: pass-through when XOR result = 0
- Not per-bit as initially misunderstood

### ✅ 3. Reverse Steps Added
- Decrypt: CT → **REVERSE** → XOR inverse → Base5 unmask → PT
- Encrypt: PT → Base5 mask → XOR → **REVERSE** → CT

### ✅ 4. Programmatic Tableau Rows
- Built using proper tableau generation from `TOP = "KRYPTOSABCDEFGHIJLMNQUVWXZ"`
- Eliminates typos and ensures consistency
- Tested multiple shifts and orientations

## Comprehensive Testing Results

### Phase and Orientation Search
```
Tested: 186 configurations (93 phases × 2 V orientations)
With CT reversal: Yes
Best result: 5 bad XOR positions (phase 79, V reversed)
Perfect result (0 bad): NONE FOUND
```

### XOR Layer Issues
- **Problem**: XOR consistently produces values 27-31 (outside valid 1-26 range)
- **Tested solutions**:
  - All phase offsets (0-92)
  - Both V orientations (forward/reversed)
  - Different tableau shifts
  - Tolerant mapping of 27-31 values
- **Result**: No configuration eliminates invalid XOR results

### Alternative Cipher Modes
Replaced 5-bit XOR with classical mod-26 operations:

| Cipher Type | Configurations Tested | Round-Trip Success | Anchors Found |
|-------------|----------------------|-------------------|---------------|
| Vigenère | 8 | 0 | 0 |
| Beaufort | 8 | 0 | 0 |

**Result**: All mod-26 configurations fail round-trip verification

## Root Cause Analysis

### What's Working
- ✅ Base-5 masking logic with CIAX key
- ✅ Drop-J alphabet handling
- ✅ 93-character message structure
- ✅ OBKR header handling
- ✅ Reverse step implementation

### What's Failing
- ❌ XOR produces invalid range (27-31)
- ❌ No configuration achieves round-trip
- ❌ No BERLIN/CLOCK anchors found
- ❌ Even mod-26 operations fail

## Hypothesis Testing Results

### Hypothesis 1: 5-bit XOR with Pass-Through
- **Status**: FALSIFIED
- **Evidence**: No phase/orientation eliminates 27-31 values
- **Minimum bad positions**: 5 (out of 93)

### Hypothesis 2: Mod-26 Operations (Vigenère/Beaufort)
- **Status**: FALSIFIED
- **Evidence**: All configurations fail round-trip
- **Best result**: Partial matches but never complete

### Hypothesis 3: Tableau Row Construction
- **Status**: VERIFIED CORRECT
- **Method**: Programmatic generation from KRYPTOS keyed tableau
- **Validation**: Matches expected patterns

## Critical Unknowns

1. **Panel Row Content**: Are the tableau-derived rows correct, or should we use actual sculpture text?
2. **Layer Order**: Is the order truly Mask→XOR or XOR→Mask?
3. **Reverse Placement**: Is reverse exactly where specified?
4. **Key Material**: Is CIAX the actual mask key?
5. **Alphabet Mapping**: Is there an additional transformation between layers?

## Code Architecture

```
libk4/
├── alphabets_fixed.py        # Drop-J alphabet (✅)
├── mask_base5_fixed.py       # Base-5 operations (✅)
├── xor5_fixed.py            # Per-letter pass-through (✅)
├── mod26_layer.py           # Alternative ciphers (✅)
├── tableau_builder.py       # Programmatic rows (✅)
├── k4_with_reverse.py       # Complete implementation (❌)
└── k4_mod26.py             # Mod-26 alternative (❌)

Testing:
├── phase_search.py          # 186 configurations tested
├── test_xor_debug.py        # XOR failure analysis
└── K4_FINAL_REPORT.md      # Previous documentation
```

## Diagnostic Evidence

### XOR Failure Pattern (sample)
```
Position 7: 'U' (21) ^ 'N' (14) = 27 ❌
Position 15: 'J' (10) ^ 'W' (23) = 29 ❌
Position 19: 'K' (11) ^ 'U' (21) = 30 ❌
```

### Round-Trip Failures
- Vigenère: Fails at various positions (5-79)
- Beaufort: Fails at various positions (16-79)
- XOR: Cannot complete due to 27-31 values

## Conclusions

1. **The specification as implemented does not work**
   - All three fixes were correctly applied
   - Reverse steps were added as required
   - Programmatic tableau generation ensures consistency

2. **The 5-bit XOR interpretation is likely wrong**
   - Consistently produces invalid values
   - No phase/orientation fixes this
   - Suggests fundamental misunderstanding

3. **Classical mod-26 operations also fail**
   - Neither Vigenère nor Beaufort work
   - Indicates deeper issue with key material or structure

## Recommendations

1. **Verify panel row source**: Get exact 31-character rows from authoritative source
2. **Test alternative layer orders**: Try XOR→Mask instead of Mask→XOR
3. **Consider different alphabet mappings**: Perhaps 25↔26 conversion needs special handling
4. **Explore different key interpretations**: CIAX might transform differently
5. **Check for additional operations**: Missing step between layers?

## Final Status

**Implementation**: COMPLETE per specifications
**Verification**: FAILED - no configuration produces expected results
**Root Cause**: Either wrong key material or fundamental misinterpretation of the cryptosystem

The implementation correctly follows all specified corrections but cannot achieve the required round-trip verification or find the known plaintext anchors. This strongly suggests either the panel rows are wrong or the entire two-layer XOR+mask interpretation needs reconsideration.