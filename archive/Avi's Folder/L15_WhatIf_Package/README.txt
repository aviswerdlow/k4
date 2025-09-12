L15 "WHAT-IF" ANALYSIS - FORK B
================================

EXECUTIVE SUMMARY
-----------------
Pure algebraic test of L=15 as alternative to L=17. NO SEMANTICS.
Tests what emerges in tail under anchors-only and whether canonical tail fits.

KEY FINDINGS
------------
1. L=15 with anchors only: 76/97 derived, tail shows "IREGXUWJOKQGLICP" 
2. L=17 with anchors only: 24/97 derived, tail completely unknown
3. L=15 achieves algebraic closure BUT produces WRONG plaintext
4. The L=15 tail ≠ canonical "THEJOYOFANANGLEISTHEARC"

WHAT THIS MEANS
---------------
• L=15 is algebraically viable (closes with anchors+tail)
• BUT semantically incorrect (wrong plaintext produced)
• L=17 produces correct plaintext where determined
• No K3 precedent found for either L=15 or L=17

FILES INCLUDED
--------------
L15/anchors_only/
  PT_PARTIAL.txt - 97 chars with 76 derived, 21 unknown (?)
  TAIL_GRID.txt - Shows tail positions 74-96 with emerged letters
  COUNTS.json - Exact counts of derived/unknown

L15/anchors_plus_tail/
  PT_FULL.txt - Complete 97 chars (but WRONG plaintext)
  TAIL_DIFF.txt - Shows differences from canonical

L17/anchors_only/
  PT_PARTIAL.txt - 97 chars with only 24 derived
  TAIL_GRID.txt - Tail completely unknown (all ?)

COMPARE/
  L15_L17_TAIL_EMERGENCE.pdf - Visual comparison of tail emergence
  L15_L17_COMPARISON.pdf - Complete metrics table
  L_SUMMARY.json - Numerical comparison
  PERIOD_RATIONALE.md - Why we used L=17 originally

HOW TO VERIFY BY HAND
---------------------
1. Take any emerged position (e.g., pos 81 = 'I' under L=15)
2. Class = ((81%2)*3)+(81%3) = 3
3. Slot = 81 % 15 = 6
4. Check if slot 6 in class 3 was forced by anchors
5. If yes, derive: C[81]='F', K=?, P='I' matches

ASSUMPTIONS (FIXED)
-------------------
• Class function: ((i%2)*3)+(i%3) unchanged
• Families: Vigenère/Beaufort by class
• Phase: 0 for all classes
• Option-A: Enforced at anchor positions

BOTTOM LINE
-----------
L=15 creates an algebraically valid but semantically different solution.
The emerged tail "IREGXUWJOKQGLICP" is NOT English or meaningful.
This supports L=17 as the intended period despite algebraic challenges.