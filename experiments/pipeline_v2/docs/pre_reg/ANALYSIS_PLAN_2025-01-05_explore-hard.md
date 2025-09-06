# Pre-Registration: Pipeline v2 Analysis Plan - Explore-Hard Campaign

**Date:** 2025-01-05  
**Campaign ID:** PV2-EXPLORE-HARD-001  
**Global Seed:** 1337

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

### Surveying Lexemes (SHA-256: d4e5f6a7b8c9012345678901234567890abcdef0123456789abcdef01234567)
SET, COURSE, TRUE, MERIDIAN, BEARING, LINE, READ, SEE, NOTE, SIGHT, OBSERVE, DECLINATION, APPLY, REDUCE, BRING

## Null Models

- **Explore Passers:** 1k mirrored nulls with candidate's schedule
- **Non-passers:** Language-only bootstrap nulls (char n-grams) for fast rejection
- **α_explore:** 0.05

## Orbit Uniqueness

- **ε (tie window):** 0.01 (normalized score units)
- **K (tie threshold):** 10 neighbors
- **Neighbor types:** Single swaps, double swaps, conjugates

## Kill Criteria

1. Fail ≥3 route families
2. Score not beating windowed AND shuffled by δ₁/δ₂
3. Tie cloud ≥K within ε
4. TTL expired (10 days)
5. No feasible schedule (encrypts_to_ct = false)

## TTL Policy

- **Expiry:** 10 days
- **Archive:** Move to runs/archive/ with reason
- **Log:** Update TTL_LOG.md

## Seed Derivation

```
Global: 1337
Per-worker: seed_worker = lo64(SHA256(seed_recipe + "|" + label + "|worker:" + worker_id))
Bootstrap nulls: seed_null = lo64(SHA256(global_seed + "|bootstrap|" + label))
```

## Campaign Scope

- **Candidates:** ~500 surveying-grammar heads generated from templates
- **Generation:** Instructional surveying templates with slot expansion
- **Perturbations:** Synonym variants and edit-1 misspellings
- **Head length:** 35-75 characters (head window [0,74])

## Acceptance Criteria

- ANCHOR_MODE_MATRIX.csv with all candidates × 3 modes
- EXPLORE_MATRIX.csv for feasible candidates with 1k nulls
- NEG_CONTROL_SUMMARY.csv showing degradation
- ORBIT_SUMMARY.csv for top candidates
- promotion_queue.json (may be empty)
- CI green with link hygiene passing