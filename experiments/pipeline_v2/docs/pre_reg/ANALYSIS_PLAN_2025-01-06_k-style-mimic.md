# Pre-Registration: Pipeline v2 Analysis Plan

**Date:** 2025-01-06  
**Campaign ID:** EXPLORE_K_STYLE_MIMIC  
**Global Seed:** 1337

## K1-K3 Register Mimic Campaign

### Hypothesis
Heads biased toward K1-K3 letter n-grams and word-length profiles will show different scoring patterns under blinding, but remain below promotion thresholds (report-only).

### Configuration

#### Data Source
- **K1 plaintext**: BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION
- **K2 plaintext**: ITWASTOTALLYINVISIBLESHOWSTHISISWASPOSSIBLETHEYDUSEDTHEEARTHSMAGNETICFIELD
- **K3 plaintext**: ONLYWTHATTHEVIRTUALLYDOESYOUCANSEEEXPERENCETHATYOUWILLNOTFINDANYWHERELSE

#### Sampling Strategy
- Extract character bigram/trigram frequencies from K1-K3
- Extract word length distribution (assuming space boundaries)
- Bias sampling toward K-style cadence
- Enforce corridor at [21,25,63]
- Mask narrative lexemes

#### Scoring Configuration
- **Mode**: Report-only (no gate changes)
- **Blinding**: ON
- **Policies**: fixed, windowed(r=2), shuffled
- **Thresholds**: Standard (δ₁=0.05, δ₂=0.10) but NOT enforced

### Expected Outcomes
- **Different n-gram distribution** compared to English corpus
- **Higher character entropy** (K texts have specific patterns)
- **Still 0 promotions** (report-only + blinding)

### Success Criteria
- Demonstrate whether K-style cadences affect Δ vs shuffled
- Maintain analytics-only approach
- No changes to promotion decisions

## Framework (Pipeline v2)
- **Explore Lane**: Report-only scoring input
- **Confirm Lane**: Stays idle
- **Seed Policy**: Global 1337