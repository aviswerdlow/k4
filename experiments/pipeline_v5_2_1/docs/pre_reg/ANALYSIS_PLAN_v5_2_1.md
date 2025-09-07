# Analysis Plan v5.2.1: Content+Function Harmonization

**Version**: 5.2.1  
**Date**: 2025-01-07  
**Commit**: [TO BE FILLED AFTER COMMIT]  
**Status**: Pre-registered

## Executive Summary

v5.2.1 addresses the content-function paradox identified in v5.2's saturation by harmonizing content-aware generation with function word requirements. This is achieved through generation improvements only - all gates remain unchanged from v5.2.

## Rails and Gates (UNCHANGED from v5.2)

### Near Gate
- **Coverage**: ≥ 0.85
- **Function words**: ≥ 8
- **Has verb**: true
- **Function word set**: {THE, OF, AND, TO, IN, IS, ARE, WAS, THEN, THERE, HERE, WITH, AT, BY, WE}

### Phrase Gate (AND-gate)
- **Flint v2**: Declination pattern with TRUE, instrument verb, EAST+NORTHEAST, instrument noun
- **Generic**: Perplexity and POS-trigram thresholds

### Additional Gates
- **Cadence**: Style metrics within bounds
- **Context**: Overall ≥ 4, semantic_specificity ≥ 3, no repetition penalty
- **Nulls**: 10k samples, Holm correction m=2, adj_p < 0.01

## Generation Changes (NEW)

### 1. Template Bank Enhancement
Function-rich scaffolds that naturally incorporate 8+ function words while maintaining semantic coherence:
- Pattern: [VERB] THE [NOUN] TO THE [ADJ] [NOUN] AND THEN [VERB] THE [NOUN]
- Ensures minimum function word count through structural design

### 2. MCMC Objective Function
**Hard constraints** (reject if unmet):
- f_words_pre ≥ 8
- has_verb_pre = true
- coverage_pre ≥ 0.85

**Soft scoring**:
- λ_fw * f_words (cap at 11): 0.9
- λ_ng * blinded trigram: 1.0
- λ_pat * verb pattern: 0.8
- λ_ctx * content ratio: 0.7
- λ_run * repetition penalty: -0.6

### 3. Function Glue Augmentation
Constrained insertion of function-rich phrases at low-saliency positions:
- Phrases: {OF THE, TO THE, IN THE, AND THEN, AND WE, BY THE, AT THE}
- Maximum 2 insertions
- Only when f_words < 8
- Preserve macro-pattern and verb structures

### 4. Anchor Placement
- Token-boundary aware placement (α=0.6, β=0.2, γ=0.2)
- Repair budget ≤ 6 moves
- Post-anchor glue insertion if f_words_post < 8
- Leakage requirement: 0.000

## Seeds and Reproducibility

- **MASTER_SEED**: 1337
- **Per-head derivation**: SHA256(f"v5.2.1_{label}_{MASTER_SEED}")
- **Worker seeds**: Deterministic from master
- **Random state**: Fully reproducible

## Stop Rules

### Pilot (K=50)
- **Near-gate pre-anchor**: ≥ 80% pass
- **Near-gate post-anchor**: ≥ 60% pass
- **Leakage**: = 0.000
- **Action if fail**: STOP, mark SATURATED

### Production (K=200)
- **Near-gate thresholds**: Same as pilot
- **Promotion requirements**: Beat both deltas (fixed+windowed), orbit isolated, 1k fast nulls pass
- **Minimum promotions**: ≥ 10 candidates
- **Action if fail**: Mark SATURATED

## Artifacts and Schema

### Required Files
- `EXPLORE_MATRIX.csv`: Full metrics including f_words pre/post, content_ratio, leakage
- `DASHBOARD.csv`: Stage-by-stage counts
- `promotion_queue.json`: Candidates beating both deltas
- `MANIFEST.sha256`: Bundle integrity
- `README.md`: Human-readable summary
- `REPRO_STEPS.md`: Exact reproduction instructions

### Policy Files
- `policies/templates.json`: Function-rich template bank
- `policies/weights.v5_2_1.json`: MCMC weights (SHA-256 pinned)
- `policies/lexicon.content.json`: Surveying vocabulary (unchanged)
- `POLICIES.SHA256`: Hash manifest of all policy files

## Success Criteria

1. **Pilot Success**: Meet all pilot thresholds
2. **Production Success**: ≥ 10 promotion-grade candidates
3. **Confirm Success**: ≥ 1 winner passing all gates
4. **Alternative**: Clean saturation documentation if criteria not met

## Quality Assurance

- **Bundle validation**: `validate_bundle.py` with strict schema
- **Hash manifests**: `make_manifest.py` for all artifacts
- **Duplicate detection**: No identical head strings
- **Leakage CI**: Zero tolerance for anchor leakage

## Guardrails

1. **No gate changes**: Near-gate bar remains at f_words ≥ 8
2. **Deterministic seeds**: MASTER_SEED = 1337 throughout
3. **Policy pinning**: All JSON/weights SHA-256 hashed
4. **Clean saturation**: If fail, document cause precisely

---
**Pre-registered**: 2025-01-07  
**Principal**: v5.2.1 Content+Function Harmonization  
**Predecessor**: v5.2 (SATURATED at f_words < 8)