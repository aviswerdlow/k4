# Analysis Plan v5: Mandatory Cadence Gate

**Date**: 2025-01-07  
**Version**: 5.0.0  
**Pre-reg Hash**: [TO BE COMPUTED POST-COMMIT]

## Executive Summary

Promoting cadence (style) from report-only to mandatory hard gate. No word-salad plaintexts will be published.

## Frame Definition

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

## Gate Order (v5)

1. **Lawfulness**: encrypts_to_ct = true, anchors at specified 0-idx positions
2. **Near-gate**: 
   - coverage ≥ 0.85
   - f_words ≥ 8
   - has_verb = true
3. **Phrase gate**: AND(Flint v2, Generic, **Cadence**)
4. **Null hypothesis**: 
   - 10k mirrored samples
   - Holm m=2 over {coverage, f_words}
   - adj_p < 0.01 for both metrics

## Cadence Thresholds (Now Mandatory)

Based on K2 declarative bootstrap (N=1000):

| Metric | Threshold | Type |
|--------|-----------|------|
| cosine_bigram | ≥ 0.65 | P5 |
| cosine_trigram | ≥ 0.60 | P5 |
| fw_gap_mean | [2.8, 5.2] | P2.5-P97.5 |
| fw_gap_cv | [0.4, 1.2] | P2.5-P97.5 |
| wordlen_chi2 | ≤ 95.0 | P95 |
| vc_ratio | [0.95, 1.15] | P2.5-P97.5 |

All six primitives must pass for cadence gate to pass.

## Seeds & Reproducibility

### Seed Recipes (Unchanged from v4)
- **Explore seed**: `SHA256("EXPLORE|{label}|seed:{base_seed}")`
- **Confirm seed**: `SHA256("CONFIRM|{label}|seed:{base_seed}")`
- **Worker seed**: `lo64(SHA256(seed_recipe + "|worker:" + wid))`
- **Null seed**: `SHA256("NULL|{label}|{metric}|sample:{i}")`

### Base Seeds
- Explore: 7689758218473226886
- Confirm: Derived from explore
- Nulls: Per-sample deterministic

## Policy Hashes

- **Cadence thresholds SHA-256**: `[TO BE COMPUTED]`
- **Policy.cadence.json SHA-256**: `[TO BE COMPUTED]`
- **Policy.phrase_gate.v5.json SHA-256**: `[TO BE COMPUTED]`

## Changes from v4

1. **Cadence promotion**: Report-only → Mandatory
2. **Phrase gate**: AND(Flint v2, Generic) → AND(Flint v2, Generic, Cadence)
3. **Schema updates**: cadence track required in phrase_gate_report.json
4. **Retraction**: HEAD_147_B retracted for failing cadence

## Validation Requirements

- All v5 bundles must pass strict schema validation
- phrase_gate_report.json must include cadence in accepted_by for passers
- Cadence metrics must be recorded with raw values and pass/fail status

## Expected Outcomes

- Elimination of word-salad plaintexts
- Possible saturation if no candidates pass style requirements
- Higher quality plaintexts that read as natural language

---
END OF PRE-REGISTRATION