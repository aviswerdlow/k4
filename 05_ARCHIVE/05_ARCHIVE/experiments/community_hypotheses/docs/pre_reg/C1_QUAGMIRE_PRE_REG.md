# Campaign C1: Quagmire III Pre-Registration

**Date:** 2025-01-06  
**Campaign:** C1_QUAGMIRE_III  
**Status:** PRE-REGISTERED

## Hypothesis

The K4 plaintext was encrypted using a Quagmire III cipher with:
- A scrambled alphabet (not standard A-Z)
- Variable offsets following a pattern (fixed, progressive, fibonacci, or prime)
- Possible key indicator embedded in the plaintext

## Method

### Quagmire III Cipher
- Polyalphabetic substitution cipher
- Uses a scrambled alphabet as the cipher alphabet
- Each position uses a different Caesar shift based on a key

### Search Space
- **Alphabets**: 4 variations including KRYPTOS-based permutations
- **Offset Patterns**: 4 types (fixed, progressive, fibonacci, prime)
- **Total Combinations**: 100 heads sampling the space

## Pre-Registered Parameters

### Generation
```python
{
    "num_heads": 100,
    "seed": 1337,
    "alphabet_variations": [
        "KRYPTOSABCDEFGHIJLMNQUVWXZ",  # KRYPTOS-first
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # Standard
        "ZYXWVUTSRQPONMLKJIHGFEDCBA",  # Reversed
        "KRYPTOSBDEFGHIJLMNQUVWXZAC"   # KRYPTOS-shifted
    ],
    "offset_patterns": ["fixed", "progressive", "fibonacci", "prime"]
}
```

### Validation (Explore Pipeline)
```python
{
    "anchor_modes": ["fixed", "windowed_r2", "windowed_r5", "shuffled"],
    "blinding": true,
    "controls": "matched_ngram",
    "delta_thresholds": {
        "δ₁": 0.05,  # vs windowed
        "δ₂": 0.10   # vs shuffled
    }
}
```

## Success Criteria

A head is promoted to Confirm if:
1. δ₁ > 0.05 (beats windowed baseline)
2. δ₂ > 0.10 (beats shuffled baseline)
3. Survives on ≥2 window policies
4. Passes 1k null hypothesis tests

## Expected Outcomes

### If Quagmire III is Correct
- Some decryptions will produce coherent English
- Anchor terms may appear at expected positions
- Language scores will significantly exceed baselines
- Pattern will be reproducible with specific alphabet/offset combo

### If Quagmire III is Incorrect
- Decryptions will produce gibberish
- No significant deltas vs baselines
- 0 promotions to Confirm (expected outcome)

## Falsifiability

This hypothesis is falsifiable because:
1. **Specific Method**: Quagmire III has precise mechanics
2. **Measurable Output**: Language coherence is quantifiable
3. **Clear Thresholds**: Pre-registered delta requirements
4. **Reproducible**: Fixed seed ensures repeatability

## Exploration Rails

- **No Cherry-Picking**: All 100 heads evaluated equally
- **Blinded Scoring**: Anchor/narrative terms masked
- **Hard Controls**: Matched n-gram distributions
- **No Tuning**: Parameters fixed before execution

## Files

- **Adapter**: `adapters/gen_quagmireIII.py`
- **Heads**: `runs/2025-01-06-campaign-c1/heads_c1_quagmire.json`
- **Scores**: `runs/2025-01-06-campaign-c1/scores_c1_*.json`
- **Manifest**: `runs/2025-01-06-campaign-c1/manifest_c1.json`

## Integrity

**Pre-Registration Hash**: [To be computed]  
**Locked Parameters**: No changes after this registration  
**Execution Date**: 2025-01-06

---

*This pre-registration locks in all parameters before Campaign C1 execution.*