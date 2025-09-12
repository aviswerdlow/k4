# Cadence Bootstrap Report

**Date**: 2025-01-06  
**Seed**: 1337  
**Source**: K1, K2, K3 plaintexts  
**Windows**: 2000 per text, 6000 total  
**Thresholds SHA-256**: 0d6ba5c3c3134e23a080653ef5b083bdd34737ab9ff1d54e728ba20d197e36c1

## Methodology

1. Extracted 2000 random head-sized (75-char) windows from each of K1, K2, K3
2. Applied tokenization v2 rules to get words
3. Computed six metrics for each window:
   - Cosine similarity of letter bigrams
   - Cosine similarity of letter trigrams
   - Function word gap mean and CV
   - Word length chi-squared distance
   - Vowel-consonant ratio
4. Computed percentiles for threshold determination

## Thresholds

| Metric | Threshold | Value |
|--------|-----------|-------|
| cosine_bigram | ≥ P5 | 0.5496 |
| cosine_trigram | ≥ P5 | 0.3896 |
| fw_gap_mean | P2.5-P97.5 | [0.00, 6.00] |
| fw_gap_cv | P2.5-P97.5 | [0.000, 0.000] |
| wordlen_chi2 | ≤ P95 | 13.895 |
| vc_ratio | P2.5-P97.5 | [0.500, 0.667] |

## Files Generated

- `THRESHOLDS.json`: Percentile thresholds for gate evaluation
- `REF_BOOTSTRAP.json`: Full bootstrap report with metrics summary
- `REF_BOOTSTRAP.md`: This report
