#!/usr/bin/env python3
"""
Head constraints sweep: Test how many head letters are needed to close L=17.
"""

import json
import csv
import hashlib
from collections import defaultdict

MASTER_SEED = 1337
CANONICAL_SHA = "4eceb739ab655d6f4ec87753569b8bf04573fe26d01c0caa68d36776dd052d79"

def compute_class_baseline(i):
    """Baseline class function: ((i%2)*3)+(i%3)"""
    return ((i % 2) * 3) + (i % 3)

def load_ciphertext():
    """Load the 97-character ciphertext"""
    with open('../../02_DATA/ciphertext_97.txt', 'r') as f:
        return f.read().strip()

def load_canonical_plaintext():
    """Load canonical plaintext"""
    with open('../../01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt', 'r') as f:
        return f.read().strip()

def get_constraint_positions():
    """Get anchor and tail positions"""
    anchors = set(range(21, 25)) | set(range(25, 34)) | set(range(63, 69)) | set(range(69, 74))
    tail = set(range(74, 97))
    return anchors | tail

def build_wheels_with_constraints(ciphertext, plaintext, constraint_indices):
    """
    Build L=17 wheels using given constraint positions.
    """
    L = 17
    
    # Initialize wheels
    wheels = {}
    for c in range(6):
        wheels[c] = {
            'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
            'L': L,
            'phase': 0,
            'residues': [None] * L
        }
    
    # Apply constraints
    for idx in constraint_indices:
        if idx >= len(plaintext):
            continue
            
        c = compute_class_baseline(idx)
        s = idx % L
        
        c_char = ciphertext[idx]
        p_char = plaintext[idx]
        
        c_val = ord(c_char) - ord('A')
        p_val = ord(p_char) - ord('A')
        
        # Compute residue
        if wheels[c]['family'] == 'vigenere':
            k_val = (c_val - p_val) % 26
        else:  # beaufort
            k_val = (p_val + c_val) % 26
        
        # Store (ignore conflicts for this test)
        if wheels[c]['residues'][s] is None:
            wheels[c]['residues'][s] = k_val
    
    return wheels

def derive_plaintext(ciphertext, wheels):
    """Derive plaintext from wheels"""
    plaintext = []
    derived_count = 0
    
    for i in range(len(ciphertext)):
        c = compute_class_baseline(i)
        s = i % 17
        
        if wheels[c]['residues'][s] is not None:
            c_char = ciphertext[i]
            c_val = ord(c_char) - ord('A')
            k_val = wheels[c]['residues'][s]
            
            if wheels[c]['family'] == 'vigenere':
                p_val = (c_val - k_val) % 26
            else:  # beaufort
                p_val = (k_val - c_val) % 26
            
            plaintext.append(chr(p_val + ord('A')))
            derived_count += 1
        else:
            plaintext.append('?')
    
    return ''.join(plaintext), derived_count

def test_head_prefix(k, ciphertext, canonical_pt):
    """Test with first k head positions as constraints"""
    base_constraints = get_constraint_positions()
    head_constraints = set(range(k))
    all_constraints = base_constraints | head_constraints
    
    # Build wheels
    wheels = build_wheels_with_constraints(ciphertext, canonical_pt, all_constraints)
    
    # Derive
    derived_pt, derived_count = derive_plaintext(ciphertext, wheels)
    
    # Check closure
    closed = (derived_count == 97)
    
    # Check SHA
    if closed:
        sha = hashlib.sha256(derived_pt.encode()).hexdigest()
        sha_match = (sha == CANONICAL_SHA)
    else:
        sha_match = False
    
    return {
        'strategy': 'prefix',
        'k': k,
        'derived_count': derived_count,
        'closed': closed,
        'sha_match': sha_match
    }

def test_every_nth(n, max_k, ciphertext, canonical_pt):
    """Test with every nth head position"""
    results = []
    base_constraints = get_constraint_positions()
    
    for k in range(1, min(max_k + 1, 74 // n + 1)):
        head_constraints = set(range(0, min(k * n, 74), n))
        all_constraints = base_constraints | head_constraints
        
        wheels = build_wheels_with_constraints(ciphertext, canonical_pt, all_constraints)
        derived_pt, derived_count = derive_plaintext(ciphertext, wheels)
        
        closed = (derived_count == 97)
        sha_match = closed and (hashlib.sha256(derived_pt.encode()).hexdigest() == CANONICAL_SHA)
        
        results.append({
            'strategy': f'every_{n}th',
            'k': len(head_constraints),
            'derived_count': derived_count,
            'closed': closed,
            'sha_match': sha_match
        })
    
    return results

def test_greedy_addition(ciphertext, canonical_pt, max_additions=50):
    """Greedy algorithm: add positions that maximize new derivations"""
    base_constraints = get_constraint_positions()
    current_constraints = set(base_constraints)
    available_head = set(range(74)) - current_constraints
    
    results = []
    
    for iteration in range(min(max_additions, len(available_head))):
        best_pos = None
        best_derived = 0
        
        # Try each available position
        for pos in available_head:
            test_constraints = current_constraints | {pos}
            wheels = build_wheels_with_constraints(ciphertext, canonical_pt, test_constraints)
            _, derived_count = derive_plaintext(ciphertext, wheels)
            
            if derived_count > best_derived:
                best_derived = derived_count
                best_pos = pos
        
        if best_pos is not None:
            current_constraints.add(best_pos)
            available_head.remove(best_pos)
            
            closed = (best_derived == 97)
            sha_match = False
            
            if closed:
                wheels = build_wheels_with_constraints(ciphertext, canonical_pt, current_constraints)
                derived_pt, _ = derive_plaintext(ciphertext, wheels)
                sha = hashlib.sha256(derived_pt.encode()).hexdigest()
                sha_match = (sha == CANONICAL_SHA)
            
            results.append({
                'strategy': 'greedy',
                'k': len(current_constraints) - len(base_constraints),
                'derived_count': best_derived,
                'closed': closed,
                'sha_match': sha_match
            })
            
            if closed:
                break
    
    return results

def main():
    """Run head constraints sweep"""
    print("\n=== L=17 Head Constraints Sweep ===")
    print(f"MASTER_SEED: {MASTER_SEED}")
    
    ciphertext = load_ciphertext()
    canonical_pt = load_canonical_plaintext()
    
    all_results = []
    
    # Test prefix strategy (k=1..30)
    print("\nTesting prefix strategy...")
    for k in range(1, 31):
        result = test_head_prefix(k, ciphertext, canonical_pt)
        all_results.append(result)
        if k % 5 == 0:
            print(f"  k={k}: {result['derived_count']} derived")
    
    # Test every 3rd position
    print("\nTesting every 3rd position...")
    every_3rd = test_every_nth(3, 30, ciphertext, canonical_pt)
    all_results.extend(every_3rd)
    
    # Test greedy addition
    print("\nTesting greedy addition...")
    greedy = test_greedy_addition(ciphertext, canonical_pt, max_additions=50)
    all_results.extend(greedy)
    
    # Save results
    output_dir = '../../04_EXPERIMENTS/L17_MISSING'
    
    with open(f'{output_dir}/HEAD_PREFIX_SWEEP.csv', 'w', newline='') as f:
        if all_results:
            writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
            writer.writeheader()
            writer.writerows(all_results)
    
    with open(f'{output_dir}/HEAD_PREFIX_SWEEP.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Find minimal closure
    min_closure = None
    for result in all_results:
        if result['closed'] and result['sha_match']:
            if min_closure is None or result['k'] < min_closure['k']:
                min_closure = result
    
    with open(f'{output_dir}/HEAD_MIN_CLOSURE.json', 'w') as f:
        json.dump(min_closure, f, indent=2)
    
    # Create summary
    with open(f'{output_dir}/HEAD_PREFIX_SWEEP.md', 'w') as f:
        f.write("# Head Constraints Sweep Results\n\n")
        f.write("## Summary\n")
        
        if min_closure:
            f.write(f"✓ Minimal closure achieved with {min_closure['k']} head constraints ")
            f.write(f"(strategy: {min_closure['strategy']})\n\n")
        else:
            f.write("✗ No closure achieved with tested strategies (up to 50 constraints)\n\n")
        
        f.write("## Prefix Strategy Results\n")
        f.write("| k | Derived | Closed |\n")
        f.write("|---|---------|--------|\n")
        
        for result in all_results:
            if result['strategy'] == 'prefix' and result['k'] % 5 == 0:
                closed = '✓' if result['closed'] else '✗'
                f.write(f"| {result['k']} | {result['derived_count']} | {closed} |\n")
    
    print("\n✅ Sweep complete.")
    if min_closure:
        print(f"Minimal closure: {min_closure['k']} constraints ({min_closure['strategy']})")
    else:
        print("No closure achieved with tested strategies")

if __name__ == "__main__":
    main()