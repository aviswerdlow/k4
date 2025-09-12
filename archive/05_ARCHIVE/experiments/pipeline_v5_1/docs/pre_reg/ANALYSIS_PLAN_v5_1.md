# Analysis Plan v5.1: LLM Context Gate

**Date**: 2025-01-07  
**Version**: 5.1.0  
**Pre-reg Hash**: [TO BE COMPUTED POST-COMMIT]

## Executive Summary

Adding LLM-based Context Gate to reject syntactically legal but semantically empty heads (word-salad, tautological detours, incoherent connectives). This gate ensures heads read as meaningful English with surveying-instruction cadence.

## Frame Definition (Unchanged from v5)

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

## Gate Order (v5.1)

1. **Lawfulness**: encrypts_to_ct = true, anchors at specified 0-idx positions
2. **Near-gate**: 
   - coverage ≥ 0.85
   - f_words ≥ 8
   - has_verb = true
3. **Phrase gate**: AND(Flint v2, Generic, Cadence, **Context**)
4. **Null hypothesis**: 
   - 10k mirrored samples
   - Holm m=2 over {coverage, f_words}
   - adj_p < 0.01 for both metrics

## Context Gate (New in v5.1)

### Purpose
- **Does**: Reject heads that are syntactically legal but semantically empty
- **Does not**: Replace cryptographic gates or quantitative style gates
- **Placement**: After Cadence passes, before Confirm compute

### Rubric Schema
```json
{
  "label": "string",
  "overall": 1-5,
  "coherence": 1-5,
  "fluency": 1-5,
  "instructional_fit": 0-5,
  "semantic_specificity": 0-5,
  "repetition_penalty": 0-1,
  "notes": "string"
}
```

### Acceptance Thresholds
All conditions must be met:
- overall ≥ 4
- coherence ≥ 4
- fluency ≥ 4
- instructional_fit ≥ 3
- semantic_specificity ≥ 3
- repetition_penalty == 0

### Model Configuration
- **Model ID**: gpt-4o-mini (fixed)
- **Temperature**: 0
- **Top-p**: 0
- **Max tokens**: 256
- **Seed**: lo64(SHA256("CONTEXT|{label}|{pt_sha}|{model_id}|v5.1"))

### Prompt Template

**System Prompt**:
```
You are a strict evaluator of one-sentence English instructions. Output JSON only; never prose. Penalize function-word salads and incoherent sequences.
```

**User Prompt**:
```
Evaluate the head window (0..74) of a proposed K4 clause.

TEXT (head only):
{HEAD_TEXT_0_74}

CONTEXT:
- The clause should read like a compact instruction (surveying/navigation cadence).
- Anchors like EAST/NORTHEAST and nouns like BERLIN/CLOCK may appear, but do not assume they make the sentence meaningful.
- Avoid crediting repeated function words or meaningless connectives.

Return JSON with these fields:
- label: string
- overall: 1-5 (general quality)
- coherence: 1-5 (logical flow; avoids non-sequiturs)
- fluency: 1-5 (grammar & naturalness)
- instructional_fit: 0-5 (imperative/surveying vibe)
- semantic_specificity: 0-5 (concrete, content-bearing tokens)
- repetition_penalty: 0-1 (1 if repeated words like "the the")
- notes: one short sentence why
```

**Prompt SHA-256**: [TO BE COMPUTED]

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

### Seed Recipes (Context Gate)
- **Context seed**: `lo64(SHA256("CONTEXT|{label}|{pt_sha}|{model_id}|v5.1"))`
- **Deterministic caching**: Hash(model_id, system_prompt, user_prompt) → cache key

### Base Seeds (Unchanged)
- Explore: 7689758218473226886
- Confirm: Derived from explore
- Nulls: Per-sample deterministic

## Policy Hashes

- **Context prompt SHA-256**: `[TO BE COMPUTED]`
- **Policy.context_gate.v5_1.json SHA-256**: `[TO BE COMPUTED]`
- **Policy.phrase_gate.v5_1.json SHA-256**: `[TO BE COMPUTED]`

## Changes from v5

1. **Context Gate addition**: LLM-based semantic evaluation
2. **Phrase gate**: AND(Flint v2, Generic, Cadence) → AND(Flint v2, Generic, Cadence, Context)
3. **Schema updates**: context_gate_report.json required for all candidates
4. **Caching**: Raw LLM responses cached for reproducibility

## Validation Requirements

- All v5.1 bundles must pass strict schema validation
- context_gate_report.json must be present with all rubric fields
- Model configuration and prompts must match pre-registered values
- Raw JSON responses must be cached in context/<label>.json

## Expected Outcomes

- Elimination of semantically empty heads beyond cadence metrics
- Higher confidence in linguistic sensibility of published results
- Full auditability through cached LLM responses
- Deterministic reproducibility via fixed seeds and settings

## Governance & Guardrails

- **No moving targets**: Thresholds and prompts pinned in this pre-reg
- **Reproducibility**: Model ID, settings, seeds, prompt hash with every judgment
- **Fail-closed**: Invalid JSON counts as context_pass=false
- **Bias prevention**: LLM sees only head text and rubric, no scores or outcomes

---
END OF PRE-REGISTRATION