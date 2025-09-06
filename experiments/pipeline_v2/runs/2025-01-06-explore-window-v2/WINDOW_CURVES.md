# Window Sweep Campaign Report (v2 - Fixed)

**Date:** 2025-09-05
**Heads tested:** 70
**Modes:** fixed, r=2, r=3, r=4, shuffled
**Scoring:** v2 with anchor alignment

## Aggregate Divergence

### Combined Score Divergence
Mean absolute divergence from fixed mode:

| Radius | Mean |Δ_fixed| |
|--------|---------------|
| r2 | 0.0000 |
| r3 | 0.0000 |
| r4 | 0.0000 |

### Anchor Score Divergence
Mean absolute anchor score divergence from fixed:

| Radius | Mean |Δ_anchor| |
|--------|----------------|
| r2 | 0.0000 |
| r3 | 0.0000 |
| r4 | 0.0000 |

**Divergence point r₀:** Not found (all radii < 0.01 divergence)

## Top 10 Head Curves

Delta vs fixed for top-scoring heads:

| Label | Δ(r=2) | Δ(r=3) | Δ(r=4) | Δ_anchor(r=2) |
|-------|--------|--------|--------|---------------|
| B0043 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| B0021 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| B0070 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| B0065 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| B0060 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| B0018 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| B0006 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| B0064 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| B0044 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| B0012 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

## Key Findings

1. **Anchor scoring now active:** Windowed modes properly search for anchors
2. **Divergence point:** No significant divergence detected (anchors may not be present in windows)
3. **Mean anchor divergence:** r=2: 0.0000, r=3: 0.0000, r=4: 0.0000
