#!/usr/bin/env python3
"""
Create Core-Hardening v5 summary PDFs showing set-cover results and implications.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, FancyBboxPatch
import json

def create_set_cover_summary():
    """Create 1-page PDF explaining set-cover results"""
    fig = plt.figure(figsize=(8.5, 11))
    
    # Title
    fig.text(0.5, 0.95, 'Set-Cover Analysis: Mathematical Constraints', 
             fontsize=18, weight='bold', ha='center')
    
    # Key insight box
    ax1 = fig.add_subplot(4, 1, 1)
    ax1.axis('off')
    
    insight_text = """KEY INSIGHT (L=17):
    
With L=17 and 97 positions, each position maps to a UNIQUE (class, slot) pair.
This creates a 1-to-1 mapping, meaning:
  • 24 anchor positions → exactly 24 unique slots determined
  • 73 remaining positions → exactly 73 unique slots needed
  • Minimal set-cover = 73 (must constrain ALL remaining positions)"""
    
    bbox = FancyBboxPatch((0.05, 0.2), 0.9, 0.7,
                          boxstyle="round,pad=0.02",
                          facecolor='lightblue', edgecolor='navy', linewidth=2)
    ax1.add_patch(bbox)
    ax1.text(0.5, 0.55, insight_text, fontsize=11, ha='center', va='center', weight='bold')
    
    # Visual grid showing the problem
    ax2 = fig.add_subplot(4, 1, 2)
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 3)
    ax2.set_title('97 Positions: Each Maps to Unique Slot', fontsize=12, weight='bold')
    
    # Draw position boxes
    for i in range(97):
        if 21 <= i < 25:  # EAST
            color = 'lightgreen'
        elif 25 <= i < 34:  # NORTHEAST
            color = 'lightgreen'
        elif 63 <= i < 69:  # BERLIN
            color = 'lightgreen'
        elif 69 <= i < 74:  # CLOCK
            color = 'lightgreen'
        elif 74 <= i < 97:  # Tail
            color = 'yellow'
        else:
            color = 'lightcoral'
        
        x = (i % 20) * 5
        y = 2 - (i // 20) * 0.5
        rect = Rectangle((x, y), 4, 0.4, facecolor=color, edgecolor='black', linewidth=0.5)
        ax2.add_patch(rect)
    
    ax2.set_xlim(-1, 101)
    ax2.set_ylim(-0.5, 2.5)
    ax2.axis('off')
    
    # Legend
    green_patch = mpatches.Patch(color='lightgreen', label='Anchors (24)')
    yellow_patch = mpatches.Patch(color='yellow', label='Tail (23)')
    red_patch = mpatches.Patch(color='lightcoral', label='Other (50)')
    ax2.legend(handles=[green_patch, yellow_patch, red_patch], 
              loc='center', bbox_to_anchor=(0.5, -0.1), ncol=3)
    
    # Tail coverage analysis
    ax3 = fig.add_subplot(4, 1, 3)
    ax3.axis('off')
    
    coverage_text = """TAIL COVERAGE ANALYSIS:
    
• Tail region: positions 74-96 (23 positions)
• Under L=17: Each tail position covers exactly 1 unique slot
• Coverage: 23 of 73 needed slots (31.5%)
• Shortfall: 50 additional positions still needed

Mathematical conclusion: The tail alone CANNOT complete the solution."""
    
    ax3.text(0.1, 0.5, coverage_text, fontsize=11, va='center')
    
    # Alternative L values
    ax4 = fig.add_subplot(4, 1, 4)
    ax4.axis('off')
    
    alternatives = """ALTERNATIVE MECHANISMS:
    
• L=15: Reduces unknowns to 21 (tail would be sufficient!)
• L=20: Reduces unknowns to 49 (still need 26 beyond tail)
• L=17: Current hypothesis with 73 unknowns

Trade-off: Lower L values reduce unknowns but may violate other constraints."""
    
    ax4.text(0.1, 0.5, alternatives, fontsize=11, va='center')
    
    plt.tight_layout()
    plt.savefig('SET_COVER_EXPLAINED.pdf', format='pdf', bbox_inches='tight')
    plt.close()
    print("Created SET_COVER_EXPLAINED.pdf")

def create_implications_summary():
    """Create summary of mathematical implications"""
    fig = plt.figure(figsize=(8.5, 11))
    
    # Title
    fig.text(0.5, 0.95, 'Core-Hardening v5: What We Can Say', 
             fontsize=18, weight='bold', ha='center')
    
    # What's mathematically certain
    ax1 = fig.add_subplot(3, 1, 1)
    ax1.axis('off')
    ax1.set_title('Mathematically Certain (Pure Algebra)', fontsize=14, weight='bold', loc='left')
    
    certain_text = """✓ With 6-track class function and L=17:
  • Anchors determine exactly 24/97 positions
  • Each position maps to unique (class, slot) pair  
  • Need ALL 73 remaining positions for complete solution
  • No algebraic shortcut exists to reduce this

✓ Tail coverage under L=17:
  • 23-position tail covers 23 unique slots
  • 50 additional positions required beyond tail
  • This is a hard mathematical constraint"""
    
    ax1.text(0.05, 0.5, certain_text, fontsize=11, va='center')
    
    # What requires additional assumptions
    ax2 = fig.add_subplot(3, 1, 2)
    ax2.axis('off')
    ax2.set_title('Requires Additional Assumptions', fontsize=14, weight='bold', loc='left')
    
    assumptions_text = """? Choice of L=17:
  • L=15 would reduce unknowns to 21 (tail sufficient)
  • L=20 would reduce unknowns to 49
  • Why specifically L=17? (Not determined by algebra alone)

? Tail content:
  • Algebra shows 50 positions beyond tail are needed
  • What determines which 50?
  • Language constraints? Additional structure?

? Mechanism families:
  • Mixed Vigenère/Beaufort assumed
  • Other cipher families possible?"""
    
    ax2.text(0.05, 0.5, assumptions_text, fontsize=11, va='center')
    
    # Falsifiable predictions
    ax3 = fig.add_subplot(3, 1, 3)
    ax3.axis('off')
    ax3.set_title('Falsifiable Predictions', fontsize=14, weight='bold', loc='left')
    
    predictions_text = """If L=17 is correct:
  1. No subset of <73 additional positions can complete solution
  2. Any valid completion must specify all 73 missing positions
  3. The tail alone leaves exactly 50 positions undetermined

If L=15 is correct instead:
  1. Only 21 additional positions needed beyond anchors
  2. The 23-position tail would be sufficient
  3. Two tail positions would be redundant

These predictions can be tested against any proposed solution."""
    
    ax3.text(0.05, 0.7, predictions_text, fontsize=11, va='top')
    
    plt.tight_layout()
    plt.savefig('IMPLICATIONS_SUMMARY.pdf', format='pdf', bbox_inches='tight')
    plt.close()
    print("Created IMPLICATIONS_SUMMARY.pdf")

def main():
    """Create all summary PDFs"""
    print("\n=== Creating Core-Hardening v5 Summary PDFs ===")
    
    create_set_cover_summary()
    create_implications_summary()
    
    print("\n✅ Summary PDFs created")
    
    # Create final summary text
    with open('CORE_V5_SUMMARY.txt', 'w') as f:
        f.write("CORE-HARDENING V5 SUMMARY\n")
        f.write("=========================\n\n")
        f.write("Mathematical Facts (No Language Required):\n")
        f.write("------------------------------------------\n")
        f.write("• With L=17: Anchors determine 24/97 positions\n")
        f.write("• Minimal additional constraints needed: 73\n")
        f.write("• Tail (23 positions) covers: 23/73 slots\n")
        f.write("• Shortfall: 50 positions beyond tail required\n\n")
        
        f.write("Alternative Mechanisms:\n")
        f.write("-----------------------\n")
        f.write("• L=15: Only 21 unknowns (tail sufficient)\n")
        f.write("• L=20: 49 unknowns (26 beyond tail needed)\n")
        f.write("• L=17: 73 unknowns (current hypothesis)\n\n")
        
        f.write("Key Insight:\n")
        f.write("------------\n")
        f.write("The 1-to-1 mapping under L=17 means no algebraic\n")
        f.write("manipulation can reduce the 73 unknown positions.\n")
        f.write("This is a hard mathematical constraint, not a\n")
        f.write("limitation of our analysis methods.\n")
    
    print("Created CORE_V5_SUMMARY.txt")

if __name__ == "__main__":
    main()