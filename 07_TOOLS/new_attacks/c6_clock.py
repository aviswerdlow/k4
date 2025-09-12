#!/usr/bin/env python3
"""
C6 - CLOCK Arithmetic Tests
Test mod-12/mod-60 structures focused around CLOCK anchor (69-73)
"""

import json
import os
import matplotlib.pyplot as plt
import numpy as np

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

def build_baseline_wheels(ciphertext, canonical_pt, anchors, tail):
    """Build L=17 baseline wheels"""
    L = 17
    wheels = {}
    
    for c in range(6):
        wheels[c] = {
            'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
            'L': L,
            'residues': [None] * L
        }
    
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
    
    return wheels

def test_clock_mod_driver(ciphertext, canonical_pt, anchors, tail, unknowns, modulus):
    """Test mod-12/60 driver for unknown positions"""
    L = 17
    wheels = build_baseline_wheels(ciphertext, canonical_pt, anchors, tail)
    
    # Apply clock-based modulation to unknowns
    for idx in unknowns:
        # Clock state based on position relative to tail start (74)
        clock_state = (idx - 74) % modulus
        
        # Use clock state to modify residue
        c = compute_class_baseline(idx)
        s = idx % L
        
        # Try to fill unknown slots with clock-driven values
        if wheels[c]['residues'][s] is None:
            # Generate pseudo-key based on clock state
            wheels[c]['residues'][s] = clock_state % 26
    
    # Derive plaintext
    derived = []
    unknown_count = 0
    
    for i in range(97):
        c = compute_class_baseline(i)
        s = i % L
        
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

def test_clock_face_transposition(ciphertext, canonical_pt, anchors, tail, unknowns):
    """Test clock-face transposition on unknown indices"""
    L = 17
    wheels = build_baseline_wheels(ciphertext, canonical_pt, anchors, tail)
    
    # Map unknowns to clock positions (12-point)
    if len(unknowns) >= 12:
        # Take first 12 unknowns and apply clock permutation
        clock_positions = unknowns[:12]
        
        # Clock permutation (e.g., opposite pairs)
        permutation = [6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5]
        
        # Apply transposition to ciphertext
        mod_ct = list(ciphertext)
        clock_chars = [ciphertext[clock_positions[i]] for i in range(12)]
        
        for i in range(12):
            mod_ct[clock_positions[i]] = clock_chars[permutation[i]]
        
        mod_ct = ''.join(mod_ct)
    else:
        mod_ct = ciphertext
    
    # Derive with modified ciphertext
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
    
    return ''.join(derived), unknown_count

def test_anchor_gated_switching(ciphertext, canonical_pt, anchors, tail, unknowns):
    """Test different mechanism for positions >= 74"""
    L = 17
    wheels = build_baseline_wheels(ciphertext, canonical_pt, anchors, tail)
    
    # For head unknowns < 74, apply clock-based modulation
    for idx in unknowns:
        if idx < 74:
            c = compute_class_baseline(idx)
            s = idx % L
            
            if wheels[c]['residues'][s] is None:
                # Distance from CLOCK anchor
                distance_to_clock = abs(idx - 71)  # Center of CLOCK
                wheels[c]['residues'][s] = (distance_to_clock % 12) % 26
    
    # Derive plaintext
    derived = []
    unknown_count = 0
    
    for i in range(97):
        c = compute_class_baseline(i)
        s = i % L
        
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
    for i in anchors + tail:
        if plaintext[i] != canonical_pt[i]:
            return False
    return True

def explain_single_index(idx, clock_state, modulus):
    """Explain derivation for a single index"""
    explanation = f"""
Index {idx} Explanation (Clock mod-{modulus}):
----------------------------------------
Position: {idx}
Clock state: (idx - 74) % {modulus} = ({idx} - 74) % {modulus} = {clock_state}
Class: ((idx%2)*3)+(idx%3) = (({idx}%2)*3)+({idx}%3) = {compute_class_baseline(idx)}
Slot (L=17): idx % 17 = {idx} % 17 = {idx % 17}

Clock-driven key: clock_state % 26 = {clock_state} % 26 = {clock_state % 26}

This fills the previously unknown slot with a clock-derived value.
"""
    return explanation

def create_results_pdf(results, output_dir):
    """Create results PDF"""
    fig = plt.figure(figsize=(8.5, 11))
    
    fig.text(0.5, 0.95, 'C6: CLOCK Arithmetic Tests', 
             fontsize=16, weight='bold', ha='center')
    
    # Clock visualization
    ax1 = plt.subplot(2, 2, 1)
    ax1.set_title('Clock Face', fontsize=10)
    ax1.set_aspect('equal')
    
    # Draw clock
    theta = np.linspace(0, 2*np.pi, 13)
    x = np.cos(theta - np.pi/2)
    y = np.sin(theta - np.pi/2)
    
    ax1.plot(x, y, 'ko-', markersize=6)
    for i in range(12):
        hour = (i + 11) % 12 + 1
        ax1.text(x[i]*1.2, y[i]*1.2, str(hour), ha='center', va='center')
    
    ax1.set_xlim(-1.5, 1.5)
    ax1.set_ylim(-1.5, 1.5)
    ax1.axis('off')
    
    # Results summary
    ax2 = plt.subplot(2, 1, 2)
    ax2.axis('off')
    
    summary_text = f"""
Test Results:
-------------
Baseline unknowns: {results['baseline']}

1. Mod-12 driver:
   Unknowns: {results.get('mod12_unknowns', 'N/A')}
   Reduction: {results.get('mod12_reduction', 0)}
   Valid: {results.get('mod12_valid', 'No')}

2. Mod-60 driver:
   Unknowns: {results.get('mod60_unknowns', 'N/A')}
   Reduction: {results.get('mod60_reduction', 0)}
   Valid: {results.get('mod60_valid', 'No')}

3. Clock-face transposition:
   Unknowns: {results.get('trans_unknowns', 'N/A')}
   Reduction: {results.get('trans_reduction', 0)}
   Valid: {results.get('trans_valid', 'No')}

4. Anchor-gated switching:
   Unknowns: {results.get('gated_unknowns', 'N/A')}
   Reduction: {results.get('gated_reduction', 0)}
   Valid: {results.get('gated_valid', 'No')}

Conclusion: {results.get('conclusion', 'Pending')}
"""
    
    ax2.text(0.1, 0.5, summary_text, fontsize=10, va='center', family='monospace')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/C6_results.pdf', format='pdf')
    plt.close()

def main():
    """Run C6 clock tests"""
    print("=== C6: CLOCK Arithmetic Tests ===\n")
    
    # Load data
    ciphertext, canonical_pt, anchors, tail, unknowns = load_data()
    
    print(f"Baseline: {len(unknowns)} unknown positions")
    
    # Create output directory
    os.makedirs('C6_clock', exist_ok=True)
    
    results = {'baseline': len(unknowns)}
    
    # Test 1: Mod-12 driver
    print("\nTest 1: Mod-12 driver...")
    pt_12, unk_12 = test_clock_mod_driver(ciphertext, canonical_pt, anchors, tail, unknowns, 12)
    valid_12 = verify_constraints(pt_12, canonical_pt, anchors, tail)
    
    results['mod12_unknowns'] = unk_12
    results['mod12_reduction'] = len(unknowns) - unk_12
    results['mod12_valid'] = 'Yes' if valid_12 else 'No'
    
    print(f"  Unknowns: {unk_12}, Valid: {results['mod12_valid']}")
    
    # Test 2: Mod-60 driver
    print("\nTest 2: Mod-60 driver...")
    pt_60, unk_60 = test_clock_mod_driver(ciphertext, canonical_pt, anchors, tail, unknowns, 60)
    valid_60 = verify_constraints(pt_60, canonical_pt, anchors, tail)
    
    results['mod60_unknowns'] = unk_60
    results['mod60_reduction'] = len(unknowns) - unk_60
    results['mod60_valid'] = 'Yes' if valid_60 else 'No'
    
    print(f"  Unknowns: {unk_60}, Valid: {results['mod60_valid']}")
    
    # Test 3: Clock-face transposition
    print("\nTest 3: Clock-face transposition...")
    pt_trans, unk_trans = test_clock_face_transposition(ciphertext, canonical_pt, anchors, tail, unknowns)
    valid_trans = verify_constraints(pt_trans, canonical_pt, anchors, tail)
    
    results['trans_unknowns'] = unk_trans
    results['trans_reduction'] = len(unknowns) - unk_trans
    results['trans_valid'] = 'Yes' if valid_trans else 'No'
    
    print(f"  Unknowns: {unk_trans}, Valid: {results['trans_valid']}")
    
    # Test 4: Anchor-gated switching
    print("\nTest 4: Anchor-gated switching...")
    pt_gated, unk_gated = test_anchor_gated_switching(ciphertext, canonical_pt, anchors, tail, unknowns)
    valid_gated = verify_constraints(pt_gated, canonical_pt, anchors, tail)
    
    results['gated_unknowns'] = unk_gated
    results['gated_reduction'] = len(unknowns) - unk_gated
    results['gated_valid'] = 'Yes' if valid_gated else 'No'
    
    print(f"  Unknowns: {unk_gated}, Valid: {results['gated_valid']}")
    
    # Determine best result
    best_reduction = 0
    best_test = None
    
    for test in ['mod12', 'mod60', 'trans', 'gated']:
        if results.get(f'{test}_valid') == 'Yes' and results.get(f'{test}_reduction', 0) > best_reduction:
            best_reduction = results[f'{test}_reduction']
            best_test = test
    
    if best_test:
        results['conclusion'] = f"SUCCESS: {best_test} reduced unknowns by {best_reduction}"
        
        # Save explanation for one index
        with open('C6_clock/EXPLAIN_IDX.txt', 'w') as f:
            if best_test == 'mod12':
                f.write(explain_single_index(unknowns[0], (unknowns[0] - 74) % 12, 12))
    else:
        results['conclusion'] = "No clock mechanism reduced unknowns"
    
    # Save results
    with open('C6_clock/RESULT.json', 'w') as f:
        json.dump({
            'unknowns_before': len(unknowns),
            'unknowns_after': min(unk_12, unk_60, unk_trans, unk_gated),
            'best_method': best_test,
            'reduction': best_reduction
        }, f, indent=2)
    
    # Save best plaintext
    if best_test == 'mod12':
        best_pt = pt_12
    elif best_test == 'mod60':
        best_pt = pt_60
    elif best_test == 'trans':
        best_pt = pt_trans
    else:
        best_pt = pt_gated if best_test == 'gated' else pt_12
    
    with open('C6_clock/PT_PARTIAL.txt', 'w') as f:
        f.write(best_pt)
    
    # Create PDF
    create_results_pdf(results, 'C6_clock')
    
    print(f"\n{results['conclusion']}")
    print("\nResults saved to C6_clock/")

if __name__ == "__main__":
    main()