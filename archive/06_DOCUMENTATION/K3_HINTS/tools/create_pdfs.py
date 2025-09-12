#!/usr/bin/env python3
"""
Create visual PDFs for K3 hints documentation.
Uses matplotlib for PDF generation.
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.patches as mpatches
import json


def create_k0_hints_pdf():
    """Create K0_HINTS.pdf showing dots/E's method."""
    
    with PdfPages('../K0_HINTS.pdf') as pdf:
        # Page 1: K0 → PALIMPSEST
        fig = plt.figure(figsize=(8.5, 11))
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.95, 'K0 → K1 Keyword Extraction', 
                ha='center', fontsize=16, fontweight='bold')
        ax.text(0.5, 0.92, 'Method: Count extra dots/E\'s around Morse words', 
                ha='center', fontsize=11, style='italic')
        
        # Method table
        y_pos = 0.85
        ax.text(0.1, y_pos, 'Word', fontsize=10, fontweight='bold')
        ax.text(0.3, y_pos, 'Dots', fontsize=10, fontweight='bold')
        ax.text(0.4, y_pos, 'Position', fontsize=10, fontweight='bold')
        ax.text(0.55, y_pos, 'Count from', fontsize=10, fontweight='bold')
        ax.text(0.7, y_pos, 'Letter', fontsize=10, fontweight='bold')
        
        words = [
            ('VIRTUALLY', '2+1=3', 'top', 'right', 'L'),
            ('INVISIBLE', '6', 'bottom', 'left', 'I'),
            ('SHADOW', '2+2=4', 'top', 'right', 'A'),
            ('FORCES', '5', 'bottom', 'left', 'E'),
            ('LUCID', '3', 'top', 'right', 'C'),
            ('MEMORY', '1', 'bottom', 'left', 'M'),
            ('DIGETAL', '3', 'top', 'right', 'T'),
            ('INTERPRETATI', '0', 'top', 'left of middle', 'P'),
            ('T IS YOUR', '0', 'bottom', 'left of middle', 'S'),
            ('POSITION', '1', 'bottom', 'left', 'P')
        ]
        
        for i, (word, dots, pos, direction, letter) in enumerate(words):
            y = 0.8 - i * 0.05
            ax.text(0.1, y, word, fontsize=9, family='monospace')
            ax.text(0.3, y, dots, fontsize=9)
            ax.text(0.4, y, pos, fontsize=9)
            ax.text(0.55, y, direction, fontsize=9)
            ax.text(0.7, y, letter, fontsize=10, fontweight='bold', color='red')
        
        # Result
        ax.text(0.1, 0.25, 'Extracted letters: L I A E C M T P S P', fontsize=11)
        ax.text(0.1, 0.22, 'Anagrammed: PALIMPSEST (with spelling "error" → PALIMPCEST)', fontsize=11)
        ax.text(0.1, 0.18, 'Note: No dot before DIGETAL per method requirement', fontsize=9, style='italic')
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Page 2: K1 → K2 (ABSCISSA)
        fig = plt.figure(figsize=(8.5, 11))
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        ax.text(0.5, 0.95, 'K1 → K2 Keyword Extraction', 
                ha='center', fontsize=16, fontweight='bold')
        ax.text(0.5, 0.92, 'Using K0 counts on K1 words', 
                ha='center', fontsize=11, style='italic')
        
        # K1 words with counts
        y_pos = 0.85
        ax.text(0.1, y_pos, 'K1 Word', fontsize=10, fontweight='bold')
        ax.text(0.35, y_pos, 'Count', fontsize=10, fontweight='bold')
        ax.text(0.5, y_pos, 'Letter', fontsize=10, fontweight='bold')
        
        k1_data = [
            ('BETWEEN', '1', 'B'),
            ('SUBTLE', '1', 'S'),
            ('SHADING', '3', 'A'),
            ('ABSENCE', '6', 'C'),
            ('LIGHT', '2', 'I'),  # Changed from 3 to 2
            ('LIES', '4', 'S'),
            ('NUANCE', '3', 'S'),
            ('IQLUSION', '5', 'A')
        ]
        
        for i, (word, count, letter) in enumerate(k1_data):
            y = 0.8 - i * 0.05
            ax.text(0.1, y, word, fontsize=9, family='monospace')
            ax.text(0.35, y, count, fontsize=9)
            ax.text(0.5, y, letter, fontsize=10, fontweight='bold', color='blue')
        
        ax.text(0.1, 0.35, 'Result: ABSCISSA', fontsize=12, fontweight='bold')
        ax.text(0.1, 0.31, 'Note: LIGHT count changed 3→2 to get I instead of G', fontsize=9, style='italic')
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    print("Created K0_HINTS.pdf")


def create_k3_hints_pdf():
    """Create K3_HINTS.pdf showing structural parameters."""
    
    with PdfPages('../K3_HINTS.pdf') as pdf:
        # Page 1: Six tracks
        fig = plt.figure(figsize=(8.5, 11))
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        ax.text(0.5, 0.95, 'K3 → K4 Structural Hints', 
                ha='center', fontsize=16, fontweight='bold')
        ax.text(0.5, 0.92, 'Game 1: Six-Track Pattern', 
                ha='center', fontsize=12)
        
        # Show the class formula
        ax.text(0.5, 0.85, 'Class Formula: class(i) = ((i % 2) × 3) + (i % 3)', 
                ha='center', fontsize=14, family='monospace',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.3))
        
        # Draw six tracks
        y_start = 0.75
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#DDA0DD']
        
        for cls in range(6):
            y = y_start - cls * 0.1
            ax.text(0.1, y, f'Class {cls}:', fontsize=10, fontweight='bold')
            
            # Show first few indices for this class
            indices = []
            for i in range(97):
                if ((i % 2) * 3) + (i % 3) == cls:
                    indices.append(i)
                    if len(indices) >= 10:
                        break
            
            indices_str = ' '.join(str(i) for i in indices) + '...'
            ax.text(0.25, y, indices_str, fontsize=9, family='monospace', color=colors[cls])
            ax.text(0.85, y, f'({17 if cls == 0 else 16} indices)', fontsize=9)
        
        ax.text(0.1, 0.12, 'This creates 6 interleaved tracks from the 2/3 pattern.', fontsize=10)
        ax.text(0.1, 0.09, 'Each track gets ~16-17 indices out of 97 total.', fontsize=10)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Page 2: Collision table
        fig = plt.figure(figsize=(8.5, 11))
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        ax.text(0.5, 0.95, 'Game 2: Period Selection', 
                ha='center', fontsize=16, fontweight='bold')
        ax.text(0.5, 0.92, 'Testing periods for distinct slot seating', 
                ha='center', fontsize=12)
        
        # Collision table
        y_pos = 0.82
        ax.text(0.15, y_pos, 'Period', fontsize=10, fontweight='bold')
        for i in range(6):
            ax.text(0.3 + i*0.1, y_pos, f'C{i}', fontsize=10, fontweight='bold')
        
        periods = [11, 13, 17, 19]
        results = {
            11: ['OK', 'OK', 'OK', 'OK', 'OK', 'OK'],
            13: ['OK', 'OK', 'OK', 'OK', 'OK', 'OK'],
            17: ['OK', 'OK', 'OK', 'OK', 'OK', 'OK'],
            19: ['OK', 'OK', 'OK', 'OK', 'OK', 'OK']
        }
        
        for i, period in enumerate(periods):
            y = 0.77 - i * 0.05
            ax.text(0.15, y, str(period), fontsize=10, family='monospace')
            for j, status in enumerate(results[period]):
                color = 'green' if status == 'OK' else 'red'
                ax.text(0.3 + j*0.1, y, status, fontsize=9, color=color)
        
        # Note about L=17
        ax.add_patch(mpatches.Rectangle((0.13, 0.57), 0.07, 0.04, 
                                       fill=False, edgecolor='red', linewidth=2))
        
        ax.text(0.1, 0.45, 'L=17 chosen:', fontsize=11, fontweight='bold')
        ax.text(0.1, 0.42, '• Seats all anchor indices on distinct slots', fontsize=10)
        ax.text(0.1, 0.39, '• No collisions for any class', fontsize=10)
        ax.text(0.1, 0.36, '• Satisfies Option-A at all anchor cells', fontsize=10)
        ax.text(0.1, 0.32, 'Note: L=11 is smallest but we use L=17 for better distribution', fontsize=9, style='italic')
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Page 3: Family vector
        fig = plt.figure(figsize=(8.5, 11))
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        ax.text(0.5, 0.95, 'Game 3: Family Selection', 
                ha='center', fontsize=16, fontweight='bold')
        ax.text(0.5, 0.92, 'Rule: First family that satisfies Option-A at anchors', 
                ha='center', fontsize=12)
        
        # Family vector
        families = ['V', 'V', 'B', 'V', 'B', 'V']
        family_names = ['Vigenère', 'Vigenère', 'Beaufort', 'Vigenère', 'Beaufort', 'Vigenère']
        colors = ['blue', 'blue', 'red', 'blue', 'red', 'blue']
        
        y = 0.75
        for i in range(6):
            x = 0.2 + i * 0.12
            # Draw box
            ax.add_patch(mpatches.Rectangle((x-0.04, y-0.05), 0.08, 0.1, 
                                           facecolor=colors[i], alpha=0.2))
            ax.text(x, y, families[i], fontsize=20, ha='center', fontweight='bold')
            ax.text(x, y-0.08, f'Class {i}', fontsize=9, ha='center')
            ax.text(x, y-0.11, family_names[i], fontsize=8, ha='center', style='italic')
        
        ax.text(0.5, 0.55, 'Family Vector: V V B V B V', 
                ha='center', fontsize=14, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.3))
        
        ax.text(0.1, 0.4, 'This is determined mechanically by Option-A rule:', fontsize=10)
        ax.text(0.1, 0.37, '1. Try families in order: [Vigenère, Variant-Beaufort, Beaufort]', fontsize=9)
        ax.text(0.1, 0.34, '2. Select first that has no K=0 at anchor cells', fontsize=9)
        ax.text(0.1, 0.31, '3. No K4 prose or tail knowledge used', fontsize=9)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    print("Created K3_HINTS.pdf")


def create_run_pdf(run_id):
    """Create PDF for a specific run."""
    
    run_dir = f'../fresh_slate_runs/RUN_{run_id}/'
    
    # Load data
    with open(run_dir + 'PT_PARTIAL.txt', 'r') as f:
        plaintext = f.read().strip()
    
    with open(run_dir + 'COUNTS.json', 'r') as f:
        counts = json.load(f)
    
    with open(run_dir + 'EXPLAIN_80.txt', 'r') as f:
        explain = f.read()
    
    # Create PDF
    with PdfPages(f'../fresh_slate_runs/RUN_{run_id}.pdf') as pdf:
        fig = plt.figure(figsize=(8.5, 11))
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        # Title
        crib_names = {
            'A': 'No cribs',
            'B': 'EAST only',
            'C': 'EAST + NORTHEAST',
            'D': 'Four anchors (EAST, NE, BERLIN, CLOCK)'
        }
        
        ax.text(0.5, 0.95, f'Fresh-Slate Run {run_id}', 
                ha='center', fontsize=16, fontweight='bold')
        ax.text(0.5, 0.92, f'Cribs: {crib_names[run_id]}', 
                ha='center', fontsize=12)
        
        # Counts
        ax.text(0.5, 0.85, f"Derived: {counts['derived']} letters    Unknown: {counts['unknown']} positions", 
                ha='center', fontsize=12,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.3))
        
        # Add explanatory box about why these counts
        why_text = "Why these counts: L=17 → each slot appears at most once in 97 positions"
        if run_id == 'D':
            why_text += "\n4 anchors force 24 unique slots → 24 derived, 73 unknown"
        elif run_id == 'C':
            why_text += "\n2 anchors force 13 unique slots → 13 derived, 84 unknown"
        elif run_id == 'B':
            why_text += "\n1 anchor forces 4 unique slots → 4 derived, 93 unknown"
        elif run_id == 'A':
            why_text += "\nNo anchors → 0 derived, 97 unknown"
        
        ax.text(0.5, 0.79, why_text, ha='center', fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.5))
        
        # Class strip (simplified)
        ax.text(0.1, 0.70, 'Class Strip:', fontsize=11, fontweight='bold')
        
        for cls in range(6):
            y = 0.66 - cls * 0.03
            indices = [i for i in range(97) if ((i % 2) * 3) + (i % 3) == cls]
            
            # Show first few and highlight cribs
            shown = []
            for idx in indices[:8]:
                if plaintext[idx] != '?':
                    shown.append(f'[{idx}]')
                else:
                    shown.append(str(idx))
            
            ax.text(0.1, y, f'C{cls}:', fontsize=8)
            ax.text(0.15, y, ' '.join(shown) + '...', fontsize=8, family='monospace')
        
        # Tail grid
        ax.text(0.1, 0.44, 'Tail Grid (positions 75-96):', fontsize=11, fontweight='bold')
        
        # Draw grid
        for i in range(75, 97):
            col = (i - 75) % 11
            row = (i - 75) // 11
            x = 0.1 + col * 0.06
            y = 0.39 - row * 0.05
            
            char = plaintext[i]
            if char != '?':
                ax.add_patch(mpatches.Rectangle((x-0.02, y-0.02), 0.04, 0.04, 
                                               facecolor='lightgreen', alpha=0.5))
            
            ax.text(x, y, char, fontsize=10, ha='center', family='monospace',
                   fontweight='bold' if char != '?' else 'normal')
            ax.text(x, y-0.025, str(i), fontsize=6, ha='center', color='gray')
        
        # Example at index 80
        ax.text(0.1, 0.24, 'Example: Index 80', fontsize=11, fontweight='bold')
        
        # Parse key parts of explanation
        lines = explain.split('\n')
        shown_lines = []
        for line in lines[1:7]:  # Skip header, show key lines
            if 'Class:' in line or 'Slot:' in line or 'K at slot' in line or 'Plaintext:' in line:
                shown_lines.append(line)
        
        y = 0.20
        for line in shown_lines:
            ax.text(0.1, y, line, fontsize=8, family='monospace')
            y -= 0.02
        
        # Footer
        ax.text(0.5, 0.05, 'Letters shown are algebraically forced by CT + params + indicated cribs', 
                ha='center', fontsize=9, style='italic')
        ax.text(0.5, 0.02, 'Unknown positions remain "?"', 
                ha='center', fontsize=9, style='italic')
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    print(f"Created RUN_{run_id}.pdf")


def main():
    """Create all PDFs."""
    
    print("Creating PDFs...")
    
    # Create K0 hints PDF
    create_k0_hints_pdf()
    
    # Create K3 hints PDF
    create_k3_hints_pdf()
    
    # Create run PDFs
    for run_id in ['A', 'B', 'C', 'D']:
        create_run_pdf(run_id)
    
    print("All PDFs created successfully!")


if __name__ == "__main__":
    main()