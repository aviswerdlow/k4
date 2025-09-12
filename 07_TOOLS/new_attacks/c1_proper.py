#!/usr/bin/env python3
"""
C1 - K3 Connection Tests (Proper Implementation)
Test 4×7 transposition and L=7 overlays on unknowns only
"""

import json
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

MASTER_SEED = 1337

def compute_class_baseline(i):
    """Baseline class function: ((i%2)*3)+(i%3)"""
    return ((i % 2) * 3) + (i % 3)

def load_data():
    """Load all required data"""
    with open('../../02_DATA/ciphertext_97.txt', 'r') as f:
        ciphertext = f.read().strip()
    
    with open('../../01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt', 'r') as f:
        canonical_pt = f.read().strip()
    
    anchors = []
    for start, end in [(21, 24), (25, 33), (63, 68), (69, 73)]:
        for i in range(start, end + 1):
            anchors.append(i)
    
    tail = list(range(74, 97))
    all_constrained = set(anchors) | set(tail)
    baseline_unknowns = [i for i in range(97) if i not in all_constrained]
    
    return ciphertext, canonical_pt, anchors, tail, baseline_unknowns

def test_4x7_transposition(ciphertext, canonical_pt, anchors, tail, unknowns):
    """Test 4×7 transposition on unknown positions only"""
    L = 17
    
    # Build baseline L=17 wheels
    wheels = {}
    for c in range(6):
        wheels[c] = {
            'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
            'L': L,
            'residues': [None] * L
        }
    
    # Apply known constraints (anchors + tail)
    for pos in anchors + tail:
        c = compute_class_baseline(pos)
        s = pos % L
        
        c_char = ciphertext[pos]
        p_char = canonical_pt[pos]
        
        c_val = ord(c_char) - ord('A')
        p_val = ord(p_char) - ord('A')
        
        if wheels[c]['family'] == 'vigenere':
            k_val = (c_val - p_val) % 26
        else:
            k_val = (p_val + c_val) % 26
        
        wheels[c]['residues'][s] = k_val
    
    # Apply 4×7 transposition to unknowns
    # Map unknowns to grid positions and read out differently
    unknown_ct = [ciphertext[i] for i in unknowns]
    
    # Try different read paths
    results = {}
    
    # Path 1: Row-major to column-major
    if len(unknown_ct) <= 28:
        grid_4x7 = []
        for r in range(4):
            row = []
            for c in range(7):
                idx = r * 7 + c
                if idx < len(unknown_ct):
                    row.append(unknown_ct[idx])
                else:
                    row.append('?')
            grid_4x7.append(row)
        
        # Read column-major
        transposed = []
        for c in range(7):
            for r in range(4):
                if grid_4x7[r][c] != '?':
                    transposed.append(grid_4x7[r][c])
        
        # Create modified ciphertext
        mod_ct = list(ciphertext)
        for i, new_char in enumerate(transposed):
            if i < len(unknowns):
                mod_ct[unknowns[i]] = new_char
        mod_ct = ''.join(mod_ct)
        
        # Decrypt with L=17 wheels
        derived = []
        unknown_count = 0
        for i in range(97):
            c = compute_class_baseline(i)
            s = i % L
            
            if wheels[c]['residues'][s] is not None:
                c_char = mod_ct[i]
                c_val = ord(c_char) - ord('A')
                k_val = wheels[c]['residues'][s]
                
                if wheels[c]['family'] == 'vigenere':
                    p_val = (c_val - k_val) % 26
                else:
                    p_val = (k_val - c_val) % 26
                
                derived.append(chr(p_val + ord('A')))
            else:
                derived.append('?')
                unknown_count += 1
        
        results['col_major'] = {
            'plaintext': ''.join(derived),
            'unknown_count': unknown_count,
            'path': 'row→col'
        }
    
    return results

def test_l7_overlay(ciphertext, canonical_pt, anchors, tail, unknowns):
    """Test L=7 overlay on unknown positions only"""
    # Keep L=17 for known positions, use L=7 mapping for unknowns
    L_base = 17
    L_unknown = 7
    
    # Build baseline wheels
    wheels = {}
    for c in range(6):
        wheels[c] = {
            'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
            'L': L_base,
            'residues': [None] * L_base
        }
    
    # Apply known constraints
    for pos in anchors + tail:
        c = compute_class_baseline(pos)
        s = pos % L_base
        
        c_char = ciphertext[pos]
        p_char = canonical_pt[pos]
        
        c_val = ord(c_char) - ord('A')
        p_val = ord(p_char) - ord('A')
        
        if wheels[c]['family'] == 'vigenere':
            k_val = (c_val - p_val) % 26
        else:
            k_val = (p_val + c_val) % 26
        
        wheels[c]['residues'][s] = k_val
    
    # For unknowns, try to use mod-7 indexing
    # Build auxiliary L=7 wheels
    wheels_7 = {}
    for c in range(6):
        wheels_7[c] = {
            'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
            'L': L_unknown,
            'residues': [None] * L_unknown
        }
    
    # Try to infer L=7 patterns from anchors
    for pos in anchors:
        c = compute_class_baseline(pos)
        s7 = pos % L_unknown
        
        c_char = ciphertext[pos]
        p_char = canonical_pt[pos]
        
        c_val = ord(c_char) - ord('A')
        p_val = ord(p_char) - ord('A')
        
        if wheels_7[c]['family'] == 'vigenere':
            k_val = (c_val - p_val) % 26
        else:
            k_val = (p_val + c_val) % 26
        
        if wheels_7[c]['residues'][s7] is None:
            wheels_7[c]['residues'][s7] = k_val
    
    # Derive plaintext using hybrid approach
    derived = []
    unknown_count = 0
    
    for i in range(97):
        c = compute_class_baseline(i)
        
        if i in unknowns:
            # Use L=7 for unknowns
            s = i % L_unknown
            if wheels_7[c]['residues'][s] is not None:
                c_char = ciphertext[i]
                c_val = ord(c_char) - ord('A')
                k_val = wheels_7[c]['residues'][s]
                
                if wheels_7[c]['family'] == 'vigenere':
                    p_val = (c_val - k_val) % 26
                else:
                    p_val = (k_val - c_val) % 26
                
                derived.append(chr(p_val + ord('A')))
            else:
                derived.append('?')
                unknown_count += 1
        else:
            # Use L=17 for known
            s = i % L_base
            if wheels[c]['residues'][s] is not None:
                c_char = ciphertext[i]
                c_val = ord(c_char) - ord('A')
                k_val = wheels[c]['residues'][s]
                
                if wheels[c]['family'] == 'vigenere':
                    p_val = (c_val - k_val) % 26
                else:
                    p_val = (k_val - c_val) % 26
                
                derived.append(chr(p_val + ord('A')))
            else:
                derived.append('?')
                unknown_count += 1
    
    return ''.join(derived), unknown_count

def verify_constraints(plaintext, canonical_pt, anchors, tail):
    """Verify anchors and tail are preserved"""
    violations = 0
    
    # Check anchors
    for i in anchors:
        if plaintext[i] != canonical_pt[i]:
            violations += 1
    
    # Check tail
    for i in tail:
        if plaintext[i] != canonical_pt[i]:
            violations += 1
    
    return violations == 0

def create_results_pdf(results, output_dir):
    """Create one-page PDF with results"""
    fig = plt.figure(figsize=(8.5, 11))
    
    fig.text(0.5, 0.95, 'C1: K3 Connection (4×7) Tests', 
             fontsize=16, weight='bold', ha='center')
    
    # Test results summary
    ax = plt.subplot(111)
    ax.axis('off')
    
    summary_text = f"""
Test Results:
-------------
1. Baseline (L=17 with anchors+tail):
   Unknown positions: {results['baseline_unknowns']}

2. 4×7 Transposition Tests:
   {results.get('4x7_summary', 'Not tested')}

3. L=7 Overlay Test:
   Unknown positions: {results.get('l7_unknowns', 'Not tested')}
   Reduction: {results.get('l7_reduction', 0)}
   Constraints preserved: {results.get('l7_valid', 'No')}

4. Hybrid 4×7 + L=7:
   {results.get('hybrid_summary', 'Not tested')}

Conclusion:
-----------
{results.get('conclusion', 'Analysis pending')}
"""
    
    ax.text(0.1, 0.5, summary_text, fontsize=11, va='center', family='monospace')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/C1_results.pdf', format='pdf')
    plt.close()

def main():
    """Run C1 tests"""
    print("=== C1: K3 Connection Tests ===\n")
    
    # Load data
    ciphertext, canonical_pt, anchors, tail, unknowns = load_data()
    
    print(f"Baseline: {len(unknowns)} unknown positions")
    
    # Create output directory
    os.makedirs('C1_4x7_28', exist_ok=True)
    os.makedirs('C1_L7', exist_ok=True)
    os.makedirs('C1_hybrid', exist_ok=True)
    
    results = {
        'baseline_unknowns': len(unknowns)
    }
    
    # Test 1: 4×7 transposition
    print("\nTest 1: 4×7 Transposition on unknowns...")
    trans_results = test_4x7_transposition(ciphertext, canonical_pt, anchors, tail, unknowns)
    
    if trans_results:
        best_trans = min(trans_results.values(), key=lambda x: x['unknown_count'])
        results['4x7_summary'] = f"Best: {best_trans['unknown_count']} unknowns ({best_trans['path']})"
        print(f"  Best result: {best_trans['unknown_count']} unknowns")
    
    # Test 2: L=7 overlay
    print("\nTest 2: L=7 overlay on unknowns...")
    pt_l7, unknown_l7 = test_l7_overlay(ciphertext, canonical_pt, anchors, tail, unknowns)
    valid_l7 = verify_constraints(pt_l7, canonical_pt, anchors, tail)
    
    results['l7_unknowns'] = unknown_l7
    results['l7_reduction'] = len(unknowns) - unknown_l7
    results['l7_valid'] = 'Yes' if valid_l7 else 'No'
    
    print(f"  Unknowns: {unknown_l7}")
    print(f"  Reduction: {results['l7_reduction']}")
    print(f"  Valid: {results['l7_valid']}")
    
    # Save L=7 results
    with open('C1_L7/RESULT.json', 'w') as f:
        json.dump({
            'unknowns_before': len(unknowns),
            'unknowns_after': unknown_l7,
            'positions_changed': [],
            'constraints_valid': valid_l7
        }, f, indent=2)
    
    with open('C1_L7/PT_PARTIAL.txt', 'w') as f:
        f.write(pt_l7)
    
    # Determine conclusion
    if results['l7_reduction'] > 0 and results['l7_valid'] == 'Yes':
        results['conclusion'] = f"SUCCESS: L=7 overlay reduced unknowns by {results['l7_reduction']}"
    else:
        results['conclusion'] = "No valid reduction achieved"
    
    # Create PDF
    create_results_pdf(results, 'C1_L7')
    
    print(f"\n{results['conclusion']}")
    print("\nResults saved to C1_*/")

if __name__ == "__main__":
    main()