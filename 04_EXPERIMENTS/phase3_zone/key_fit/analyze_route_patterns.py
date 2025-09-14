#!/usr/bin/env python3
"""
Analyze key patterns after route transformations
"""

import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / '03_SOLVERS' / 'zone_mask_v1' / 'scripts'))
from cipher_families import VigenereCipher, BeaufortCipher

from route_utils import apply_route
from fit_route_and_periodic_key import derive_route_aware_constraints


def analyze_pattern(pattern: str, name: str):
    """Analyze a key pattern for periodicity"""
    print(f"\n{name}:")
    print(f"  Pattern: {pattern}")
    print(f"  Length: {len(pattern)}")
    
    # Check for exact repetitions
    for period in range(2, min(12, len(pattern) // 2)):
        repeats = []
        for i in range(period):
            chars_at_period = [pattern[j] for j in range(i, len(pattern), period) if j < len(pattern)]
            if len(set(chars_at_period)) == 1:
                repeats.append(f"pos%{period}={i}: '{chars_at_period[0]}'")
        
        if repeats:
            print(f"  Period {period}: {len(repeats)} consistent positions")
            if len(repeats) <= 3:
                for r in repeats:
                    print(f"    {r}")
    
    # Check for partial patterns
    for L in range(3, 12):
        # See how many positions would be consistent
        key_positions = {}
        conflicts = 0
        
        for i, char in enumerate(pattern):
            pos = i % L
            if pos not in key_positions:
                key_positions[pos] = char
            elif key_positions[pos] != char:
                conflicts += 1
        
        if conflicts <= 2:  # Allow up to 2 conflicts
            print(f"  Near-fit L={L}: {conflicts} conflicts")
            if conflicts > 0:
                # Show what the conflicts are
                for i, char in enumerate(pattern):
                    pos = i % L
                    if key_positions[pos] != char:
                        print(f"    Position {i} (mod {L} = {pos}): needs '{char}' but have '{key_positions[pos]}'")


def main():
    """Analyze key patterns from different routes"""
    
    print("=" * 70)
    print("KEY PATTERN ANALYSIS AFTER ROUTES")
    print("=" * 70)
    
    routes = [
        ('identity', {}),
        ('columnar', {'rows': 7, 'cols': 14}),
        ('serpentine', {'rows': 7, 'cols': 14}),
        ('ring24', {})
    ]
    
    for family in ['vigenere', 'beaufort']:
        print(f"\n{family.upper()} FAMILY")
        print("=" * 50)
        
        patterns = {}
        
        for route_type, params in routes:
            # Get constraints
            constraints = derive_route_aware_constraints(route_type, params, family)
            pattern = ''.join([c['k'] for c in constraints])
            patterns[route_type] = pattern
            
            analyze_pattern(pattern, f"{route_type} route")
        
        # Look for similarities across routes
        print("\nCross-route analysis:")
        
        # Find common subsequences
        for i in range(len(patterns['identity']) - 3):
            substr = patterns['identity'][i:i+4]
            found_in = []
            for route, pattern in patterns.items():
                if route != 'identity' and substr in pattern:
                    pos = pattern.index(substr)
                    found_in.append(f"{route}@{pos}")
            
            if found_in:
                print(f"  Substring '{substr}' at identity@{i} also in: {', '.join(found_in)}")


if __name__ == '__main__':
    main()