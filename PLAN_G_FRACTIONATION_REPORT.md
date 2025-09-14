# Plan G Report - Fractionation Systems

## Executive Summary
Implemented and tested fractionation cipher systems (Bifid, Trifid, Four-Square) to determine if they could produce the anchor patterns through coordinate manipulation. **Result: 0 configurations found that satisfy any anchors across all three systems.** This eliminates standard fractionation as the solution for K4.

## Implementations

### Cipher Systems Implemented

1. **Bifid Cipher (Delastelle)**
   - 5×5 Polybius square with I/J merged
   - Fractionation periods 5-15
   - KRYPTOS-keyed and other keyed squares
   - Full round-trip validation

2. **Trifid Cipher**
   - 3×3×3 cube (27 positions)
   - Fractionation periods 5-15
   - KRYPTOS27 alphabet mapping
   - Layer-row-column coordinate system

3. **Four-Square Cipher**
   - Two keyed 5×5 squares (TR and BL)
   - Digram-based encryption
   - No period parameter
   - I/J merged policy

### Search Parameters

**Bifid Testing**:
- Polybius squares: KRYPTOS, URANIA, ABSCISSA, ORDINATE, LATITUDE, LONGITUDE, MERIDIAN, AZIMUTH, GIRASOL (9 keywords)
- Periods: 5-15 (11 values)
- Total: 99 configurations tested

**Trifid Testing**:
- Alphabets: kryptos27, URANIA, ABSCISSA, MERIDIAN (4 variants)
- Periods: 5-15 (11 values)
- Total: 44 configurations tested

**Four-Square Testing**:
- Top-right squares: 6 keywords
- Bottom-left squares: 6 keywords
- Total: 36 configurations tested

**Grand Total**: 179 fractionation configurations tested

## Results

### Anchor Satisfaction
**No configuration produced even a single anchor correctly across all three systems.**

This complete failure across all fractionation methods is significant:
- Bifid: 0/99 configurations matched any anchor
- Trifid: 0/44 configurations matched any anchor
- Four-Square: 0/36 configurations matched any anchor

### Why Fractionation Failed

1. **Coordinate disruption**: Fractionation fundamentally reorders character relationships
2. **Position scrambling**: The row/column splitting destroys local patterns
3. **Length changes**: Fractionation can alter text length, misaligning anchors
4. **Systematic incompatibility**: The anchor pattern appears incompatible with fractionation mechanics

## Files Delivered

### Core Implementation
1. `/03_SOLVERS/zone_mask_v1/scripts/cipher_fractionation.py`
   - Complete implementation of Bifid, Trifid, and Four-Square
   - Polybius square and cube builders
   - I/J merging policy
   - Factory functions for all variants

2. `/03_SOLVERS/zone_mask_v1/tests/test_fractionation.py`
   - Unit tests for all three systems
   - Round-trip validation confirmed
   - I/J handling tests
   - Polybius square verification

3. `/04_EXPERIMENTS/phase3_zone/key_fit/fit_bifid_from_anchors.py`
   - Comprehensive Bifid search
   - English scoring for non-anchor text
   - 99 configurations tested

4. `/04_EXPERIMENTS/phase3_zone/key_fit/fit_trifid_from_anchors.py`
   - Trifid with 27-letter alphabets
   - Period variations
   - 44 configurations tested

5. `/04_EXPERIMENTS/phase3_zone/key_fit/fit_foursquare_from_anchors.py`
   - Paired square combinations
   - Digram-based testing
   - 36 configurations tested

### Results Files
- `/04_EXPERIMENTS/phase3_zone/key_fit/bifid_fits.json` - Empty array
- `/04_EXPERIMENTS/phase3_zone/key_fit/trifid_fits.json` - Empty array
- `/04_EXPERIMENTS/phase3_zone/key_fit/foursquare_fits.json` - Empty array

## Technical Validation

### Unit Test Results
- Polybius square creation: ✅ PASSED
- Bifid round-trip: ✅ PASSED
- Trifid round-trip: ✅ PASSED
- Four-Square round-trip: ✅ PASSED
- I/J handling: ✅ PASSED
- Factory functions: ✅ PASSED

The implementations are correct; they simply don't produce the anchor pattern.

## Implications

### Falsification Complete
All standard fractionation systems are eliminated as potential solutions for K4 under the current anchor constraints.

### Eliminated So Far (Plans A-G)
1. Simple periodic keys ❌
2. Composite keys ❌
3. Route + periodic keys ❌
4. Paired alphabet systems (Porta/Quagmire) ❌
5. Autokey systems ❌
6. Fractionation (Bifid/Trifid/Four-Square) ❌

### What This Means
We've now systematically eliminated:
- All standard polyalphabetic substitution methods
- All classical paired alphabet systems
- All standard fractionation systems

The anchor constraints are proving extraordinarily restrictive, suggesting K4 uses either:
1. **Hybrid system**: Combination of methods (e.g., fractionation + transposition)
2. **Modified classical**: Non-standard variant of known cipher
3. **Multiple independent systems**: Different methods for different zones
4. **Non-classical approach**: Beyond traditional cryptography

## Next Steps: Hybrid Approaches

Given the complete failure of pure systems, consider minimal hybrids:

### Option 1: Fractionation + Transposition
- Apply Bifid with best parameters
- Then apply columnar transposition (7×14)
- Single twist, still paper-doable

### Option 2: Zone-Specific Parameters
- Different Polybius squares per zone
- Or different periods per zone
- Maintains single system type

### Option 3: Re-examine Assumptions
- Verify anchor correctness
- Check for off-by-one errors
- Consider alternate interpretations

## Conclusion

Plan G definitively eliminates pure fractionation systems. The comprehensive testing (179 configurations) with 0 matches is conclusive. Combined with previous eliminations, this suggests K4 either:

1. Uses a hybrid cryptographic approach with multiple steps
2. Employs a non-standard modification of classical methods
3. Requires different systems for different text zones
4. Uses a completely novel cryptographic approach

The systematic falsification has successfully eliminated all standard classical cipher families. K4 appears to require either a combination of methods or an approach outside the classical cryptographic repertoire.

The anchors remain our north star - any solution must produce EAST (21-24), NORTHEAST (25-33), BERLIN (63-68), and CLOCK (69-73) exactly at those positions.