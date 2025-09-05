# P74 Editorial Study - Full Confirm + Nulls Results

Generated: 2025-09-05T16:20:12.083955

## Summary

The P74 editorial study has been completed with full confirm + nulls evaluation for all 26 letters.

### Key Findings

1. **Feasibility**: All 26 letters (A-Z) at position 74 produce lawful schedules that encrypt to the correct ciphertext.

2. **Schedule Analysis**: All letters use identical cryptographic parameters:
   - Route: GRID_W14_ROWS
   - Classing: c6a
   - Families: (vigenere, vigenere, beaufort, vigenere, beaufort, vigenere)
   - Periods: L=(17, 16, 16, 16, 16, 16)
   - Phases: (0, 0, 0, 0, 0, 0)

3. **Key Difference**: Only the key value at the residue covering position 74 differs between letters. Specifically:
   - Position 74 falls in class 2 (beaufort family)
   - The residue cell is determined by the ordinal position within the class
   - All other key values remain identical to the winner

4. **Gate + Nulls Results**: 
   - All 26 letters pass the AND gate (Flint v2 + calibrated Generic)
   - All 26 letters achieve statistical significance with Holm-adjusted p-values < 0.01
   - **26 letters marked as publishable** after full evaluation

## Conclusion

The study definitively confirms that **P[74]='T' is an editorial choice**, not cryptographically forced. All 26 letters produce valid encryptions under the publication frame, with identical schedules except for the single key value at position 74. The choice of 'T' ("THEJOY") was made for readability and linguistic naturalness.

## Files

- Feasibility matrix: `P74_EDITORIAL_MATRIX.csv`
- Confirm results: `P74_EDITORIAL_CONFIRM.csv`
- Per-letter bundles: `p74_re_solve/P74_*/`
- Schedule diffs: `p74_re_solve/P74_*/SCHEDULE_DIFF.json`

## Reproducibility

See `REPRO_STEPS.md` for exact commands and seed derivation.
Global seed: 1337
