# CONFIRM SATURATED - BLINDED_CH00_I003

## Status: SATURATED

The candidate BLINDED_CH00_I003 has **passed feasibility** (encrypts_to_ct = TRUE) but **failed quality gates**.

## Gate Results

### Near-Gate: **FAILED**
- Coverage: 0.278 (threshold: 0.85) ❌
- F-words: 0 (threshold: 8) ❌
- Has verb: False ❌

### Phrase Gate: **FAILED**

#### Flint v2 Track: FAILED
- EAST present: True ✅
- NORTHEAST present: True ✅
- Instrument verb: False ❌ (missing READ/SEE/NOTE/SIGHT/OBSERVE)
- Instrument noun: True ✅ (has BERLIN, CLOCK)
- Content count: 16 ✅
- Max repeat: 1 ✅

#### Generic Track: FAILED
- Perplexity percentile: 95.0% (threshold: ≤1%) ❌
- POS score: 0.25 (threshold: ≥0.60) ❌
- Content count: 16 ✅
- Max repeat: 1 ✅

#### AND Gate: FAILED
- Accepted by: NONE
- Both tracks must pass for acceptance

## Feasibility Summary

✅ **Successfully proven lawful:**
- Route: GRID_W14_ROWS (SHA: a5260415...)
- Classing: c6a
- Schedule: Modified with class 4 as Beaufort to avoid K=0 violation
- Encrypts to K4 CT: TRUE
- Option-A constraints: PASSED

## Head Analysis

The head text after anchor insertion:
```
NKQCBNYHFQDZEXQBZOAKMEASTNORTHEASTRQJOYQWZUWPJZZHCJKDMCNUXNPWVZBERLINCLOCKV
```

While the anchors are correctly placed and the text encrypts properly, it lacks:
1. Coherent English words (mostly random letter sequences)
2. Function words necessary for grammatical structure
3. Verbs required for semantic meaning
4. Low perplexity (appears random to language models)

## Conclusion

This candidate demonstrates that the Explore v4 pipeline can generate heads that:
- Pass cipher feasibility with proper anchor placement
- Satisfy Option-A constraints
- Encrypt correctly to K4 ciphertext

However, the blinded MCMC generation optimized for n-gram scores in masked space does not produce semantically meaningful English text when anchors are inserted.

## Recommendation

Do not proceed with nulls or further validation. The fundamental issue is that the generation method (blinded MCMC) produces heads that lack linguistic structure. No amount of null testing will change the fact that the plaintext fails basic English language requirements.

**Next steps:**
- Do not spin up new candidates from this approach
- Consider alternative generation methods that balance:
  - Cipher feasibility
  - Semantic coherence
  - Anchor integration

## Post-Mortem

**Root Cause**: Blinded-first generation preserved masked n-gram quality, but anchor insertion degraded linguistic structure in the head window. Flint and Generic failed under pre-registered thresholds.

**What Worked**:
- Cryptographic feasibility (Option-A, route schedule)
- No leakage in blinding pipeline (delta diff = 0.000)
- Deterministic seeds and reproducible generation

**What Didn't**:
- Head-window English quality after anchor insertion
- Function word density and verb presence
- Perplexity and POS-trigram scores

**Next Options** (not started unless green-lit):
- Grammar-first constrained generation (WFSA/PCFG with POS templates) before anchor placement
- Anchor placeholders during generation ([EAST], [NORTHEAST], [BERLIN], [CLOCK]) with constrained in-place rewriter for final substitution + repair
- Constrained inpainting: preserve saliency regions; replace only low-saliency tokens post-anchor
- Keep Explore idle until a survivor clears both deltas in blinded space and maintains Flint/Generic when anchors are inserted

---

*Saturated: 2025-01-06*
*Reason: Failed both near-gate and phrase gate quality checks*
*Candidate is SATURATED at Confirm under the current policy*