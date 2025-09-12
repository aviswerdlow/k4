# Fork H-Shadow - Shadow-Surveying-Modified Cipher Integration

Physically-informed zones that modify cipher parameters at specific indices based on solar geometry.

## Hypothesis

Sanborn's "fucking with" the standard system is not a different cipher class, but a **physically gated modification** to an otherwise classical scheme:

- **Shadow geometry** (sun altitude/azimuth at meaningful moments) combined with **plaza surveying bearings** create zone-specific parameter tweaks
- These zone changes (light vs shadow) create the mathematical underdetermination quantified for uniform models
- A single L (e.g., 17) cannot resolve all positions because different zones use different parameters

## Architecture

### Solar/Shadow Module (`lib/sun_shadow.py`)

Implements simplified NOAA Solar Position Algorithm locally:
- `solar_alt_az()`: Calculate sun altitude and azimuth for any datetime/location
- `shadow_params()`: Derive shadow angle, bearing, and length
- No external dependencies, fully deterministic

### Zone Mapping Strategies (`lib/zones.py`)

Three independent methods to convert shadow into index masks:

#### A-zones (Anchor-aligned)
- Hard-coded segments aligned with anchor positions
- Head [0-20], EAST+NORTHEAST [21-33], Mid [34-62], BERLIN+CLOCK [63-73], Tail [74-96]
- Segments marked as shadow if shadow_angle ≥ threshold (default 30°)

#### B-zones (Periodic bands)
- Shadow bearing → stride for repeating patterns
- Creates alternating light/shadow bands across text

#### C-zones (Depth gradient)
- Three shadow levels based on angle: <20° (light), 20-35° (mid), >35° (deep)
- Complex gradients with anchor regions getting deeper shadows

### Shadow-Modified Cipher (`lib/shadow_polyalpha.py`)

Per-zone parameter modifications:

```python
Light (state=0):    Base parameters, Vigenère
Shadow (state=1):   L' = L - shadow_angle/3, Beaufort
Deep (state=2):     L' = L - shadow_angle/2, Variant-Beaufort
```

**Position-preserving**: No reordering occurs; per-index key schedule maintains zone coherence.

## Test Matrix

### Phase 1: Shadow Analysis
- 4 critical datetimes × ±60 min in 15-min increments = 36 shadow calculations
- 3 mask types per datetime = 108 total masks

### Phase 2: Zone Decryption
- 5 base bearings (61.6959°, 50.8041°, etc.)
- 3 configurations (S-Light, S-Swap, S-Tri)
- Multiple phase/offset combinations
- Position-aligned evaluation with anchor checking

### Phase 3: Rendering-Specific
- Stylized Nov 3, 2 PM shadow (35° angle)
- Anchor bands in shadow, others in light
- ENE bearing (67.5° → L=68 light, L=33 shadow)

### Phase 4: Time Progression
- Hourly progression through dedication day (9 AM - 3 PM)
- Track shadow movement and anchor preservation

## Critical Datetimes

1. **Berlin Wall Opening**: 1989-11-09 18:53 CET
2. **Kryptos Dedication**: 1990-11-03 14:00 EST
3. **Summer Solstice 1990**: 1990-06-21 12:00 EDT
4. **Winter Solstice 1990**: 1990-12-21 12:00 EST

## Key Parameters

### CIA Langley Location
- Latitude: 38.95° N
- Longitude: 77.146° W

### Survey Bearings (degrees from TRUE)
- ENE: 67.5°
- true_ne_plus: 61.6959°
- true_ene_minus: 50.8041°
- mag_ne_plus_1989: 59.5959°
- mag_ene_minus_1989: 48.7041°
- offset_only: 16.6959°

### Declinations
- Langley 1990: ~9.5° W
- Berlin 1989: ~2° E

## Usage

### Quick Start
```bash
# Run complete test suite
make shadow-all

# Quick test with dedication datetime
make shadow-quick

# Test individual components
make test-solar    # Solar calculations
make test-zones    # Zone mapping
make test-cipher   # Shadow cipher
```

### Output Files

#### Result Cards (`results/*.json`)
```json
{
  "id": "HSH-1990-11-03T14:00-Azones-true_ne_plus-S-Light",
  "shadow": {
    "sun_alt": 28.9,
    "shadow_angle": 61.1,
    "mask_type": "Azones"
  },
  "zone_profiles": [
    {"state": "light", "family": "vigenere", "L": 62},
    {"state": "shadow", "family": "beaufort", "L": 31}
  ],
  "anchors": {"preserved": false},
  "metrics": {
    "vowel_ratio": 0.35,
    "max_consonant_run": 4
  }
}
```

#### Masks (`masks/*.json`)
Zone masks for each datetime and strategy

#### Summary Files
- `RUN_SUMMARY.csv`: All tests with key metrics
- `FINAL_REPORT.md`: Human-readable analysis

## Validation

### Hard Constraints
- Anchors must be preserved exactly at indices:
  - EAST [21-24]
  - NORTHEAST [25-33]
  - BERLIN [63-68]
  - CLOCK [69-73]

### Soft Metrics
- Vowel ratio in head [0-20]
- Maximum consonant run ≤ 4
- Survey term presence (MERIDIAN, ANGLE, BEARING, etc.)

### Negative Controls
- Scrambled anchors test
- Random mask test
- Ensures we're not finding artifacts

## Success Criteria

A configuration is a **candidate** if:
1. All four anchors preserved exactly
2. Max consonant run ≤ 4 in head
3. At least one survey term appears

Ranking: anchors → consonant run → survey terms → simpler masks

## Technical Notes

### Position Preservation
Absolutely no reordering at evaluation. This fork tests **parameter changes**, not permutations.

### Per-Index Key Schedule
Each zone maintains its own (position → key) mapping. Document explicitly in result cards.

### No Post-Hoc Tuning
All parameter deltas derived formulaically from shadow geometry.

### Night Cases
When sun_alt < 0, treat as "deep shadow everywhere"

### Timezone Handling
Historic times converted correctly with DST awareness

## Determinism

- **MASTER_SEED**: 1337
- All calculations deterministic
- No external API calls
- Complete reproducibility

## Value Proposition

Even if no matches are found, this comprehensively tests and documents:
- The physical gating hypothesis
- Shadow-based parameter modification
- Zone-aware cipher variations
- Position-preserving transformations

A single anchor-preserving candidate would be a major lead. Clean negatives retire this speculation class.

---

*Fork H-Shadow - Shadow-Surveying-Modified Cipher Integration*  
*Master Seed: 1337*