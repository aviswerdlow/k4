#!/usr/bin/env python3
"""
E1 - Mechanism switch at position 74
Test if tail (74-96) uses a different cipher family than head
"""

import json
import os
import hashlib
from typing import Dict, List, Optional, Tuple

MASTER_SEED = 1337

# Fixed keyword set for non-polyalphabetic ciphers
KEYWORDS = ['KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'SANBORN']

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

def test_monoalphabetic_tail(ciphertext, canonical_pt, tail):
    """Test if tail uses simple monoalphabetic substitution"""
    # Build mapping from tail constraints
    mapping = {}
    conflicts = 0
    
    for pos in tail:
        c_char = ciphertext[pos]
        p_char = canonical_pt[pos]
        
        if c_char in mapping:
            if mapping[c_char] != p_char:
                conflicts += 1
        else:
            mapping[c_char] = p_char
    
    return {
        'type': 'monoalphabetic',
        'mapping_size': len(mapping),
        'conflicts': conflicts,
        'valid': conflicts == 0,
        'mapping': mapping if conflicts == 0 else None
    }

def generate_playfair_square(keyword):
    """Generate 5x5 Playfair square from keyword"""
    # Remove J (combine with I)
    alphabet = 'ABCDEFGHIKLMNOPQRSTUVWXYZ'
    
    # Build key square
    used = set()
    square = []
    
    # Add keyword letters
    for c in keyword.upper():
        if c == 'J':
            c = 'I'
        if c in alphabet and c not in used:
            square.append(c)
            used.add(c)
    
    # Add remaining letters
    for c in alphabet:
        if c not in used:
            square.append(c)
    
    # Convert to 5x5 grid
    grid = []
    for i in range(5):
        grid.append(square[i*5:(i+1)*5])
    
    return grid

def find_in_square(grid, letter):
    """Find position of letter in Playfair square"""
    if letter == 'J':
        letter = 'I'
    
    for r in range(5):
        for c in range(5):
            if grid[r][c] == letter:
                return r, c
    return None, None

def decrypt_playfair_pair(c1, c2, grid):
    """Decrypt a Playfair digraph"""
    r1, col1 = find_in_square(grid, c1)
    r2, col2 = find_in_square(grid, c2)
    
    if r1 is None or r2 is None:
        return None, None
    
    if r1 == r2:
        # Same row - shift left
        p1 = grid[r1][(col1 - 1) % 5]
        p2 = grid[r2][(col2 - 1) % 5]
    elif col1 == col2:
        # Same column - shift up
        p1 = grid[(r1 - 1) % 5][col1]
        p2 = grid[(r2 - 1) % 5][col2]
    else:
        # Rectangle - swap columns
        p1 = grid[r1][col2]
        p2 = grid[r2][col1]
    
    return p1, p2

def test_playfair_tail(ciphertext, canonical_pt, tail, keyword):
    """Test if tail uses Playfair with given keyword"""
    grid = generate_playfair_square(keyword)
    
    # Process tail in pairs
    matches = 0
    total = 0
    
    for i in range(0, len(tail) - 1, 2):
        pos1, pos2 = tail[i], tail[i + 1]
        
        c1 = ciphertext[pos1]
        c2 = ciphertext[pos2]
        
        p1_expected = canonical_pt[pos1]
        p2_expected = canonical_pt[pos2]
        
        p1_derived, p2_derived = decrypt_playfair_pair(c1, c2, grid)
        
        total += 2
        if p1_derived == p1_expected:
            matches += 1
        if p2_derived == p2_expected:
            matches += 1
    
    return {
        'type': 'playfair',
        'keyword': keyword,
        'matches': matches,
        'total': total,
        'valid': matches == total
    }

def test_straddling_checkerboard_tail(ciphertext, canonical_pt, tail):
    """Test if tail uses straddling checkerboard"""
    # Use standard ETAOIN board
    board = {
        '0': 'E', '1': 'T', '2': 'A', '3': 'O', '4': 'I', '5': 'N',
        '6': 'S', '7': 'H', '8': 'R', '9': 'D',
        '20': 'L', '21': 'U', '22': 'C', '23': 'M', '24': 'W',
        '25': 'F', '26': 'Y', '27': 'G', '28': 'P', '29': 'B',
        '30': 'V', '31': 'K', '32': 'Q', '33': 'J', '34': 'X', '35': 'Z'
    }
    
    # Reverse mapping
    char_to_code = {v: k for k, v in board.items()}
    
    # Check if tail can be encoded/decoded
    matches = 0
    for pos in tail:
        p_char = canonical_pt[pos]
        if p_char in char_to_code:
            # This is a simplified test - real checkerboard would need digit stream
            matches += 1
    
    return {
        'type': 'checkerboard',
        'board': 'ETAOIN',
        'matches': matches,
        'total': len(tail),
        'valid': False  # Simplified - would need full implementation
    }

def explain_tail_mechanism(mechanism, pos, c_char, p_char):
    """Explain how tail mechanism works at a position"""
    explanation = f"""
Tail Position {pos} Explanation:
================================
Mechanism: {mechanism['type']}
Ciphertext: '{c_char}'
Plaintext: '{p_char}'
"""
    
    if mechanism['type'] == 'monoalphabetic':
        explanation += f"""
Simple substitution: C['{c_char}'] → P['{p_char}']
Mapping size: {mechanism['mapping_size']} unique substitutions
"""
    elif mechanism['type'] == 'playfair':
        explanation += f"""
Playfair with keyword: {mechanism['keyword']}
(Digraph decryption - see full square in documentation)
"""
    
    return explanation

def main():
    """Run E1 tail switch tests"""
    print("=== E1: Mechanism Switch at Position 74 ===\n")
    
    os.makedirs('E1_tail_switch', exist_ok=True)
    
    # Load data
    ciphertext, canonical_pt, anchors, tail = load_data()
    
    print(f"Testing tail positions: {tail[0]}-{tail[-1]} ({len(tail)} letters)")
    print(f"Tail plaintext: {canonical_pt[tail[0]:tail[-1]+1]}")
    
    results = []
    
    # Test 1: Monoalphabetic
    print("\n1. Testing monoalphabetic substitution...")
    mono_result = test_monoalphabetic_tail(ciphertext, canonical_pt, tail)
    print(f"   Mapping size: {mono_result['mapping_size']}")
    print(f"   Conflicts: {mono_result['conflicts']}")
    print(f"   Valid: {mono_result['valid']}")
    results.append(mono_result)
    
    if mono_result['valid']:
        # Save monoalphabetic results
        os.makedirs('E1_tail_switch/monoalphabetic', exist_ok=True)
        
        with open('E1_tail_switch/monoalphabetic/RESULT.json', 'w') as f:
            json.dump(mono_result, f, indent=2)
        
        # Explain one position
        pos = tail[0]
        explanation = explain_tail_mechanism(
            mono_result, pos,
            ciphertext[pos], canonical_pt[pos]
        )
        
        with open('E1_tail_switch/monoalphabetic/EXPLAIN_IDX.txt', 'w') as f:
            f.write(explanation)
    
    # Test 2: Playfair with various keywords
    print("\n2. Testing Playfair...")
    for keyword in KEYWORDS:
        playfair_result = test_playfair_tail(ciphertext, canonical_pt, tail, keyword)
        print(f"   {keyword}: {playfair_result['matches']}/{playfair_result['total']} matches")
        
        if playfair_result['valid']:
            os.makedirs(f'E1_tail_switch/playfair_{keyword}', exist_ok=True)
            
            with open(f'E1_tail_switch/playfair_{keyword}/RESULT.json', 'w') as f:
                json.dump(playfair_result, f, indent=2)
        
        results.append(playfair_result)
    
    # Test 3: Straddling checkerboard
    print("\n3. Testing straddling checkerboard...")
    checker_result = test_straddling_checkerboard_tail(ciphertext, canonical_pt, tail)
    print(f"   Matches: {checker_result['matches']}/{checker_result['total']}")
    results.append(checker_result)
    
    # Summary
    print("\n=== Summary ===")
    valid_mechanisms = [r for r in results if r.get('valid', False)]
    
    if valid_mechanisms:
        print(f"Found {len(valid_mechanisms)} valid tail mechanism(s):")
        for mech in valid_mechanisms:
            print(f"  - {mech['type']}")
            if mech['type'] == 'playfair':
                print(f"    Keyword: {mech['keyword']}")
    else:
        print("No simple tail mechanism found that perfectly reproduces the tail")
        print("The tail likely uses the same L=17 polyalphabetic as the head")
    
    # Save overall summary
    summary = {
        'tail_positions': tail,
        'tail_text': canonical_pt[tail[0]:tail[-1]+1],
        'mechanisms_tested': len(results),
        'valid_mechanisms': len(valid_mechanisms),
        'conclusion': 'Tail uses different mechanism' if valid_mechanisms else 'Tail uses same L=17 as head'
    }
    
    with open('E1_tail_switch/SUMMARY.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\nResults saved to E1_tail_switch/")

if __name__ == "__main__":
    main()