# Control Mode Patch Report

## Executive Summary
Implemented control-mode event scheduling in zone_runner.py with partial success. Key rotation works, but BERLINCLOCK still not appearing naturally with standard keys.

## Patch Implementation

### Files Modified
1. **`/03_SOLVERS/zone_mask_v1/scripts/zone_runner.py`**
   - Added `_get_control_events()` method for event detection
   - Added `_apply_with_control()` method for segmented processing
   - Updated `decrypt()` to use control-aware processing
   - Supports processing order via manifest `order` field

### Features Implemented
✅ **Key rotation at control points** (`rotate_on_control`)
✅ **Processing order control** (`order: ["mask", "cipher"]`)
✅ **Event-based segmentation** for zones
⚠️ **Family overrides** (partial - structure in place)
⚠️ **Mask overrides** (partial - structure in place)
⚠️ **Route overrides** (partial - structure in place)

## Test Results

### Control Mode Unit Tests
```
Testing key rotation: ✅ PASS
Testing family override: ❌ FAIL (needs debugging)
Testing mask override: ❌ FAIL (needs debugging)
Testing round-trip: ✅ PASS
```

### Control Grid Re-run Results

| Manifest | Control Text | Expected | Round-trip | Score |
|----------|-------------|----------|------------|-------|
| S1_vig_ABSCISSA_period5 | MGNNBBMZFPK | BERLINCLOCK | ❌ | 0.025 |
| S1_beau_LATLONG_diag12 | CENABRFGWBK | BERLINCLOCK | ❌ | 0.000 |
| S2_toggle_mid | TIRLNNGTZJE | BERLINCLOCK | ❌ | 0.012 |
| S3_switch_mask | NYPVTTMZFPK | BERLINCLOCK | ❌ | 0.025 |
| S4_serpentine_flip | FUDXZZGTNDI | BERLINCLOCK | ❌ | 0.012 |

### Key Observations

1. **Control text is changing** - The patch is having an effect (different from raw ciphertext)
2. **No natural BERLINCLOCK** - Standard keys don't produce the target
3. **Round-trip failures** - Control mode breaking encryption symmetry
4. **Low English scores** - No meaningful content emerging

## Code Sample - Working Key Rotation

```python
def _get_control_events(self, zone_name: str, zone_start: int, zone_end: int) -> List[int]:
    """Get control event indices for a zone (converted to zone-local offsets)"""
    events = []
    
    # Check for control indices
    if self.control_mode == 'control' and self.control_indices:
        for idx in self.control_indices:
            if zone_start <= idx <= zone_end:
                local_offset = idx - zone_start
                if local_offset not in events:
                    events.append(local_offset)
    
    # Check for schedule-specific indices
    if 'cipher' in self.manifest:
        schedule = self.manifest['cipher'].get('schedule', 'static')
        if schedule == 'rotate_on_control':
            params = self.manifest['cipher'].get('schedule_params', {})
            for idx in params.get('indices', []):
                if zone_start <= idx <= zone_end:
                    local_offset = idx - zone_start
                    if local_offset not in events:
                        events.append(local_offset)
    
    return sorted(events)
```

## Next Steps

### Option 1: Debug Control Mode Features
1. Fix family override logic (Vigenere ↔ Beaufort switching)
2. Fix mask override logic (mask type switching at indices)
3. Fix route override logic (serpentine flip direction)
4. Add more comprehensive tests

### Option 2: Natural Key Discovery (Recommended)
Since control mode is partially working but not finding BERLINCLOCK naturally:

1. **Expanded key search with current code**:
   - TANGENT, SECANT, RADIAN, DEGREE
   - LODESTONE, GIRASOL  
   - Compound keys: ABSCISSAORDINATE, BERLINCLOCKKEY

2. **Key phase scanning**:
   ```python
   for offset in range(len(key)):
       rotated_key = key[offset:] + key[:offset]
       # Test with rotated key
   ```

3. **Zone edge adjustments**:
   - Test MID 35-73 (shift right by 1)
   - Test MID 34-72 (shift left by 1)

## Conclusion

The control-mode patch provides the infrastructure for event-based processing, with key rotation working correctly. However, the complexity of control modes may not be necessary - the real issue appears to be finding the right key that naturally produces BERLINCLOCK.

**Recommendation**: Focus on systematic key discovery with the working framework rather than perfecting control-mode features.

## Files Delivered

1. **Patched zone_runner.py** with control-mode support
2. **test_control_mode.py** for validation
3. **Control grid manifests** (S1-S4) for testing
4. **Summary report** showing results

The patch achieves partial success but demonstrates that control modes alone won't solve K4 without the right keys.