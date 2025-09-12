# Pre-Registration: Campaign B (Route-First/Structure-Led)

**Date:** 2025-01-06  
**Campaign ID:** PV2-EXPLORE-ROUTE-001  
**Branch:** `pipeline-v2-explore-route`

## Hypothesis

H₀: Route structure variation cannot overcome delta thresholds when holding plaintext constant.  
H₁: At least one route-text combination beats both δ₁ and δ₂ thresholds (≥0.05 normalized units).

## Methodology

### Input Seeds
- **Source:** Top 20 candidates from Explore-Breadth campaign
- **Selection:** Ordered by fixed_score (4.56 to 3.75 range)
- **Rationale:** Best-performing texts from Campaign A

### Route Ensemble (39 total)
1. **GRID Family (9 routes)**
   - GRID_6x17, GRID_9x11, GRID_10x10
   - GRID_11x9, GRID_14x7, GRID_17x6
   - GRID_21x5, GRID_25x4, GRID_33x3

2. **SPOKE Family (9 routes)**
   - SPOKE_6x17, SPOKE_9x11, SPOKE_10x10
   - SPOKE_11x9, SPOKE_14x7, SPOKE_17x6
   - SPOKE_21x5, SPOKE_25x4, SPOKE_33x3

3. **RAILFENCE Family (9 routes)**
   - RAILFENCE_2, RAILFENCE_3, RAILFENCE_4
   - RAILFENCE_5, RAILFENCE_7, RAILFENCE_9
   - RAILFENCE_11, RAILFENCE_13, RAILFENCE_17

4. **HALF_INTERLEAVE (6 routes)**
   - HL_6x17, HL_10x10, HL_14x7
   - HR_6x17, HR_10x10, HR_14x7

5. **NA-only Permutations (6 routes)**
   - GRID_10x10_NA1, GRID_10x10_NA2, GRID_10x10_NA3
   - SPOKE_10x10_NA1, SPOKE_10x10_NA2, SPOKE_10x10_NA3

### Experimental Design
- **Total tests:** 20 seeds × 39 routes = 780 combinations
- **Anchor modes:** Fixed, Windowed, Shuffled (per usual)
- **Blinding:** Standard (anchors + narrative)
- **Scoring:** Normalized against shuffled baseline
- **Delta thresholds:** δ₁=0.05, δ₂=0.05
- **Nulls:** 1k bootstrap for Explore
- **Seed:** 1337 (deterministic)

### Success Criteria
1. At least one combination passes both delta thresholds
2. Feasible schedule exists (lawfulness check)
3. Passes 1k nulls (α=0.05)
4. Unique in orbit space (ε=0.01, K=10)

### Outputs
- `runs/2025-01-06-explore-route/ROUTE_MATRIX.csv`
- `runs/2025-01-06-explore-route/promotion_queue.json`
- `runs/2025-01-06-explore-route/ROUTE_REPORT.md`
- Orbit maps for top 5 combinations (if any pass)

## Predictions

Based on Campaign A results:
- **Expected outcome:** 0 promotions (structure variation insufficient)
- **Best performers:** GRID_10x10, SPOKE_10x10 (balanced aspect ratios)
- **Worst performers:** Extreme aspect ratios (33x3, 3x33)
- **Delta patterns:** Similar to Campaign A (δ₁=0, δ₂<0.05)

## Analysis Plan

1. Run all 780 combinations through standard Explore pipeline
2. Sort by combined delta score (δ₁ + δ₂)
3. Map orbits for top 5 (even if all fail)
4. Analyze route family patterns
5. Document failure modes if 0 promotions

## Declaration

This plan is committed before running any tests. No post-hoc adjustments to thresholds or metrics.

---
*Registered: 2025-01-06T00:00:00Z*