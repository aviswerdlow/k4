# Fork S-ShadowΔ - Delta Report vs Fork S

Generated: 2025-09-11 09:49:38

## What Changed from Fork S

### Fork S (Baseline)
- **Uniform Parameters**: Single L, phase, offset across all 97 indices
- **Single Operation**: One cipher family per test
- **No Position Dependence**: Same behavior everywhere
- **Result**: 0/120 configurations preserved anchors

### Fork S-ShadowΔ (This Fork)
- **Zone-Based Parameters**: Different behavior in light/shadow zones
- **Operation Switching**: Vigenère ↔ Beaufort based on position
- **Shadow-Driven Zones**: Physical geometry determines zones
- **Three Profiles**:
  - P-Light: Simple light→Vigenère, shadow→Beaufort
  - P-Tri: Three-state with offset adjustments
  - P-Flip: Toggles at anchor boundaries

## Key Innovation
**Position-dependent cipher behavior** driven by shadow geometry,
not just different surveying numbers.

## Results Summary
- Total tests: 4
- Anchors preserved: 0
- Best consonant run: 6

## No Matches Found

Zone-driven cipher behavior with these specific profiles
did not produce anchor-preserving plaintexts.

## Conclusion
Fork S-ShadowΔ tested the critical missing component from Fork S:
**position-dependent behavior**. The results show whether shadow
geometry can gate cipher operations to preserve anchors.
