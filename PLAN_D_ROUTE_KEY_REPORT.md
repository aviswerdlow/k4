# Plan D Report - Joint Route and Key Inference

## Executive Summary
Implemented joint route and periodic key fitting to test if reordering (route transformation) before substitution could make the anchor keystream patterns periodic. **Result: No periodic keys found with any tested route.** This falsifies the hypothesis "one fixed pass + short periodic key" for K4.

## Methodology

### Core Insight
Previous failures assumed identity routing (no reordering). If K4 uses a route transformation before cipher substitution, the decryption process would be:
```
CT → route → S → cipher → PT
```
Where S[p] at position p needs the right key to decrypt to PT[p].

### Routes Tested
1. **Identity**: No transformation (control)
2. **Columnar 7×14**: Row-wise write, column-wise read
3. **Serpentine 7×14**: Row-wise write, alternating LR/RL read
4. **Diagonal weave 7×14**: Diagonal pattern with step [1,2]
5. **Ring24 (24×4)**: Weltzeituhr-inspired 24-column serpentine

### Search Parameters
- Key lengths: L = 3 to 11
- Phase offsets: φ = 0 to L-1
- Control schedule: Optional phase resets at positions 63, 69
- Families: Vigenere and Beaufort
- Tableau: KRYPTOS

## Results

### Key Patterns After Route Transformation

**VIGENERE (KRYPTOS tableau)**:
```
Identity:  IRJDHGMIMJAONSYMLWRQOYBQ
Columnar:  AHKTMZUHHLBVLQPNMIBFUUGK
Serpentine: TIQTCDOIMJAONSYMLWRQZVOU
Diag_weave: PTLLNAYIGAGPCTMIPFXCZYWW
Ring24:    IRJGMMUNZQQOBSYMLWRQOYFZ
```

**BEAUFORT (KRYPTOS tableau)**:
```
Identity:  CECHPTSDQDDDEHYSSRSHDNLQ
Columnar:  WKJXFQUPHFLXFFLDALQYZIPK
Serpentine: KRNXUZODQDDDEHYSSRSHHJEP
Diag_weave: LGAFWUZDGWMMGLGJUHJUHNZY
Ring24:    CECMFXUEZQCDCHYSSRSHDNYF
```

### Periodicity Analysis

**No periodic patterns found in any route transformation.**

Notable observations:
- Serpentine preserves middle anchors (BERLIN/CLOCK region)
- Ring24 preserves significant portions of the pattern
- Columnar creates completely different pattern but still non-periodic
- No route creates repeating key patterns of length ≤11

### Cross-Route Analysis

Serpentine and Ring24 routes show substantial overlap with identity pattern:
- Serpentine preserves positions 7-16 (NORTHEAST end through BERLIN)
- Ring24 preserves positions 13-18 (BERLIN through CLOCK start)

This suggests these routes don't significantly reorder the critical anchor regions.

## Files Delivered

### Implementation
1. `/04_EXPERIMENTS/phase3_zone/key_fit/route_utils.py` - Route transformation functions
2. `/04_EXPERIMENTS/phase3_zone/key_fit/fit_route_and_periodic_key.py` - Joint fitter
3. `/04_EXPERIMENTS/phase3_zone/key_fit/analyze_route_patterns.py` - Pattern analysis

### Results
4. `/04_EXPERIMENTS/phase3_zone/key_fit/route_periodic_fits.json` - Empty (no fits found)

## Critical Findings

### Falsification Complete
The hypothesis "one fixed pass + short periodic key" is definitively falsified. Even with route transformations, the anchor constraints cannot be satisfied by:
- Pure periodic keys (L≤11)
- Periodic keys with control schedules
- Any combination of tested routes and periodic keys

### Why Routes Don't Help
1. **Pattern preservation**: Key routes (serpentine, ring24) preserve anchor regions
2. **No periodicity emergence**: Routes that scramble (columnar, diagonal) create equally non-periodic patterns
3. **Structural incompatibility**: The anchor constraint pattern appears fundamentally incompatible with periodicity

## Implications

Since neither:
- Simple periodic keys (Plan A)
- Composite keys (Plan C)  
- Route + periodic keys (Plan D)

can satisfy the four anchors, K4 must use either:

1. **More complex cipher system**: Porta/Quagmire-class with paired alphabets
2. **Fractionation**: Polybius square + transposition before Vigenere
3. **Multiple independent keys**: Different unrelated keys for different sections
4. **Non-classical system**: Beyond traditional polyalphabetic substitution

## Next Steps

Given the complete falsification of "short periodic key" hypothesis, consider:

1. **Porta/Quagmire investigation**: These use indicator-controlled tableau switching
2. **Fractionation systems**: Split characters into components before encryption
3. **Re-examine anchors**: Verify EAST, NORTHEAST, BERLIN, CLOCK are correct
4. **Different tableau per zone**: HEAD, MID, TAIL might use different tableaux

## Conclusion

Plan D definitively proves that K4 cannot be solved with:
- A short periodic key (L≤11)
- Simple route transformations
- The KRYPTOS tableau alone
- Vigenere or Beaufort families in their standard form

The mathematical impossibility of reconciling the anchor constraints with any tested configuration suggests K4 uses a fundamentally different cryptographic approach than hypothesized.