#!/usr/bin/env python3
"""Create wheel-slot hit chart showing slot usage per class."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages


def create_slot_chart():
    """Create a visual chart showing slot usage for each class."""
    
    # Calculate slot usage for each class
    slot_usage = {}
    for cls in range(6):
        slot_usage[cls] = {}
        for i in range(97):
            if ((i % 2) * 3) + (i % 3) == cls:
                slot = i % 17
                if slot not in slot_usage[cls]:
                    slot_usage[cls][slot] = []
                slot_usage[cls][slot].append(i)
    
    # Create figure
    fig = plt.figure(figsize=(11, 8.5))
    ax = fig.add_subplot(111)
    ax.axis('off')
    
    # Title
    ax.text(0.5, 0.95, 'Wheel Slot Usage Chart (L=17)', 
            ha='center', fontsize=16, fontweight='bold')
    ax.text(0.5, 0.92, 'Each slot appears at most once per class in 97 positions', 
            ha='center', fontsize=12, style='italic')
    
    # Create grid for each class
    y_start = 0.85
    for cls in range(6):
        # Class header
        ax.text(0.05, y_start - cls * 0.14, f'Class {cls}:', 
                fontsize=11, fontweight='bold')
        
        # Family label
        families = ['vigenere', 'vigenere', 'beaufort', 'vigenere', 'beaufort', 'vigenere']
        ax.text(0.15, y_start - cls * 0.14, f'({families[cls]})', 
                fontsize=9, style='italic')
        
        # Draw slot grid
        for slot in range(17):
            x = 0.25 + slot * 0.04
            y = y_start - cls * 0.14
            
            # Check if slot is used
            if slot in slot_usage[cls]:
                indices = slot_usage[cls][slot]
                # Color based on whether it's a crib position
                crib_positions = [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33,
                                 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73]
                is_crib = any(idx in crib_positions for idx in indices)
                
                if is_crib:
                    color = 'lightgreen'
                    text_color = 'darkgreen'
                else:
                    color = 'lightblue'
                    text_color = 'darkblue'
                
                # Draw filled box
                ax.add_patch(mpatches.Rectangle((x-0.018, y-0.025), 0.036, 0.045, 
                                               facecolor=color, edgecolor='black', linewidth=0.5))
                
                # Show index in box
                ax.text(x, y, str(indices[0]), ha='center', va='center', 
                       fontsize=7, color=text_color)
                
                # Slot number below
                ax.text(x, y-0.04, str(slot), ha='center', va='center', 
                       fontsize=6, color='gray')
            else:
                # Draw empty box
                ax.add_patch(mpatches.Rectangle((x-0.018, y-0.025), 0.036, 0.045, 
                                               facecolor='white', edgecolor='gray', 
                                               linewidth=0.5, linestyle='--'))
                # Slot number below
                ax.text(x, y-0.04, str(slot), ha='center', va='center', 
                       fontsize=6, color='lightgray')
    
    # Legend
    ax.text(0.1, 0.08, 'Legend:', fontsize=11, fontweight='bold')
    
    # Crib position box
    ax.add_patch(mpatches.Rectangle((0.2, 0.06), 0.03, 0.025, 
                                   facecolor='lightgreen', edgecolor='black'))
    ax.text(0.25, 0.07, 'Crib position (anchors)', fontsize=9)
    
    # Non-crib position box
    ax.add_patch(mpatches.Rectangle((0.45, 0.06), 0.03, 0.025, 
                                   facecolor='lightblue', edgecolor='black'))
    ax.text(0.50, 0.07, 'Non-crib position', fontsize=9)
    
    # Empty slot box
    ax.add_patch(mpatches.Rectangle((0.7, 0.06), 0.03, 0.025, 
                                   facecolor='white', edgecolor='gray', linestyle='--'))
    ax.text(0.75, 0.07, 'Unused slot (>96)', fontsize=9)
    
    # Footer notes
    ax.text(0.5, 0.02, 'Numbers in boxes show message index (0-96), numbers below show slot (0-16)', 
            ha='center', fontsize=8, style='italic')
    
    # Save as PDF
    with PdfPages('../SLOT_USAGE_CHART.pdf') as pdf:
        pdf.savefig(fig, bbox_inches='tight')
    
    # Also save as PNG for embedding
    plt.savefig('../SLOT_USAGE_CHART.png', dpi=150, bbox_inches='tight')
    
    plt.close()
    print("Created SLOT_USAGE_CHART.pdf and SLOT_USAGE_CHART.png")


if __name__ == "__main__":
    create_slot_chart()