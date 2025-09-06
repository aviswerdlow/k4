# Pre-Registration: Anchor-Constrained Routes (Geometry-Respecting)

**Date:** 2025-01-06  
**Campaign ID:** PV2-EXPLORE-GRID-AUTOS-001  
**Branch:** `pipeline-v2-grid-autos`

## Hypothesis

H₀: Geometry-respecting transformations cannot produce candidates that beat delta thresholds.  
H₁: At least one anchor-constrained GRID variant beats both δ₁ and δ₂ thresholds while preserving anchor relationships.

## Methodology

### Anchor Geometry Constraints

Preserve the following spatial relationships:
1. **EAST** at positions [21,24] 
2. **NORTHEAST** at positions [25,33]
3. **BERLINCLOCK** at positions [63,73]
4. **Adjacency:** EAST→NORTHEAST contiguous
5. **NA-domain:** Positions [54,74] connectivity

### GRID Automorphisms (Anchor-Fixing)

Only transformations that maintain anchor relative positions:

1. **GRID_10x10_FIXED**: Standard 10x10 with anchors in fixed rows
2. **GRID_10x10_ROW_PERM**: Permute non-anchor rows only
3. **GRID_10x10_COL_SHIFT**: Cyclic column shifts preserving anchor columns
4. **GRID_11x9_PINNED**: 11x9 with anchor rows/cols pinned
5. **GRID_9x11_PINNED**: 9x11 with anchor rows/cols pinned
6. **GRID_CONJUGATE_1**: Row↔Col transpose if anchor-preserving
7. **GRID_CONJUGATE_2**: Block-diagonal with anchor blocks fixed
8. **GRID_CONJUGATE_3**: Strided read with anchor stride preserved

### Validation Requirements

For each transformation T:
- Verify T(EAST_positions) maps to valid anchor zone
- Verify T(NORTHEAST_positions) maintains adjacency
- Verify T(BERLINCLOCK_positions) stays in NA-domain
- Compute T⁻¹ exists and is anchor-preserving

### Input Seeds
- Top 10 candidates from Explore-Breadth campaign
- Plus 5 new lexicon-injected variants (if time permits)

### Experimental Design
- **Tests:** 15 seeds × 8 transformations = 120
- **Anchor modes:** Fixed, Windowed (±1), Shuffled
- **Blinding:** Standard (anchors + narrative)
- **Delta thresholds:** δ₁=0.05, δ₂=0.05
- **Orbit mapping:** For any passers (ε=0.01, K=10)
- **Nulls:** 1k bootstrap for delta passers
- **Seed:** 1337 (deterministic)

### Success Criteria
1. ≥1 head beats both windowed and shuffled by δ
2. Passes on ≥2 anchor-constrained variants
3. Survives orbit uniqueness test (no tie cloud)
4. Passes 1k nulls (α=0.05)

### Outputs
- `runs/2025-01-06-explore-grid-autos/ANCHOR_MODE_MATRIX.csv`
- `runs/2025-01-06-explore-grid-autos/EXPLORE_MATRIX.csv`
- `runs/2025-01-06-explore-grid-autos/ORBIT_SUMMARY.csv`
- `runs/2025-01-06-explore-grid-autos/NEG_CONTROL_SUMMARY.csv`
- `runs/2025-01-06-explore-grid-autos/promotion_queue.json`
- `runs/2025-01-06-explore-grid-autos/EXPLORE_REPORT.md`
- `runs/2025-01-06-explore-grid-autos/MANIFEST.sha256`
- `runs/2025-01-06-explore-grid-autos/REPRO_STEPS.md`

## Predictions

Based on previous campaigns:
- **Expected promotions:** 0-2 (geometry constraints help but may not suffice)
- **Best performers:** GRID_10x10 variants with minimal perturbation
- **Worst performers:** Conjugates with high distortion
- **Delta patterns:** Improved δ₁ due to preserved anchors

## Analysis Plan

1. Verify each transformation preserves anchor geometry
2. Run standard Explore pipeline with constraints
3. Sort by combined delta score
4. Map orbits for top 3 (even if fail)
5. Run negative controls
6. Document geometry preservation metrics

## Declaration

This plan is committed before running any tests. Transformations will be validated for anchor preservation before scoring.

---
*Registered: 2025-01-06T12:00:00Z*