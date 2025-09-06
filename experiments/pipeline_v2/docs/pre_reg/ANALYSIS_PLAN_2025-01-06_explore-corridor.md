# Pre-Registration: Pipeline v2 Analysis Plan

**Date:** 2025-01-06  
**Campaign ID:** EXPLORE_CORRIDOR_WINDOW_ELASTICITY  
**Global Seed:** 1337

## Campaign G: Anchor-Aligned Heads & Window Elasticity

### Hypothesis
Heads with anchors placed at expected corridor positions (EAST@21, NORTHEAST@25, BERLINCLOCK@63) will show measurable divergence between fixed and windowed modes when anchors are slightly offset from canonical positions.

### Primary Questions
1. At what window radius r₀ does divergence from fixed mode become measurable (Δ > 0.01)?
2. How does anchor score degradation scale with position offset and typo count?
3. Do corridor-aligned heads show the expected monotonic increase in flexibility: fixed < r=1 < r=2 < r=3 < r=4?

## Methods

### Data Generation
- **Input**: K4 plaintext from Kryptos sculptor
- **Transformations**: 
  - Generate 100 heads with anchors at canonical positions
  - Create systematic offsets: position shifts ±1, ±2, ±3
  - Introduce typos: 0, 1, 2 edit distance
- **Output**: Anchor-aligned heads with controlled variations

### Anchor Corridor Specification
- **EAST**: positions 21-24 (canonical: 21)
- **NORTHEAST**: positions 25-33 (canonical: 25)
- **BERLINCLOCK**: positions 63-73 (canonical: 63)

### Scoring Configuration
- **Anchor Modes**: fixed, windowed(r=1), windowed(r=2), windowed(r=3), windowed(r=4), shuffled
- **Blinding**: anchors and narrative (after anchor scoring)
- **Null Generation**: 1k (Explore lane)
- **Seed**: 1337

### Success Criteria
- **Threshold δ₁**: 0.01 normalized units (measurable divergence)
- **Threshold δ₂**: 0.05 normalized units (promotion threshold - NOT EXPECTED)
- **Statistical Test**: Mean absolute deviation across head variations

## Expected Outcomes

### Primary Outcome
Windowed modes will show increasing tolerance for anchor position variation:
- r=1: Small divergence for ±1 offsets
- r=2: Moderate divergence for ±2 offsets
- r=3-4: Larger divergence, diminishing returns

### Secondary Outcomes
- Anchor score histogram will show clear corridor alignment
- Delta curves will be monotonic with window radius
- No heads will exceed δ₂ threshold (stay in Explore)

## Risk Mitigation
- **Risk 1**: Synthetic heads too artificial → Use K4 plaintext as base
- **Risk 2**: Window search not working → Validated with unit tests and sanity checks

## Computational Requirements
- **Estimated Runtime**: 10 minutes (100 heads × 6 modes)
- **Resource Usage**: <2GB memory, single CPU
- **Output Size**: ~5MB (matrices and reports)

## Post-Analysis Actions
1. Generate corridor histogram showing anchor alignment
2. Create delta curves for window elasticity analysis
3. Document divergence point r₀ and update exploration strategy

## Framework (Pipeline v2)

- **Explore Lane:** Fast triage with soft anchors, blinded scorer, 1k nulls
- **Confirm Lane:** Hard rails with frozen anchors, full gates, 10k nulls
- **Route Families:** GRID, SPOKE, RAILFENCE (NA-only permutations)
- **Classings:** c6a, c6b

## Gate Order (Confirm Lane)

1. Near-gate check
2. Flint v2 & Generic (AND gate), tokenization v2
3. 10k mirrored nulls, Holm m=2
4. Publish if both adj-p < 0.01

## Explore Metrics

### Scorer Components
- **N-gram plausibility:** Weight = 0.4
- **Coverage proxy:** Weight = 0.3  
- **Compressibility:** Weight = 0.3

### Blinding Lists (SHA-256: e5f6a7b8c9d01234)
- Anchor words: EAST, NORTHEAST, BERLINCLOCK
- Narrative lexemes: DIAL, SET, COURSE, TRUE, READ, SEE, NOTE, SIGHT, OBSERVE, MERIDIAN, DECLINATION, BEARING, LINE

## Promotion Thresholds

- **δ₁ (vs Windowed):** 0.05
- **δ₂ (vs Shuffled):** 0.10
- **α_explore:** 0.05 (for 1k nulls)
- **Route families required:** ≥2 of 3

## Null Budgets

- **Explore:** 1k mirrored nulls
- **Confirm:** 10k mirrored nulls

## Kill Criteria

- 3 route family failures → archive
- Orbit ties ≥5 within ε=0.02 → downgrade
- TTL expired (10 days) → archive

## Holm Family

All Confirm runs in this campaign share alpha spending.

## Seed Policy

```
Global: 1337
Per-worker: seed_worker = lo64(SHA256(seed_recipe + "|" + label + "|worker:" + worker_id))
Replicates: Add "|rep:n|" tag before "|worker:..."
```

## Acceptance Criteria

- Explore produces blinded matrices and promotion queue
- Confirm produces full mini-bundles with Holm reports
- All thresholds match this pre-registration
- CI enforces link hygiene and bundle completeness