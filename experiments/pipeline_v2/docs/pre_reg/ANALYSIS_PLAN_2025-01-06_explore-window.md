# Pre-Registration: Window Sweep Campaign

**Date:** 2025-01-06  
**Campaign ID:** PV2-EXPLORE-WINDOW-001  
**Branch:** `pipeline-v2-explore-window`

## Purpose

Quantify where "windowed" diverges from "fixed" by measuring deltas at progressively wider anchor windows. This is measurement only - no promotions to Confirm.

## Hypothesis

H₀: Windowed mode remains equivalent to fixed mode regardless of window radius.  
H₁: At some radius r₀, windowed mode begins to diverge meaningfully from fixed mode.

## Methodology

### Anchor Modes
1. **Fixed**: Exact positions required
2. **Windowed(r=2)**: ±2 positions, typo_budget=1
3. **Windowed(r=3)**: ±3 positions, typo_budget=1  
4. **Windowed(r=4)**: ±4 positions, typo_budget=1
5. **Shuffled**: Random positions (control)

### Test Corpus
- 100 heads sampled across score distribution:
  - 40 top performers (scores > 3.0)
  - 40 middle performers (scores 1.0-3.0)
  - 20 bottom performers (scores < 1.0)
- Source: Breadth and Grid-Autos campaigns

### Routes
- GRID_W14_ROWS only (anchor-respecting)
- Additional routes optional for validation

### Experimental Parameters
- **Promotion**: DISABLED (measurement only)
- **Delta margins**: δ₁=0.05, δ₂=0.05 (unchanged, for reporting only)
- **Blinding**: Anchors + narrative lexemes masked
- **Blinding hash**: e5f6a7b8c9d01234 (pinned)
- **Nulls**: 1k language-only bootstrap for measurement
- **Orbit test**: DISABLED (not needed for sweep)
- **TTL**: 10 days
- **Seed**: 1337

### Success Metrics
1. Identify r₀ where mean(|δ_windowed(r) - δ_fixed|) > 0.01
2. Characterize delta curves across radius
3. No promotions (Confirm remains idle)

## Outputs

### Primary Data
- `ANCHOR_MODE_MATRIX.csv`: Full results matrix
  ```
  label,route,mode,score_norm,coverage_norm,compress_norm,z_ngram_norm
  ```

### Derived Analysis
- `DELTA_CURVES.csv`: Per-head delta progressions
  ```
  label,route,delta_vs_shuffled_fixed,delta_vs_shuffled_r2,delta_vs_shuffled_r3,delta_vs_shuffled_r4,
  delta_vs_fixed_r2,delta_vs_fixed_r3,delta_vs_fixed_r4
  ```

### Reports
- `WINDOW_CURVES.md`: Visualization and analysis
  - Top 10 head curves
  - Aggregate mean curves
  - Divergence point r₀
- `REPRO_STEPS.md`: Exact reproduction instructions
- `MANIFEST.sha256`: File integrity hashes

## Predictions

Based on Campaign A-C results:
- **r=1**: No divergence (already proven)
- **r=2**: Minimal divergence (<0.05 mean delta)
- **r=3**: Moderate divergence (0.05-0.15 mean delta)
- **r=4**: Significant divergence (>0.15 mean delta)
- **r₀**: Expected between 2 and 3

## Analysis Plan

1. Run all 100 heads through 5 modes
2. Compute delta matrices
3. Identify divergence point r₀
4. Plot delta curves for visualization
5. Document patterns and thresholds

## Declaration

This plan is committed before execution. No thresholds will be changed. No promotions will occur. This is purely a measurement campaign to understand window elasticity.

---
*Registered: 2025-01-06T14:00:00Z*