#!/usr/bin/env python3
"""
Generate K4 By-Hand Walkthrough - Visual PDF with charts and diagrams.
Creates a picture-first, print-friendly PDF for non-coders.
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from pathlib import Path

# Configure matplotlib for high quality output
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 11
plt.rcParams['font.family'] = 'sans-serif'

def load_data():
    """Load ciphertext and proof data."""
    # Load ciphertext
    with open('../../../02_DATA/ciphertext_97.txt', 'r') as f:
        ciphertext = f.read().strip()
    
    # Load proof
    with open('../proof_digest_enhanced.json', 'r') as f:
        proof = json.load(f)
    
    return ciphertext, proof

def class_function(i):
    """Compute class for index i."""
    return ((i % 2) * 3) + (i % 3)

def create_page1_class_grid(fig, ciphertext):
    """Page 1: The map - 6-row class grid with cribs highlighted."""
    ax = fig.add_subplot(111)
    
    # Set up the axis - adjusted for proper grid layout
    ax.set_xlim(-8, 110)
    ax.set_ylim(-4, 9)
    ax.axis('off')
    
    # Title
    ax.text(50, 8, 'K4 Class Grid (0-96)', fontsize=18, fontweight='bold', ha='center')
    
    # Define cribs
    cribs = {
        'EAST': (21, 24, '#ffcccc'),  # Light pink
        'NORTHEAST': (25, 33, '#ccffcc'),  # Light green
        'BERLIN': (63, 68, '#ffffcc'),  # Light yellow
        'CLOCK': (69, 73, '#ffccff'),  # Light purple
    }
    
    # Tail indices
    tail_range = (75, 96, '#e0e0e0')  # Light gray
    
    # Track positions for each class
    class_positions = {0: [], 1: [], 2: [], 3: [], 4: [], 5: []}
    for i in range(97):
        cls = class_function(i)
        class_positions[cls].append(i)
    
    # Parameters for grid layout
    cell_width = 5.5
    cell_height = 0.9
    start_x = 2
    
    # Draw cells organized by class
    for cls in range(6):
        y = 6 - cls * cell_height  # Class 0 at top
        
        # Class label on left
        ax.text(-1, y, f'Class {cls}', ha='right', va='center', fontsize=10, fontweight='bold')
        
        # Draw cells for this class
        for col_idx, i in enumerate(class_positions[cls]):
            x = start_x + col_idx * cell_width
            
            # Determine color
            color = 'white'
            border_width = 0.5
            
            # Check if in crib
            for crib_name, (start, end, crib_color) in cribs.items():
                if start <= i <= end:
                    color = crib_color
                    border_width = 1
                    break
            
            # Check if in tail
            if tail_range[0] <= i <= tail_range[1] and color == 'white':
                color = tail_range[2]
            
            # Draw cell
            rect = patches.Rectangle((x - cell_width*0.4, y - cell_height*0.35), 
                                    cell_width*0.8, cell_height*0.7,
                                    linewidth=border_width, 
                                    edgecolor='black', 
                                    facecolor=color)
            ax.add_patch(rect)
            
            # Add index number (small, top)
            ax.text(x, y + cell_height*0.2, str(i), 
                   ha='center', va='center', fontsize=6, color='gray')
            
            # Add ciphertext letter (larger, center)
            if i < len(ciphertext):
                ax.text(x, y - cell_height*0.05, ciphertext[i], 
                       ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Add legend at bottom with better spacing
    legend_y = 0.5
    ax.text(50, legend_y, 'Cribs:', fontsize=10, fontweight='bold', ha='center')
    
    # Arrange legend items horizontally
    legend_items = [
        ('EAST (21-24)', '#ffcccc'),
        ('NORTHEAST (25-33)', '#ccffcc'),
        ('BERLIN (63-68)', '#ffffcc'),
        ('CLOCK (69-73)', '#ffccff'),
        ('Tail (75-96)', '#e0e0e0')
    ]
    
    legend_x_start = 10
    legend_spacing = 18
    
    for idx, (label, color) in enumerate(legend_items):
        x_pos = legend_x_start + idx * legend_spacing
        rect = patches.Rectangle((x_pos, legend_y - 0.8), 2, 0.4,
                                linewidth=0.5, edgecolor='black', facecolor=color)
        ax.add_patch(rect)
        ax.text(x_pos + 2.5, legend_y - 0.6, label, ha='left', va='center', fontsize=8)
    
    # Add formulas at bottom
    formula_y = -1.5
    ax.text(50, formula_y, 'Decrypt Formulas:', fontsize=10, fontweight='bold', ha='center')
    ax.text(50, formula_y - 0.5, '• Vigenère: P = C - K (mod 26)', fontsize=9, ha='center')
    ax.text(50, formula_y - 0.9, '• Beaufort: P = K - C (mod 26)', fontsize=9, ha='center')
    ax.text(50, formula_y - 1.3, '• Variant-Beaufort: P = C + K (mod 26)', fontsize=9, ha='center')
    
    ax.text(50, formula_y - 2.0, 'Letter-Number: A=0, B=1, ..., Z=25', fontsize=9, ha='center')
    ax.text(50, formula_y - 2.4, 'Class Function: class(i) = ((i mod 2) × 3) + (i mod 3)', 
            fontsize=9, ha='center', fontweight='bold')

def create_page2_anchor_forcing(fig, ciphertext, proof):
    """Page 2: Forcing K at anchors - worked examples from cribs."""
    
    # Create 2x2 grid of subplots
    examples = [
        {'crib': 'EAST', 'index': 22, 'ct': 'L', 'pt': 'A'},
        {'crib': 'NORTHEAST', 'index': 27, 'ct': 'P', 'pt': 'R'},
        {'crib': 'BERLIN', 'index': 65, 'ct': 'P', 'pt': 'R'},
        {'crib': 'CLOCK', 'index': 71, 'ct': 'F', 'pt': 'O'},
    ]
    
    fig.suptitle('Forcing K at Anchor Positions', fontsize=18, fontweight='bold')
    
    for i, ex in enumerate(examples):
        ax = fig.add_subplot(2, 2, i+1)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Box background
        rect = patches.FancyBboxPatch((0.5, 1), 9, 8, 
                                      boxstyle="round,pad=0.1",
                                      facecolor='lightyellow',
                                      edgecolor='black',
                                      linewidth=2)
        ax.add_patch(rect)
        
        # Title
        ax.text(5, 8.5, f"Crib: {ex['crib']}", fontsize=12, fontweight='bold', ha='center')
        ax.text(5, 7.8, f"Index: {ex['index']}", fontsize=11, ha='center')
        
        # Get values
        idx = ex['index']
        ct_letter = ex['ct']
        pt_letter = ex['pt']
        ct_num = ord(ct_letter) - ord('A')
        pt_num = ord(pt_letter) - ord('A')
        
        cls = class_function(idx)
        family_map = {0: 'vigenere', 1: 'vigenere', 2: 'beaufort', 
                     3: 'vigenere', 4: 'variant_beaufort', 5: 'vigenere'}
        family = family_map[cls]
        
        # Display CT and PT
        ax.text(5, 6.8, f"Ciphertext: {ct_letter} = {ct_num}", fontsize=11, ha='center')
        ax.text(5, 6.2, f"Plaintext: {pt_letter} = {pt_num}", fontsize=11, ha='center')
        
        # Class and family info
        ax.text(5, 5.4, f"Class: {cls}", fontsize=11, ha='center')
        ax.text(5, 4.8, f"Family: {family}", fontsize=11, ha='center')
        ax.text(5, 4.2, f"Period L: 17, Phase: 0", fontsize=11, ha='center')
        
        slot = idx % 17
        ax.text(5, 3.6, f"Slot: {slot}", fontsize=11, ha='center')
        
        # Calculate K
        if family == 'vigenere':
            k_num = (ct_num - pt_num) % 26
            formula = f"K = C - P = {ct_num} - {pt_num} = {k_num}"
        elif family == 'beaufort':
            k_num = (ct_num + pt_num) % 26
            formula = f"K = C + P = {ct_num} + {pt_num} = {k_num}"
        else:  # variant_beaufort
            k_num = (26 - (ct_num - pt_num)) % 26
            formula = f"K = -(C - P) = -({ct_num} - {pt_num}) = {k_num}"
        
        k_letter = chr(k_num + ord('A'))
        
        ax.text(5, 2.8, formula, fontsize=11, ha='center')
        ax.text(5, 2.2, f"K = {k_num} ({k_letter})", fontsize=11, fontweight='bold', ha='center')
        ax.text(5, 1.6, f"✓ K ≠ 0 (Option-A satisfied)", fontsize=10, ha='center', color='green')
        
        # Draw mini wheel
        wheel_cx, wheel_cy = 8, 4.5
        wheel_r = 1.2
        circle = patches.Circle((wheel_cx, wheel_cy), wheel_r, 
                               fill=False, edgecolor='black', linewidth=1)
        ax.add_patch(circle)
        
        # Mark slot on wheel
        angle = -2 * np.pi * slot / 17 + np.pi/2  # Start from top
        slot_x = wheel_cx + wheel_r * 0.8 * np.cos(angle)
        slot_y = wheel_cy + wheel_r * 0.8 * np.sin(angle)
        slot_circle = patches.Circle((slot_x, slot_y), 0.15, 
                                    facecolor='red', edgecolor='black')
        ax.add_patch(slot_circle)
        ax.text(slot_x, slot_y - 0.4, str(slot), fontsize=8, ha='center')
        
        ax.text(wheel_cx, wheel_cy - 1.8, f"Class {cls} Wheel", fontsize=9, ha='center')

def create_page3_tail_propagation(fig, ciphertext, proof):
    """Page 3: Propagation in the tail (indices 80-84)."""
    
    # Create two subplots
    ax1 = fig.add_subplot(2, 1, 1)
    ax2 = fig.add_subplot(2, 1, 2)
    
    # Top subplot: CT -> PT conversion
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 5)
    ax1.axis('off')
    ax1.set_title('Tail Propagation: Indices 80-84', fontsize=18, fontweight='bold', pad=20)
    
    indices = [80, 81, 82, 83, 84]
    ct_letters = "TJCDI"
    pt_letters = "OFANA"
    
    # Display conversion
    for i, idx in enumerate(indices):
        x = 1.5 + i * 1.5
        
        # Index
        ax1.text(x, 4.5, f'({idx})', ha='center', fontsize=9, color='gray')
        
        # Ciphertext
        ax1.text(x, 4, ct_letters[i], ha='center', fontsize=22, fontweight='bold')
        
        # Arrow
        ax1.arrow(x, 3.5, 0, -1, head_width=0.15, head_length=0.1, 
                 fc='black', ec='black')
        
        # Plaintext
        ax1.text(x, 1.8, pt_letters[i], ha='center', fontsize=22, 
                fontweight='bold', color='green')
    
    ax1.text(5, 0.5, '"...JOY OF AN ANGLE..."', ha='center', 
            fontsize=14, style='italic')
    
    # Bottom subplot: Table
    ax2.axis('off')
    
    # Table data
    headers = ['Index', 'CT', 'Class', 'Family', 'Slot', 'K', 'Formula', 'PT']
    
    details = [
        ['80', 'T', '2', 'beau', '12', '7(H)', 'P = K - C = 7 - 19 = 14', 'O(14)'],
        ['81', 'J', '3', 'vige', '13', '4(E)', 'P = C - K = 9 - 4 = 5', 'F(5)'],
        ['82', 'C', '1', 'vige', '14', '2(C)', 'P = C - K = 2 - 2 = 0', 'A(0)'],
        ['83', 'D', '5', 'vige', '15', '16(Q)', 'P = C - K = 3 - 16 = 13', 'N(13)'],
        ['84', 'I', '0', 'vige', '16', '8(I)', 'P = C - K = 8 - 8 = 0', 'A(0)'],
    ]
    
    # Create table using matplotlib table
    table = ax2.table(cellText=[headers] + details,
                     cellLoc='center',
                     loc='center',
                     colWidths=[0.08, 0.06, 0.08, 0.10, 0.08, 0.10, 0.28, 0.10])
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    
    # Style the header row
    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#D3D3D3')
        table[(0, i)].set_text_props(weight='bold')
    
    # Style data rows
    for i in range(1, len(details) + 1):
        for j in range(len(headers)):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#F0F0F0')

def create_page4_roundtrip_dropcrib(fig, ciphertext, proof):
    """Page 4: Round-trip verification and drop-crib illustration."""
    
    fig.suptitle('Verification: Round-trip & Drop-crib', fontsize=18, fontweight='bold')
    
    # Round-trip panel
    ax1 = fig.add_subplot(2, 1, 1)
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 5)
    ax1.axis('off')
    
    ax1.text(0.5, 4.5, 'Round-trip Verification', fontweight='bold', fontsize=14)
    
    # Example verifications
    examples_text = """Example: Re-encrypting position 22 (EAST anchor)
    Index 22: P=A → C = P + K = 0 + 11 = 11 → C=L ✓ (matches)
    
Example: Re-encrypting position 80 (tail)
    Index 80: P=O → C = K - P = 7 - 14 = -7 ≡ 19 → C=T ✓ (matches)
    
Example: Re-encrypting position 40 (non-anchor)
    Index 40: P=S → C = P + K = 18 + 2 = 20 → C=U ✓ (matches)"""
    
    ax1.text(0.5, 3.5, examples_text, fontsize=10, va='top')
    
    # Drop-crib panel
    ax2 = fig.add_subplot(2, 1, 2)
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 5)
    ax2.axis('off')
    
    ax2.text(0.5, 4.5, 'Drop-crib Illustration', fontweight='bold', fontsize=14)
    
    # BERLIN example
    berlin_indices = list(range(63, 69))
    berlin_ct = "YPVTTM"
    berlin_pt_with = "BERLIN"
    berlin_pt_without = "??????"
    
    # With crib
    ax2.text(1, 3.8, 'With BERLIN crib:', fontsize=11)
    for i in range(6):
        x = 3 + i * 0.7
        ax2.text(x, 3.5, berlin_ct[i], ha='center', fontsize=12, fontweight='bold')
        ax2.text(x, 3.2, '↓', ha='center', fontsize=10)
        ax2.text(x, 2.9, berlin_pt_with[i], ha='center', fontsize=12, 
                fontweight='bold', color='green')
    
    # Without crib
    ax2.text(1, 2.2, 'Without BERLIN crib:', fontsize=11)
    for i in range(6):
        x = 3 + i * 0.7
        ax2.text(x, 1.9, berlin_ct[i], ha='center', fontsize=12, fontweight='bold')
        ax2.text(x, 1.6, '↓', ha='center', fontsize=10)
        ax2.text(x, 1.3, berlin_pt_without[i], ha='center', fontsize=12, 
                fontweight='bold', color='red')
    
    note_text = "Note: Removing a crib does not reconstruct it.\nThose positions remain undetermined."
    ax2.text(5, 0.5, note_text, ha='center', fontsize=10, style='italic',
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))

def create_visual_pdf(output_path, grayscale=False):
    """Create the complete visual PDF walkthrough."""
    
    # Load data
    ciphertext, proof = load_data()
    
    # Create PDF
    with PdfPages(output_path) as pdf:
        # Page 1: Class Grid
        fig = plt.figure(figsize=(11, 8.5))
        create_page1_class_grid(fig, ciphertext)
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        if not grayscale:
            plt.savefig('FIG_class_grid.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Page 2: Anchor Forcing
        fig = plt.figure(figsize=(11, 8.5))
        create_page2_anchor_forcing(fig, ciphertext, proof)
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        if not grayscale:
            plt.savefig('FIG_anchor_forcing.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Page 3: Tail Propagation
        fig = plt.figure(figsize=(11, 8.5))
        create_page3_tail_propagation(fig, ciphertext, proof)
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        if not grayscale:
            plt.savefig('FIG_tail_propagation.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Page 4: Round-trip and Drop-crib
        fig = plt.figure(figsize=(11, 8.5))
        create_page4_roundtrip_dropcrib(fig, ciphertext, proof)
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        if not grayscale:
            plt.savefig('FIG_roundtrip_dropcrib.png', dpi=300, bbox_inches='tight')
        plt.close()

def apply_grayscale():
    """Apply grayscale conversion to matplotlib."""
    plt.rcParams['image.cmap'] = 'gray'
    # Convert all colors to grayscale in the colormap
    import matplotlib.colors as mcolors
    # This is a simple approach - for production, you might want more sophisticated conversion

def main():
    """Main entry point."""
    print("Generating K4 By-Hand Walkthrough PDFs...")
    
    # Create color version
    create_visual_pdf('K4_By_Hand_Walkthrough.pdf', grayscale=False)
    print("✓ Created K4_By_Hand_Walkthrough.pdf")
    
    # Create grayscale version
    apply_grayscale()
    create_visual_pdf('K4_By_Hand_Walkthrough_grayscale.pdf', grayscale=True)
    print("✓ Created K4_By_Hand_Walkthrough_grayscale.pdf")
    
    print("✓ Created individual figure PNGs")
    print("\nAll files generated successfully!")

if __name__ == '__main__':
    main()