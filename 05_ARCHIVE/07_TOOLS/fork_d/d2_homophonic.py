#!/usr/bin/env python3
"""
D2 - Homophonic Augmentation
Monotone mapping on the baseline effective key stream
"""

import json
import os
import hashlib
from typing import Dict, List, Optional

MASTER_SEED = 1337

# Affine mapping multipliers (must be coprime to 26)
AFFINE_A = [1, 5, 7, 11, 13, 17, 19, 23, 25]

def compute_class_baseline(i):
    """Baseline class function"""
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
    known_positions = set(anchors) | set(tail)
    unknown_positions = [i for i in range(97) if i not in known_positions]
    
    return ciphertext, canonical_pt, anchors, tail, known_positions, unknown_positions

def build_baseline_l17(ciphertext, canonical_pt, known_positions):
    """Build baseline L=17 wheels"""
    L = 17
    wheels = {}
    
    for c in range(6):
        wheels[c] = {
            'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
            'L': L,
            'residues': [None] * L
        }
    
    # Fill from known positions
    for pos in known_positions:
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
        
        if wheels[c]['residues'][s] is None:
            wheels[c]['residues'][s] = k_val
    
    return wheels

def compute_baseline_keys(wheels, positions):
    """Compute baseline L17 keys at given positions"""
    L = 17
    k_baseline = {}
    
    for pos in positions:
        c = compute_class_baseline(pos)
        s = pos % L
        
        if wheels[c]['residues'][s] is not None:
            k_baseline[pos] = wheels[c]['residues'][s]
        else:
            k_baseline[pos] = None
    
    return k_baseline

def compute_effective_keys(ciphertext, canonical_pt, wheels, positions):
    """Compute empirically needed effective keys at positions"""
    k_eff = {}
    
    for pos in positions:
        c = compute_class_baseline(pos)
        
        c_char = ciphertext[pos]
        p_char = canonical_pt[pos]
        
        c_val = ord(c_char) - ord('A')
        p_val = ord(p_char) - ord('A')
        
        if wheels[c]['family'] == 'vigenere':
            k_eff[pos] = (c_val - p_val) % 26
        else:
            k_eff[pos] = (p_val + c_val) % 26
    
    return k_eff

def fit_affine_mapping(k_baseline, k_eff, positions):
    """Find affine mapping h(k) = (a*k + b) mod 26 that fits known positions"""
    best_mapping = None
    best_matches = 0
    
    for a in AFFINE_A:
        for b in range(26):
            matches = 0
            valid = True
            
            for pos in positions:
                if k_baseline[pos] is not None:
                    # Apply affine mapping
                    h_k = (a * k_baseline[pos] + b) % 26
                    
                    # Check if it matches effective key
                    if h_k == k_eff[pos]:
                        matches += 1
                    else:
                        valid = False
                        break
            
            if valid and matches > best_matches:
                best_matches = matches
                best_mapping = {
                    'type': 'affine',
                    'a': a,
                    'b': b,
                    'matches': matches,
                    'total': len([p for p in positions if k_baseline[p] is not None])
                }
    
    return best_mapping

def apply_homophonic(ciphertext, canonical_pt, mapping, wheels, known_positions, unknown_positions):
    """Apply homophonic mapping to derive plaintext"""
    L = 17
    derived = []
    newly_determined = []
    
    for i in range(97):
        if i in known_positions:
            # Use known plaintext
            derived.append(canonical_pt[i])
        else:
            c = compute_class_baseline(i)
            s = i % L
            
            if wheels[c]['residues'][s] is not None:
                # Apply homophonic mapping
                k_base = wheels[c]['residues'][s]
                
                if mapping['type'] == 'affine':
                    k_eff = (mapping['a'] * k_base + mapping['b']) % 26
                else:
                    k_eff = k_base  # Identity fallback
                
                # Decrypt
                c_char = ciphertext[i]
                c_val = ord(c_char) - ord('A')
                
                if wheels[c]['family'] == 'vigenere':
                    p_val = (c_val - k_eff) % 26
                else:
                    p_val = (k_eff - c_val) % 26
                
                derived.append(chr(p_val + ord('A')))
                
                # This is newly determined if it wasn't in baseline
                if i in unknown_positions:
                    newly_determined.append(i)
            else:
                derived.append('?')
    
    return ''.join(derived), newly_determined

def explain_index(idx, mapping, k_base, k_eff, c_val, p_val):
    """Explain derivation for a single index"""
    return f"""
Index {idx} Explanation (Homophonic Layer):
==========================================
Position: {idx}

Step 1: Baseline key
  K_L17[{idx}] = {k_base}

Step 2: Homophonic mapping
  Type: {mapping['type']}
  h(k) = ({mapping['a']} * k + {mapping['b']}) mod 26
  K_eff = h({k_base}) = ({mapping['a']} * {k_base} + {mapping['b']}) mod 26 = {k_eff}

Step 3: Decrypt
  C = {c_val} ('{chr(c_val + ord('A'))}')
  P = (C - K_eff) mod 26 = ({c_val} - {k_eff}) mod 26 = {p_val}
  P = '{chr(p_val + ord('A'))}'
"""

def verify_constraints(plaintext, canonical_pt, anchors, tail):
    """Verify anchors and tail are preserved"""
    for i in anchors + tail:
        if plaintext[i] != canonical_pt[i]:
            return False
    return True

def main():
    """Run D2 homophonic tests"""
    print("=== D2: Homophonic Augmentation ===\n")
    
    os.makedirs('D2_homophonic', exist_ok=True)
    
    # Load data
    ciphertext, canonical_pt, anchors, tail, known_positions, unknown_positions = load_data()
    
    print(f"Known positions: {len(known_positions)}")
    print(f"Unknown positions: {len(unknown_positions)}")
    
    # Build baseline
    wheels = build_baseline_l17(ciphertext, canonical_pt, known_positions)
    
    # Get baseline plaintext
    baseline_pt = []
    baseline_unknowns = 0
    for i in range(97):
        if i in known_positions:
            baseline_pt.append(canonical_pt[i])
        else:
            c = compute_class_baseline(i)
            s = i % 17
            if wheels[c]['residues'][s] is not None:
                c_val = ord(ciphertext[i]) - ord('A')
                k_val = wheels[c]['residues'][s]
                if wheels[c]['family'] == 'vigenere':
                    p_val = (c_val - k_val) % 26
                else:
                    p_val = (k_val - c_val) % 26
                baseline_pt.append(chr(p_val + ord('A')))
            else:
                baseline_pt.append('?')
                baseline_unknowns += 1
    
    baseline_pt_str = ''.join(baseline_pt)
    
    print(f"Baseline unknowns: {baseline_unknowns}")
    
    with open('D2_homophonic/PT_PARTIAL_BEFORE.txt', 'w') as f:
        f.write(baseline_pt_str)
    
    # Compute keys
    k_baseline = compute_baseline_keys(wheels, known_positions)
    k_eff = compute_effective_keys(ciphertext, canonical_pt, wheels, known_positions)
    
    # Fit affine mapping
    print("\nFitting affine mapping...")
    best_mapping = fit_affine_mapping(k_baseline, k_eff, known_positions)
    
    if best_mapping and best_mapping['matches'] == best_mapping['total']:
        print(f"Found perfect affine mapping: a={best_mapping['a']}, b={best_mapping['b']}")
        print(f"Matches: {best_mapping['matches']}/{best_mapping['total']}")
        
        # Apply mapping
        derived_pt, newly_determined = apply_homophonic(
            ciphertext, canonical_pt, best_mapping,
            wheels, known_positions, unknown_positions
        )
        
        unknowns_after = derived_pt.count('?')
        valid = verify_constraints(derived_pt, canonical_pt, anchors, tail)
        
        print(f"\nUnknowns after homophonic: {unknowns_after}")
        print(f"Reduction: {baseline_unknowns - unknowns_after}")
        print(f"Constraints preserved: {valid}")
        
        # Save results
        config_dir = f"D2_homophonic/affine_a_{best_mapping['a']}_b_{best_mapping['b']}"
        os.makedirs(config_dir, exist_ok=True)
        
        with open(f'{config_dir}/PT_PARTIAL_AFTER.txt', 'w') as f:
            f.write(derived_pt)
        
        result = {
            'unknowns_before': baseline_unknowns,
            'unknowns_after': unknowns_after,
            'changed_positions': newly_determined,
            'mechanism_params': best_mapping,
            'checksum': hashlib.sha256(derived_pt.encode()).hexdigest(),
            'constraints_valid': valid
        }
        
        with open(f'{config_dir}/RESULT.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        if newly_determined and unknowns_after < baseline_unknowns:
            print(f"\nSUCCESS: Reduced unknowns from {baseline_unknowns} to {unknowns_after}")
        else:
            print("\nNo reduction achieved")
    else:
        print("No perfect affine mapping found")
        if best_mapping:
            print(f"Best partial: a={best_mapping['a']}, b={best_mapping['b']} ({best_mapping['matches']}/{best_mapping['total']} matches)")
    
    print("\nResults saved to D2_homophonic/")

if __name__ == "__main__":
    main()