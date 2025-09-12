#!/usr/bin/env python3
"""
Phase 3: Compare L=14,15,16,17 for context.
Pure algebra comparison.
"""

import json
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def compute_class_baseline(i):
    """Baseline class function: ((i%2)*3)+(i%3)"""
    return ((i % 2) * 3) + (i % 3)

def load_ciphertext():
    """Load the 97-character ciphertext"""
    with open('../../02_DATA/ciphertext_97.txt', 'r') as f:
        return f.read().strip()

def load_anchors():
    """Load anchor positions and plaintext"""
    return {
        'EAST': (21, 24),
        'NORTHEAST': (25, 33),
        'BERLIN': (63, 68),
        'CLOCK': (69, 73)
    }

def get_tail_plaintext():
    """Get tail plaintext from published solution"""
    with open('../../01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt', 'r') as f:
        full_pt = f.read().strip()
    return full_pt[74:97]

def test_L_value(L, ciphertext, anchors, tail_plaintext, phase=0):
    """
    Test a specific L value with anchors and tail.
    Returns statistics.
    """
    # Initialize wheels
    wheels = {}
    for c in range(6):
        wheels[c] = {
            'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
            'L': L,
            'phase': phase,
            'residues': [None] * L
        }
    
    # Process anchors
    anchor_forced = 0
    conflicts = 0
    
    for crib_text, (start, end) in anchors.items():
        for i, p_char in enumerate(crib_text):
            pos = start + i
            if pos > end:
                break
                
            c = compute_class_baseline(pos)
            s = (pos + phase) % L
            
            c_char = ciphertext[pos]
            c_val = ord(c_char) - ord('A')
            p_val = ord(p_char) - ord('A')
            
            # Compute residue
            if wheels[c]['family'] == 'vigenere':
                k_val = (c_val - p_val) % 26
            else:  # beaufort
                k_val = (p_val + c_val) % 26
            
            # Check for conflicts
            if wheels[c]['residues'][s] is not None:
                if wheels[c]['residues'][s] != k_val:
                    conflicts += 1
            else:
                wheels[c]['residues'][s] = k_val
                anchor_forced += 1
    
    # Count derived from anchors only
    derived_anchors = 0
    for i in range(97):
        c = compute_class_baseline(i)
        s = (i + phase) % L
        if wheels[c]['residues'][s] is not None:
            derived_anchors += 1
    
    # Add tail
    tail_forced = 0
    for i, p_char in enumerate(tail_plaintext):
        pos = 74 + i
        c = compute_class_baseline(pos)
        s = (pos + phase) % L
        
        if wheels[c]['residues'][s] is None:
            c_char = ciphertext[pos]
            c_val = ord(c_char) - ord('A')
            p_val = ord(p_char) - ord('A')
            
            if wheels[c]['family'] == 'vigenere':
                k_val = (c_val - p_val) % 26
            else:
                k_val = (p_val + c_val) % 26
            
            wheels[c]['residues'][s] = k_val
            tail_forced += 1
    
    # Count total derived
    derived_total = 0
    for i in range(97):
        c = compute_class_baseline(i)
        s = (i + phase) % L
        if wheels[c]['residues'][s] is not None:
            derived_total += 1
    
    return {
        'L': L,
        'anchor_forced_slots': anchor_forced,
        'conflicts': conflicts,
        'derived_anchors_only': derived_anchors,
        'unknown_anchors_only': 97 - derived_anchors,
        'tail_forced_slots': tail_forced,
        'derived_with_tail': derived_total,
        'unknown_with_tail': 97 - derived_total
    }

def create_comparison_chart(results):
    """Create comparison chart for different L values"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    L_values = [r['L'] for r in results]
    unknowns_anchors = [r['unknown_anchors_only'] for r in results]
    unknowns_tail = [r['unknown_with_tail'] for r in results]
    
    # Chart 1: Unknown positions
    x = range(len(L_values))
    width = 0.35
    
    bars1 = ax1.bar([i - width/2 for i in x], unknowns_anchors, width, 
                    label='Anchors only', color='lightcoral')
    bars2 = ax1.bar([i + width/2 for i in x], unknowns_tail, width,
                    label='Anchors + Tail', color='lightgreen')
    
    ax1.set_xlabel('Period (L)', fontsize=12)
    ax1.set_ylabel('Unknown Positions', fontsize=12)
    ax1.set_title('Unknown Positions by Period', fontsize=14, weight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(L_values)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{int(height)}', ha='center', va='bottom', fontsize=10)
    
    for bar in bars2:
        height = bar.get_height()
        if height > 0:
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{int(height)}', ha='center', va='bottom', fontsize=10)
    
    # Chart 2: Sufficiency indicator
    sufficiency = ['Complete' if r['unknown_with_tail'] == 0 else 'Incomplete' 
                  for r in results]
    colors = ['green' if s == 'Complete' else 'red' for s in sufficiency]
    
    ax2.bar(x, [1 if s == 'Complete' else 0.3 for s in sufficiency], color=colors)
    ax2.set_xlabel('Period (L)', fontsize=12)
    ax2.set_ylabel('Solution Status', fontsize=12)
    ax2.set_title('Completeness with Anchors + Tail', fontsize=14, weight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(L_values)
    ax2.set_ylim(0, 1.2)
    ax2.set_yticks([0, 0.3, 1])
    ax2.set_yticklabels(['', 'Incomplete', 'Complete'])
    
    # Add status text
    for i, (l, s) in enumerate(zip(L_values, sufficiency)):
        color = 'green' if s == 'Complete' else 'red'
        y_pos = 1.05 if s == 'Complete' else 0.35
        ax2.text(i, y_pos, s, ha='center', fontsize=10, weight='bold', color=color)
    
    plt.suptitle('Period Comparison: Algebraic Coverage', fontsize=16, weight='bold')
    plt.tight_layout()
    plt.savefig('L_COMPARE.pdf', format='pdf', bbox_inches='tight')
    plt.close()
    print("Created L_COMPARE.pdf")

def main():
    """Run period comparison"""
    print("\n" + "="*60)
    print("PHASE 3: Period Comparison (L=14,15,16,17)")
    print("="*60)
    
    ciphertext = load_ciphertext()
    anchors = load_anchors()
    tail_plaintext = get_tail_plaintext()
    
    results = []
    
    for L in [14, 15, 16, 17]:
        print(f"\nTesting L={L}...")
        stats = test_L_value(L, ciphertext, anchors, tail_plaintext)
        results.append(stats)
        
        # Create directory and save summary
        os.makedirs(f'L{L}', exist_ok=True)
        with open(f'L{L}/L{L}_SUMMARY.json', 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"  Anchors only: {stats['derived_anchors_only']} derived, {stats['unknown_anchors_only']} unknown")
        print(f"  With tail: {stats['derived_with_tail']} derived, {stats['unknown_with_tail']} unknown")
        
        if stats['unknown_with_tail'] == 0:
            print(f"  ✓ Complete solution possible")
        else:
            print(f"  ✗ {stats['unknown_with_tail']} positions remain unknown")
    
    # Create comparison chart
    create_comparison_chart(results)
    
    print("\n" + "="*60)
    print("COMPARISON SUMMARY")
    print("="*60)
    
    print("\n| L  | Anchors Only | With Tail | Status    |")
    print("|----|--------------|-----------|-----------|")
    for r in results:
        status = "Complete" if r['unknown_with_tail'] == 0 else "Incomplete"
        print(f"| {r['L']:2d} | {r['unknown_anchors_only']:3d} unknown | {r['unknown_with_tail']:3d} unknown | {status:9s} |")
    
    # Find which L values work
    complete = [r['L'] for r in results if r['unknown_with_tail'] == 0]
    if complete:
        print(f"\n✓ L values that achieve complete solution: {complete}")
    else:
        print("\n✗ No L value achieves complete solution")

if __name__ == "__main__":
    main()