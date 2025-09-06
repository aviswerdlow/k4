# Explore v4 - Sensitivity-led, Pareto Generation Analysis Plan

**Pre-Registration Date:** 2025-01-06  
**Branch:** pipeline-v4-explore-sensitivity-20250106  
**Commit Hash:** 9ce4d3b  
**Global Seed:** 1337  

## Core Hypothesis

By generating heads that maximize structure in the blinded space and placing anchors where they do the least damage (via sensitivity analysis and Pareto optimization), we can overcome the trade-off between anchor alignment and surviving blinding that defeated v3.

## Invariants (Explore Rails)

- **Family:** NA-only T₂ family
- **Validator:** Option-A available but not solved in Explore
- **Head Window:** [0,74]
- **Tokenization:** v2
- **Seam:** Ignored
- **Anchor Scoring:** BEFORE blinding
- **Language Scoring:** On BLINDED text
- **Deltas:** vs windowed/shuffled baselines exactly as in v2.3/v3
- **Thresholds:** δ_windowed > 0.05, δ_shuffled > 0.10 (calibrated ROC FPR ~0%)

## Track Specifications

### Track A: Blinded-first MCMC + Saliency-aware Anchor Placement

**Components:**
1. **Blinded-first generator** (`gen_blinded_mcmc.py`): Generate 1000 heads maximizing blinded n-gram quality
2. **Saliency map** (`saliency_map.py`): Compute per-position contribution to blinded score
3. **Pareto anchor placement** (`place_anchors_pareto.py`): Optimize (anchor_cost, score_drop) jointly
4. **Neutral repair** (`neutral_repair.py`): Saliency-preserving transforms to recover score
5. **Explore scoring** (`run_explore_v4.py`): Standard pipeline with anchors→blind→deltas

**Objective (unanchored):**
```
S_blind = α * z_trigram_blinded + β * z_bigram_blinded 
         + γ * z_compress_blinded
         - λ_content * max(0, 6 - content_count_blinded)
         - λ_repeat * max(0, max_repeat_non_anchor_content_blinded - 2)
```

**Stop Rule:** After K=200 heads or when <5 within ε=0.10 after 100 candidates

### Track B: Pareto MCMC (Anchors Inside Sampler)

**Script:** `gen_pareto_joint.py`  
**Method:** ε-Pareto MCMC with state = head WITH anchors already placed  
**Objectives:**
- f₁ = -C_anchor (0 in fixed mode, small in windowed)
- f₂ = S_blind (blinded language score)

**Stop Rule:** Pareto front stabilization for 500 iterations or 8 hours

### Track C: Sensitivity-aware Cipher-space Search

**Script:** `cipher_space_sensitivity.py`  
**Method:** T₂/T₁ hill-climb with sensitivity regularizer  
**Objective:** maximize S_blind - μ * saliency_in_anchor_windows

**Stop Rule:** Best objective stalls for 1000 steps or 8 hours

## Promotion Gate (Unchanged)

A head enters `promotion_queue.json` only if ALL are true:
1. Beats both deltas under fixed + ≥1 windowed mode in ≥2 GRID variants
2. Survives orbits (no collapse across ≥10 neighbors)
3. 1k nulls feasibility: both metrics p_raw < 0.01 in two independent replicates

## Deliverables

Per Track:
- `EXPLORE_MATRIX.csv` - Full scoring results
- `SALIENCY.json` - Position sensitivity maps (Track A exemplars)
- `ORBIT_SUMMARY.json` - Stability analysis for passers
- `FAST_NULLS.json` - Null hypothesis testing for passers
- `MANIFEST.sha256` - File integrity
- `REPRO_STEPS.md` - Reproducibility documentation

Consolidated:
- `DASHBOARD.csv` - Summary across all tracks
- `EXPLORE_REPORT.md` - Analysis and conclusions

## Stop Rules & Time Boxes

- **Track A:** Stop after K=200 saliency-placed heads or <5 within ε=0.10 after 100
- **Track B:** Stop when Pareto front stable for 500 iterations or 8 hours
- **Track C:** Stop when best objective stalls for 1000 steps or 8 hours

## Success Criteria

Primary: At least one head passes both delta thresholds with orbit stability
Secondary: Improved delta scores compared to v3 baseline
Tertiary: Demonstrate that sensitivity-aware placement recovers S_blind

## Seed Documentation

- Global generation seed: 1337
- Per-worker null seeds: Derived deterministically as seed + worker_id * 1000
- All seeds documented in `REPRO_STEPS.md` for each run

---

**Pre-Registration Complete at Commit:** 9ce4d3b