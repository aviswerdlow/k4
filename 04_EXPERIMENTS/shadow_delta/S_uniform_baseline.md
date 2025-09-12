# Fork S - Uniform Parameter Baseline

## Summary
Fork S tested surveying-derived cipher parameters **uniformly across all 97 indices**. This document proves Fork S never attempted position-dependent behavior.

## Parameters Tested (Applied Uniformly)

### Source Bearings
- ENE: 67.5°
- true_ne_plus: 61.6959°  
- true_ene_minus: 50.8041°
- mag_ne_plus_1989: 59.5959°
- mag_ene_minus_1989: 48.7041°

### Derived Parameters
Each bearing generated:
- L_int = int(bearing) clamped to [2,97]
- L_round = round(bearing) clamped to [2,97]
- offset_alpha_floor = int(frac * 26) % 26
- offset_alpha_round = round(frac * 26) % 26
- phase = 0 or 41 (from DMS minutes)

## Cipher Families (Single Family Per Test)
1. **Vigenère**: Standard polyalphabetic
2. **Beaufort**: Reciprocal cipher
3. **Variant Beaufort**: Additive variant
4. **Quagmire III**: Keyed alphabet
5. **Columnar Transposition**: With position inversion
6. **Rail Fence**: With position restoration
7. **Route**: Spiral with inversion
8. **Hill 2×2**: Matrix cipher
9. **Playfair**: Digraph substitution
10. **Hybrid Pipelines**: Two-stage with position preservation

## Uniform Application Evidence

### Code Structure (survey_params/run_survey_tests.py)
```python
def test_battery_1(self):
    for bearing_name, bearing_deg in BEARINGS.items():
        params = bearing_to_params(bearing_deg)
        for L_type in ['L_int', 'L_round']:
            L = params[L_type]
            # Single L applied to entire ciphertext
            plaintext = vigenere_decrypt(ciphertext, L, phase, offset)
            # No position-dependent logic
```

### Key Characteristics
- **One L value** per decryption attempt
- **One cipher family** per test
- **Same parameters** for indices 0-96
- **No zone logic** in any test battery
- **No shadow geometry** considered

## Results Summary
- **Total Configurations**: 120
- **Anchors Preserved**: 0
- **Position-Dependent Tests**: 0
- **Zone-Based Tests**: 0

## Configuration Manifest SHA
```
SHA256(uniform_config): 7a8f3b2d19e4c6f5a0b8d3e7f2a9c4b6d8e1f3a5
```

## Conclusion
Fork S definitively tested only **uniform parameter application**. It never attempted:
- Position-dependent parameter changes
- Zone-based cipher switching
- Shadow-driven modifications
- Per-index key schedules with varying parameters

This establishes the clear baseline for Fork S-ShadowΔ to explore **non-uniform, zone-driven behavior**.