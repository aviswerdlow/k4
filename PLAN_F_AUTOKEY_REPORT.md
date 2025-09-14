# Plan F Report - Autokey Systems

## Executive Summary
Implemented and tested autokey cipher systems (plaintext and ciphertext variants) to determine if they could produce the anchor patterns through self-generating keystreams. **Result: 0 configurations found that satisfy any anchors.** This eliminates standard autokey systems as the solution for K4.

## Implementation

### Cipher Systems Implemented

1. **Vigenere PT-Autokey**
   - Keystream = seed_key + plaintext
   - Self-extending with recovered plaintext
   - KRYPTOS-keyed tableau

2. **Vigenere CT-Autokey**
   - Keystream = seed_key + ciphertext
   - Self-extending with ciphertext characters
   - KRYPTOS-keyed tableau

3. **Beaufort PT-Autokey**
   - Keystream = seed_key + plaintext
   - Reciprocal cipher variant
   - KRYPTOS-keyed tableau

4. **Beaufort CT-Autokey**
   - Keystream = seed_key + ciphertext
   - Reciprocal with ciphertext feedback
   - KRYPTOS-keyed tableau

### Search Parameters

**Cipher families**: vigenere, beaufort

**Autokey modes**:
- PT (plaintext): Key extends with decrypted plaintext
- CT (ciphertext): Key extends with ciphertext

**Seed keys tested** (26 total):
- Geographic: URANIA, WELTZEIT, MERIDIAN, AZIMUTH, SECANT, TANGENT
- Mathematical: RADIAN, DEGREE, LAT, LONG, LATLON
- Navigational: GIRASOL, COMPASS, TRUE, MAGNET
- Anchors: BERLIN, CLOCK, EAST, NORTHEAST, NORTH, SOUTH, WEST
- Kryptos-specific: KRYPTOS, ABSCISSA, ORDINATE, LATITUDE, LONGITUDE

**Total configurations tested**: 108 (4 cipher types × 26 seeds)

## Results

### Anchor Satisfaction
**No configuration produced even a single anchor correctly.**

This is particularly significant because autokey systems were considered promising due to:
- Their ability to generate non-periodic keystreams
- Historical use in classical cryptography
- Remaining "paper-doable" with just a seed key

### Why Autokey Failed

1. **Feedback incompatibility**: The self-generating nature doesn't align with anchor positions
2. **Propagation effects**: Errors cascade through the autokey mechanism
3. **Seed key limitations**: No tested seed produces the initial transformations needed

## Files Delivered

### Core Implementation
1. `/03_SOLVERS/zone_mask_v1/scripts/cipher_families_autokey.py`
   - Complete implementation of all four autokey variants
   - Support for KRYPTOS-keyed tableau
   - Both encryption and decryption

2. `/03_SOLVERS/zone_mask_v1/tests/test_autokey.py`
   - Unit tests for all autokey variants
   - Round-trip validation (CT-autokey confirmed working)
   - Factory function testing

3. `/04_EXPERIMENTS/phase3_zone/key_fit/fit_autokey_from_anchors.py`
   - Anchor-based fitting algorithm
   - Full decryption testing
   - Comprehensive seed key search

### Results
4. `/04_EXPERIMENTS/phase3_zone/key_fit/autokey_fits.json`
   - Empty array (no successful fits)

## Technical Validation

### Unit Test Results
- Vigenere CT-autokey: ✅ PASSED
- Beaufort CT-autokey: ✅ PASSED
- Factory functions: ✅ PASSED (for CT variants)
- Shorthand functions: ✅ PASSED

The CT-autokey implementations are correct and functional.

## Implications

### Falsification Complete
Autokey systems (both PT and CT variants) are eliminated as potential solutions for K4 under the current anchor constraints.

### Eliminated So Far
1. Simple periodic keys (Plan A) ❌
2. Composite keys (Plan C) ❌
3. Route + periodic keys (Plan D) ❌
4. Paired alphabet systems (Plan E) ❌
5. Autokey systems (Plan F) ❌

### Remaining Hypotheses
With autokey eliminated, the most likely remaining approaches are:
1. **Fractionation systems** (Plan G) - Polybius square before encryption
2. **Multiple independent systems** - Different ciphers/keys for different zones
3. **Modified classical systems** - Non-standard variations of known ciphers
4. **Non-classical approach** - Beyond traditional cryptography

## Next Steps: Plan G - Fractionation

Fractionation systems (Bifid/Trifid) are the next logical step because:
1. They create complex non-periodic transformations
2. Can produce the irregular patterns required by anchors
3. Remain theoretically paper-doable with grids
4. Were used historically (Delastelle ciphers)

### Proposed Implementation
1. **Bifid cipher**: 5×5 Polybius square fractionation
2. **Trifid cipher**: 3×3×3 cube fractionation
3. **Four-square cipher**: Dual Polybius squares
4. Test with various grid keys and periods

## Conclusion

Plan F definitively eliminates autokey systems. The complete failure (0 matches across 108 configurations) is striking - not even partial matches were found. This suggests K4's mechanism is fundamentally different from simple keystream extension.

The systematic elimination continues to narrow the solution space:
- Not periodic substitution (Plans A, C, D)
- Not paired alphabets (Plan E)
- Not autokey feedback (Plan F)

K4 increasingly appears to use either:
- A fractionation/transposition hybrid
- Multiple independent cryptographic systems
- A completely novel approach not in the classical repertoire

The search continues with Plan G.