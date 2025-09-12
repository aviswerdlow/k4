# Fork F - Final Summary

## Critical Finding: F1 Implementation Bug

The F1 anchor search reported numerous high-gain candidates (17-21 positions), but verification revealed these are **FALSE POSITIVES** due to an implementation bug.

### The Bug

The F1 code doesn't properly validate conflicts when testing candidate anchors. When we manually verified MERIDIAN@34-41 with L=11:
- **Every single position conflicted** with existing anchor constraints
- The wheels were already fully constrained by the 24 anchors
- Adding MERIDIAN creates irreconcilable conflicts

### What Actually Happened

1. The search function counted "propagation" without checking if the candidate was actually compatible with existing constraints
2. It reported gains of 17-21 positions when in reality these placements are **impossible**
3. The high numbers came from counting positions that could theoretically be determined IF the conflicts didn't exist

## Corrected Assessment

### F1: Systematic Anchor Search
- **Status**: Implementation flawed, results invalid
- **Next Step**: Fix conflict validation in `build_wheels()` function
- **Likely Reality**: Few if any candidates will survive proper conflict checking

### F2: Non-Polyalphabetic Ciphers  
- **Status**: Framework created, ready for testing
- **Potential**: Still worth exploring as these escape the wheel constraint problem

### Key Lessons

1. **Validation is Critical**: Always verify promising results independently
2. **Conflict Checking**: Must be rigorous when building constrained systems
3. **Too Good to Be True**: 21-position gains should have been a red flag

## What Fork F Revealed

Despite the bug, Fork F provided valuable insights:

1. **L=17 May Be Wrong**: The system is so constrained with L=17 that even small additions cause conflicts
2. **Need Different Approach**: Pure mechanical search without semantics may be insufficient
3. **Quality Over Quantity**: Better to have one verified constraint than thousands of false positives

## Recommendations

1. **Fix F1 Implementation**: Add proper conflict validation
2. **Focus on F2**: Non-polyalphabetic ciphers remain unexplored
3. **Consider F4**: Error tolerance might reveal if K4 has transcription errors
4. **Physical Inspection**: F3 packet still valuable for on-site investigation

## Bottom Line

**Fork F exposed that the K4 constraint system is even tighter than expected.** With proper conflict checking, we'll likely find that very few (if any) additional anchors are mechanically compatible with the existing constraints under standard polyalphabetic assumptions.

This suggests either:
- K4 uses a different cipher system entirely (explore F2)
- There are errors in the ciphertext or our anchors (explore F4)
- Additional information is needed from physical inspection (F3)

---

**Status: Fork F requires bug fixes before meaningful results can be obtained.**

The search for new anchors remains the right strategy, but the implementation must properly validate mechanical compatibility.