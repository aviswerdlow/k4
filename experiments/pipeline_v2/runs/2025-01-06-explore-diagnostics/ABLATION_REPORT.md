# Feature Ablation Report

## Feature Means

### Controls
- anchor_score: 0.0000
- z_ngram: -0.1639
- z_coverage: 0.0000
- z_compress: -0.1690

### Campaign Heads
- anchor_score: 0.5300
- z_ngram: 2.2293
- z_coverage: 0.0000
- z_compress: -15.3453

## Feature Importance

### Correlation with Full Score
- anchor_score: r=0.704 (p=0.0000)
- z_ngram: r=0.984 (p=0.0000)
- z_coverage: r=0.000 (p=0.0000)
- z_compress: r=-0.330 (p=0.0000)

## Key Finding

**z_ngram** has the strongest correlation with the full score (r=0.984).

### Feature Differences (Heads - Controls)
- anchor_score: +0.5300
- z_ngram: +2.3932
- z_coverage: +0.0000
- z_compress: -15.1763
