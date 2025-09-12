# Rebuild From Anchors Test

This experiment demonstrates building cipher wheels from anchor constraints alone, without requiring the full plaintext.

## Quick Run

```bash
# From this directory:
python3 run.py
```

## Expected Results

With anchors-only (no plaintext provided):
- **26 undetermined positions** out of 97 total
- Determined positions: EAST (21-24), NORTHEAST (25-33), BERLIN (63-68), CLOCK (69-73)
- All other positions show '?' (undetermined)

## What This Proves

1. The solver uses algebraic constraint propagation, not AI/ML
2. Only positions algebraically constrained by anchors are determined
3. No "hallucination" of expected patterns - undetermined means undetermined

## Files Generated

- `wheels.json` - Cipher wheels with partial key residues
- `derived_plaintext.txt` - Plaintext with '?' for undetermined positions
- `summary.json` - Statistics on determined vs undetermined positions

## Main Tool

The core implementation is at: `07_TOOLS/rebuild_from_anchors.py`

This runner simply calls that tool with the repository's default inputs.
