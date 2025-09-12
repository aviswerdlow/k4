#!/usr/bin/env python3
"""
D1 - Rotor-like stepping layer
Fit a low-complexity rotor to known per-position shifts, then extrapolate
"""

import json
import os
import hashlib
from typing import Dict, List, Tuple, Optional

MASTER_SEED = 1337

# Predefined rotor permutations (small library)
ROTOR_PERMS = {
    'identity': list(range(26)),
    'caesar': [(i + 1) % 26 for i in range(26)],
    'vigenere': [(i + 3) % 26 for i in range(26)],
    'disorder1': [17, 4, 11, 0, 19, 8, 13, 22, 5, 14, 1, 20, 9, 24, 3, 18, 7, 12, 21, 6, 15, 2, 23, 10, 25, 16],
    'disorder2': [7, 14, 3, 21, 8, 25, 12, 1, 19, 6, 23, 10, 4, 17, 24, 11, 0, 18, 5, 22, 9, 16, 13, 2, 20, 15],
    'mirror1': list(range(13)) + list(range(25, 12, -1)),
    'mirror2': list(range(25, 12, -1)) + list(range(13)),
    'split13': list(range(13, 26)) + list(range(13))
}

def compute_class_baseline(i):
    """Baseline class function"""
    return ((i % 2) * 3) + (i % 3)

def load_data():
    """Load all required data"""
    with open('../../02_DATA/ciphertext_97.txt', 'r') as f:
        ciphertext = f.read().strip()
    
    with open('../../01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt', 'r') as f:
        canonical_pt = f.read().strip()
    
    # Define constraints
    anchors = []
    for start, end in [(21, 24), (25, 33), (63, 68), (69, 73)]:
        for i in range(start, end + 1):
            anchors.append(i)
    
    tail = list(range(74, 97))
    
    # All known positions
    known_positions = set(anchors) | set(tail)
    
    # Unknown positions (everything else)
    unknown_positions = [i for i in range(97) if i not in known_positions]
    
    return ciphertext, canonical_pt, anchors, tail, known_positions, unknown_positions

def build_baseline_l17(ciphertext, canonical_pt, known_positions):
    """Build baseline L=17 wheels and compute effective keys at known positions"""
    L = 17
    wheels = {}
    
    # Initialize wheels
    for c in range(6):
        wheels[c] = {
            'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
            'L': L,
            'residues': [None] * L
        }
    
    # Compute effective keys at known positions
    k_eff_known = {}
    
    for pos in known_positions:
        c = compute_class_baseline(pos)
        s = pos % L
        
        c_char = ciphertext[pos]
        p_char = canonical_pt[pos]
        
        c_val = ord(c_char) - ord('A')
        p_val = ord(p_char) - ord('A')
        
        # Compute effective key needed
        if wheels[c]['family'] == 'vigenere':
            k_eff = (c_val - p_val) % 26
        else:
            k_eff = (p_val + c_val) % 26
        
        k_eff_known[pos] = k_eff
        
        # Store in wheels for baseline
        if wheels[c]['residues'][s] is None:
            wheels[c]['residues'][s] = k_eff
    
    return wheels, k_eff_known

def compute_rotor_output(perm_name, ring, start, position):
    """Compute rotor output at given position"""
    perm = ROTOR_PERMS[perm_name]
    rotor_pos = (start + position) % 26
    return (perm[rotor_pos] + ring) % 26

def fit_rotor(k_eff_known, known_positions):
    """Find rotor parameters that match known effective keys"""
    best_fit = None
    best_matches = 0
    
    for perm_name, perm in ROTOR_PERMS.items():
        for ring in range(26):
            for start in range(26):
                for law in ['+', '-']:
                    matches = 0
                    
                    # Test this configuration
                    for pos in known_positions:
                        rotor_out = compute_rotor_output(perm_name, ring, start, pos)
                        
                        # We need to determine what K_L17 would be
                        # For simplicity, assume K_L17 = 0 at unknown positions initially
                        # This is where we'd compose with actual L17 baseline
                        
                        # For known positions, check if rotor explains the effective key
                        if law == '+':
                            # K_eff = (K_L17 + R) mod 26
                            # Since we know K_eff, we'd need K_L17 from baseline
                            pass
                        else:
                            # K_eff = (K_L17 - R) mod 26
                            pass
                        
                        # Simplified: just check if rotor output matches effective key
                        if rotor_out == k_eff_known[pos]:
                            matches += 1
                    
                    if matches > best_matches:
                        best_matches = matches
                        best_fit = {
                            'perm': perm_name,
                            'ring': ring,
                            'start': start,
                            'law': law,
                            'matches': matches,
                            'total': len(known_positions)
                        }
    
    return best_fit

def apply_rotor(ciphertext, canonical_pt, rotor_params, wheels_baseline, known_positions, unknown_positions):
    """Apply fitted rotor to derive plaintext"""
    L = 17
    derived = []
    newly_determined = []
    
    for i in range(97):
        if i in known_positions:
            # Use known plaintext
            derived.append(canonical_pt[i])
        else:
            # Apply rotor to unknown position
            c = compute_class_baseline(i)
            s = i % L
            
            # Get rotor output
            rotor_out = compute_rotor_output(
                rotor_params['perm'],
                rotor_params['ring'],
                rotor_params['start'],
                i
            )
            
            # Get baseline key (if available)
            k_base = wheels_baseline[c]['residues'][s] if wheels_baseline[c]['residues'][s] is not None else 0
            
            # Compose with rotor
            if rotor_params['law'] == '+':
                k_eff = (k_base + rotor_out) % 26
            else:
                k_eff = (k_base - rotor_out) % 26
            
            # Decrypt
            c_char = ciphertext[i]
            c_val = ord(c_char) - ord('A')
            
            if wheels_baseline[c]['family'] == 'vigenere':
                p_val = (c_val - k_eff) % 26
            else:
                p_val = (k_eff - c_val) % 26
            
            p_char = chr(p_val + ord('A'))
            
            # Check if this gives us something new
            if wheels_baseline[c]['residues'][s] is None:
                derived.append(p_char)
                newly_determined.append(i)
            else:
                derived.append(p_char)
    
    return ''.join(derived), newly_determined

def explain_index(idx, rotor_params, k_base, k_eff, c_val, p_val):
    """Explain derivation for a single index"""
    return f"""
Index {idx} Explanation (Rotor Layer):
=====================================
Position: {idx}
Rotor: {rotor_params['perm']} (ring={rotor_params['ring']}, start={rotor_params['start']})

Step 1: Rotor position
  pos(i) = (start + i) mod 26 = ({rotor_params['start']} + {idx}) mod 26 = {(rotor_params['start'] + idx) % 26}

Step 2: Rotor output
  R[i] = (perm[pos] + ring) mod 26 = {compute_rotor_output(rotor_params['perm'], rotor_params['ring'], rotor_params['start'], idx)}

Step 3: Compose with baseline
  K_base = {k_base}
  Law: {rotor_params['law']}
  K_eff = {"(K_base + R) mod 26" if rotor_params['law'] == '+' else "(K_base - R) mod 26"} = {k_eff}

Step 4: Decrypt
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
    """Run D1 rotor tests"""
    print("=== D1: Rotor-like Stepping Layer ===\n")
    
    # Create output directory structure
    os.makedirs('D1_rotor', exist_ok=True)
    
    # Load data
    ciphertext, canonical_pt, anchors, tail, known_positions, unknown_positions = load_data()
    
    print(f"Known positions: {len(known_positions)}")
    print(f"Unknown positions: {len(unknown_positions)}")
    
    # Build baseline and get effective keys
    wheels_baseline, k_eff_known = build_baseline_l17(ciphertext, canonical_pt, known_positions)
    
    # Count baseline unknowns
    baseline_unknowns = 0
    baseline_pt = []
    for i in range(97):
        if i in known_positions:
            baseline_pt.append(canonical_pt[i])
        else:
            c = compute_class_baseline(i)
            s = i % 17
            if wheels_baseline[c]['residues'][s] is None:
                baseline_pt.append('?')
                baseline_unknowns += 1
            else:
                # Can derive from baseline
                c_val = ord(ciphertext[i]) - ord('A')
                k_val = wheels_baseline[c]['residues'][s]
                if wheels_baseline[c]['family'] == 'vigenere':
                    p_val = (c_val - k_val) % 26
                else:
                    p_val = (k_val - c_val) % 26
                baseline_pt.append(chr(p_val + ord('A')))
    
    baseline_pt_str = ''.join(baseline_pt)
    
    print(f"\nBaseline unknowns: {baseline_unknowns}")
    
    # Save baseline
    with open('D1_rotor/PT_PARTIAL_BEFORE.txt', 'w') as f:
        f.write(baseline_pt_str)
    
    # Fit rotor
    print("\nFitting rotor parameters...")
    best_rotor = fit_rotor(k_eff_known, known_positions)
    
    if best_rotor:
        print(f"Best rotor: {best_rotor['perm']} (ring={best_rotor['ring']}, start={best_rotor['start']}, law={best_rotor['law']})")
        print(f"Matches: {best_rotor['matches']}/{best_rotor['total']}")
        
        # Apply rotor
        derived_pt, newly_determined = apply_rotor(
            ciphertext, canonical_pt, best_rotor,
            wheels_baseline, known_positions, unknown_positions
        )
        
        # Count unknowns after
        unknowns_after = derived_pt.count('?')
        
        # Verify constraints
        valid = verify_constraints(derived_pt, canonical_pt, anchors, tail)
        
        print(f"\nUnknowns after rotor: {unknowns_after}")
        print(f"Reduction: {baseline_unknowns - unknowns_after}")
        print(f"Constraints preserved: {valid}")
        
        # Create output directory for this configuration
        config_dir = f"D1_rotor/{best_rotor['perm']}_rho_{best_rotor['ring']}_start_{best_rotor['start']}_law_{best_rotor['law']}"
        os.makedirs(config_dir, exist_ok=True)
        
        # Save results
        with open(f'{config_dir}/PT_PARTIAL_AFTER.txt', 'w') as f:
            f.write(derived_pt)
        
        result = {
            'unknowns_before': baseline_unknowns,
            'unknowns_after': unknowns_after,
            'changed_positions': newly_determined,
            'mechanism_params': best_rotor,
            'checksum': hashlib.sha256(derived_pt.encode()).hexdigest(),
            'constraints_valid': valid
        }
        
        with open(f'{config_dir}/RESULT.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        # If we determined any new positions, explain one
        if newly_determined and unknowns_after < baseline_unknowns:
            idx = newly_determined[0]
            c = compute_class_baseline(idx)
            s = idx % 17
            k_base = wheels_baseline[c]['residues'][s] if wheels_baseline[c]['residues'][s] is not None else 0
            
            rotor_out = compute_rotor_output(
                best_rotor['perm'],
                best_rotor['ring'],
                best_rotor['start'],
                idx
            )
            
            if best_rotor['law'] == '+':
                k_eff = (k_base + rotor_out) % 26
            else:
                k_eff = (k_base - rotor_out) % 26
            
            c_val = ord(ciphertext[idx]) - ord('A')
            
            if wheels_baseline[c]['family'] == 'vigenere':
                p_val = (c_val - k_eff) % 26
            else:
                p_val = (k_eff - c_val) % 26
            
            explanation = explain_index(idx, best_rotor, k_base, k_eff, c_val, p_val)
            
            with open(f'{config_dir}/EXPLAIN_IDX.txt', 'w') as f:
                f.write(explanation)
            
            print(f"\nSUCCESS: Reduced unknowns from {baseline_unknowns} to {unknowns_after}")
        else:
            print("\nNo reduction achieved")
    else:
        print("No rotor configuration found")
    
    print("\nResults saved to D1_rotor/")

if __name__ == "__main__":
    main()