#!/usr/bin/env python3
"""
C.1: Test if mechanism changes at index 74 (tail boundary).
No semantics, pure mechanics.
"""

import json
import csv
import os

MASTER_SEED = 1337

def compute_class_baseline(i):
    """Baseline class function: ((i%2)*3)+(i%3)"""
    return ((i % 2) * 3) + (i % 3)

def load_ciphertext():
    """Load ciphertext"""
    with open('../../02_DATA/ciphertext_97.txt', 'r') as f:
        return f.read().strip()

def load_canonical_plaintext():
    """Load canonical plaintext for constraints only"""
    with open('../../01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt', 'r') as f:
        return f.read().strip()

def get_base_constraints():
    """Get anchor and tail constraint positions"""
    constraints = set()
    
    # Anchors
    for start, end in [(21, 24), (25, 33), (63, 68), (69, 73)]:
        for i in range(start, end + 1):
            constraints.add(i)
    
    # Tail
    for i in range(74, 97):
        constraints.add(i)
    
    return constraints

def test_variant(ciphertext, canonical_pt, variant_config):
    """
    Test a specific tail split variant.
    Returns derived_count, unknown_count, closure status.
    """
    L_head = 17
    L_tail = variant_config.get('L_tail', 17)
    tail_family_flip = variant_config.get('tail_family_flip', {})
    tail_transposition = variant_config.get('tail_transposition', None)
    
    # Build wheels for head (0-73)
    wheels_head = {}
    for c in range(6):
        wheels_head[c] = {
            'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
            'L': L_head,
            'phase': 0,
            'residues': [None] * L_head
        }
    
    # Build wheels for tail (74-96) with potential changes
    wheels_tail = {}
    for c in range(6):
        base_family = 'vigenere' if c in [1, 3, 5] else 'beaufort'
        
        # Apply family flip if specified
        if c in tail_family_flip:
            if base_family == 'vigenere':
                family = 'beaufort'
            else:
                family = 'vigenere'
        else:
            family = base_family
        
        wheels_tail[c] = {
            'family': family,
            'L': L_tail,
            'phase': 0,
            'residues': [None] * L_tail
        }
    
    # Apply constraints
    constraints = get_base_constraints()
    
    for idx in constraints:
        c = compute_class_baseline(idx)
        
        if idx < 74:
            # Head region
            s = idx % L_head
            wheels = wheels_head
        else:
            # Tail region
            s = (idx - 74) % L_tail  # Reset slot counting at tail
            wheels = wheels_tail
        
        c_char = ciphertext[idx]
        p_char = canonical_pt[idx]
        
        c_val = ord(c_char) - ord('A')
        p_val = ord(p_char) - ord('A')
        
        # Compute residue
        if wheels[c]['family'] == 'vigenere':
            k_val = (c_val - p_val) % 26
        else:
            k_val = (p_val + c_val) % 26
        
        # Store (ignore conflicts for this test)
        if wheels[c]['residues'][s] is None:
            wheels[c]['residues'][s] = k_val
    
    # Derive plaintext
    derived_pt = []
    derived_count = 0
    unknown_indices = []
    
    for i in range(97):
        c = compute_class_baseline(i)
        
        if i < 74:
            s = i % L_head
            wheels = wheels_head
        else:
            s = (i - 74) % L_tail
            wheels = wheels_tail
        
        if wheels[c]['residues'][s] is not None:
            c_char = ciphertext[i]
            c_val = ord(c_char) - ord('A')
            k_val = wheels[c]['residues'][s]
            
            if wheels[c]['family'] == 'vigenere':
                p_val = (c_val - k_val) % 26
            else:
                p_val = (k_val - c_val) % 26
            
            derived_pt.append(chr(p_val + ord('A')))
            derived_count += 1
        else:
            derived_pt.append('?')
            unknown_indices.append(i)
    
    derived_str = ''.join(derived_pt)
    
    # Apply tail transposition if specified
    if tail_transposition and derived_count == 97:
        # Simple transposition: swap positions within tail
        tail_chars = list(derived_str[74:97])
        for swap in tail_transposition:
            i, j = swap
            if i < len(tail_chars) and j < len(tail_chars):
                tail_chars[i], tail_chars[j] = tail_chars[j], tail_chars[i]
        derived_str = derived_str[:74] + ''.join(tail_chars)
    
    unknown_count = 97 - derived_count
    closure = (derived_count == 97)
    
    return {
        'derived_count': derived_count,
        'unknown_count': unknown_count,
        'closure': closure,
        'unknown_indices': unknown_indices,
        'plaintext': derived_str if closure else None
    }

def run_tail_split_tests():
    """Run all tail split variant tests"""
    ciphertext = load_ciphertext()
    canonical_pt = load_canonical_plaintext()
    
    results = []
    
    # C.1.1: Family switch in tail (try flipping each class)
    print("\nC.1.1: Testing family switches in tail...")
    for c in range(6):
        variant = {
            'tail_family_flip': {c: True}
        }
        
        result = test_variant(ciphertext, canonical_pt, variant)
        results.append({
            'variant_id': f'family_flip_class_{c}',
            'derived_count': result['derived_count'],
            'unknown_count': result['unknown_count'],
            'closure': result['closure'],
            'notes': f'Flipped family for class {c} in tail'
        })
        
        print(f"  Class {c} flip: {result['derived_count']}/97 derived")
    
    # C.1.2: Period change in tail
    print("\nC.1.2: Testing period changes in tail...")
    for L_tail in [11, 13, 15]:
        variant = {
            'L_tail': L_tail
        }
        
        result = test_variant(ciphertext, canonical_pt, variant)
        results.append({
            'variant_id': f'tail_period_{L_tail}',
            'derived_count': result['derived_count'],
            'unknown_count': result['unknown_count'],
            'closure': result['closure'],
            'notes': f'Tail period L={L_tail}'
        })
        
        print(f"  L_tail={L_tail}: {result['derived_count']}/97 derived")
    
    # C.1.3: Tail transposition shim
    print("\nC.1.3: Testing tail transposition...")
    # Simple swap pattern
    transpositions = [
        [(0, 11), (1, 12), (2, 13)],  # Width 11
        [(0, 15), (1, 16), (2, 17)]   # Width 15
    ]
    
    for i, trans in enumerate(transpositions):
        variant = {
            'tail_transposition': trans
        }
        
        result = test_variant(ciphertext, canonical_pt, variant)
        width = 11 if i == 0 else 15
        results.append({
            'variant_id': f'tail_transpose_w{width}',
            'derived_count': result['derived_count'],
            'unknown_count': result['unknown_count'],
            'closure': result['closure'],
            'notes': f'Tail transposition width {width}'
        })
        
        print(f"  Transpose w{width}: {result['derived_count']}/97 derived")
    
    return results

def main():
    """Run tail split tests"""
    print("\n=== C.1: Tail Split Mechanism Tests ===")
    print(f"MASTER_SEED: {MASTER_SEED}")
    
    results = run_tail_split_tests()
    
    # Create output directory
    os.makedirs('C1_tail_split', exist_ok=True)
    
    # Save results CSV
    with open('C1_tail_split/RESULTS.csv', 'w', newline='') as f:
        fieldnames = ['variant_id', 'derived_count', 'unknown_count', 'closure', 'notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    # Check for any closures
    closures = [r for r in results if r['closure']]
    
    print("\n=== Summary ===")
    if closures:
        print(f"✓ Found {len(closures)} variants achieving closure:")
        for c in closures:
            print(f"  - {c['variant_id']}")
    else:
        print("✗ No tail split variant achieved closure")
        print(f"Best result: {max(results, key=lambda x: x['derived_count'])['derived_count']}/97")
    
    # Save summary
    with open('C1_tail_split/SUMMARY.json', 'w') as f:
        json.dump({
            'master_seed': MASTER_SEED,
            'total_variants_tested': len(results),
            'closures_found': len(closures),
            'best_derived_count': max(r['derived_count'] for r in results),
            'results': results
        }, f, indent=2)
    
    print("\n✅ Tail split tests complete")

if __name__ == "__main__":
    main()