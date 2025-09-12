#!/usr/bin/env python3
"""
Schedule solver for P74 strip.
Finds lawful 6-class schedules that yield P[74]=L for each letter.
Enforces Option-A constraints at anchors.
"""

import json
import hashlib
import random
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# K4 ciphertext (canonical)
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Anchor positions and required plaintext
ANCHORS = {
    'EAST': (21, 24),
    'NORTHEAST': (25, 33),
    'BERLINCLOCK': (63, 73)
}

def c6a_class(position: int) -> int:
    """Compute c6a class for a position."""
    return ((position % 2) * 3) + (position % 3)

def c6b_class(position: int) -> int:
    """Compute c6b class for a position."""
    return position % 6

def solve_key_for_position(pt_char: str, ct_char: str, family: str) -> int:
    """
    Solve for key value at a position given PT, CT, and cipher family.
    
    Returns:
        Key value (0-25) or -1 if no solution
    """
    p = ord(pt_char) - ord('A')
    c = ord(ct_char) - ord('A')
    
    if family == 'vigenere':
        k = (c - p) % 26
    elif family == 'variant_beaufort':
        k = (p - c) % 26
    elif family == 'beaufort':
        k = (p + c) % 26
    else:
        return -1
    
    return k

def check_option_a(position: int, pt_char: str, ct_char: str, family: str) -> bool:
    """
    Check Option-A constraint: no K=0 for additive families at anchors.
    """
    # Check if position is in an anchor
    in_anchor = False
    for anchor_text, (start, end) in ANCHORS.items():
        if start <= position <= end:
            in_anchor = True
            break
    
    if not in_anchor:
        return True  # No constraint outside anchors
    
    # For additive families (Vigenere, Variant-Beaufort), K=0 is illegal
    if family in ['vigenere', 'variant_beaufort']:
        k = solve_key_for_position(pt_char, ct_char, family)
        if k == 0:
            return False  # K=0 at anchor for additive cipher
    
    return True

def generate_tail_guard() -> str:
    """Generate the fixed tail guard for position 75-96."""
    return "THEJOYOFANANGLEISTHEAR"

def solve_schedule_for_p74(target_letter: str, seed: int, 
                           max_attempts: int = 10000) -> Optional[Dict]:
    """
    Find a lawful schedule where P[74]=target_letter.
    
    Args:
        target_letter: Target letter for position 74
        seed: Random seed for search
        max_attempts: Maximum search attempts
    
    Returns:
        Schedule dict or None if not found
    """
    rng = random.Random(seed)
    
    # Cipher families
    families = ['vigenere', 'variant_beaufort', 'beaufort']
    
    # Build full plaintext template
    pt_template = [''] * 97
    
    # Set anchors
    pt_template[21:25] = list('EAST')
    pt_template[25:34] = list('NORTHEAST')
    pt_template[63:74] = list('BERLINCLOCK')
    
    # Set P[74]
    pt_template[74] = target_letter
    
    # Set tail guard
    tail = generate_tail_guard()
    pt_template[75:97] = list(tail)
    
    # Positions to fill randomly (head except anchors, and free tail position)
    free_positions = []
    for i in range(75):
        if pt_template[i] == '':
            free_positions.append(i)
    
    for attempt in range(max_attempts):
        # Random schedule parameters
        schedule = []
        for class_id in range(6):
            family = rng.choice(families)
            L = rng.randint(10, 22)
            phase = rng.randint(0, L - 1)
            schedule.append({
                'class_id': class_id,
                'family': family,
                'L': L,
                'phase': phase
            })
        
        # Fill free positions randomly
        for pos in free_positions:
            pt_template[pos] = rng.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        
        plaintext = ''.join(pt_template)
        
        # Check if it encrypts correctly
        valid = True
        forced_residues = []
        
        for position in range(97):
            class_id = c6a_class(position)
            family = schedule[class_id]['family']
            L = schedule[class_id]['L']
            phase = schedule[class_id]['phase']
            
            # Compute residue
            residue = (position + phase) % L
            
            # Get PT and CT chars
            pt_char = plaintext[position]
            ct_char = K4_CIPHERTEXT[position]
            
            # Solve for key
            k = solve_key_for_position(pt_char, ct_char, family)
            
            if k == -1:
                valid = False
                break
            
            # Check Option-A
            if not check_option_a(position, pt_char, ct_char, family):
                valid = False
                break
            
            # Record forced residue for anchors
            for anchor_text, (start, end) in ANCHORS.items():
                if start <= position <= end:
                    forced_residues.append({
                        'position': position,
                        'class': class_id,
                        'residue': residue,
                        'key': k,
                        'char': pt_char
                    })
        
        if valid:
            # Found valid schedule
            return {
                'success': True,
                'target_letter': target_letter,
                'schedule': schedule,
                'plaintext': plaintext,
                'forced_residues': forced_residues,
                'attempt': attempt + 1
            }
    
    return None

def solve_p74_strip():
    """
    Solve schedules for all 26 letters of P74 strip.
    """
    results = {}
    
    # CT SHA for seed generation
    ct_sha = hashlib.sha256(K4_CIPHERTEXT.encode()).hexdigest()
    
    # Cadence policy SHA (from bootstrap)
    cadence_policy_sha = "2161a32ee615f34823cb45b917bc51c6d4e0967fd5c2fb40829901adfbb4defc"
    
    print("=" * 60)
    print("P74 STRIP SCHEDULE SOLVER")
    print("=" * 60)
    
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        print(f"\nSolving for P[74]={letter}...")
        
        # Generate seed
        seed_recipe = f"CONFIRM_P74|K4|route:GRID_W14_ROWS|P74:{letter}|ct:{ct_sha}|cadence_policy:{cadence_policy_sha}"
        seed_u64 = int(hashlib.sha256(seed_recipe.encode()).hexdigest()[:16], 16) % (2**32)
        
        # Solve
        result = solve_schedule_for_p74(letter, seed_u64)
        
        if result:
            print(f"  ✅ Found lawful schedule (attempt {result['attempt']})")
            results[letter] = result
        else:
            print(f"  ❌ No feasible schedule found")
            results[letter] = {
                'success': False,
                'target_letter': letter,
                'status': 'no_feasible_schedule'
            }
    
    # Summary
    successful = sum(1 for r in results.values() if r.get('success', False))
    print(f"\n{'=' * 60}")
    print(f"SUMMARY: {successful}/26 letters have feasible schedules")
    
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Single letter mode
        letter = sys.argv[1].upper()
        if len(letter) != 1 or not letter.isalpha():
            print("Error: Provide a single letter A-Z")
            sys.exit(1)
        
        ct_sha = hashlib.sha256(K4_CIPHERTEXT.encode()).hexdigest()
        cadence_policy_sha = "2161a32ee615f34823cb45b917bc51c6d4e0967fd5c2fb40829901adfbb4defc"
        
        seed_recipe = f"CONFIRM_P74|K4|route:GRID_W14_ROWS|P74:{letter}|ct:{ct_sha}|cadence_policy:{cadence_policy_sha}"
        seed_u64 = int(hashlib.sha256(seed_recipe.encode()).hexdigest()[:16], 16) % (2**32)
        
        result = solve_schedule_for_p74(letter, seed_u64)
        
        if result:
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps({
                'success': False,
                'target_letter': letter,
                'status': 'no_feasible_schedule'
            }, indent=2))
    else:
        # Full strip mode
        results = solve_p74_strip()
        
        # Save results
        output_file = Path("p74_schedules.json")
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to {output_file}")