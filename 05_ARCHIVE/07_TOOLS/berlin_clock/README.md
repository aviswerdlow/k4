# Berlin Clock K4 Tests

## Overview

The Berlin Clock (Mengenlehreuhr) is the only external object explicitly mentioned by Sanborn as relevant to K4 ("delve into that particular clock"). This implementation tests whether Berlin Clock states can provide keystreams that determine unknown K4 positions.

## Clock Structure

The Berlin Clock displays time using illuminated lamps in four rows:
- **Row 1**: 4 lamps (5-hour blocks) 
- **Row 2**: 4 lamps (1-hour blocks)
- **Row 3**: 11 lamps (5-minute blocks, positions 3/6/9 are red for quarter-hours)
- **Row 4**: 4 lamps (1-minute blocks)

Example: 14:35 = 2 five-hour lamps + 4 one-hour lamps + 7 five-minute lamps + 0 one-minute lamps

## Keystream Mapping Methods

All methods use frozen constants (no post-hoc tuning):

### 1. on_off_count_per_row
Maps the count of lit lamps in each row to a keystream.
- Formula: `k[i] = (counts[i%4] * 7 + i * 3) % 26`
- Constants: repeat_factor=7, position_offset=3

### 2. base5_vector  
Interprets rows as base-5 digits, hashes to 26-position keystream.
- Formula: `k[i] = (11 * base5_num + 7 * i + 13) % 26`
- Constants: a=11, b=7, c=13

### 3. pattern_signature
Creates FNV-1a hash of the on/off pattern per row.
- Constants: fnv_prime=16777619, fnv_offset=2166136261
- Extraction: byte-wise from 32-bit hash

### 4. row3_triplet_marks
Uses quarter-hour markers (red lamps at positions 3/6/9) for sparse keystream.
- Marker positions in keystream: 0, 8, 16
- Fill formula: `k[i] = (num_quarters * 5 + i * 2) % 26`

## Test Suite

### Fixed Timestamps (UTC)
- **1990-11-03 14:00** - Kryptos dedication ceremony window
- **1989-11-09 18:53** - Berlin Wall opening reference
- **Hourly tests** - Every hour on the hour (00:00 through 23:00)
- **Quarter marks** - 12:00, 15:00, 18:00, 21:00

### Files

- `berlin_clock_simulator.py` - Core clock simulator
- `berlin_clock_k4.py` - Original K4 application (has bug)
- `berlin_clock_k4_fixed.py` - Corrected implementation
- `METHODS_MANIFEST.json` - Frozen constants documentation

## Results

**CLEAN NEGATIVE**: No Berlin Clock configuration determined additional K4 positions.

### Why It Doesn't Work

With only 24 anchor positions and 6 wheels of length 17:
- We have 102 total wheel positions (6 × 17)
- Anchors constrain only 24 of these
- This leaves 78 positions unconstrained
- No external keystream can uniquely determine these without more constraints

### Wheel Coverage from Anchors
```
Wheel 0 (beaufort): 4/17 slots filled
Wheel 1 (vigenere): 4/17 slots filled  
Wheel 2 (beaufort): 3/17 slots filled
Wheel 3 (vigenere): 5/17 slots filled
Wheel 4 (beaufort): 4/17 slots filled
Wheel 5 (vigenere): 4/17 slots filled
```

Average coverage: ~24% of wheel positions

## Reproducibility

All tests use `MASTER_SEED = 1337` for complete determinism.

To reproduce:
```bash
cd 07_TOOLS/berlin_clock
python3 berlin_clock_k4_fixed.py
```

Results will be in `runs_fixed/` directory.