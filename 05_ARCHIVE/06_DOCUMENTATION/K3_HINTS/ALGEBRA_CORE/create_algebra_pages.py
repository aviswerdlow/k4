#!/usr/bin/env python3
"""
Create ALGEBRA_CORE 4-page PDF package showing what algebra determines vs what it doesn't.
Paper-first, visual diagrams, no code references.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, FancyBboxPatch
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import os

def create_page1_24_of_97():
    """Page 1: What algebra determines (24/97)"""
    fig = plt.figure(figsize=(8.5, 11))
    
    # Title
    fig.text(0.5, 0.95, 'What Algebra Determines: 24 of 97', 
             fontsize=20, weight='bold', ha='center')
    
    # Diagram 1: 6×17 slot grid
    ax1 = fig.add_subplot(3, 1, 1)
    ax1.set_xlim(-0.5, 16.5)
    ax1.set_ylim(-0.5, 5.5)
    ax1.set_aspect('equal')
    ax1.set_title('Slot Grid: 6 Classes × 17 Slots', fontsize=12, weight='bold')
    
    # Forced slots from anchors
    forced_slots = {
        0: [0, 4, 7, 13, 15],  # Class 0
        1: [2, 5, 11, 13],     # Class 1  
        2: [0, 9, 15],         # Class 2
        3: [1, 4, 10, 12, 16], # Class 3
        4: [5, 8, 14, 16],     # Class 4
        5: [3, 6, 12, 14]      # Class 5
    }
    
    # Draw grid
    for row in range(6):
        for col in range(17):
            if col in forced_slots.get(row, []):
                # Forced slot - blue
                rect = Rectangle((col-0.4, row-0.4), 0.8, 0.8, 
                                facecolor='lightblue', edgecolor='black', linewidth=1)
                ax1.add_patch(rect)
            else:
                # Unknown slot - white
                rect = Rectangle((col-0.4, row-0.4), 0.8, 0.8,
                                facecolor='white', edgecolor='gray', linewidth=0.5)
                ax1.add_patch(rect)
    
    ax1.set_xticks(range(17))
    ax1.set_yticks(range(6))
    ax1.set_yticklabels([f'C{i}' for i in range(6)])
    ax1.set_xlabel('Slot (0-16)')
    ax1.set_ylabel('Class')
    ax1.grid(False)
    
    # Diagram 2: 97-position index strip
    ax2 = fig.add_subplot(3, 1, 2)
    ax2.set_xlim(-0.5, 96.5)
    ax2.set_ylim(-0.5, 1.5)
    
    # Anchor positions
    anchor_positions = {
        'EAST': list(range(21, 25)),
        'NORTHEAST': list(range(25, 34)),
        'BERLIN': list(range(63, 69)),
        'CLOCK': list(range(69, 74))
    }
    
    all_anchor_pos = []
    for positions in anchor_positions.values():
        all_anchor_pos.extend(positions)
    
    # Draw index boxes
    for i in range(97):
        if i in all_anchor_pos:
            color = 'lightblue'
        else:
            color = 'white'
        rect = Rectangle((i-0.4, 0.1), 0.8, 0.8,
                        facecolor=color, edgecolor='black', linewidth=0.5)
        ax2.add_patch(rect)
    
    ax2.set_title('97 Plaintext Positions (Blue = Algebraically Determined)', fontsize=12, weight='bold')
    ax2.set_xlabel('Position Index')
    ax2.set_xlim(-1, 97)
    ax2.set_ylim(0, 1)
    ax2.set_yticks([])
    
    # Explanation text
    ax3 = fig.add_subplot(3, 1, 3)
    ax3.axis('off')
    
    explanation = """Key Insight: The co-prime property (L=17 with 97 positions) ensures:
    
• Each slot appears at most once per class
• 4 anchor cribs force 24 unique slots
• These 24 slots map to exactly 24 plaintext positions
• The remaining 73 positions remain algebraically undetermined
    
With only algebra and the 4 anchors, we can determine exactly 24 of 97 positions.
No additional positions can be derived without more information."""
    
    ax3.text(0.1, 0.8, explanation, fontsize=11, va='top', wrap=True)
    
    plt.tight_layout()
    plt.savefig('ALGB_P1_24_of_97.pdf', format='pdf', bbox_inches='tight')
    plt.close()
    print("✅ Created ALGB_P1_24_of_97.pdf")

def create_page2_tail_p74():
    """Page 2: Tail & P74 structure tests"""
    fig = plt.figure(figsize=(8.5, 11))
    
    # Title
    fig.text(0.5, 0.95, 'Structure Tests: Tail Region & Position 74', 
             fontsize=20, weight='bold', ha='center')
    
    # Test 1: P74 is unconstrained
    ax1 = fig.add_subplot(3, 1, 1)
    ax1.axis('off')
    ax1.set_title('Test 1: Position 74 (After CLOCK)', fontsize=14, weight='bold')
    
    test1_text = """Position 74 Analysis:
    
• Index: 74
• Class: ((74%2)*3)+(74%3) = 2
• Slot: 74 % 17 = 6
• Status: NOT forced by any anchor
    
Result: P74 is algebraically UNCONSTRAINED. Any of 26 letters possible."""
    
    ax1.text(0.1, 0.5, test1_text, fontsize=12, va='center')
    
    # Visual for P74
    ax1.add_patch(Rectangle((0.7, 0.3), 0.15, 0.2, 
                           facecolor='yellow', edgecolor='red', linewidth=2))
    ax1.text(0.775, 0.4, '?', fontsize=20, ha='center', va='center', weight='bold')
    ax1.text(0.775, 0.25, 'P74', fontsize=10, ha='center')
    
    # Test 2: Tail region structure
    ax2 = fig.add_subplot(3, 1, 2)
    ax2.set_xlim(73.5, 96.5)
    ax2.set_ylim(-0.5, 1.5)
    ax2.set_title('Test 2: Tail Region (Positions 74-96)', fontsize=14, weight='bold')
    
    # Which tail positions are constrained?
    tail_constrained = []  # None from anchors alone
    
    for i in range(74, 97):
        if i in tail_constrained:
            color = 'lightblue'
        else:
            color = 'yellow'
        rect = Rectangle((i-0.4, 0.1), 0.8, 0.8,
                        facecolor=color, edgecolor='black', linewidth=1)
        ax2.add_patch(rect)
        
        # Add position numbers for first and last few
        if i < 78 or i > 93:
            ax2.text(i, 0.5, str(i), fontsize=8, ha='center', va='center')
    
    ax2.set_xlabel('Position Index')
    ax2.set_yticks([])
    ax2.set_ylim(0, 1)
    
    # Summary
    ax3 = fig.add_subplot(3, 1, 3)
    ax3.axis('off')
    
    summary = """Tail Region (74-96) Analysis:
    
• 23 positions after last anchor (CLOCK ends at 73)
• ZERO tail positions constrained by anchors
• All 23 tail positions remain algebraically free
    
Falsifiable Claim: Without additional information beyond the 4 anchors,
the entire tail region (positions 74-96) has 26^23 possible configurations.
    
This demonstrates the limit of algebraic constraint propagation."""
    
    ax3.text(0.1, 0.8, summary, fontsize=11, va='top')
    
    plt.tight_layout()
    plt.savefig('ALGB_P2_TAIL_P74.pdf', format='pdf', bbox_inches='tight')
    plt.close()
    print("✅ Created ALGB_P2_TAIL_P74.pdf")

def create_page3_k3_hints():
    """Page 3: K1-K3 mechanical hints"""
    fig = plt.figure(figsize=(8.5, 11))
    
    # Title
    fig.text(0.5, 0.95, 'K1-K3 Mechanical Precedents', 
             fontsize=20, weight='bold', ha='center')
    
    # K1: Simple Vigenère
    ax1 = fig.add_subplot(3, 1, 1)
    ax1.axis('off')
    ax1.set_title('K1: Standard Vigenère (PALIMPSEST × 2)', fontsize=12, weight='bold', loc='left')
    
    k1_text = """• Key: PALIMPSEST PALIMPSEST
• Length: 10 characters repeated
• Method: C[i] = (P[i] + K[i mod 10]) mod 26
• Solved: 1999 (brute force search)"""
    
    ax1.text(0.05, 0.5, k1_text, fontsize=11, va='center')
    
    # K2: Keyed Caesar  
    ax2 = fig.add_subplot(3, 1, 2)
    ax2.axis('off')
    ax2.set_title('K2: Keyed Caesar (ABSCISSA)', fontsize=12, weight='bold', loc='left')
    
    k2_text = """• Key: ABSCISSA (single word)
• Alphabet: ABSCISSA + remaining letters
• Method: Monoalphabetic substitution with keyed alphabet
• Solved: 1999 (frequency analysis)"""
    
    ax2.text(0.05, 0.5, k2_text, fontsize=11, va='center')
    
    # K3: Transposition + Vigenère
    ax3 = fig.add_subplot(3, 1, 3)
    ax3.axis('off')
    ax3.set_title('K3: Columnar Transposition + Vigenère', fontsize=12, weight='bold', loc='left')
    
    # Visual grid for K3
    grid_ax = fig.add_axes([0.55, 0.12, 0.35, 0.15])
    grid_ax.set_xlim(-0.5, 6.5)
    grid_ax.set_ylim(-0.5, 4.5)
    
    # Draw 4×7 grid
    for row in range(4):
        for col in range(7):
            rect = Rectangle((col-0.4, row-0.4), 0.8, 0.8,
                           facecolor='lightgray', edgecolor='black', linewidth=0.5)
            grid_ax.add_patch(rect)
    
    grid_ax.set_xticks(range(7))
    grid_ax.set_yticks(range(4))
    grid_ax.set_xticklabels(range(7), fontsize=8)
    grid_ax.set_yticklabels(range(4), fontsize=8)
    grid_ax.set_xlabel('Columns (0-6)', fontsize=9)
    grid_ax.set_ylabel('Rows', fontsize=9)
    grid_ax.set_title('4×7 Co-prime Grid', fontsize=10)
    
    k3_text = """• Stage 1: Columnar transposition (4 rows × 7 columns)
• Stage 2: Vigenère decryption
• Co-prime dimensions: gcd(4,7) = 1
• Key insight: Fixed pattern from typographic cues
• Solved: 2000 (pattern recognition)

The 4×7 grid ensures full coverage through
co-prime property - precedent for K4's 
97 positions with L=17."""
    
    ax3.text(0.05, 0.5, k3_text, fontsize=11, va='center')
    
    plt.tight_layout()
    plt.savefig('ALGB_P3_K3_HINTS.pdf', format='pdf', bbox_inches='tight')
    plt.close()
    print("✅ Created ALGB_P3_K3_HINTS.pdf")

def create_page4_next_tests():
    """Page 4: What forces uniqueness"""
    fig = plt.figure(figsize=(8.5, 11))
    
    # Title
    fig.text(0.5, 0.95, 'What Forces Unique Solution?', 
             fontsize=20, weight='bold', ha='center')
    
    # Current constraints
    ax1 = fig.add_subplot(3, 1, 1)
    ax1.axis('off')
    ax1.set_title('Current Algebraic Constraints', fontsize=14, weight='bold', loc='left')
    
    current = """With 4 Anchors Alone:
    
✓ 24 positions determined (indices where anchors appear)
✗ 73 positions undetermined
✗ 26^73 possible completions
    
The algebra cannot determine more without additional information."""
    
    ax1.text(0.05, 0.5, current, fontsize=12, va='center')
    
    # What would force uniqueness?
    ax2 = fig.add_subplot(3, 1, 2)
    ax2.axis('off')
    ax2.set_title('Potential Additional Constraints', fontsize=14, weight='bold', loc='left')
    
    additional = """To achieve unique solution, need ONE of:
    
1. More anchor positions (cribs/known plaintext)
   • Each new anchor potentially determines its slot
   
2. Language constraints (if plaintext is English)
   • Dictionary words, bigram/trigram frequencies
   • Semantic coherence
   
3. Additional algebraic structure
   • Constraints on key material
   • Relationships between positions
   
4. The actual plaintext (ground truth)"""
    
    ax2.text(0.05, 0.5, additional, fontsize=12, va='center')
    
    # Falsifiable predictions
    ax3 = fig.add_subplot(3, 1, 3)
    ax3.axis('off')
    ax3.set_title('Falsifiable Predictions', fontsize=14, weight='bold', loc='left')
    
    predictions = """If this analysis is correct:
    
• Adding a 5th anchor at an unconstrained position would 
  determine exactly 1 more position (25 total)
  
• The tail region (74-96) cannot be determined without
  information beyond the current 4 anchors
  
• Position 74 specifically must remain free under any
  algebraic analysis using only the 4 anchors
  
• No algebraic manipulation can extract more than 24
  positions from these specific 4 anchors with L=17"""
    
    ax3.text(0.05, 0.7, predictions, fontsize=11, va='top')
    
    plt.tight_layout()
    plt.savefig('ALGB_P4_NEXT_TESTS.pdf', format='pdf', bbox_inches='tight')
    plt.close()
    print("✅ Created ALGB_P4_NEXT_TESTS.pdf")

def create_anchor_ledger():
    """Create text anchor ledger"""
    ledger = """K4 ANCHOR ARITHMETIC LEDGER
======================================================================

Index | Anchor | Class | Slot | C    | P    | K    | Formula
----------------------------------------------------------------------
   21 | EAST   |     3 |    4 | F= 5 | E= 4 | B= 1 | K = C - P = 5 - 4 = 1 (mod 26)
   22 | EAST   |     1 |    5 | L=11 | A= 0 | L=11 | K = C - P = 11 - 0 = 11 (mod 26)
   23 | EAST   |     5 |    6 | R=17 | S=18 | Z=25 | K = C - P = 17 - 18 = 25 (mod 26)
   24 | EAST   |     0 |    7 | V=21 | T=19 | C= 2 | K = C - P = 21 - 19 = 2 (mod 26)
   
   25 | NORTHE |     4 |    8 | Q=16 | N=13 | D= 3 | K = C - P = 16 - 13 = 3 (mod 26)
   26 | NORTHE |     2 |    9 | Q=16 | O=14 | C= 2 | K = C - P = 16 - 14 = 2 (mod 26)
   27 | NORTHE |     3 |   10 | P=15 | R=17 | Y=24 | K = C - P = 15 - 17 = 24 (mod 26)
   28 | NORTHE |     1 |   11 | R=17 | T=19 | Y=24 | K = C - P = 17 - 19 = 24 (mod 26)
   29 | NORTHE |     5 |   12 | N=13 | H= 7 | G= 6 | K = C - P = 13 - 7 = 6 (mod 26)
   30 | NORTHE |     0 |   13 | G= 6 | E= 4 | C= 2 | K = C - P = 6 - 4 = 2 (mod 26)
   31 | NORTHE |     4 |   14 | K=10 | A= 0 | K=10 | K = C - P = 10 - 0 = 10 (mod 26)
   32 | NORTHE |     2 |   15 | S=18 | S=18 | A= 0 | K = C - P = 18 - 18 = 0 (mod 26)
   33 | NORTHE |     3 |   16 | S=18 | T=19 | Z=25 | K = C - P = 18 - 19 = 25 (mod 26)
   
   63 | BERLIN |     3 |   12 | N=13 | B= 1 | M=12 | K = C - P = 13 - 1 = 12 (mod 26)
   64 | BERLIN |     1 |   13 | Y=24 | E= 4 | U=20 | K = C - P = 24 - 4 = 20 (mod 26)
   65 | BERLIN |     5 |   14 | P=15 | R=17 | Y=24 | K = C - P = 15 - 17 = 24 (mod 26)
   66 | BERLIN |     0 |   15 | V=21 | L=11 | K=10 | K = C - P = 21 - 11 = 10 (mod 26)
   67 | BERLIN |     4 |   16 | T=19 | I= 8 | L=11 | K = C - P = 19 - 8 = 11 (mod 26)
   68 | BERLIN |     2 |    0 | T=19 | N=13 | G= 6 | K = C - P = 19 - 13 = 6 (mod 26)
   
   69 | CLOCK  |     3 |    1 | M=12 | C= 2 | K=10 | K = C - P = 12 - 2 = 10 (mod 26)
   70 | CLOCK  |     1 |    2 | Z=25 | L=11 | O=14 | K = C - P = 25 - 11 = 14 (mod 26)
   71 | CLOCK  |     5 |    3 | F= 5 | O=14 | R=17 | K = C - P = 5 - 14 = 17 (mod 26)
   72 | CLOCK  |     0 |    4 | P=15 | C= 2 | N=13 | K = C - P = 15 - 2 = 13 (mod 26)
   73 | CLOCK  |     4 |    5 | K=10 | K=10 | A= 0 | K = C - P = 10 - 10 = 0 (mod 26)

Total: 24 positions algebraically determined by 4 anchors
"""
    
    with open('ANCHOR_LEDGER.txt', 'w') as f:
        f.write(ledger)
    print("✅ Created ANCHOR_LEDGER.txt")

def create_wheel_card_before():
    """Create visual wheel card showing before state"""
    fig = plt.figure(figsize=(11, 8.5))
    
    # Title
    fig.text(0.5, 0.95, 'Wheel State: Anchors Only (24 Determined)', 
             fontsize=18, weight='bold', ha='center')
    
    # Create 6 subplots for 6 classes
    for class_idx in range(6):
        ax = fig.add_subplot(2, 3, class_idx + 1)
        ax.set_xlim(-0.5, 16.5)
        ax.set_ylim(-0.5, 1.5)
        ax.set_title(f'Class {class_idx}', fontsize=12, weight='bold')
        
        # Forced slots for this class
        forced_slots = {
            0: {4: 'N', 7: 'C', 13: 'C', 15: 'K'},
            1: {2: 'O', 5: 'L', 11: 'Y', 13: 'U'},
            2: {0: 'G', 9: 'C', 15: 'A'},
            3: {1: 'K', 4: 'B', 10: 'Y', 12: 'M', 16: 'Z'},
            4: {5: 'A', 8: 'D', 14: 'K', 16: 'L'},
            5: {3: 'R', 6: 'Z', 12: 'G', 14: 'Y'}
        }
        
        # Draw slots
        for slot in range(17):
            if slot in forced_slots.get(class_idx, {}):
                # Forced - show value
                rect = Rectangle((slot-0.4, 0.1), 0.8, 0.8,
                               facecolor='lightblue', edgecolor='black', linewidth=1)
                ax.add_patch(rect)
                ax.text(slot, 0.5, forced_slots[class_idx][slot], 
                       fontsize=10, ha='center', va='center', weight='bold')
            else:
                # Unknown
                rect = Rectangle((slot-0.4, 0.1), 0.8, 0.8,
                               facecolor='white', edgecolor='gray', linewidth=0.5)
                ax.add_patch(rect)
                ax.text(slot, 0.5, '?', fontsize=10, ha='center', va='center', color='gray')
        
        ax.set_xticks(range(0, 17, 2))
        ax.set_yticks([])
        ax.set_xlabel('Slot', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('WHEEL_CARD_BEFORE.pdf', format='pdf', bbox_inches='tight')
    plt.close()
    print("✅ Created WHEEL_CARD_BEFORE.pdf")

def main():
    """Generate all ALGEBRA_CORE artifacts"""
    print("\n=== Creating ALGEBRA_CORE Package ===\n")
    
    # Create PDFs
    create_page1_24_of_97()
    create_page2_tail_p74()
    create_page3_k3_hints()
    create_page4_next_tests()
    
    # Create text artifacts
    create_anchor_ledger()
    create_wheel_card_before()
    
    print("\n✅ All ALGEBRA_CORE artifacts created!")
    print("\nFiles created:")
    print("  - ALGB_P1_24_of_97.pdf")
    print("  - ALGB_P2_TAIL_P74.pdf")
    print("  - ALGB_P3_K3_HINTS.pdf")
    print("  - ALGB_P4_NEXT_TESTS.pdf")
    print("  - ANCHOR_LEDGER.txt")
    print("  - WHEEL_CARD_BEFORE.pdf")

if __name__ == "__main__":
    main()