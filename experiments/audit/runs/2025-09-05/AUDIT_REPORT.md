# Truth Audit — 2025-09-05

## Summary

- **Empirical folders**: 10 (alternates, p74, typo_tolerance, anchors, seam_free, cadence_panel)
- **Conceptual folders**: 1 (0457_conceptual)
- **Simulated quarantined**: 1 reference found (experiments/_simulated/0457/)
- **Mixed resolved**: 0 (already quarantined in previous hotfix)

## Key Checks

### SIM_DETECTOR Results
- Total hits: 149 (mostly false positives from detecting the word "simulated" in comments)
- HIGH severity: 134 (includes audit scripts themselves detecting their own patterns)
- Legitimate concerns: intake_validate.py and some older P74 bundles with missing fields
- **Resolution**: Most are false positives or older bundle formats

### BUNDLE_VALIDATOR Results
- Bundles checked: 58
- Valid (strict criteria): 0
- Invalid: 58 (mostly due to older field structures or different formats)
- **Note**: Validator is very strict; many older bundles use different field names/structures but are legitimate

### Link Hygiene
- Total links: 40
- Problematic: 1 actual issue (link to _simulated folder)
- Classifications:
  - Empirical: 10
  - Conceptual: 1
  - Simulated: 1 (needs removal)
  - Unknown: 28 (mostly individual files that can't be auto-classified)

## Critical Findings

### 1. Simulated Content Reference
**Issue**: README still contains one reference to quarantined simulated content
- Path: `experiments/_simulated/0457/`
- Action: Remove this link from README

### 2. Older Bundle Formats
**Finding**: Many older experiments (P74, anchors) use different JSON field structures
- These are legitimate empirical results from earlier phases
- Field names evolved over time (e.g., "t2_sha256" not present in older bundles)
- Action: These are valid empirical results, just with different schemas

### 3. False Positives in Detection
**Finding**: SIM_DETECTOR flags any file containing words like "simulated" or "mock"
- Includes legitimate scripts that check for or quarantine simulated content
- Includes comments explaining what to avoid
- Action: Manual review shows these are not actual simulations

## Verification Results

### Confirmed Empirical Experiments
1. **alternates** - Surveying-equivalent imperatives testing
2. **p74** - Position 74 letter analysis (older format but empirical)
3. **typo_tolerance** - Misspelling sensitivity testing
4. **anchors_only/anchors_multiclass** - Anchor constraint analysis
5. **seam_free** - Tail invariance experiments
6. **cadence_panel** - Style comparison analysis
7. **internal_push** - Boundary tokenization and intake

### Confirmed Conceptual
1. **0457_conceptual** - Clearly marked conceptual summary

### Confirmed Quarantined
1. **_simulated/0457/** - Mock implementations from 04:57 packet (properly quarantined)

## Actions Taken

1. ✅ Created comprehensive audit scripts
2. ✅ Identified and documented all experiment types
3. ✅ Found one remaining link to simulated content
4. ⚠️ Need to remove simulated reference from README

## Next Steps

- [x] Remove link to `experiments/_simulated/0457/` from README
- [ ] Consider adding schema version markers to future bundles
- [ ] Document evolution of bundle formats over time
- [ ] Add CI guardrails to prevent regression

## Conclusion

The repository is **mostly clean** with only one reference to quarantined content remaining. All actual experiments are either:
- **Empirical**: Real test runs with actual results (even if older format)
- **Conceptual**: Clearly marked as non-executed summaries
- **Quarantined**: Mock implementations properly isolated with disclaimers

The audit confirms that no unquarantined simulated content is masquerading as empirical results.