# Key Sweep Report

## Executive Summary
Completed systematic sweep of 1470 configurations. **Zero manifests produced BERLINCLOCK** at positions 63-73.

## Sweep Parameters

### Tested Configuration Space
- **Keys**: 18 keys (ABSCISSA through BERLINCLOCK)
- **Families**: Vigenere, Beaufort
- **Key phases**: All rotations (0 to key_length-1)
- **Masks**: identity, period5, diag_weave(1,2)
- **Orders**: mask→cipher, cipher→mask
- **Total tests**: 1470

### Fixed Parameters
- **Zones**: HEAD 0-20, MID 34-73, TAIL 74-96
- **Control**: positions 63-73 (zero-based)
- **HEAD key**: KRYPTOS
- **TAIL key**: PALIMPSEST

## Results

### BERLINCLOCK Discovery
**0 out of 1470 tests produced BERLINCLOCK**

### Why No BERLINCLOCK?
Analysis shows the required key patterns at control positions:
- **Vigenere needs**: "MUYKLGKORNA" at MID positions 29-39
- **Beaufort needs**: "OCGGBGOKTRU" at MID positions 29-39

None of our dictionary keys contain these substrings or align to produce them through rotation.

### Top 3 Manifests (by score)

| Rank | Manifest | Control Text | Score | Function Words |
|------|----------|--------------|-------|----------------|
| 1 | id_vig_ABSCISSA_ph0_mc | NYPVTTMZFPK | 1 | 0 |
| 2 | p5_vig_ABSCISSA_ph0_mc | NYPVTTMZFPK | 1 | 0 |
| 3 | dw_vig_ABSCISSA_ph0_mc | NYPVTTMZFPK | 1 | 0 |

All top results show:
- ❌ No BERLINCLOCK
- ✅ Round-trip passes
- ❌ No function words outside control
- ❌ Control text unchanged (ciphertext showing through)

### Manifest Paths
1. `/04_EXPERIMENTS/phase3_zone/configs/sweep/id_vig_ABSCISSA_ph0_mc.json`
2. `/04_EXPERIMENTS/phase3_zone/configs/sweep/p5_vig_ABSCISSA_ph0_mc.json`
3. `/04_EXPERIMENTS/phase3_zone/configs/sweep/dw_vig_ABSCISSA_ph0_mc.json`

## Analysis

### Key Findings
1. **No natural alignment**: Standard dictionary keys don't naturally produce BERLINCLOCK
2. **Control region unchanged**: Most tests show "NYPVTTMZFPK" (raw ciphertext) at control
3. **Low English content**: Maximum score of 1 (essentially random)
4. **No function words**: Zero function words found outside control span

### The Fundamental Problem
The K4 control region requires a very specific key pattern that doesn't appear in:
- Geographic terms (LATITUDE, LONGITUDE, AZIMUTH)
- Clock/time words (SHADOW, LIGHT, WELTZEIT)
- Mathematical terms (TANGENT, SECANT, RADIAN)
- Compound keys (ABSCISSAORDINATE)

## Recommendations

### Option 1: Engineered Key (Like R4)
Accept that BERLINCLOCK requires an artificial key:
```
MID key: "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAMUYKLGKORNA"
```
This works but feels engineered rather than discovered.

### Option 2: Different Approach
1. **Zone boundary adjustment**: Try MID starting at different positions
2. **Control indices shift**: Maybe BERLINCLOCK appears at different positions
3. **Different cipher combination**: Try other classical ciphers
4. **Key derivation**: Maybe the key is derived from another part of K4

### Option 3: Expand Key Search
Add more keys to test:
- COMPASS, DECLINATION, TRUE, MAGNETIC
- Berlin-related: CHECKPOINT, WALLFALL, EASTWEST
- Time zones: UTC, GMT, ZULU

## Conclusion

The systematic sweep proves that:
1. **R4 remains the only working solution** with its engineered key
2. **No standard dictionary key produces BERLINCLOCK** naturally
3. **The control-mode patch works** but doesn't help without the right key

The search space has been thoroughly explored with current parameters. Either:
- The key is not a standard word/phrase
- The zones need adjustment
- There's additional transformation we're missing

## Next Steps

Since no candidates passed the BERLINCLOCK gate:

1. **Keep R4 as calibration** - It proves the framework works
2. **Try zone edge adjustments** - MID 35-73 or 34-72
3. **Test additional keys** - COMPASS, DECLINATION, etc.
4. **Consider key derivation** - Maybe the key comes from K1-K3 solutions

No manifests qualify for null hypothesis testing or packaging.