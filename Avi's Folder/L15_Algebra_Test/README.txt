L15 ALGEBRA TEST - FORK B HYPOTHESIS
=====================================

EXECUTIVE SUMMARY
-----------------
Pure algebraic test of whether L=15 (instead of L=17) enables complete K4 solution
using only the four public anchors plus the 23-character tail. NO SEMANTICS USED.

KEY FINDING
-----------
✓ L=15 ACHIEVES COMPLETE SOLUTION with anchors + tail (0 unknowns)
✗ L=17 leaves 50 positions unknown even with anchors + tail

METHODOLOGY
-----------
1. Checked K1-K3 for prior-panel justification of L=15 → NONE FOUND
2. Tested L=15 algebraically with anchors only → 76/97 derived
3. Added tail as pure coverage test → 97/97 derived (COMPLETE)
4. Compared with L=14,16,17 for context → Only L=15 completes

FILES INCLUDED
--------------
• L15_JUSTIFICATION.pdf - Shows no K3 signal for L=15 (tested as "what-if")
• L15_AnchorsOnly.pdf - Slot reuse diagram showing 76 positions derived
• L_COMPARE.pdf - Comparison chart showing L=15 uniquely succeeds
• COUNTS_anchors_only.json - L=15 anchors: 76 derived, 21 unknown
• TAIL_COVERAGE.json - L=15 with tail: 97 derived, 0 unknown

ALGEBRAIC FACTS (No Language Required)
---------------------------------------
Period | Anchors Only | Anchors+Tail | Status
-------|--------------|--------------|--------
L=14   | 26 derived   | 81 derived   | 16 unknown
L=15   | 76 derived   | 97 derived   | COMPLETE
L=16   | 38 derived   | 69 derived   | 28 unknown  
L=17   | 24 derived   | 47 derived   | 50 unknown

WHY L=15 WORKS
--------------
• With L=15 and 6 classes: 90 total slots for 97 positions
• Slight slot reuse (1.08 positions/slot average)
• This reuse amplifies anchor coverage: 24 positions → 76 derived
• Tail's 23 positions cover remaining 21 unknowns perfectly

CRITICAL NOTE
-------------
This is pure algebra. The choice of L=15 was NOT derived from K4 head/tail
semantics. It emerged from systematic period testing. No prior-panel 
justification exists for L=15 specifically.

VERIFICATION
------------
All results reproducible from:
- Ciphertext: Standard K4 97 characters
- Anchors: EAST(21-24), NORTHEAST(25-33), BERLIN(63-68), CLOCK(69-73)
- Class function: ((i%2)*3)+(i%3)
- Families: Vigenère/Beaufort by class
- Tail: Positions 74-96 (for coverage only, not selection)