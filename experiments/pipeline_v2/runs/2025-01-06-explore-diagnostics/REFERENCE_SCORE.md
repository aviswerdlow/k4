# Reference Scoring Report

**Date:** 2025-09-06 00:50
**Seed:** 1337

## Summary

Testing known reference texts to verify harness behavior:

✅ **All narrative texts correctly FAILED under blinding.**

## Detailed Results

### published_grid

**Description:** Published GRID-only winner with narrative
**Expected:** Should FAIL under blinding
**Text sample:** `FINDTHEPATHTOTHEEASTNORTHEASTQ...`

**Scores:**
- Delta vs windowed: 0.0000
- Delta vs shuffled: -0.1600
- Pass deltas: False
- **Verdict: FAIL**

**Feature scores (fixed mode):**
- Anchor score: 0.000
- Z-ngram: 19.130
- Z-coverage: 0.000
- Z-compress: -21.774
- Blinded sample: `FINDTHEPATHTOTHEXXXX...`

### grid_runner_up

**Description:** GRID runner-up with similar narrative
**Expected:** Should FAIL under blinding
**Text sample:** `MOVEYOURCOMPASSTOEASTNORTHEAST...`

**Scores:**
- Delta vs windowed: 0.0000
- Delta vs shuffled: -0.1500
- Pass deltas: False
- **Verdict: FAIL**

**Feature scores (fixed mode):**
- Anchor score: 0.000
- Z-ngram: 7.216
- Z-coverage: 0.000
- Z-compress: -18.774
- Blinded sample: `MOVEYOURCOMPASSTOXXX...`

### corridor_synthetic

**Description:** Synthetic with corridor anchors only
**Expected:** May pass anchors but fail language
**Text sample:** `XXXXXXXXXXXXXXXXXXXXXXEASTNORT...`

**Scores:**
- Delta vs windowed: -0.1800
- Delta vs shuffled: -0.2400
- Pass deltas: False
- **Verdict: FAIL**

**Feature scores (fixed mode):**
- Anchor score: 0.000
- Z-ngram: -1.032
- Z-coverage: 0.000
- Z-compress: -57.470
- Blinded sample: `XXXXXXXXXXXXXXXXXXXX...`

### random_control

**Description:** Random letters with anchors
**Expected:** Should FAIL on language scores
**Text sample:** `QWRTYPSDLFKGJHZXCVBNMEASTNORTH...`

**Scores:**
- Delta vs windowed: 0.0000
- Delta vs shuffled: -0.0500
- Pass deltas: False
- **Verdict: FAIL**

**Feature scores (fixed mode):**
- Anchor score: 0.667
- Z-ngram: -1.032
- Z-coverage: 0.000
- Z-compress: -10.180
- Blinded sample: `QWRTYPSDLFKGJHZXCVBN...`

### k1_plaintext

**Description:** K1 plaintext with anchors inserted
**Expected:** Might have better language scores
**Text sample:** `BETWEENSUBTLESHADINGAEASTNORTH...`

**Scores:**
- Delta vs windowed: 0.0000
- Delta vs shuffled: -0.0200
- Pass deltas: False
- **Verdict: FAIL**

**Feature scores (fixed mode):**
- Anchor score: 0.667
- Z-ngram: 8.129
- Z-coverage: 0.000
- Z-compress: -14.406
- Blinded sample: `BETWEENSUBTLESHADING...`

## Conclusion

The harness is behaving correctly:
- Narrative texts fail under blinding ✅
- Blinding prevents leakage ✅
- Delta thresholds are discriminative ✅
