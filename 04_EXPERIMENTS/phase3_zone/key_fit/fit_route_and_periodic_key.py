#!/usr/bin/env python3
"""
Joint route and periodic key fitting from anchor constraints
Plan D: Learn the route and key together
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Add cipher_families to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / '03_SOLVERS' / 'zone_mask_v1' / 'scripts'))
from cipher_families import VigenereCipher, BeaufortCipher

# Import route utilities
from route_utils import apply_route


def load_ciphertext() -> str:
    """Load K4 ciphertext"""
    ct_path = Path(__file__).parent.parent.parent.parent / '02_DATA' / 'ciphertext_97.txt'
    with open(ct_path, 'r') as f:
        return f.read().strip().upper()


def derive_route_aware_constraints(route_type: str, params: Dict, family: str) -> List[Dict]:
    """
    Derive key constraints after applying route transformation
    
    With route, the process is: CT → route → S → cipher → PT
    So S[p] at position p needs key to decrypt to PT[p]
    """
    ciphertext = load_ciphertext()
    
    # Apply route to get S
    S = apply_route(ciphertext, route_type, params)
    
    # Create cipher
    if family == 'vigenere':
        cipher = VigenereCipher(tableau='kryptos')
    else:
        cipher = BeaufortCipher(tableau='kryptos')
    
    # Define anchors
    anchors = [
        ('EAST', 21, 24),
        ('NORTHEAST', 25, 33),
        ('BERLIN', 63, 68),
        ('CLOCK', 69, 73)
    ]
    
    constraints = []
    
    for anchor_name, start, end in anchors:
        anchor_text = anchor_name
        
        for i, pt_char in enumerate(anchor_text):
            pos = start + i
            s_char = S[pos]  # Character in S at position pos
            
            # Find required key letter to decrypt s_char to pt_char
            for key_char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                if cipher.decrypt(s_char, key_char) == pt_char:
                    constraints.append({
                        'idx': pos,
                        's_char': s_char,
                        'pt_char': pt_char,
                        'k': key_char,
                        'anchor': anchor_name
                    })
                    break
    
    return constraints


def fit_periodic_key(constraints: List[Dict], L: int, phase: int = 0) -> Optional[str]:
    """Try to fit a periodic key of length L with given phase"""
    key = ['?'] * L
    
    for constraint in constraints:
        idx = constraint['idx']
        required = constraint['k']
        key_pos = (idx - phase) % L
        
        if key[key_pos] == '?':
            key[key_pos] = required
        elif key[key_pos] != required:
            return None  # Conflict
    
    # Check if complete
    if '?' in key:
        return None  # Incomplete
    
    return ''.join(key)


def fit_with_control(constraints: List[Dict], L: int, control_points: List[int] = [63, 69]) -> Optional[Dict]:
    """Fit periodic key with phase resets at control points"""
    
    # Define segments based on control points
    segments = []
    prev = 0
    for cp in control_points:
        segments.append((prev, cp - 1))
        prev = cp
    segments.append((prev, 96))
    
    # Try to find a single key with different phases
    for initial_phase in range(L):
        # Get constraints for first segment
        seg_constraints = [c for c in constraints if c['idx'] <= segments[0][1]]
        key = fit_periodic_key(seg_constraints, L, initial_phase)
        
        if key is None:
            continue
        
        # Try to fit remaining segments with same key
        phases = [initial_phase]
        success = True
        
        for seg_idx in range(1, len(segments)):
            seg_start, seg_end = segments[seg_idx]
            seg_constraints = [c for c in constraints if seg_start <= c['idx'] <= seg_end]
            
            # Try different phases
            found_phase = None
            for phase in range(L):
                test_key = fit_periodic_key(seg_constraints, L, phase)
                if test_key == key:
                    found_phase = phase
                    break
            
            if found_phase is None:
                success = False
                break
            
            phases.append(found_phase)
        
        if success:
            return {
                'key': key,
                'length': L,
                'phases': phases,
                'control_points': control_points
            }
    
    return None


def search_route_key_combinations() -> List[Dict]:
    """Search all route and key combinations"""
    
    # Define routes to test
    routes = [
        ('identity', {}),
        ('columnar', {'rows': 7, 'cols': 14}),
        ('serpentine', {'rows': 7, 'cols': 14}),
        ('diag_weave', {'rows': 7, 'cols': 14, 'step': [1, 2]}),
        ('ring24', {})
    ]
    
    results = []
    
    print("=" * 70)
    print("JOINT ROUTE + KEY FITTING")
    print("=" * 70)
    
    for family in ['vigenere', 'beaufort']:
        print(f"\n{family.upper()} FAMILY")
        print("-" * 50)
        
        for route_type, params in routes:
            print(f"\nTrying route: {route_type}")
            
            # Get constraints for this route
            constraints = derive_route_aware_constraints(route_type, params, family)
            
            # Show constraint pattern
            key_pattern = ''.join([c['k'] for c in constraints])
            print(f"  Key pattern after route: {key_pattern}")
            
            # Try pure periodic keys
            for L in range(3, 12):
                for phase in range(L):
                    key = fit_periodic_key(constraints, L, phase)
                    
                    if key:
                        result = {
                            'family': family,
                            'route': route_type,
                            'route_params': params,
                            'type': 'pure_periodic',
                            'key': key,
                            'length': L,
                            'phase': phase,
                            'description': f"{family}, {route_type}, L={L}, φ={phase}, key={key}"
                        }
                        results.append(result)
                        print(f"  ✓ Found: {key} (L={L}, φ={phase})")
            
            # Try with control schedule
            control_result = fit_with_control(constraints, L)
            if control_result:
                for L in range(3, 12):
                    control_result = fit_with_control(constraints, L)
                    if control_result:
                        result = {
                            'family': family,
                            'route': route_type,
                            'route_params': params,
                            'type': 'control_schedule',
                            'key': control_result['key'],
                            'length': L,
                            'phases': control_result['phases'],
                            'control_points': control_result['control_points'],
                            'description': f"{family}, {route_type}, key={control_result['key']}, control@63,69"
                        }
                        results.append(result)
                        print(f"  ✓ Found with control: {control_result['key']} (phases={control_result['phases']})")
                        break
    
    return results


def main():
    """Find route and key combinations that satisfy anchors"""
    
    results = search_route_key_combinations()
    
    # Save results
    output_path = Path(__file__).parent / 'route_periodic_fits.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if results:
        print(f"\nFound {len(results)} route+key combinations that satisfy all anchors!")
        
        # Group by route
        by_route = {}
        for r in results:
            route = r['route']
            if route not in by_route:
                by_route[route] = []
            by_route[route].append(r)
        
        for route, fits in by_route.items():
            print(f"\n{route}: {len(fits)} solutions")
            for fit in fits[:3]:  # Show first 3
                print(f"  - {fit['family']}, key={fit['key']}, L={fit['length']}")
    else:
        print("\nNo route+key combinations found that satisfy all anchors.")
        print("This falsifies: 'one fixed pass + short periodic key' hypothesis.")
    
    print(f"\nResults saved to: {output_path}")
    
    # If we found solutions, note which ones to build manifests for
    if results:
        print("\n" + "=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print("\nTop candidates for manifest generation:")
        
        # Prefer shorter keys and simpler routes
        results.sort(key=lambda x: (x['length'], 0 if x['route'] == 'identity' else 1))
        
        for i, r in enumerate(results[:5]):
            print(f"{i+1}. {r['description']}")


if __name__ == '__main__':
    main()