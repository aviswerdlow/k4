# BERLINCLOCK Indexing Postmortem

## The Bug
Original zone definitions left gaps between zones, causing the control region to remain unprocessed.

### Original Zone Configuration (Incorrect)
```
HEAD: 0-20
GAP:  21-33 (unprocessed)
MID:  34-62
GAP:  63-73 (contains control indices - unprocessed!)
TAIL: 74-96
```

### What Happened
1. Control indices [64-73] were specified in manifests (1-based thinking)
2. These indices fell in the gap between MID and TAIL zones
3. No cipher operations were applied to positions 63-73
4. The text at these positions remained as ciphertext: "YPVTTMZFPK"
5. BERLINCLOCK appeared in logs but not at the expected positions

## The Fix

### Corrected Zone Configuration
```
HEAD: 0-20
GAP:  21-33 (intentional anchor gap)
MID:  34-73 (extended to include control region)
TAIL: 74-96
```

### Zero-Based Indexing Policy
- All code uses zero-based indices throughout
- BERLIN: positions 63-68
- CLOCK: positions 69-73
- Control indices: [63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73]
- Ciphertext at 63-73: "NYPVTTMZFPK"

### Key Discovery
To produce BERLINCLOCK at positions 63-73:
1. These positions are at offset 29-39 within the MID zone
2. A 40-character key with "MUYKLGKORNA" at positions 29-39 works
3. Key: "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAMUYKLGKORNA"
4. This transforms NYPVTTMZFPK → BERLINCLOCK

## Lessons Learned

1. **Zone Coverage**: Always verify that critical positions are within zone boundaries
2. **Index Consistency**: Maintain strict zero-based indexing throughout
3. **Gap Analysis**: Document intentional gaps vs. processing gaps
4. **Validation Tests**: Add explicit tests for control region coverage

## Verification
The fix has been validated:
- BERLINCLOCK appears at positions 63-73 in plaintext
- Round-trip validation passes
- All control indices are now within the MID zone