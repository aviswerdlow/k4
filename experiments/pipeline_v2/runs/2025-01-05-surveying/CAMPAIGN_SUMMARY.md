# Campaign Summary: PV2-SURVEY-001

**Date:** 2025-01-05  
**Campaign:** Surveying hypothesis testing  
**Status:** Complete

## Results

### Explore Lane
- **Candidates tested:** 3
  - surveying_bearing: "SET THE BEARING TRUE..."
  - surveying_berlin: "READ THE BERLIN CLOCK..."  
  - surveying_observe: "OBSERVE THE DIALS..."
- **Promoted:** 0
- **Reasons:** All failed promotion thresholds (δ₂ < 0 vs required 0.10)

### Anchor Mode Analysis
All candidates showed identical scores across fixed/windowed/shuffled modes, indicating:
- Anchors appear at correct positions
- No windowing advantage
- Shuffled control performs better than candidates (unexpected)

### Negative Controls
For surveying_bearing:
- Original: 0.242
- Scrambled anchors: -20% (0.194)
- Permuted seam: -12% (0.214)
- Random shuffle: -74% (0.063)

### Orbit Analysis
surveying_bearing:
- Neighbors examined: 2,418
- Ties within ε=0.02: 1,995
- Unique: FALSE (far exceeds threshold of 5)

## Conclusion

As expected, surveying-equivalent phrasings do not pass the Explore lane thresholds. The candidates:
1. Score worse than shuffled controls (negative δ₂)
2. Show no uniqueness in orbit space
3. Degrade appropriately under negative controls

No candidates promoted to Confirm lane.

## Files
- Pre-registration: `docs/pre_reg/ANALYSIS_PLAN_2025-01-05_surveying.md`
- Explore matrix: `ANCHOR_MODE_MATRIX.csv`
- Negative controls: `neg_controls/NEG_CONTROL_SUMMARY.csv`
- Orbit analysis: `orbits/surveying_bearing/orbit_analysis.json`
- Manifest: `MANIFEST.sha256`
- Repro steps: `REPRO_STEPS.md`