# Explore v4.1 Sanity Check Analysis

## Summary

The v4.1 language-first pipeline with improved anchor placement shows mixed results:

### Successes
- **Excellent score management**: Predicted drops ~2.5, actual drops range from -5 to +5 (near zero average)
- **Function word preservation**: Maintaining 12-21 f-words post-insertion (good retention)
- **Zero leakage**: All heads pass leakage test (0.000 diff)
- **MCMC optimization**: 100% of heads meet criteria after optimization

### Challenges
- **Low gate pass rate**: Only 3/10 heads (30%) meet both f-words ≥8 AND has_verb requirements
- **Verb loss**: 70% of heads lose their verbs during anchor insertion
- **Recovery issues**: Neutral repair showing limited effectiveness (0-75% recovery)

## Root Cause Analysis

### 1. MCMC Output Quality
The MCMC is producing heads that are mostly function words with minimal content:
- Example: "ARE THERE YOUR ONE ITS ON ALL SO WHO THIS HAS IN OR BUT OF NOT WE WAIT OR"
- High f-word count (16-19) but only 1-2 verbs per head
- Verbs are isolated and easily disrupted

### 2. Anchor Placement Issues
Token-boundary insertion improvements:
- Successfully avoiding early positions (positions now >3)
- Better f-word preservation
- But still disrupting verb connections

### 3. Repair Limitations
Enhanced repair is not recovering verbs effectively:
- Can add/swap function words
- Cannot reconstruct lost verb phrases
- Limited by nearby context

## Recommendations

### Immediate Actions
1. **Adjust MCMC weights**: Increase verb weight (λ_verb) to ensure more robust verb presence
2. **Protect verb phrases**: Modify placement to avoid positions within 15 chars of verbs
3. **Enhance repair**: Add verb-specific recovery moves

### Before Scaling to 200 Heads
- Need to achieve ≥80% gate pass rate (8/10 heads)
- Current 30% rate would yield only 60/200 survivors at scale
- Focus on verb preservation as primary bottleneck

## Metrics Comparison

| Metric | Target | v4.1 Original | v4.1 Improved |
|--------|--------|---------------|---------------|
| Gate Pass | 80% | 20% | 30% |
| Avg Drop | <30% | 4.2% | ~0% |
| F-words Post | ≥8 | 3-6 | 12-21 |
| Has Verb | True | 20% | 30% |
| Leakage | 0.000 | 0.000 | 0.000 |

## Next Steps

1. **Fix verb preservation** in MCMC generation (increase verb diversity)
2. **Refine placement** to protect verb phrases better
3. **Re-test** with adjusted parameters
4. **Scale to 200** only after achieving 80% gate pass rate

The placement mechanics are working well for score and f-words, but verb preservation remains the critical bottleneck preventing scale-up to 200 heads.