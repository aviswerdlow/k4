# Core-Hardening v5: Mathematical Constraints Analysis

## Executive Summary

This analysis quantifies exactly how many additional plaintext constraints beyond the four anchors are mathematically required to determine all 97 positions under different period lengths (L values).

## Key Findings

### With L=17 (Current Hypothesis)
- **Anchors determine**: 24/97 positions
- **Mathematical requirement**: ALL 73 remaining positions must be constrained
- **Tail coverage**: 23/73 slots (31.5%)
- **Shortfall**: 50 additional positions beyond tail required

### Why 73?
With L=17 and 97 positions, the co-prime property (gcd(17,97)=1) creates a perfect 1-to-1 mapping between positions and (class,slot) pairs. This means:
- Each position determines exactly one unique slot
- No position is redundant
- The minimal set-cover size equals the number of unconstrained positions (73)

### Alternative Mechanisms
Testing other period lengths shows:
- **L=15**: Only 21 unknowns (tail would be sufficient!)
- **L=20**: 49 unknowns (26 beyond tail needed)
- **L=11**: 55 unknowns

The choice of L=17 is NOT optimal for minimizing unknowns from anchors alone.

## Files Included

### Visual Summaries (PDFs)
- `SET_COVER_EXPLAINED.pdf` - Visual explanation of set-cover problem
- `IMPLICATIONS_SUMMARY.pdf` - What we can/cannot say mathematically
- `MECH_SURVEY_CHART.pdf` - Comparison of different L values

### Detailed Analysis
- `SET_COVER_SUMMARY.md` - Set-cover analysis details
- `MECH_SURVEY_SUMMARY.md` - Mechanism survey results
- `CORE_V5_SUMMARY.txt` - Plain text summary

### Raw Data (JSON)
- `SET_COVER_MINIMAL.json` - Minimal set-cover solutions
- `TAIL_COVERAGE.json` - Tail coverage analysis
- `COPRIME_ANALYSIS.json` - Co-prime property verification

## What We Can Say (Mathematical Facts)

1. **With L=17 and 4 anchors**: Exactly 24 positions determined, 73 unknown
2. **Minimal additional constraints**: 73 (must specify ALL remaining positions)
3. **No algebraic shortcut exists**: The 1-to-1 mapping prevents any reduction
4. **Tail insufficient**: 23-position tail covers only 31.5% of needed slots

## What Requires Additional Assumptions

1. **Why L=17?** - Other values (L=15) would work better algebraically
2. **Tail content** - What determines the specific 50 positions beyond tail?
3. **Language constraints** - Not addressed in this pure-algebra analysis

## Falsifiable Predictions

If L=17 is correct:
- No subset of <73 additional positions can complete the solution
- The tail alone leaves exactly 50 positions undetermined
- Any valid solution must specify all 97 positions

If L=15 is correct instead:
- Only 21 additional positions needed
- The 23-position tail would be sufficient
- Two tail positions would be redundant

## Success Criteria Met

✓ **Pure algebra** - No language gates or AI used
✓ **Quantified constraints** - Exact numbers for all mechanisms
✓ **Alternative testing** - Surveyed L∈[7,97] systematically  
✓ **Falsifiable claims** - Clear predictions that can be tested
✓ **Paper-verifiable** - All math checkable by hand

## Conclusion

The analysis proves that under L=17, the algebra alone cannot determine more than 24 positions from the four anchors. The remaining 73 positions require additional constraints - either more plaintext anchors or language-based restrictions. The 23-position tail provides less than a third of what's needed, making additional assumptions necessary for any complete solution.