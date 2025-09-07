# Analysis Plan v5.2: Content-Aware Generation

**Date**: 2025-01-07  
**Version**: 5.2.0  
**Pre-reg Hash**: [TO BE COMPUTED POST-COMMIT]

## Executive Summary

Pivot from post-hoc filtering to content-aware generation. Heads must carry actual meaning (content nouns, concrete surveying terms) during generation, not just pass syntactic checks. This addresses the root cause of v5.1 saturation: all 200 v4.1.1 heads were function-word salads.

## Frame Definition (Unchanged from v5.1)

### Cryptographic Rails
- **Routes**: GRID-only (W{10,12,14} × {ROWS,BOU,NE,NW})
- **Permutations**: NA-only
- **Lawfulness**: Option-A strict
- **Classings**: {c6a, c6b}
- **Families**: {vigenere, variant_beaufort, beaufort}
- **Periods**: L ∈ [10, 22]
- **Phases**: 0..L-1
- **Anchors**: 0-idx plaintext at fixed positions

### Window & Tokenization
- **Head window**: [0, 74]
- **Tokenization**: v2 (head-only, no inferred splits)
- **Seam**: Ignored for style/gates

## Gate Order (v5.2)

1. **Lawfulness**: encrypts_to_ct = true, anchors at specified 0-idx positions
2. **Near-gate**: 
   - coverage ≥ 0.85
   - f_words ≥ 8
   - has_verb = true
3. **Content constraints** (NEW - enforced during generation):
   - content_ratio ≥ 0.35
   - np_count ≥ 2
   - unique_content_types ≥ 3
   - no_function_run ≥ 3
   - repetition_penalty == 0
4. **Phrase gate**: AND(Flint v2, Generic, Cadence, Context)
5. **Null hypothesis**: 
   - 10k mirrored samples
   - Holm m=2 over {coverage, f_words}
   - adj_p < 0.01 for both metrics

## Content Constraints (NEW in v5.2)

### Generation-Time Enforcement
Must be met both pre-anchor and post-anchor:

| Constraint | Threshold | Description |
|------------|-----------|-------------|
| content_ratio | ≥ 0.35 | Content tokens / total head tokens |
| np_count | ≥ 2 | Noun phrases from POS tagger |
| unique_content_types | ≥ 3 | Distinct content noun types |
| no_function_run | ≥ 3 | Max consecutive function words |
| repetition_penalty | == 0 | No repeated bigrams like "the the" |

### Content Lexicons

**Path**: `experiments/pipeline_v5_2/policies/lexicon.content.json`  
**SHA-256**: [TO BE COMPUTED]

Categories:
- SURVEY_NOUNS: ARC, ANGLE, SECTOR, QUADRANT, MERIDIAN, etc.
- ACTION_VERBS: SET, READ, SIGHT, NOTE, OBSERVE, MARK, etc.
- RELATORS: TO, FROM, ALONG, ACROSS, OVER, AT, etc.
- MEASURE_TERMS: DEGREES, MINUTES, SECONDS, TRUE, MAGNETIC, etc.
- NEGATIVE_FILLS: THIS, THAT, THESE, THOSE (to avoid)

### Generation Weights

**Path**: `experiments/pipeline_v5_2/policies/weights.explore_v5_2.json`  
**SHA-256**: [TO BE COMPUTED]

Key weights:
- lambda_content_ratio: 1.0
- lambda_np: 0.8
- lambda_mi: 0.6
- penalty_consec_function: 1.0
- penalty_repetition: 1.0

## Generator Updates (v5.2)

### Template Bank
Content-bearing imperative templates with surveying vocabulary:
- "SET THE LINE TO TRUE MERIDIAN; THEN READ THE DIAL"
- "SIGHT THE MARKER; THEN NOTE THE ANGLE"
- "APPLY DECLINATION; THEN READ BEARING"

Requirements per template:
- Min 2 content nouns
- Min 2 verbs
- At least one RELATOR or MEASURE term

### WFSA Hard Constraints
- Disallow FUNCTION,FUNCTION,FUNCTION sequences
- Enforce content_ratio ≥ 0.35 during decode
- Ensure np_count ≥ 2 via pattern matching

### MCMC Objective
- Add content terms to objective function
- Early stop when all constraints met
- Balance coverage with semantic coherence

## Anchor Placement (v5.2)

### Content-Aware Avoidance
- Do not break inside noun phrases
- Prefer boundaries after RELATORS or before DETERMINERS
- Maintain verb protection (±2 tokens)
- Min spacing: 5 tokens between anchors

### Neutral Repair
- Budget ≤6 tokens
- Must preserve content_ratio ≥ 0.35
- Must preserve np_count ≥ 2
- Reject repairs that violate content constraints

## Context Gate (Unchanged from v5.1)

Same rubric and thresholds:
- overall ≥ 4
- coherence ≥ 4
- fluency ≥ 4
- instructional_fit ≥ 3
- semantic_specificity ≥ 3
- repetition_penalty == 0

**Model**: gpt-4o-mini  
**Prompt SHA-256**: [SAME AS v5.1]

## Cadence Thresholds (Unchanged from v5)

| Metric | Threshold | Type |
|--------|-----------|------| 
| cosine_bigram | ≥ 0.65 | P5 |
| cosine_trigram | ≥ 0.60 | P5 |
| fw_gap_mean | [2.8, 5.2] | P2.5-P97.5 |
| fw_gap_cv | [0.4, 1.2] | P2.5-P97.5 |
| wordlen_chi2 | ≤ 95.0 | P95 |
| vc_ratio | [0.95, 1.15] | P2.5-P97.5 |

## Seeds & Reproducibility

### Seed Recipes (Unchanged)
- **Explore seed**: `SHA256("EXPLORE|{label}|seed:{base_seed}")`
- **Context seed**: `lo64(SHA256("CONTEXT|{label}|{pt_sha}|{model_id}|v5.1"))`
- **Worker seed**: `lo64(SHA256(seed_recipe + "|worker:" + wid))`

### Base Seeds
- Pilot K=100: 1337
- Production K=200: 7689758218473226886

## Run Plan

### Phase 1: Pilot K=100
Acceptance criteria to scale:
- Head gate (pre-anchor) ≥ 80%
- Context pass rate ≥ 50%
- Deltas pass ≥ 25%
- Leakage = 0.000

### Phase 2: Production K=200
Only if pilot passes all criteria

### Phase 3: Promotion & Confirm
- Filter by Context pass
- Standard orbit isolation
- Full gate validation

## Policy Hashes

- **Lexicon SHA-256**: `[TO BE COMPUTED]`
- **Weights SHA-256**: `[TO BE COMPUTED]`
- **Policy.explore_v5_2.json SHA-256**: `[TO BE COMPUTED]`

## Changes from v5.1

1. **Generation-time content enforcement**: Not just post-hoc filtering
2. **Content lexicons**: Surveying vocabulary priors
3. **Template bank**: Content-bearing imperatives
4. **WFSA constraints**: Hard limits on function-word runs
5. **Anchor placement**: Content-aware boundaries

## Expected Outcomes

- Meaningful English heads with surveying vocabulary
- Context Gate pass rate >50% (vs 0% in v5.1)
- Balanced coverage and semantic coherence
- Natural-sounding instructional cadence

## Validation Requirements

- All content constraints validated pre/post anchor
- Context Gate evaluation for all candidates
- Cached LLM responses for audit
- Full schema compliance

---
END OF PRE-REGISTRATION