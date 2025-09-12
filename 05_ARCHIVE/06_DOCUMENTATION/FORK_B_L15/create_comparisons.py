#!/usr/bin/env python3
"""
Create comparison PDFs and period rationale for Fork B.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, FancyBboxPatch
import json

def create_tail_emergence_pdf():
    """Create PDF comparing L=15 vs L=17 tail emergence"""
    fig = plt.figure(figsize=(11, 8.5))
    
    # Title
    fig.text(0.5, 0.95, 'Tail Emergence: L=15 vs L=17 (Anchors Only)', 
             fontsize=18, weight='bold', ha='center')
    
    # Panel A: L=15 tail
    ax1 = fig.add_subplot(2, 1, 1)
    ax1.set_xlim(-0.5, 22.5)
    ax1.set_ylim(-0.5, 2.5)
    ax1.axis('off')
    ax1.set_title('L=15: 16 of 23 tail positions emerge', fontsize=14, weight='bold')
    
    # L=15 tail data (from TAIL_GRID.txt)
    l15_tail = ['?','?','?','?','?','?','?','I','R','E','G',
                'X','U','W','J','O','K','Q','G','L','I','C','P']
    
    for i, char in enumerate(l15_tail):
        x = i
        y = 1
        if char == '?':
            color = 'lightgray'
            edge = 'gray'
        else:
            color = 'lightblue'
            edge = 'black'
        
        rect = Rectangle((x-0.4, y-0.4), 0.8, 0.8,
                        facecolor=color, edgecolor=edge, linewidth=1)
        ax1.add_patch(rect)
        ax1.text(x, y, char, ha='center', va='center', 
                fontsize=12, weight='bold' if char != '?' else 'normal')
        ax1.text(x, y-0.7, str(74+i), ha='center', va='center', fontsize=8)
    
    # Explanation
    ax1.text(11, 0, "Why: Slot reuse with L=15 propagates anchor constraints", 
            ha='center', fontsize=11, style='italic')
    
    # Panel B: L=17 tail
    ax2 = fig.add_subplot(2, 1, 2)
    ax2.set_xlim(-0.5, 22.5)
    ax2.set_ylim(-0.5, 2.5)
    ax2.axis('off')
    ax2.set_title('L=17: 0 of 23 tail positions emerge', fontsize=14, weight='bold')
    
    # L=17 tail - all unknown
    for i in range(23):
        x = i
        y = 1
        rect = Rectangle((x-0.4, y-0.4), 0.8, 0.8,
                        facecolor='lightgray', edgecolor='gray', linewidth=1)
        ax2.add_patch(rect)
        ax2.text(x, y, '?', ha='center', va='center', fontsize=12)
        ax2.text(x, y-0.7, str(74+i), ha='center', va='center', fontsize=8)
    
    # Explanation
    ax2.text(11, 0, "Why: One-to-one mapping with L=17 prevents propagation", 
            ha='center', fontsize=11, style='italic')
    
    # Summary box
    summary_text = """Key Difference:
L=15: Each anchor position can determine multiple positions (slot reuse)
L=17: Each anchor position determines exactly one position (1-to-1 mapping)"""
    
    fig.text(0.5, 0.08, summary_text, ha='center', fontsize=11,
            bbox=dict(boxstyle="round,pad=0.5", facecolor='lightyellow'))
    
    plt.tight_layout()
    plt.savefig('COMPARE/L15_L17_TAIL_EMERGENCE.pdf', format='pdf', bbox_inches='tight')
    plt.close()
    print("Created COMPARE/L15_L17_TAIL_EMERGENCE.pdf")

def create_period_rationale():
    """Create period rationale markdown"""
    
    rationale = """# Period Rationale

## Why L=17 Originally?

### Objective Signals from Prior Panels

1. **Co-prime Coverage**: L=17 is prime and creates perfect 1-to-1 mapping with 97 positions
   - gcd(17, 97) = 1
   - Total slots = 6 × 17 = 102 > 97 (no collision)
   - Each position maps to unique (class, slot) pair

2. **Collision Avoidance**: L=17 ensures no anchor conflicts
   - All four anchors seat without slot collisions
   - Option-A constraint satisfied at all anchor positions

3. **"Distinct Slots" Heuristic**: Preference for unique determination
   - Each plaintext position should ideally determine one wheel slot
   - Avoids ambiguity in reconstruction

### What We Don't Have

**No K3 precedent for L=15**: 
- K3 uses 4×7 grid (28 positions)
- L=14 (2×7) has clearer K3 relationship
- L=15 (3×5) has no direct K3 derivation
- L=17 (prime) also lacks K3 connection

## L=15 as "What-If"

L=15 emerged from systematic algebraic testing:
- Achieves complete closure with anchors + tail
- BUT produces different plaintext than canonical
- Tail under L=15: "...IREGXUWJOKQGLICP" (not "THEJOYOFANANGLEISTHEARC")

This shows L=15 is algebraically viable but semantically different.

## Invitation to Community

If you can show a K3→K4 clue that fixes L=15, we'll adopt it.
Current evidence favors L=17 based on:
1. Produces canonical plaintext
2. 1-to-1 mapping property
3. No slot collision issues

## State of Evidence

- **L=17**: Canonical plaintext match, but needs more than tail
- **L=15**: Algebraic closure, but different plaintext
- **Open question**: Is there a prior-panel signal we're missing?
"""
    
    with open('COMPARE/PERIOD_RATIONALE.md', 'w') as f:
        f.write(rationale)
    
    print("Created COMPARE/PERIOD_RATIONALE.md")

def create_summary_table():
    """Create a summary comparison table"""
    
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    ax.axis('off')
    
    # Title
    fig.text(0.5, 0.95, 'L=15 vs L=17: Complete Comparison', 
             fontsize=18, weight='bold', ha='center')
    
    # Table data
    headers = ['Metric', 'L=15', 'L=17']
    data = [
        ['Anchors only (derived)', '76/97', '24/97'],
        ['Tail positions emerged', '16/23', '0/23'],
        ['With canonical tail', '97/97', '47/97'],
        ['Produces canonical PT', 'NO ✗', 'Partial'],
        ['Slot mapping', 'Reuse (1.08/slot)', '1-to-1'],
        ['K3 justification', 'None', 'None'],
        ['Algebraic closure', 'YES ✓', 'NO ✗']
    ]
    
    # Create table
    table = ax.table(cellText=data, colLabels=headers, 
                    cellLoc='center', loc='center',
                    colWidths=[0.4, 0.3, 0.3])
    
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 2)
    
    # Style header
    for i in range(3):
        table[(0, i)].set_facecolor('#4472C4')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Color code rows
    for i in range(1, 8):
        if i == 4:  # Canonical PT row
            table[(i, 1)].set_facecolor('#ffcccc')  # L=15 fails
        elif i == 7:  # Closure row
            table[(i, 1)].set_facecolor('#ccffcc')  # L=15 succeeds
            table[(i, 2)].set_facecolor('#ffcccc')  # L=17 fails
    
    # Key insight box
    insight = """Key Finding: L=15 achieves algebraic closure but produces DIFFERENT plaintext.
The emerged tail "IREGXUWJOKQGLICP" ≠ "THEJOYOFANANGLEISTHEARC"
This suggests L=15 is mathematically viable but semantically incorrect."""
    
    fig.text(0.5, 0.15, insight, ha='center', fontsize=11,
            bbox=dict(boxstyle="round,pad=0.5", facecolor='lightyellow'))
    
    plt.tight_layout()
    plt.savefig('COMPARE/L15_L17_COMPARISON.pdf', format='pdf', bbox_inches='tight')
    plt.close()
    print("Created COMPARE/L15_L17_COMPARISON.pdf")

def main():
    """Create all comparison materials"""
    print("\n=== Creating Comparison Materials ===")
    
    create_tail_emergence_pdf()
    create_period_rationale()
    create_summary_table()
    
    print("\n✅ Comparison materials created")

if __name__ == "__main__":
    main()