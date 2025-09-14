#!/usr/bin/env python3
"""
Fit periodic key to anchor constraints
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from collections import defaultdict


def load_constraints(family: str = 'vigenere') -> List[Dict]:
    """Load anchor keystream constraints"""
    constraints_file = Path(__file__).parent.parent / 'notes' / f'anchor_keystream_{family}_kryptos.json'
    with open(constraints_file, 'r') as f:
        data = json.load(f)
    return data['constraints']


def fit_periodic_key(constraints: List[Dict], L: int, phase: int, 
                    allow_partial: bool = False, verbose: bool = False) -> Optional[str]:
    """
    Try to fit a periodic key of length L with given phase offset
    
    Args:
        constraints: List of {'idx': position, 'k': required_key_letter}
        L: Key length to try
        phase: Phase offset (key position = (idx - phase) mod L)
        allow_partial: If True, return partial keys with '?' for unconstrained positions
        verbose: If True, print debug info
    
    Returns:
        The fitted key string if consistent, None if contradictions
    """
    key = ['?'] * L  # Initialize with unknowns
    conflicts = []
    
    for constraint in constraints:
        idx = constraint['idx']
        required = constraint['k']
        
        # Calculate position in key
        key_pos = (idx - phase) % L
        
        # Check consistency
        if key[key_pos] == '?':
            key[key_pos] = required
        elif key[key_pos] != required:
            # Contradiction
            conflicts.append(f"Position {idx} (key_pos {key_pos}): needs '{required}' but have '{key[key_pos]}'")
            if verbose:
                print(f"    Conflict: {conflicts[-1]}")
            return None
    
    # Check if we have a complete key
    if '?' in key:
        if not allow_partial:
            return None
        # For partial keys, could fill with common letters
        # but for now just return with ?s
    
    return ''.join(key)


def fit_with_control_schedule(constraints: List[Dict], L: int, 
                             control_points: List[int] = [63, 69]) -> Optional[Dict]:
    """
    Fit periodic key with phase changes at control points
    
    Returns:
        Dict with key and phase offsets for each segment
    """
    # Define segments
    segments = []
    prev = 0
    for cp in control_points:
        segments.append((prev, cp - 1))
        prev = cp
    segments.append((prev, 96))  # Last segment
    
    # Try to find a single key that works with different phases
    for phase0 in range(L):
        # Start with first segment
        segment_constraints = [c for c in constraints if c['idx'] <= segments[0][1]]
        key = fit_periodic_key(segment_constraints, L, phase0)
        
        if key is None:
            continue
        
        # Try to fit remaining segments with same key but different phases
        phases = [phase0]
        success = True
        
        for seg_idx in range(1, len(segments)):
            seg_start, seg_end = segments[seg_idx]
            seg_constraints = [c for c in constraints 
                              if seg_start <= c['idx'] <= seg_end]
            
            # Try different phases for this segment
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
                'control_points': control_points,
                'segments': segments
            }
    
    return None


def score_key_wordlike(key: str) -> float:
    """Score how word-like a key is (higher is better)"""
    score = 0.0
    
    # Common letter frequencies in English
    freq = {'E': 12.7, 'T': 9.0, 'A': 8.2, 'O': 7.5, 'I': 7.0, 'N': 6.7,
            'S': 6.3, 'H': 6.0, 'R': 6.0, 'D': 4.3, 'L': 4.0, 'U': 2.8}
    
    for char in key:
        score += freq.get(char, 0.5)
    
    # Check for common bigrams
    bigrams = ['TH', 'HE', 'IN', 'ER', 'AN', 'ED', 'ND', 'TO', 'EN', 'ES',
               'ST', 'AR', 'OU', 'IT', 'TE', 'NG', 'ON', 'AT', 'AL', 'LE']
    
    for bg in bigrams:
        if bg in key:
            score += 5
    
    # Check for theme words (optional bonus)
    themes = ['TIME', 'CLOCK', 'BERLIN', 'EAST', 'NORTH', 'LIGHT', 'SHADOW']
    for theme in themes:
        if theme in key:
            score += 20
    
    # Penalize repeated letters
    for i in range(len(key) - 1):
        if key[i] == key[i + 1]:
            score -= 2
    
    return score / len(key)  # Normalize by length


def find_all_fits(family: str = 'vigenere', max_length: int = 11) -> List[Dict]:
    """Find all periodic key fits for given family"""
    
    constraints = load_constraints(family)
    fits = []
    
    print(f"\nSearching for {family.upper()} periodic keys...")
    print("=" * 50)
    
    # Show the constraint pattern
    print("\nConstraint indices:", [c['idx'] for c in constraints])
    print("Required keys:", ''.join([c['k'] for c in constraints]))
    
    # Try pure periodic keys
    for L in range(3, max_length + 1):
        print(f"\nTrying length {L}:")
        found_any = False
        
        for phase in range(L):
            # First try with partial to see what we get
            partial_key = fit_periodic_key(constraints, L, phase, allow_partial=True)
            
            if partial_key and '?' not in partial_key:
                # Complete key found
                score = score_key_wordlike(partial_key)
                fit = {
                    'family': family,
                    'type': 'pure_periodic',
                    'key': partial_key,
                    'length': L,
                    'phase': phase,
                    'score': score,
                    'description': f"L={L}, φ={phase}, key={partial_key}"
                }
                fits.append(fit)
                print(f"  ✓ Found: {partial_key} (phase={phase}, score={score:.2f})")
                found_any = True
            elif partial_key:
                # Partial key - show for debugging
                if not found_any and phase == 0:  # Only show first phase for brevity
                    print(f"  × Partial: {partial_key} (phase={phase})")
        
        if not found_any:
            # Try to understand why no fit - check for conflicts
            key = fit_periodic_key(constraints, L, 0, verbose=True)
            if key is None and L <= 5:  # Only show details for small L
                print(f"    No consistent key possible for L={L}")
    
    # Try with control schedule
    print(f"\nTrying with control schedule at [63, 69]:")
    
    for L in range(3, max_length + 1):
        result = fit_with_control_schedule(constraints, L, [63, 69])
        
        if result:
            score = score_key_wordlike(result['key'])
            fit = {
                'family': family,
                'type': 'control_schedule',
                'key': result['key'],
                'length': L,
                'phases': result['phases'],
                'control_points': result['control_points'],
                'score': score,
                'description': f"L={L}, key={result['key']}, phases={result['phases']}"
            }
            fits.append(fit)
            print(f"  Found: {result['key']} (phases={result['phases']}, score={score:.2f})")
    
    # Sort by length first, then score
    fits.sort(key=lambda x: (x['length'], -x['score']))
    
    return fits


def main():
    """Find periodic key fits for both cipher families"""
    
    print("=" * 70)
    print("PERIODIC KEY FITTING")
    print("=" * 70)
    
    all_fits = {}
    
    for family in ['vigenere', 'beaufort']:
        fits = find_all_fits(family)
        all_fits[family] = fits
        
        print(f"\n\nTOP 5 FITS FOR {family.upper()}:")
        print("-" * 50)
        
        for i, fit in enumerate(fits[:5]):
            print(f"\n{i+1}. {fit['description']}")
            print(f"   Type: {fit['type']}")
            print(f"   Score: {fit['score']:.2f}")
    
    # Save results
    output_path = Path(__file__).parent / 'periodic_key_fits.json'
    with open(output_path, 'w') as f:
        json.dump(all_fits, f, indent=2)
    
    print(f"\n\nResults saved to: {output_path}")
    
    # Also save control schedule fits separately
    control_fits = {}
    for family in ['vigenere', 'beaufort']:
        control_fits[family] = [f for f in all_fits[family] 
                                if f['type'] == 'control_schedule']
    
    if any(control_fits.values()):
        control_output = Path(__file__).parent / 'periodic_key_fits_control.json'
        with open(control_output, 'w') as f:
            json.dump(control_fits, f, indent=2)
        print(f"Control schedule fits saved to: {control_output}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    for family in ['vigenere', 'beaufort']:
        pure_count = sum(1 for f in all_fits[family] if f['type'] == 'pure_periodic')
        control_count = sum(1 for f in all_fits[family] if f['type'] == 'control_schedule')
        
        print(f"\n{family.upper()}:")
        print(f"  Pure periodic fits: {pure_count}")
        print(f"  Control schedule fits: {control_count}")
        
        if all_fits[family]:
            best = all_fits[family][0]
            print(f"  Best fit: {best['key']} (L={best['length']}, type={best['type']})")


if __name__ == '__main__':
    main()