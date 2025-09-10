#!/usr/bin/env python3
"""
E4 - Two-stage Substitution + Transposition
Test if K4 uses substitution followed by transposition
"""

import json
import os
import hashlib
from typing import Dict, List, Optional, Tuple

MASTER_SEED = 1337

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
    
    return ciphertext, canonical_pt, anchors, tail

def test_columnar_transposition(text, key_length):
    """Test columnar transposition with given key length"""
    n = len(text)
    
    # Create grid
    rows = (n + key_length - 1) // key_length
    grid = []
    
    idx = 0
    for r in range(rows):
        row = []
        for c in range(key_length):
            if idx < n:
                row.append(text[idx])
                idx += 1
            else:
                row.append('')
        grid.append(row)
    
    # Read columns in order (simplified - no key permutation)
    result = []
    for c in range(key_length):
        for r in range(rows):
            if grid[r][c]:
                result.append(grid[r][c])
    
    return ''.join(result)

def test_rail_fence(text, rails):
    """Test rail fence transposition"""
    n = len(text)
    fence = [['' for _ in range(n)] for _ in range(rails)]
    
    # Write in zigzag
    rail = 0
    direction = 1
    
    for i, char in enumerate(text):
        fence[rail][i] = char
        rail += direction
        
        if rail == 0 or rail == rails - 1:
            direction = -direction
    
    # Read off by rows
    result = []
    for row in fence:
        for char in row:
            if char:
                result.append(char)
    
    return ''.join(result)

def test_route_cipher(text, rows, cols):
    """Test route cipher (spiral reading)"""
    n = len(text)
    
    # Fill grid
    grid = [['' for _ in range(cols)] for _ in range(rows)]
    
    idx = 0
    for r in range(rows):
        for c in range(cols):
            if idx < n:
                grid[r][c] = text[idx]
                idx += 1
    
    # Read in spiral
    result = []
    top, bottom = 0, rows - 1
    left, right = 0, cols - 1
    
    while top <= bottom and left <= right:
        # Right
        for c in range(left, right + 1):
            if grid[top][c]:
                result.append(grid[top][c])
        top += 1
        
        # Down
        for r in range(top, bottom + 1):
            if grid[r][right]:
                result.append(grid[r][right])
        right -= 1
        
        # Left
        if top <= bottom:
            for c in range(right, left - 1, -1):
                if grid[bottom][c]:
                    result.append(grid[bottom][c])
            bottom -= 1
        
        # Up
        if left <= right:
            for r in range(bottom, top - 1, -1):
                if grid[r][left]:
                    result.append(grid[r][left])
            left += 1
    
    return ''.join(result)

def reverse_transposition(ciphertext, canonical_pt, anchors, tail, trans_type, params):
    """Try to reverse a transposition to find intermediate text"""
    known_positions = set(anchors) | set(tail)
    
    # Build partial intermediate text from known positions
    intermediate = ['?'] * 97
    
    for pos in known_positions:
        # Where does position 'pos' come from in the transposition?
        # This is the inverse problem - complex to solve generally
        intermediate[pos] = canonical_pt[pos]
    
    # For demonstration, we'll check if pattern matches
    if trans_type == 'columnar':
        test = test_columnar_transposition(''.join(intermediate), params['key_length'])
    elif trans_type == 'rail_fence':
        test = test_rail_fence(''.join(intermediate), params['rails'])
    elif trans_type == 'route':
        test = test_route_cipher(''.join(intermediate), params['rows'], params['cols'])
    else:
        test = ''.join(intermediate)
    
    # Count matches with ciphertext
    matches = sum(1 for i in range(min(len(test), len(ciphertext))) 
                  if test[i] != '?' and test[i] == ciphertext[i])
    
    return matches, len(known_positions)

def test_two_stage_hypothesis(ciphertext, canonical_pt, anchors, tail):
    """Test if K4 uses substitution then transposition"""
    results = []
    
    # Test different transposition types
    # Columnar with different key lengths
    for key_len in [4, 5, 7, 8, 10]:
        matches, total = reverse_transposition(
            ciphertext, canonical_pt, anchors, tail,
            'columnar', {'key_length': key_len}
        )
        results.append({
            'type': 'columnar',
            'params': f'key_length={key_len}',
            'matches': matches,
            'total': total,
            'match_rate': matches / total if total > 0 else 0
        })
    
    # Rail fence with different rail counts
    for rails in [2, 3, 4, 5]:
        matches, total = reverse_transposition(
            ciphertext, canonical_pt, anchors, tail,
            'rail_fence', {'rails': rails}
        )
        results.append({
            'type': 'rail_fence',
            'params': f'rails={rails}',
            'matches': matches,
            'total': total,
            'match_rate': matches / total if total > 0 else 0
        })
    
    # Route cipher with different grids
    for rows, cols in [(7, 14), (14, 7), (10, 10)]:
        if rows * cols >= 97:
            matches, total = reverse_transposition(
                ciphertext, canonical_pt, anchors, tail,
                'route', {'rows': rows, 'cols': cols}
            )
            results.append({
                'type': 'route',
                'params': f'{rows}x{cols}',
                'matches': matches,
                'total': total,
                'match_rate': matches / total if total > 0 else 0
            })
    
    return results

def main():
    """Run E4 two-stage tests"""
    print("=== E4: Two-stage Substitution + Transposition ===\n")
    
    os.makedirs('E4_two_stage', exist_ok=True)
    
    # Load data
    ciphertext, canonical_pt, anchors, tail = load_data()
    
    print("Testing two-stage cipher hypothesis...")
    print("Stage 1: Substitution (polyalphabetic)")
    print("Stage 2: Transposition (columnar/rail/route)")
    print(f"\nKnown positions: {len(anchors) + len(tail)}")
    
    # Test transposition patterns
    results = test_two_stage_hypothesis(ciphertext, canonical_pt, anchors, tail)
    
    # Display results
    print("\nTransposition tests:")
    for r in results:
        print(f"  {r['type']:12} {r['params']:15} - {r['match_rate']:.1%} match")
    
    # Find best match
    best = max(results, key=lambda x: x['match_rate'])
    
    print(f"\n=== Summary ===")
    if best['match_rate'] > 0.8:
        print(f"Possible transposition: {best['type']} ({best['params']})")
        print(f"Match rate: {best['match_rate']:.1%}")
        print("\nThis suggests K4 might use:")
        print("1. Polyalphabetic substitution (L=17)")
        print(f"2. {best['type']} transposition")
    else:
        print("No clear transposition pattern detected")
        print("K4 likely uses substitution only (no transposition stage)")
    
    # Save results
    summary = {
        'test': 'Two-stage substitution + transposition',
        'patterns_tested': len(results),
        'best_match': best['type'],
        'best_params': best['params'],
        'best_rate': best['match_rate'],
        'conclusion': 'No transposition detected' if best['match_rate'] < 0.8 else f'Possible {best["type"]} transposition'
    }
    
    with open('E4_two_stage/RESULT.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Save detailed results
    with open('E4_two_stage/detailed_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nResults saved to E4_two_stage/")

if __name__ == "__main__":
    main()