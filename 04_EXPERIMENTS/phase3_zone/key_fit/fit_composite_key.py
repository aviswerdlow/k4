#!/usr/bin/env python3
"""
Fit composite keys when simple periodic keys fail
Plan C: Two-word composite or affine shift
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple


def load_constraints(family: str = 'vigenere') -> List[Dict]:
    """Load anchor keystream constraints"""
    constraints_file = Path(__file__).parent.parent / 'notes' / f'anchor_keystream_{family}_kryptos.json'
    with open(constraints_file, 'r') as f:
        data = json.load(f)
    return data['constraints']


def fit_periodic_key_segment(constraints: List[Dict], L: int, phase: int = 0) -> Optional[str]:
    """Fit a periodic key to a segment of constraints"""
    key = ['?'] * L
    
    for constraint in constraints:
        idx = constraint['idx']
        required = constraint['k']
        key_pos = (idx - phase) % L
        
        if key[key_pos] == '?':
            key[key_pos] = required
        elif key[key_pos] != required:
            return None
    
    # For composite keys, allow partial keys
    return ''.join(key)


def fit_two_word_composite(constraints: List[Dict], max_length: int = 7) -> List[Dict]:
    """
    Plan C-1: Two-word composite key with single splice at position 63
    W1 for positions 0-62, W2 for positions 63-96
    """
    results = []
    
    # Split constraints
    head_constraints = [c for c in constraints if c['idx'] < 63]
    tail_constraints = [c for c in constraints if c['idx'] >= 63]
    
    print("\nTrying two-word composite keys (splice at 63)...")
    print(f"  HEAD constraints: positions {[c['idx'] for c in head_constraints]}")
    print(f"  TAIL constraints: positions {[c['idx'] for c in tail_constraints]}")
    
    # Try different lengths for W1 and W2
    for L1 in range(3, max_length + 1):
        for phase1 in range(L1):
            W1 = fit_periodic_key_segment(head_constraints, L1, phase1)
            
            if W1 and '?' not in W1:  # Only complete keys
                # Found W1, now try W2
                for L2 in range(3, max_length + 1):
                    for phase2 in range(L2):
                        # Phase2 needs to account for the offset at position 63
                        adjusted_phase2 = (phase2 - 63) % L2
                        W2 = fit_periodic_key_segment(tail_constraints, L2, 63 - adjusted_phase2)
                        
                        if W2 and '?' not in W2:  # Only complete keys
                            result = {
                                'type': 'two_word_composite',
                                'W1': W1,
                                'L1': L1,
                                'phase1': phase1,
                                'W2': W2,
                                'L2': L2,
                                'phase2': phase2,
                                'splice_point': 63,
                                'total_length': L1 + L2,
                                'description': f"W1={W1}(L={L1}), W2={W2}(L={L2}), splice@63"
                            }
                            results.append(result)
                            print(f"  ✓ Found: {result['description']}")
    
    # Sort by total length
    results.sort(key=lambda x: x['total_length'])
    return results


def fit_with_rotate_at_69(constraints: List[Dict], max_length: int = 7) -> List[Dict]:
    """
    Extended C-1: Allow rotation at position 69 within the tail segment
    """
    results = []
    
    # Split constraints into three segments
    head_constraints = [c for c in constraints if c['idx'] < 63]
    mid_constraints = [c for c in constraints if 63 <= c['idx'] < 69]
    tail_constraints = [c for c in constraints if c['idx'] >= 69]
    
    print("\nTrying composite with rotation at 69...")
    print(f"  HEAD: positions {[c['idx'] for c in head_constraints]}")
    print(f"  MID (63-68): positions {[c['idx'] for c in mid_constraints]}")
    print(f"  TAIL (69+): positions {[c['idx'] for c in tail_constraints]}")
    
    # Find W1 for HEAD
    for L1 in range(3, max_length + 1):
        for phase1 in range(L1):
            W1 = fit_periodic_key_segment(head_constraints, L1, phase1)
            
            if W1 and '?' not in W1:
                # Find W2 that works for both MID and TAIL with rotation
                for L2 in range(3, max_length + 1):
                    for phase2_mid in range(L2):
                        # Try W2 on MID segment
                        adjusted_phase_mid = (phase2_mid - 63) % L2
                        W2_mid = fit_periodic_key_segment(mid_constraints, L2, 63 - adjusted_phase_mid)
                        
                        if W2_mid and '?' not in W2_mid:
                            # Now check if same W2 works for TAIL with different phase
                            for phase2_tail in range(L2):
                                adjusted_phase_tail = (phase2_tail - 69) % L2
                                W2_tail = fit_periodic_key_segment(tail_constraints, L2, 69 - adjusted_phase_tail)
                                
                                if W2_tail == W2_mid:  # Same key, different phase
                                    result = {
                                        'type': 'composite_with_rotation',
                                        'W1': W1,
                                        'L1': L1,
                                        'phase1': phase1,
                                        'W2': W2_mid,
                                        'L2': L2,
                                        'phase2_mid': phase2_mid,
                                        'phase2_tail': phase2_tail,
                                        'control_points': [63, 69],
                                        'total_length': L1 + L2,
                                        'description': f"W1={W1}, W2={W2_mid}, rotate@69"
                                    }
                                    results.append(result)
                                    print(f"  ✓ Found: {result['description']}")
    
    results.sort(key=lambda x: x['total_length'])
    return results


def fit_affine_shift(constraints: List[Dict], max_length: int = 11, max_shift: int = 5) -> List[Dict]:
    """
    Plan C-2: Single key with Caesar shift at boundaries
    """
    results = []
    
    print("\nTrying affine shift (Caesar offset at 63/69)...")
    
    # For each possible base key length
    for L in range(3, max_length + 1):
        for phase in range(L):
            # Try different Caesar shifts
            for shift63 in range(-max_shift, max_shift + 1):
                if shift63 == 0:
                    continue  # No shift is the pure periodic case
                
                # Build the key with shift
                key = ['?'] * L
                success = True
                
                for constraint in constraints:
                    idx = constraint['idx']
                    required = constraint['k']
                    
                    # Apply shift if past boundary
                    if idx >= 63:
                        # Reverse the shift to find base key letter
                        base_required = chr(((ord(required) - ord('A') - shift63) % 26) + ord('A'))
                    else:
                        base_required = required
                    
                    key_pos = (idx - phase) % L
                    
                    if key[key_pos] == '?':
                        key[key_pos] = base_required
                    elif key[key_pos] != base_required:
                        success = False
                        break
                
                if success and '?' not in key:
                    key_str = ''.join(key)
                    result = {
                        'type': 'affine_shift',
                        'base_key': key_str,
                        'length': L,
                        'phase': phase,
                        'shift63': shift63,
                        'description': f"key={key_str}(L={L}), shift+{shift63}@63"
                    }
                    results.append(result)
                    print(f"  ✓ Found: {result['description']}")
                
                # Also try with additional shift at 69
                for shift69 in range(-max_shift, max_shift + 1):
                    if shift69 == 0:
                        continue
                    
                    key = ['?'] * L
                    success = True
                    
                    for constraint in constraints:
                        idx = constraint['idx']
                        required = constraint['k']
                        
                        # Apply shifts based on position
                        if idx >= 69:
                            base_required = chr(((ord(required) - ord('A') - shift63 - shift69) % 26) + ord('A'))
                        elif idx >= 63:
                            base_required = chr(((ord(required) - ord('A') - shift63) % 26) + ord('A'))
                        else:
                            base_required = required
                        
                        key_pos = (idx - phase) % L
                        
                        if key[key_pos] == '?':
                            key[key_pos] = base_required
                        elif key[key_pos] != base_required:
                            success = False
                            break
                    
                    if success and '?' not in key:
                        key_str = ''.join(key)
                        result = {
                            'type': 'affine_double_shift',
                            'base_key': key_str,
                            'length': L,
                            'phase': phase,
                            'shift63': shift63,
                            'shift69': shift69,
                            'description': f"key={key_str}, +{shift63}@63, +{shift69}@69"
                        }
                        results.append(result)
                        if len(results) < 10:  # Limit output
                            print(f"  ✓ Found: {result['description']}")
    
    results.sort(key=lambda x: (x['length'], abs(x.get('shift63', 0)) + abs(x.get('shift69', 0))))
    return results


def main():
    """Try composite key fitting approaches"""
    
    print("=" * 70)
    print("COMPOSITE KEY FITTING (Plan C)")
    print("=" * 70)
    
    all_results = {}
    
    for family in ['vigenere', 'beaufort']:
        print(f"\n{family.upper()} FAMILY")
        print("=" * 50)
        
        constraints = load_constraints(family)
        
        # Show constraint pattern
        print(f"\nRequired keys: {''.join([c['k'] for c in constraints])}")
        print(f"At positions: {[c['idx'] for c in constraints]}")
        
        # Try different approaches
        results = {
            'two_word': fit_two_word_composite(constraints),
            'with_rotation': fit_with_rotate_at_69(constraints),
            'affine_shift': fit_affine_shift(constraints)
        }
        
        all_results[family] = results
    
    # Save results
    output_path = Path(__file__).parent / 'composite_key_fits.json'
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n\nResults saved to: {output_path}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    for family in ['vigenere', 'beaufort']:
        print(f"\n{family.upper()}:")
        for approach, results in all_results[family].items():
            if results:
                print(f"  {approach}: {len(results)} solutions found")
                if results:
                    best = results[0]
                    print(f"    Best: {best['description']}")
            else:
                print(f"  {approach}: No solutions")


if __name__ == '__main__':
    main()