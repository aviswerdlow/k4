# Cadence Panel Report - Comprehensive Analysis

Generated: 2025-09-05

## Executive Summary

This comprehensive report compares candidate K4 heads to K1-K3 style using multiple metrics, reference distributions, and weight configurations. **This is a report-only analysis and does not change any gating decisions.**

**Key Finding**: Winner maintains higher CCS than runner across all sensitivity analyses.

## Main Results (Baseline Token-Window)

### Combined Cadence Scores (CCS)

| Candidate | CCS | J_content | J_content_lev1 | Cosine_Bi | Cosine_Tri | Has_Quirks |
|-----------|-----|-----------|----------------|-----------|------------|------------|
| winner_GRID_W14_ROWS_head | -1.552 | 0.0000 | 0.0236 | 0.6263 | 0.3749 | No |
| runner_GRID_W10_NW_head | -1.942 | 0.0000 | 0.0160 | 0.6314 | 0.3253 | No |

## Sensitivity Analyses

### Appendix A - Window Type Comparison

| Analysis | Winner CCS | Runner CCS | Δ CCS | Ordering |
|----------|------------|------------|-------|----------|
| Token Windows (75 tokens) | -1.552 | -1.942 | 0.390 | Winner > Runner ✓ |
| Character Windows (450 chars) | -4.195 | -4.420 | 0.225 | Winner > Runner ✓ |
| Declarative Reference | -0.684 | -0.956 | 0.272 | Winner > Runner ✓ |

**Interpretation**: The winner maintains a higher CCS across all window types. Character windows show larger negative CCS values due to different statistical properties of character-based sampling, but relative ordering is preserved. The declarative reference (removing K2's coordinate block) shows less extreme CCS values, suggesting the coordinate block contributes to stylistic divergence.

### Appendix B - Weight Sensitivity Analysis

| Weight Configuration | Winner CCS | Runner CCS | Δ CCS | Ordering |
|---------------------|------------|------------|-------|----------|
| Baseline | -1.552 | -1.942 | 0.390 | Winner > Runner ✓ |
| Bigram/Trigram Heavy (+50%) | -2.646 | -2.977 | 0.331 | Winner > Runner ✓ |
| Rhythm Heavy (+180% fw weights) | -0.118 | -0.698 | 0.580 | Winner > Runner ✓ |
| Uniform (equal weights) | -0.894 | -1.393 | 0.499 | Winner > Runner ✓ |

**Interpretation**: The winner consistently outperforms the runner across all weight configurations. The rhythm-heavy weights show the smallest absolute CCS values, while bigram/trigram-heavy weights amplify the style divergence. The ordering remains robust to weight perturbations.

### Appendix C - Reference Distribution Analysis

| Reference Type | Description | Key Observations |
|----------------|-------------|------------------|
| Full K1-K3 | All three K texts | Baseline for comparison |
| Declarative K2 | Coordinate block removed | Reduces extreme values, more coherent narrative register |
| Character Windows | 450-char sampling | Emphasizes local structure over token boundaries |

### Appendix D - Metric Stability

| Metric | Baseline σ | Char-Window σ | Declarative σ | CV |
|--------|------------|---------------|---------------|-----|
| fw_mean_gap | 2.336 | 2.092 | 2.279 | 0.054 |
| cosine_bigram | 0.119 | 0.187 | 0.145 | 0.221 |
| cosine_trigram | 0.088 | 0.139 | 0.106 | 0.224 |
| vc_ratio | 0.156 | 0.139 | 0.155 | 0.064 |

## Register Analysis

The K1-K3 texts exhibit narrative/declarative register with:
- Orthographic quirks (IQLUSION, UNDERGRUUND, DESPARATLY)
- Prose-like n-gram distributions
- Variable sentence structure

The K4 candidates show:
- Instructional/imperative register
- Surveying/navigation terminology
- More consistent word lengths
- Absence of orthographic quirks

## Conclusions

1. **Robust Ordering**: Winner maintains higher CCS than runner across all analyses
2. **Register Distinction**: K4 candidates are stylistically distinct from K1-K3
3. **No Style Match**: Neither candidate shows strong stylistic similarity to Sanborn's earlier panels
4. **Weight Insensitivity**: CCS ordering is robust to reasonable weight variations

## Technical Notes

- Bootstrap: 2000 windows per K text, seed=1337
- Token windows: 75 tokens (resampled for K1)
- Character windows: 450 characters
- Tokenization: v2 with canonical cuts for heads
- All metrics computed on head positions 0-74 only

## Important Reminder

**This analysis is report-only and does not change any gating decisions or published results.**