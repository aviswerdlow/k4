# K4 Two-Layer Cryptosystem Implementation Notes

## System Overview

Implementation of the K4 cipher based on the "assumed-true" two-layer XOR + base-5 mask theory.

### Architecture
```
Plaintext (93 chars, 25-letter alphabet)
    ↓
Layer A: Base-5 Mask (key: CIAX/CIAW)
    ↓
Layer B: 5-bit XOR with pass-through (panel row keys)
    ↓
Ciphertext (OBKR + 93 chars, 26-letter alphabet)
```

## Key Components

### Alphabets
- **25-letter**: `ABCDEFGHIJKLMNOPQRSTUVWYZ` (no X)
- **26-letter**: `ABCDEFGHIJKLMNOPQRSTUVWXYZ` (standard)

### Layer A: Base-5 Mask
- **Key**: "CIAX" (brief specification) → "CIAW" (implementation, since X not in 25-letter alphabet)
- **Operation**: Modular addition/subtraction in 25-letter space
- **Formula**: `masked[i] = (plaintext[i] + key[i % len(key)]) % 25`

### Layer B: 5-bit XOR with Pass-through
- **Keys**: Three 31-character panel rows from Kryptos right side
  - Row 1: `VFPJUDEEHZWETZYVGWHKKQETGFQJNCE`
  - Row 2: `PFSCZZRLFCUOACDJMVMSPDFOIUYANDS`
  - Row 3: `OHCNSCDTGEUAAIYREBRTAWXVUIENLNN`
- **Pass-through rule**: If key bit is 0, plaintext bit passes unchanged
- **Bit-wise operation**:
  ```python
  if key_bit == 0:
      result_bit = plaintext_bit  # Pass through
  else:
      result_bit = plaintext_bit ^ key_bit  # XOR
  ```

## Implementation Files

### Core Library (`libk4/`)
1. **alphabets.py**: Alphabet utilities and 5-bit encoding
2. **mask_base5.py**: Base-5 masking operations
3. **xor5.py**: 5-bit XOR with pass-through
4. **cryptosystem.py**: Main cipher class
5. **cryptosystem_v2.py**: Revised implementation
6. **k4_final.py**: Final attempt with alphabet mapping

### Test Files
1. **k4_verifier.py**: Round-trip verification tests
2. **test_layers.py**: Layer-by-layer debugging
3. **test_simple.py**: Anchor position analysis

## Known K4 Constraints

### Ciphertext
```
OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR
```
- Total: 97 characters
- Header: "OBKR" (4 chars)
- Body: 93 characters

### Expected Plaintext Anchors
- **BERLIN**: positions 63-69
- **CLOCK**: positions 69-74

## Current Status

### Implementation Attempts
1. **Version 1**: Basic two-layer system
   - Issue: Alphabet conversion problems
   - Result: No anchors found at expected positions

2. **Version 2**: Improved alphabet handling
   - Issue: Values outside 25-letter range after XOR
   - Result: Still no anchors found

3. **Final Version**: Explicit 25/26 mapping
   - Issue: Round-trip fails, anchors not found
   - Key adjustment: CIAX → CIAW (X not in 25-letter alphabet)

### Debugging Findings
- XOR produces 5-bit values (0-31 range)
- Mapping between 25 and 26 letter alphabets is critical
- Pass-through rule interpretation affects results
- Panel row 2 originally had 32 chars (corrected to 31)

## Open Questions

1. **Mask Key**: Is "CIAX" correct given X isn't in 25-letter alphabet?
2. **Alphabet Mapping**: How exactly should 25↔26 letter conversion work?
3. **XOR Range**: Should XOR output be constrained to 0-25 or 0-31?
4. **Pass-through Rule**: Is our interpretation correct?
5. **Panel Keys**: Are the panel row transcriptions accurate?

## Test Results Summary

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| Decrypt K4 | Plaintext with anchors | Various results | ❌ |
| BERLIN at 63-69 | "BERLIN" | Different text | ❌ |
| CLOCK at 69-74 | "CLOCK" | Different text | ❌ |
| Round-trip | Original K4 | Mismatches | ❌ |

## Next Steps

1. Verify panel row key transcriptions
2. Clarify mask key (CIAX vs alternative)
3. Review pass-through rule interpretation
4. Consider alternative alphabet mappings
5. Test with known plaintext-ciphertext pairs if available

## Command Line Usage

```bash
# Run verifier
python3 k4_verifier.py

# Test final implementation
python3 libk4/k4_final.py

# Layer-by-layer analysis
python3 test_layers.py
```

## Notes

The implementation follows the specifications from the K4 Engineer Brief but does not yet produce the expected results. The two-layer system (XOR + base-5 mask) is implemented with the pass-through rule, but the decryption does not reveal BERLIN and CLOCK at the expected positions, suggesting either:

1. Implementation error in the layer operations
2. Incorrect key values or parameters
3. Misunderstanding of the alphabet conversion requirements
4. The theory itself may need adjustment

Further investigation and clarification of the specifications are needed to achieve a working implementation.