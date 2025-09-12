# Pre-Registration: Pipeline v2 Analysis Plan

**Date:** 2025-01-06  
**Campaign ID:** EXPLORE_I_DATA_DRIVEN_SEARCH  
**Global Seed:** 1337

## Campaign I: Data-Driven Head Search

### Hypothesis
Heads generated through n-gram constrained sampling to maximize letter regularity under blinding will explore a broader search space but remain below promotion thresholds.

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
- Same tokens as Campaign H

#### Sampling Configuration
- **Corpus**: English character-level Markov (bi/tri-gram)
- **Corpus SHA-256**: [TO BE COMPUTED]
- **Beam width**: 50
- **Batches**: 20
- **Constraints**:
  - Enforce corridor at [21,25]
  - Avoid masked tokens outside anchor positions
  - Head length ≤ 75 chars
  - Rank by z_ngram after blinding

#### Thresholds
- **δ₁ (vs Windowed)**: 0.05
- **δ₂ (vs Shuffled)**: 0.10
- **α_explore**: 0.05
- **Nulls**: 1k mirrored for passers only
- **TTL**: 10 days

### Expected Outcomes
- **Heads generated**: 2000-5000
- **Higher z_ngram scores** due to optimization
- **Corridor alignment**: ~100% (enforced)
- **Promotions**: 0 expected (blinding prevents leakage)

### Success Criteria
- Demonstrate whether blind letter-regularity alone can beat δ margins
- Maintain Explore discipline (no premature promotions)
- CI remains green

### Computational Requirements
- **Sampling time**: ~10 minutes
- **Evaluation time**: ~2 hours (5000 heads × 6 modes × 4 routes)
- **Output size**: ~50MB

## Framework (Pipeline v2)
- **Explore Lane**: Soft rails, blinded scoring, falsifiable anchors, 1k nulls
- **Confirm Lane**: Stays idle (no promotions)
- **Seed Policy**: Global 1337, per-worker lo64(SHA256(seed + "|" + label + "|worker:" + id))