# Pre-Registration: Pipeline v2 Analysis Plan

**Date:** 2025-01-06  
**Campaign ID:** EXPLORE_H_REGISTER_EXPANSION  
**Global Seed:** 1337

## Campaign H: Register Expansion

### Hypothesis
Non-surveying head registers with explicitly embedded EAST/NORTHEAST corridor at positions 21/25 will show measurable window elasticity but remain below promotion thresholds under blinded scoring.

### Configuration

#### Routes
- GRID_W14_ROWS
- GRID_W14_NE  
- GRID_W14_NW
- GRID_W14_BOU

#### Anchor Configuration
- **Corridor enforced**: EAST at position 21, NORTHEAST at position 25
- **BERLINCLOCK**: position 63
- **Modes**: fixed, windowed(r=1), windowed(r=2), windowed(r=3), windowed(r=4), shuffled
- **Typo budget**: 1 (for windowed modes)

#### Scoring Configuration
- **Blinding**: ON
- **Masked lexemes hash**: e5f6a7b8c9d01234
- **Anchor tokens**: EAST, NORTHEAST, BERLINCLOCK
- **Narrative tokens**: DIAL, SET, COURSE, TRUE, READ, SEE, NOTE, SIGHT, OBSERVE, MERIDIAN, DECLINATION, BEARING, LINE

#### Thresholds
- **δ₁ (vs Windowed)**: 0.05
- **δ₂ (vs Shuffled)**: 0.10
- **α_explore**: 0.05
- **Nulls**: 1k mirrored for passers only
- **TTL**: 10 days
- **Kill criteria**: Standard (3 route failures, orbit ties ≥5, TTL expired)

### Head Registers

1. **Instructional signage**: "TEXT IS CLEAR", "NOTICE THE TEXT", "READ THEN SEE"
2. **Declarative prose**: "THE TEXT APPEARS PLAIN"
3. **Museum/caption**: "THE PANEL TEXT IS SHOWN"
4. **Neutral imperative**: "READ THE TEXT THEN SEE" (non-surveying verbs)
5. **Minimalist declarative**: "TEXT IS TRUE", "TEXT IS PLAIN", "TEXT IS EVIDENT"

### Expected Outcomes

- **Corridor alignment**: ~100% (enforced during generation)
- **Window elasticity**: Non-degenerate Δ vs r curves
- **Promotions**: 0 expected (δ thresholds not exceeded)
- **Anchor scores**: Monotonic increase with window radius

### Success Criteria

- All heads have corridor_ok = true
- Window elasticity measurable (r=n captures ±n shifts)
- No false promotions (maintain Explore discipline)
- CI remains green

### Computational Requirements

- **Estimated heads**: 1,000-3,000
- **Modes**: 6 (fixed + 4 windowed + shuffled)
- **Routes**: 4
- **Total evaluations**: ~72,000
- **Runtime**: ~30 minutes
- **Output size**: ~20MB

### Post-Analysis Actions

1. Generate ANCHOR_MODE_MATRIX.csv with alignment columns
2. Compute DELTA_CURVES.csv for elasticity analysis
3. Run 1k nulls only for passers (if any)
4. Document in EXPLORE_REPORT.md
5. Create MANIFEST.sha256 and REPRO_STEPS.md

## Framework (Pipeline v2)

- **Explore Lane**: Soft rails, blinded scoring, falsifiable anchors, 1k nulls
- **Confirm Lane**: Stays idle (no promotions)
- **Seed Policy**: Global 1337, per-worker lo64(SHA256(seed + "|" + label + "|worker:" + id))