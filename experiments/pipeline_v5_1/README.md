# Pipeline v5.1: LLM Context Gate

## Overview

Version 5.1 adds an LLM-based Context Gate to reject syntactically legal but semantically empty plaintexts (word-salads). This provides the critical "sanity check" between cryptographic validity and meaningful English.

## What's New in v5.1

1. **Context Gate**: LLM evaluation of semantic content
2. **Six-metric rubric**: coherence, fluency, instructional_fit, semantic_specificity, repetition_penalty, overall
3. **Deterministic evaluation**: Fixed model, prompts, and seeds
4. **Full auditability**: Cached responses and SHA-256 hashes

## Gate Order

1. **Lawfulness** (cryptographic validity)
2. **Near-gate** (coverage, f_words, has_verb)
3. **Phrase gate**: AND(Flint v2, Generic, Cadence, **Context**)
4. **Null hypothesis** (statistical significance)

## Implementation

### Scripts

- `run_context_gate.py`: Production evaluator using OpenAI API
- `run_context_gate_mock.py`: Mock evaluator using heuristics
- Both generate identical output formats

### Running Context Gate

```bash
# With real LLM (requires OpenAI API key)
python3 run_context_gate.py \
  --catalog path/to/PLAINTEXT_CATALOG.csv \
  --out runs/context_gate_v5_1/ \
  --api-key YOUR_API_KEY

# With mock evaluator (for testing)
python3 run_context_gate_mock.py \
  --catalog path/to/PLAINTEXT_CATALOG.csv \
  --out runs/context_gate_v5_1/
```

### Output Structure

```
runs/context_gate_v5_1/
├── CONTEXT_JUDGMENTS.csv      # All evaluations with pass/fail
├── CONTEXT_SUMMARY.md          # Statistical summary
├── MANIFEST.sha256            # File hashes for verification
└── context/                   # Individual JSON responses
    ├── HEAD_00_B.json
    ├── HEAD_01_B.json
    └── ...
```

## Thresholds

All must pass:
- **overall** ≥ 4
- **coherence** ≥ 4 (logical flow)
- **fluency** ≥ 4 (grammar)
- **instructional_fit** ≥ 3 (surveying vibe)
- **semantic_specificity** ≥ 3 (content words)
- **repetition_penalty** == 0 (no "the the")

## Results on v4.1.1 K=200

- **Evaluated**: 200 candidates
- **Passed Context Gate**: 0 (0%)
- **Critical failure**: semantic_specificity (all scored 1/5)
- **Conclusion**: Complete saturation - all are function-word salads

## Reproducibility

### Deterministic Settings
- Model: `gpt-4o-mini` (fixed)
- Temperature: 0
- Top-p: 0
- Seed: `lo64(SHA256("CONTEXT|{label}|{pt_sha}|{model_id}|v5.1"))`

### Cached Responses
All LLM responses cached in `context/<label>.json` for replay and audit.

## Integration with Confirm Pipeline

```python
# Filter promotion queue by Context Gate
python3 select_next_confirm_candidate.py \
  --queue promotion_queue.json \
  --context CONTEXT_JUDGMENTS.csv \
  --require-context-pass \
  --out next.json
```

## Mock Evaluator Details

The mock evaluator (`run_context_gate_mock.py`) uses heuristics:
- Counts function words vs content words
- Detects repetition patterns
- Checks for surveying keywords
- Assigns scores based on ratios

While not as sophisticated as an LLM, it correctly identifies function-word salads and provides consistent, deterministic results for testing.

## Next Steps

1. **Production deployment**: Use real LLM for final validation
2. **Generator v6**: Add semantic priors to avoid word-salads
3. **Progressive filtering**: Fail fast on obvious rejects
4. **Vocabulary constraints**: Consider surveying term requirements