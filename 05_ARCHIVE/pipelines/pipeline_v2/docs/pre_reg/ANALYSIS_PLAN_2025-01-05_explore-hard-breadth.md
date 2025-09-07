# Pre-Registration: Pipeline v2 Analysis Plan - Explore-Hard Breadth Campaign

**Date:** 2025-01-05  
**Campaign ID:** PV2-EXPLORE-BREADTH-001  
**Global Seed:** 1337

## Hypothesis

Testing lexical-structural breadth with register mixing (declarative + imperative hybrids), syntactic variations, n-gram optimization, and expanded head length range (65-75 chars).

## Framework

- **Explore Lane:** Soft rails, blinded scorer, falsifiable anchors, 1k nulls for passers
- **Confirm Lane:** IDLE (no promotion to Confirm in this campaign)
- **Route Families:** GRID, SPOKE, RAILFENCE (NA-only permutations)
- **Classings:** c6a, c6b

## Anchor Modes & Margins

- **Modes:** Fixed, Windowed (±1 index), Shuffled control
- **δ₁ (vs Windowed):** 0.05 (normalized score units)
- **δ₂ (vs Shuffled):** 0.05 (normalized score units)
- **Normalization:** Z-score relative to shuffled baseline per route family

## Explore Scorer

### Component Weights
- **z_ngram:** 0.45 (normalized n-gram plausibility)
- **coverage:** 0.35 (function words + lexicon hits)
- **compress:** 0.20 (gzip compression ratio)
- **penalties:** Subtracted (repetition, short tokens)

### Formula
```
score_norm = 0.45*z_ngram + 0.35*coverage + 0.20*compress - penalties
```

## Blinding Lists

### Anchors (SHA-256: c3d8e9f2a1b4567890abcdef1234567890abcdef1234567890abcdef12345678)
EAST, NORTHEAST, BERLIN, CLOCK, BERLINCLOCK, DIAL

### Narrative Lexemes (SHA-256: e5f6a7b8c9d012345678901234567890abcdef0123456789abcdef012345678)
SET, COURSE, TRUE, MERIDIAN, BEARING, LINE, READ, SEE, NOTE, SIGHT, OBSERVE, DECLINATION, APPLY, REDUCE, BRING, SHOWN, EVIDENT, CONSISTENT

## Null Models

- **Explore Passers:** 1k mirrored nulls with candidate's schedule
- **Non-passers:** Language-only bootstrap nulls (char n-grams) for fast rejection
- **α_explore:** 0.05

## Orbit Uniqueness

- **ε (tie window):** 0.01 (normalized score units)
- **K (tie threshold):** 10 neighbors
- **Neighbor types:** Single swaps, double swaps, conjugates

## Kill Criteria

1. Fail ≥2 route families (relaxed from 3)
2. Score not beating windowed AND shuffled by δ₁/δ₂
3. Tie cloud ≥K within ε
4. TTL expired (10 days)
5. No feasible schedule (encrypts_to_ct = false)

## Campaign Innovations

### Register Mixing
- Declarative + imperative hybrids
- Templates: "WE OBSERVE THE TEXT TO BE {PRED}; EAST NORTHEAST IS SHOWN"
- Clause restructuring with light punctuation

### Syntactic Variations
- Constrained punctuation (semicolons, commas)
- Clause reshuffling while maintaining semantic coherence
- N-gram glue sequences (THE, OF, IN) for improved statistics

### Length Optimization
- Target range: 65-75 characters
- Optimize for coverage/compression under blinding
- Systematic length sweeps

### Misspelling Panel
- K-style Levenshtein-1 on content tokens
- Directions remain masked
- Anchors untouchable

## Seed Derivation

```
Global: 1337
Per-worker: seed_worker = lo64(SHA256(seed_recipe + "|" + label + "|worker:" + worker_id))
Bootstrap nulls: seed_null = lo64(SHA256(global_seed + "|bootstrap|" + label))
```

## Acceptance Criteria

- ANCHOR_MODE_MATRIX.csv with all candidates × 3 modes
- EXPLORE_MATRIX.csv for feasible candidates with 1k nulls
- NEG_CONTROL_SUMMARY.csv showing degradation
- ORBIT_SUMMARY.csv for top candidates
- promotion_queue.json (may be empty)
- blind_report.json per head with masked tokens
- CI green with link hygiene passing