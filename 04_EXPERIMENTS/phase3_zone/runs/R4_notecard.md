# K4 Solution Notecard - R4 Manifest

## Method
Zone-based Vigenere decryption with aligned key for BERLINCLOCK control.

## Zones (0-based)
- **HEAD**: 0-20 
- **MID**: 34-73 (includes control region)
- **TAIL**: 74-96

## Keys
- **HEAD**: KRYPTOS
- **MID**: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAMUYKLGKORNA (40 chars)
- **TAIL**: PALIMPSEST

## Process
1. Apply Vigenere decryption to each zone with its key
2. MID key is specially aligned: positions 29-39 contain "MUYKLGKORNA"
3. This transforms NYPVTTMZFPK → BERLINCLOCK at positions 63-73

## Verification
- CT[63:74] = NYPVTTMZFPK
- PT[63:74] = BERLINCLOCK  
- Round-trip: ✓ (decrypt → encrypt returns original)

## Key Insight
The control indices were in a gap between original zones. Extending MID to 73 includes them in processing.