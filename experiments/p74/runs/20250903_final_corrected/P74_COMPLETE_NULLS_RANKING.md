# P74 Complete Nulls Analysis - Ranking Report

## Executive Summary

**Key Finding**: All 26 P[74] candidates are statistically equivalent under the complete analysis pipeline.

- **Cryptographic**: All 26 letters are lawful under multi-class schedules
- **AND Gate**: All 26 letters pass both Flint v2 + Generic tracks  
- **Nulls Analysis**: All 26 letters achieve identical statistical significance
- **Discrimination**: The choice of P[74]='T' appears to be based on tie-breaker criteria not captured in our current nulls implementation

## Complete Rankings

Based on the P74_SWEEP_SUMMARY.csv analysis, here are the "next 10 likely winners" after P[74]='T':

### Tier 1: Statistically Identical Alternatives (All Publishable)

All candidates show identical performance metrics:
- **Coverage adj-p**: 0.001 (highly significant)
- **F-words adj-p**: 0.001 (highly significant) 
- **Publishable**: True (all pass adj-p < 0.01 threshold)

**Next 10 Alternatives to P[74]='T' (alphabetical order)**:

1. **P[74]='A'** - AHEJOYOFANANGLEISTHEARC
2. **P[74]='B'** - BHEJOYOFANANGLEISTHEARC  
3. **P[74]='C'** - CHEJOYOFANANGLEISTHEARC
4. **P[74]='D'** - DHEJOYOFANANGLEISTHEARC
5. **P[74]='E'** - EHEJOYOFANANGLEISTHEARC
6. **P[74]='F'** - FHEJOYOFANANGLEISTHEARC
7. **P[74]='G'** - GHEJOYOFANANGLEISTHEARC
8. **P[74]='H'** - HHEJOYOFANANGLEISTHEARC
9. **P[74]='I'** - IHEJOYOFANANGLEISTHEARC
10. **P[74]='J'** - JHEJOYOFANANGLEISTHEARC

### Linguistic Analysis of Alternatives

**Most Plausible Phrase Patterns**:
- **P[74]='H'**: "H HE JOY" → Could be interpreted as emphatic "H! HE JOY..."
- **P[74]='S'**: "S HE JOY" → Could suggest "SHE JOY" pattern  
- **P[74]='A'**: "A HE JOY" → Article pattern "A HE JOY..."

**Less Natural but Valid**:
- **P[74]='I'**: "I HE JOY" → Personal pronoun pattern
- **P[74]='E'**: "E HE JOY" → Letter sound pattern

## Detailed Analysis Results

### Statistical Performance

All 26 candidates show **identical statistical behavior**:

```
Route: GRID_W14_ROWS, Classing: c6a
├── Lawful: TRUE (all 26)
├── AND Gate: TRUE (all 26) 
│   ├── Flint v2: PASS (domain semantics)
│   └── Generic: PASS (perplexity + POS)
└── Nulls (10K mirrored, Holm m=2):
    ├── Coverage adj-p: 0.001 (all 26)
    ├── F-words adj-p: 0.001 (all 26)
    └── Publishable: TRUE (all 26)
```

### Implications

1. **No Algebraic Forcing**: P[74] is not mathematically constrained by the cipher system
2. **Gate Agnostic**: The AND gate (Flint v2 + Generic) does not discriminate between P[74] candidates
3. **Nulls Equivalence**: Statistical analysis cannot distinguish between alternatives
4. **Decision Gate Compulsion**: The selection of P[74]='T' represents effective policy choice rather than cryptographic necessity

### Winner Selection Criteria

Since all candidates are statistically equivalent, the choice of P[74]='T' must be based on **tie-breaker criteria** such as:

1. **Coverage fine-grained comparison** (beyond 3 decimal places)
2. **Function words fine-grained comparison** 
3. **Additional metrics** not captured in current analysis
4. **Linguistic coherence preferences**
5. **Pre-registered tie-breaker rules**

## Methodology Notes

- **Data Source**: P74_SWEEP_SUMMARY.csv (complete 26-candidate analysis)
- **Nulls**: 10,000 mirrored nulls per candidate
- **Correction**: Holm m=2 over {coverage, f_words}
- **Threshold**: adj-p < 0.01 for publishable status
- **Deterministic**: All seeds derived from cryptographic hashes

## Conclusion

**Answer to "Next 10 Likely Winners"**: 

From a statistical significance perspective, there are **NO meaningful alternatives** to P[74]='T' - all 26 candidates are equally publishable. The selection represents **decision-gate compulsion** based on fine-grained tie-breakers rather than fundamental cryptographic or linguistic constraints.

**Most Plausible Alternatives** (linguistic coherence):
1. P[74]='H' ("HHEJOY...")  
2. P[74]='S' ("SHEJOY...")
3. P[74]='A' ("AHEJOY...")

But statistically, **any of the 26 letters would be equally valid** as "THE JOY" bridge character.

---

*Analysis Date: 2025-09-03*  
*Method: Complete P74 sweep with 10K mirrored nulls*  
*Status: All 26 candidates statistically equivalent*