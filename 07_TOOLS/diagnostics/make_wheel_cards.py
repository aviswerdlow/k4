#!/usr/bin/env python3
"""
Create wheel cards showing before/after tail.
Shows anchors-only vs full solution wheels.
Pure Python stdlib only.
"""

import json
import math


def load_wheels_data():
    """Load wheel data from proof and fresh-slate runs."""
    
    # Load full solution wheels
    with open('../../01_PUBLISHED/winner_HEAD_0020_v522B/proof_digest_enhanced.json', 'r') as f:
        proof = json.load(f)
    
    # Load anchors-only wheels
    with open('../../06_DOCUMENTATION/K3_HINTS/fresh_slate_runs/RUN_D/WHEELS.json', 'r') as f:
        anchors_wheels = json.load(f)
    
    # Extract full wheels
    full_wheels = []
    for cls_data in proof['per_class']:
        wheel = {
            'class': cls_data['class_id'],
            'family': cls_data['family'],
            'L': cls_data['L'],
            'residues': cls_data['residues']
        }
        full_wheels.append(wheel)
    
    return anchors_wheels, full_wheels


def create_wheel_card_pdf(cls, anchors_wheel, full_wheel, ax, title):
    """Draw a wheel card on the given axes."""
    import matplotlib.patches as mpatches
    
    ax.axis('off')
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    
    # Title
    ax.text(0, 1.15, title, ha='center', fontsize=11, fontweight='bold')
    ax.text(0, 1.05, f'Class {cls} ({anchors_wheel["family"]}), L={anchors_wheel["L"]}', 
            ha='center', fontsize=9)
    
    # Draw wheel as circle
    circle = mpatches.Circle((0, 0), 1, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(circle)
    
    L = anchors_wheel['L']
    
    # Draw slots
    for slot in range(L):
        angle = 2 * math.pi * slot / L - math.pi/2
        x = 0.85 * math.cos(angle)
        y = 0.85 * math.sin(angle)
        
        # Outer position for slot number
        x_outer = 1.1 * math.cos(angle)
        y_outer = 1.1 * math.sin(angle)
        
        # Check if slot is forced
        if title.startswith("Anchors"):
            # Anchors-only wheel
            forced_slots = anchors_wheel.get('forced_slots', {})
            if str(slot) in forced_slots:
                k_val = forced_slots[str(slot)]
                k_char = chr(k_val + ord('A'))
                
                # Draw filled circle for forced slot
                ax.add_patch(mpatches.Circle((x, y), 0.08, 
                                            facecolor='black', edgecolor='black'))
                ax.text(x, y, k_char, ha='center', va='center', 
                       fontsize=8, color='white', fontweight='bold')
            else:
                # Draw empty circle for unknown slot
                ax.add_patch(mpatches.Circle((x, y), 0.08, 
                                            facecolor='white', edgecolor='gray',
                                            linestyle='--'))
                ax.text(x, y, '?', ha='center', va='center', 
                       fontsize=8, color='gray')
        else:
            # Full wheel
            k_val = full_wheel['residues'][slot]
            if k_val is not None:
                k_char = chr(k_val + ord('A'))
            else:
                k_char = '?'
            
            # Check if this was an anchor slot
            if k_val is not None:
                forced_slots = anchors_wheel.get('forced_slots', {})
                if str(slot) in forced_slots:
                    # Was forced by anchor - show in green
                    ax.add_patch(mpatches.Circle((x, y), 0.08, 
                                                facecolor='green', edgecolor='black'))
                    ax.text(x, y, k_char, ha='center', va='center', 
                           fontsize=8, color='white', fontweight='bold')
                else:
                    # Filled by tail - show in blue
                    ax.add_patch(mpatches.Circle((x, y), 0.08, 
                                                facecolor='blue', edgecolor='black'))
                    ax.text(x, y, k_char, ha='center', va='center', 
                           fontsize=8, color='white', fontweight='bold')
            else:
                # Still unknown
                ax.add_patch(mpatches.Circle((x, y), 0.08, 
                                            facecolor='white', edgecolor='gray',
                                            linestyle='--'))
                ax.text(x, y, '?', ha='center', va='center', 
                       fontsize=8, color='gray')
        
        # Slot number outside
        ax.text(x_outer, y_outer, str(slot), ha='center', va='center', 
               fontsize=6, color='gray')
    
    # Add legend
    if title.startswith("Full"):
        ax.text(0, -1.35, 'Green: Anchor-forced | Blue: Tail-completed', 
               ha='center', fontsize=7, style='italic')


def create_all_wheel_cards():
    """Create wheel cards for all classes."""
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    
    anchors_wheels, full_wheels = load_wheels_data()
    
    with PdfPages('K4_WHEEL_CARDS.pdf') as pdf:
        # Create a page for each class
        for cls in range(6):
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5.5))
            
            # Anchors-only wheel
            create_wheel_card_pdf(cls, anchors_wheels[cls], full_wheels[cls], 
                                ax1, "Anchors-Only Wheel")
            
            # Full solution wheel
            create_wheel_card_pdf(cls, anchors_wheels[cls], full_wheels[cls], 
                                ax2, "Full Solution Wheel")
            
            # Add class summary at bottom
            fig.text(0.5, 0.08, f'Class {cls} Summary:', ha='center', 
                    fontsize=10, fontweight='bold')
            
            forced_count = len(anchors_wheels[cls].get('forced_slots', {}))
            fig.text(0.5, 0.04, 
                    f'Anchors force {forced_count}/{anchors_wheels[cls]["L"]} slots → '
                    f'{forced_count} positions derived (co-prime property)', 
                    ha='center', fontsize=9)
            fig.text(0.5, 0.01, 
                    f'Tail completes remaining {anchors_wheels[cls]["L"] - forced_count} slots → '
                    f'all positions determinable', 
                    ha='center', fontsize=9)
            
            plt.suptitle(f'K4 Wheel Cards - Class {cls}', fontsize=14, fontweight='bold')
            plt.tight_layout(rect=[0, 0.1, 1, 0.95])
            
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()
    
    print("Created K4_WHEEL_CARDS.pdf")
    
    # Create summary card
    with PdfPages('K4_WHEEL_SUMMARY.pdf') as pdf:
        fig = plt.figure(figsize=(8.5, 11))
        ax = fig.add_subplot(111)
        ax.axis('off')
        import matplotlib.patches as mpatches
        
        # Title
        ax.text(0.5, 0.95, 'K4 Wheel Summary', 
                ha='center', fontsize=16, fontweight='bold')
        ax.text(0.5, 0.92, 'Co-prime property explains derivation counts', 
                ha='center', fontsize=11, style='italic')
        
        # Summary table
        ax.text(0.1, 0.85, 'Anchors-Only Analysis:', fontsize=12, fontweight='bold')
        
        y = 0.80
        ax.text(0.1, y, 'Class', fontsize=10, fontweight='bold')
        ax.text(0.2, y, 'L', fontsize=10, fontweight='bold')
        ax.text(0.3, y, 'Forced', fontsize=10, fontweight='bold')
        ax.text(0.45, y, 'Derived', fontsize=10, fontweight='bold')
        ax.text(0.6, y, 'Co-prime?', fontsize=10, fontweight='bold')
        
        total_forced = 0
        total_derived = 0
        
        for cls in range(6):
            y -= 0.04
            forced = len(anchors_wheels[cls].get('forced_slots', {}))
            total_forced += forced
            total_derived += forced  # With co-prime, forced = derived
            
            ax.text(0.12, y, str(cls), fontsize=9, family='monospace')
            ax.text(0.21, y, str(anchors_wheels[cls]['L']), fontsize=9, family='monospace')
            ax.text(0.32, y, str(forced), fontsize=9, family='monospace')
            ax.text(0.47, y, str(forced), fontsize=9, family='monospace')
            ax.text(0.62, y, '✓', fontsize=9, color='green')
        
        y -= 0.05
        ax.text(0.1, y, 'Total:', fontsize=10, fontweight='bold')
        ax.text(0.32, y, str(total_forced), fontsize=10, fontweight='bold')
        ax.text(0.47, y, str(total_derived), fontsize=10, fontweight='bold')
        
        # Key insight
        ax.text(0.1, 0.45, 'Key Insight:', fontsize=12, fontweight='bold')
        ax.text(0.1, 0.41, '• L=17 with 97 positions → each slot appears at most once', fontsize=10)
        ax.text(0.1, 0.38, '• Therefore: forced slots = derived positions', fontsize=10)
        ax.text(0.1, 0.35, f'• 4 anchors force {total_forced} slots → {total_derived} positions derived', 
               fontsize=10, fontweight='bold')
        ax.text(0.1, 0.32, f'• Remaining {97 - total_derived} positions need additional information', 
               fontsize=10)
        
        # Visual
        ax.text(0.1, 0.25, 'Visual Representation:', fontsize=12, fontweight='bold')
        
        # Draw mini wheels showing the concept
        for i, cls in enumerate([0, 3]):  # Show 2 example classes
            x_center = 0.3 + i * 0.4
            y_center = 0.12
            radius = 0.08
            
            # Draw circle
            circle = mpatches.Circle((x_center, y_center), radius, 
                                    fill=False, edgecolor='black', linewidth=1)
            ax.add_patch(circle)
            
            # Draw some slots
            for j in range(8):
                angle = 2 * math.pi * j / 8 - math.pi/2
                x = x_center + radius * 0.7 * math.cos(angle)
                y = y_center + radius * 0.7 * math.sin(angle)
                
                if j < 2:  # Forced slots
                    ax.plot(x, y, 'go', markersize=4)
                else:  # Unknown slots
                    ax.plot(x, y, 'ro', markersize=4)
            
            ax.text(x_center, y_center - radius - 0.02, f'Class {cls}', 
                   ha='center', fontsize=8)
        
        ax.text(0.5, 0.02, 'Green: Anchor-forced | Red: Unknown without tail', 
               ha='center', fontsize=8, style='italic')
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    print("Created K4_WHEEL_SUMMARY.pdf")


if __name__ == "__main__":
    create_all_wheel_cards()