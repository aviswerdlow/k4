#!/usr/bin/env python3
"""
C.2: Test autokey and running-key mechanisms.
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

def test_autokey_variant(ciphertext, canonical_pt, variant_config):
    """
    Test autokey variant where plaintext feeds back into key.
    """
    L = 17
    use_autokey = variant_config.get('use_autokey', False)
    autokey_start = variant_config.get('autokey_start', 0)
    autokey_delay = variant_config.get('autokey_delay', 0)
    
    # Build initial wheels from constraints
    wheels = {}
    for c in range(6):
        wheels[c] = {
            'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
            'L': L,
            'phase': 0,
            'residues': [None] * L
        }
    
    # Apply initial constraints
    constraints = get_base_constraints()
    
    for idx in constraints:
        c = compute_class_baseline(idx)
        s = idx % L
        
        c_char = ciphertext[idx]
        p_char = canonical_pt[idx]
        
        c_val = ord(c_char) - ord('A')
        p_val = ord(p_char) - ord('A')
        
        if wheels[c]['family'] == 'vigenere':
            k_val = (c_val - p_val) % 26
        else:
            k_val = (p_val + c_val) % 26
        
        wheels[c]['residues'][s] = k_val
    
    if use_autokey and autokey_start < 97:
        # Autokey: Use derived plaintext to fill unknowns
        # Multiple passes to propagate
        for pass_num in range(3):
            made_progress = False
            
            for i in range(autokey_start, 97):
                if i in constraints:
                    continue
                
                # Try to derive this position
                c = compute_class_baseline(i)
                s = i % L
                
                if wheels[c]['residues'][s] is not None:
                    continue
                
                # Check if we can use autokey
                feedback_idx = i - autokey_delay - 1
                if feedback_idx >= 0 and feedback_idx < i:
                    # Try to get plaintext from feedback position
                    fc = compute_class_baseline(feedback_idx)
                    fs = feedback_idx % L
                    
                    if wheels[fc]['residues'][fs] is not None:
                        # Can derive feedback plaintext
                        fc_char = ciphertext[feedback_idx]
                        fc_val = ord(fc_char) - ord('A')
                        fk_val = wheels[fc]['residues'][fs]
                        
                        if wheels[fc]['family'] == 'vigenere':
                            fp_val = (fc_val - fk_val) % 26
                        else:
                            fp_val = (fk_val - fc_val) % 26
                        
                        # Use as key for current position
                        wheels[c]['residues'][s] = fp_val
                        made_progress = True
            
            if not made_progress:
                break
    
    # Derive plaintext
    derived_pt = []
    derived_count = 0
    unknown_indices = []
    
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
            
            derived_pt.append(chr(p_val + ord('A')))
            derived_count += 1
        else:
            derived_pt.append('?')
            unknown_indices.append(i)
    
    derived_str = ''.join(derived_pt)
    unknown_count = 97 - derived_count
    closure = (derived_count == 97)
    
    return {
        'derived_count': derived_count,
        'unknown_count': unknown_count,
        'closure': closure,
        'unknown_indices': unknown_indices,
        'plaintext': derived_str if closure else None
    }

def test_running_key_variant(ciphertext, canonical_pt, variant_config):
    """
    Test running-key variant with external key source.
    """
    L = 17
    key_source = variant_config.get('key_source', 'fixed')
    key_pattern = variant_config.get('key_pattern', 'A' * L)
    
    # Build wheels
    wheels = {}
    for c in range(6):
        wheels[c] = {
            'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
            'L': L,
            'phase': 0,
            'residues': [None] * L
        }
    
    # Apply constraints
    constraints = get_base_constraints()
    
    for idx in constraints:
        c = compute_class_baseline(idx)
        s = idx % L
        
        c_char = ciphertext[idx]
        p_char = canonical_pt[idx]
        
        c_val = ord(c_char) - ord('A')
        p_val = ord(p_char) - ord('A')
        
        if wheels[c]['family'] == 'vigenere':
            k_val = (c_val - p_val) % 26
        else:
            k_val = (p_val + c_val) % 26
        
        wheels[c]['residues'][s] = k_val
    
    if key_source == 'running':
        # Fill unknown slots with pattern
        for c in range(6):
            for s in range(L):
                if wheels[c]['residues'][s] is None:
                    # Use pattern character
                    pattern_idx = s % len(key_pattern)
                    wheels[c]['residues'][s] = ord(key_pattern[pattern_idx]) - ord('A')
    
    # Derive plaintext
    derived_pt = []
    derived_count = 0
    unknown_indices = []
    
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
            
            derived_pt.append(chr(p_val + ord('A')))
            derived_count += 1
        else:
            derived_pt.append('?')
            unknown_indices.append(i)
    
    derived_str = ''.join(derived_pt)
    unknown_count = 97 - derived_count
    closure = (derived_count == 97)
    
    return {
        'derived_count': derived_count,
        'unknown_count': unknown_count,
        'closure': closure,
        'unknown_indices': unknown_indices,
        'plaintext': derived_str if closure else None
    }

def run_autokey_tests():
    """Run all autokey and running-key tests"""
    ciphertext = load_ciphertext()
    canonical_pt = load_canonical_plaintext()
    
    results = []
    
    # C.2.1: Basic autokey
    print("\nC.2.1: Testing basic autokey...")
    for start in [0, 21, 34, 74]:
        variant = {
            'use_autokey': True,
            'autokey_start': start,
            'autokey_delay': 0
        }
        
        result = test_autokey_variant(ciphertext, canonical_pt, variant)
        results.append({
            'variant_id': f'autokey_start_{start}',
            'derived_count': result['derived_count'],
            'unknown_count': result['unknown_count'],
            'closure': result['closure'],
            'notes': f'Autokey starting at position {start}'
        })
        
        print(f"  Start={start}: {result['derived_count']}/97 derived")
    
    # C.2.2: Delayed autokey
    print("\nC.2.2: Testing delayed autokey...")
    for delay in [1, 2, 5, 10]:
        variant = {
            'use_autokey': True,
            'autokey_start': 0,
            'autokey_delay': delay
        }
        
        result = test_autokey_variant(ciphertext, canonical_pt, variant)
        results.append({
            'variant_id': f'autokey_delay_{delay}',
            'derived_count': result['derived_count'],
            'unknown_count': result['unknown_count'],
            'closure': result['closure'],
            'notes': f'Autokey with delay={delay}'
        })
        
        print(f"  Delay={delay}: {result['derived_count']}/97 derived")
    
    # C.2.3: Running key
    print("\nC.2.3: Testing running key...")
    patterns = ['KRYPTOS', 'PALIMPSEST', 'ABCDEFGHIJKLMNOPQ']
    
    for pattern in patterns:
        variant = {
            'key_source': 'running',
            'key_pattern': pattern
        }
        
        result = test_running_key_variant(ciphertext, canonical_pt, variant)
        results.append({
            'variant_id': f'running_key_{pattern[:7]}',
            'derived_count': result['derived_count'],
            'unknown_count': result['unknown_count'],
            'closure': result['closure'],
            'notes': f'Running key pattern: {pattern}'
        })
        
        print(f"  Pattern={pattern[:7]}: {result['derived_count']}/97 derived")
    
    return results

def main():
    """Run autokey tests"""
    print("\n=== C.2: Autokey/Running-Key Tests ===")
    print(f"MASTER_SEED: {MASTER_SEED}")
    
    results = run_autokey_tests()
    
    # Create output directory
    os.makedirs('C2_autokey', exist_ok=True)
    
    # Save results CSV
    with open('C2_autokey/RESULTS.csv', 'w', newline='') as f:
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
        print("✗ No autokey/running-key variant achieved closure")
        print(f"Best result: {max(results, key=lambda x: x['derived_count'])['derived_count']}/97")
    
    # Save summary
    with open('C2_autokey/SUMMARY.json', 'w') as f:
        json.dump({
            'master_seed': MASTER_SEED,
            'total_variants_tested': len(results),
            'closures_found': len(closures),
            'best_derived_count': max(r['derived_count'] for r in results),
            'results': results
        }, f, indent=2)
    
    print("\n✅ Autokey tests complete")

if __name__ == "__main__":
    main()