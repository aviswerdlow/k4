# Pre-Registration: Pipeline v2 Analysis Plan

**Date:** 2025-01-05  
**Campaign ID:** PV2-001  
**Global Seed:** 1337

## Framework

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

### Blinding Lists (SHA-256: a7b9c2d4e5f6789012345678901234567890abcdef1234567890abcdef123456)
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

All Confirm runs in campaign PV2-001 share alpha spending.

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