#!/usr/bin/env python3
"""
Create anchor arithmetic ledger for K4.
Shows the calculation for each anchor position.
Pure Python stdlib only.
"""

import json


def load_k4_data():
    """Load K4 ciphertext and anchor data."""
    
    # K4 ciphertext
    with open('../../02_DATA/ciphertext_97.txt', 'r') as f:
        ciphertext = f.read().strip().upper()
    
    # Anchor definitions
    anchors = {
        'EAST': {'start': 21, 'end': 24, 'text': 'EAST'},
        'NORTHEAST': {'start': 25, 'end': 33, 'text': 'NORTHEAST'},
        'BERLIN': {'start': 63, 'end': 68, 'text': 'BERLIN'},
        'CLOCK': {'start': 69, 'end': 73, 'text': 'CLOCK'}
    }
    
    # Class function
    def compute_class(i):
        return ((i % 2) * 3) + (i % 3)
    
    # Families from proof
    families = ['vigenere', 'vigenere', 'beaufort', 'vigenere', 'beaufort', 'vigenere']
    
    return ciphertext, anchors, compute_class, families


def create_ledger_entries():
    """Create ledger entries for each anchor position."""
    
    ciphertext, anchors, compute_class, families = load_k4_data()
    
    entries = []
    
    for anchor_name, anchor_data in anchors.items():
        start = anchor_data['start']
        end = anchor_data['end']
        text = anchor_data['text']
        
        for offset, p_char in enumerate(text):
            idx = start + offset
            if idx > end:
                break
            
            c_char = ciphertext[idx]
            c_val = ord(c_char) - ord('A')
            p_val = ord(p_char) - ord('A')
            
            cls = compute_class(idx)
            family = families[cls]
            period = 17  # All classes use L=17
            slot = idx % period
            
            # Calculate K based on family
            if family == 'vigenere':
                k_val = (c_val - p_val) % 26
                formula = f"K = C - P = {c_val} - {p_val} = {k_val} (mod 26)"
            elif family == 'beaufort':
                k_val = (p_val + c_val) % 26
                formula = f"K = P + C = {p_val} + {c_val} = {k_val} (mod 26)"
            elif family == 'variant_beaufort':
                k_val = (p_val - c_val) % 26
                formula = f"K = P - C = {p_val} - {c_val} = {k_val} (mod 26)"
            
            entry = {
                'index': idx,
                'anchor': anchor_name,
                'class': cls,
                'family': family,
                'period': period,
                'slot': slot,
                'C_char': c_char,
                'C_val': c_val,
                'P_char': p_char,
                'P_val': p_val,
                'K_val': k_val,
                'K_char': chr(k_val + ord('A')),
                'formula': formula
            }
            
            entries.append(entry)
    
    return entries


def create_ledger_pdf():
    """Create PDF of anchor arithmetic ledger."""
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    
    entries = create_ledger_entries()
    
    with PdfPages('K4_ANCHOR_LEDGER.pdf') as pdf:
        # Create pages with ~10 entries each
        entries_per_page = 10
        n_pages = (len(entries) + entries_per_page - 1) // entries_per_page
        
        for page_num in range(n_pages):
            fig = plt.figure(figsize=(8.5, 11))
            ax = fig.add_subplot(111)
            ax.axis('off')
            
            # Title
            ax.text(0.5, 0.95, 'K4 Anchor Arithmetic Ledger', 
                    ha='center', fontsize=14, fontweight='bold')
            ax.text(0.5, 0.92, f'Page {page_num + 1} of {n_pages}', 
                    ha='center', fontsize=10)
            
            # Headers
            y = 0.87
            ax.text(0.05, y, 'Idx', fontsize=9, fontweight='bold')
            ax.text(0.10, y, 'Anchor', fontsize=9, fontweight='bold')
            ax.text(0.20, y, 'Class', fontsize=9, fontweight='bold')
            ax.text(0.26, y, 'Family', fontsize=9, fontweight='bold')
            ax.text(0.36, y, 'Slot', fontsize=9, fontweight='bold')
            ax.text(0.42, y, 'C', fontsize=9, fontweight='bold')
            ax.text(0.47, y, 'P', fontsize=9, fontweight='bold')
            ax.text(0.52, y, 'K', fontsize=9, fontweight='bold')
            ax.text(0.57, y, 'Calculation', fontsize=9, fontweight='bold')
            
            # Draw entries
            start_idx = page_num * entries_per_page
            end_idx = min(start_idx + entries_per_page, len(entries))
            
            for i, entry in enumerate(entries[start_idx:end_idx]):
                y = 0.83 - i * 0.08
                
                # Draw box
                ax.add_patch(plt.Rectangle((0.03, y - 0.03), 0.94, 0.06, 
                                          facecolor='lightgray' if i % 2 else 'white',
                                          edgecolor='black', linewidth=0.5))
                
                # Index
                ax.text(0.05, y, str(entry['index']), fontsize=8, family='monospace')
                
                # Anchor
                ax.text(0.10, y, entry['anchor'][:4], fontsize=8)
                
                # Class
                ax.text(0.22, y, str(entry['class']), fontsize=8, family='monospace')
                
                # Family
                fam_abbr = {'vigenere': 'V', 'beaufort': 'B', 'variant_beaufort': 'VB'}
                ax.text(0.28, y, fam_abbr[entry['family']], fontsize=8)
                
                # Slot
                ax.text(0.38, y, str(entry['slot']), fontsize=8, family='monospace')
                
                # C character and value
                ax.text(0.42, y, f"{entry['C_char']}={entry['C_val']:2}", 
                       fontsize=8, family='monospace')
                
                # P character and value
                ax.text(0.47, y, f"{entry['P_char']}={entry['P_val']:2}", 
                       fontsize=8, family='monospace')
                
                # K character and value
                ax.text(0.52, y, f"{entry['K_char']}={entry['K_val']:2}", 
                       fontsize=8, family='monospace', fontweight='bold')
                
                # Formula (abbreviated)
                if entry['family'] == 'vigenere':
                    calc = f"C-P={entry['C_val']}-{entry['P_val']}={entry['K_val']}"
                elif entry['family'] == 'beaufort':
                    calc = f"P+C={entry['P_val']}+{entry['C_val']}={entry['K_val']}"
                else:
                    calc = f"P-C={entry['P_val']}-{entry['C_val']}={entry['K_val']}"
                
                ax.text(0.57, y, calc, fontsize=7, family='monospace')
            
            # Footer
            ax.text(0.5, 0.05, 'All arithmetic is modulo 26. Letters: A=0, B=1, ..., Z=25', 
                   ha='center', fontsize=8, style='italic')
            ax.text(0.5, 0.02, 'Families: V=Vigenère (K=C-P), B=Beaufort (K=P+C)', 
                   ha='center', fontsize=8, style='italic')
            
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()
    
    print("Created K4_ANCHOR_LEDGER.pdf")
    
    # Also save as text
    with open('K4_ANCHOR_LEDGER.txt', 'w') as f:
        f.write("K4 ANCHOR ARITHMETIC LEDGER\n")
        f.write("=" * 70 + "\n\n")
        f.write("Index | Anchor | Class | Family | Slot | C    | P    | K    | Formula\n")
        f.write("-" * 70 + "\n")
        
        for entry in entries:
            fam = entry['family'][:4]
            f.write(f"{entry['index']:5} | {entry['anchor']:6} | {entry['class']:5} | {fam:6} | "
                   f"{entry['slot']:4} | {entry['C_char']}={entry['C_val']:2} | "
                   f"{entry['P_char']}={entry['P_val']:2} | {entry['K_char']}={entry['K_val']:2} | "
                   f"{entry['formula']}\n")
    
    print("Created K4_ANCHOR_LEDGER.txt")


if __name__ == "__main__":
    create_ledger_pdf()