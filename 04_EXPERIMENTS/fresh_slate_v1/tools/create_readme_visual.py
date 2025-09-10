#!/usr/bin/env python3
"""Create visual README diagram."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages

def create_visual_readme():
    """Create a visual README showing the fresh-slate derivation."""
    
    fig = plt.figure(figsize=(11, 8.5))
    
    # Title
    fig.text(0.5, 0.95, 'Fresh-Slate K4 Derivation', 
             ha='center', fontsize=20, fontweight='bold')
    fig.text(0.5, 0.92, 'Ciphertext + Cribs → Partial Plaintext (No AI, No Guessing)', 
             ha='center', fontsize=12, style='italic')
    
    # Create subplots
    ax1 = plt.subplot2grid((4, 2), (0, 0), colspan=2)  # Class strips
    ax2 = plt.subplot2grid((4, 2), (1, 0))  # Wheel diagram
    ax3 = plt.subplot2grid((4, 2), (1, 1))  # Decrypt rules
    ax4 = plt.subplot2grid((4, 2), (2, 0), colspan=2)  # Tail grid
    ax5 = plt.subplot2grid((4, 2), (3, 0), colspan=2)  # Results table
    
    # 1. Class strips
    ax1.set_title('6-Track Class System', fontsize=12, fontweight='bold')
    ax1.axis('off')
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#DDA0DD']
    class_positions = {
        0: [0, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72, 78, 84, 90, 96],
        1: [1, 7, 13, 19, 25, 31, 37, 43, 49, 55, 61, 67, 73, 79, 85, 91],
        2: [2, 8, 14, 20, 26, 32, 38, 44, 50, 56, 62, 68, 74, 80, 86, 92],
        3: [3, 9, 15, 21, 27, 33, 39, 45, 51, 57, 63, 69, 75, 81, 87, 93],
        4: [4, 10, 16, 22, 28, 34, 40, 46, 52, 58, 64, 70, 76, 82, 88, 94],
        5: [5, 11, 17, 23, 29, 35, 41, 47, 53, 59, 65, 71, 77, 83, 89, 95]
    }
    
    for cls in range(6):
        y = 0.8 - cls * 0.15
        ax1.text(0.02, y, f'Class {cls}:', fontsize=10, fontweight='bold')
        
        positions = class_positions[cls]
        for i, pos in enumerate(positions):
            x = 0.12 + i * 0.05
            if x > 0.95:
                break
            
            # Highlight crib positions
            if 21 <= pos <= 24:  # EAST
                ax1.add_patch(plt.Rectangle((x-0.02, y-0.02), 0.04, 0.06, 
                                           facecolor='yellow', alpha=0.5))
            elif 25 <= pos <= 33:  # NORTHEAST
                ax1.add_patch(plt.Rectangle((x-0.02, y-0.02), 0.04, 0.06, 
                                           facecolor='lightgreen', alpha=0.5))
            elif 63 <= pos <= 68:  # BERLIN
                ax1.add_patch(plt.Rectangle((x-0.02, y-0.02), 0.04, 0.06, 
                                           facecolor='lightblue', alpha=0.5))
            elif 69 <= pos <= 73:  # CLOCK
                ax1.add_patch(plt.Rectangle((x-0.02, y-0.02), 0.04, 0.06, 
                                           facecolor='pink', alpha=0.5))
            
            ax1.text(x, y, str(pos), fontsize=8, ha='center', 
                    color=colors[cls], fontweight='bold')
    
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    
    # 2. Wheel diagram
    ax2.set_title('Wheel Example (Class 3)', fontsize=11, fontweight='bold')
    ax2.axis('off')
    
    # Draw wheel slots
    slots = ['16', '3', '?', '12', '?', '?', '7', '?', '?', '?', '?', '?', '?', '4']
    slot_labels = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13']
    
    for i, (slot, label) in enumerate(zip(slots, slot_labels)):
        y = 0.8 - i * 0.06
        ax2.text(0.1, y, f'Slot {label}:', fontsize=9)
        
        if slot != '?':
            ax2.add_patch(plt.Rectangle((0.35, y-0.02), 0.15, 0.04, 
                                       facecolor='lightgreen', alpha=0.5))
            ax2.text(0.425, y, f'K={slot}', fontsize=9, ha='center', fontweight='bold')
        else:
            ax2.text(0.425, y, '?', fontsize=9, ha='center', color='gray')
        
        # Add index markers
        if i == 0:
            ax2.text(0.55, y, '← i=21 (E)', fontsize=8, color='blue')
        elif i == 3:
            ax2.text(0.55, y, '← i=15', fontsize=8, color='blue')
        elif i == 6:
            ax2.text(0.55, y, '← i=63 (B)', fontsize=8, color='blue')
    
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    
    # 3. Decrypt rules
    ax3.set_title('Decrypt Rules', fontsize=11, fontweight='bold')
    ax3.axis('off')
    
    rules = [
        ('Vigenère:', 'P = C - K (mod 26)'),
        ('Beaufort:', 'P = K - C (mod 26)'),
        ('Variant:', 'P = C + K (mod 26)')
    ]
    
    for i, (name, formula) in enumerate(rules):
        y = 0.7 - i * 0.2
        ax3.text(0.1, y, name, fontsize=10, fontweight='bold')
        ax3.text(0.1, y-0.08, formula, fontsize=9, family='monospace')
    
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    
    # 4. Tail grid
    ax4.set_title('Tail Region (Positions 74-96)', fontsize=11, fontweight='bold')
    ax4.axis('off')
    
    tail = "????????REGXUT?JOYQGMICH"
    positions = list(range(74, 97))
    
    # Draw grid
    for i, (pos, char) in enumerate(zip(positions, tail)):
        x = 0.05 + (i % 12) * 0.075
        y = 0.6 - (i // 12) * 0.3
        
        if char != '?':
            ax4.add_patch(plt.Rectangle((x-0.025, y-0.05), 0.05, 0.1, 
                                       facecolor='lightgreen', alpha=0.3))
        
        ax4.text(x, y+0.05, str(pos), fontsize=7, ha='center', color='gray')
        ax4.text(x, y-0.05, char, fontsize=10, ha='center', 
                fontweight='bold' if char != '?' else 'normal',
                color='black' if char != '?' else 'gray')
    
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    
    # 5. Results table
    ax5.set_title('Derivation Results', fontsize=11, fontweight='bold')
    ax5.axis('off')
    
    results = [
        ('Cribs Used', 'Derived', 'Unknown'),
        ('4 anchors (EAST, NE, BERLIN, CLOCK)', '71', '26'),
        ('3 anchors (no BERLIN)', '58', '39'),
        ('3 anchors (no CLOCK)', '57', '40'),
        ('2 anchors (EAST, NE)', '43', '54')
    ]
    
    for i, row in enumerate(results):
        y = 0.8 - i * 0.15
        style = 'bold' if i == 0 else 'normal'
        
        ax5.text(0.1, y, row[0], fontsize=9, fontweight=style)
        ax5.text(0.65, y, row[1], fontsize=9, ha='center', fontweight=style)
        ax5.text(0.85, y, row[2], fontsize=9, ha='center', fontweight=style)
        
        if i == 0:
            ax5.plot([0.05, 0.95], [y-0.05, y-0.05], 'k-', linewidth=1)
    
    ax5.set_xlim(0, 1)
    ax5.set_ylim(0, 1)
    
    # Save
    plt.tight_layout()
    plt.savefig('04_EXPERIMENTS/fresh_slate_v1/README_visual.png', dpi=150, bbox_inches='tight')
    
    # Also save as PDF
    with PdfPages('04_EXPERIMENTS/fresh_slate_v1/README_visual.pdf') as pdf:
        pdf.savefig(fig, bbox_inches='tight')
    
    plt.close()
    
    print("✅ Created README_visual.png and README_visual.pdf")

if __name__ == "__main__":
    create_visual_readme()