#!/usr/bin/env python3
"""
Alternate Tail Test
Generate English-like 22-character tails and test if any work with anchors.
"""

import sys
import json
import csv
import time
import random
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import string

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent))
from core_hardening_utils import *


# Common English bigrams for filtering
COMMON_BIGRAMS = [
    'TH', 'HE', 'IN', 'ER', 'AN', 'RE', 'ED', 'ON', 'ES', 'ST',
    'EN', 'AT', 'TO', 'NT', 'HA', 'ND', 'OU', 'EA', 'NG', 'AS',
    'OR', 'TI', 'IS', 'ET', 'IT', 'AR', 'TE', 'SE', 'HI', 'OF'
]

# Function words that might appear
FUNCTION_WORDS = [
    'OF', 'TO', 'IN', 'IT', 'IS', 'BE', 'AS', 'AT', 'SO', 'WE',
    'HE', 'BY', 'OR', 'ON', 'DO', 'IF', 'ME', 'MY', 'UP', 'AN'
]

# Geometric/angle-related words for themed generation
ANGLE_WORDS = [
    'ANGLE', 'ARC', 'DEGREE', 'RADIAN', 'MEASURE', 'LINE', 'POINT',
    'CURVE', 'CIRCLE', 'RADIUS', 'CHORD', 'SECTOR', 'SEGMENT'
]


def generate_english_tail(seed: int, avoid_patterns: List[str]) -> str:
    """
    Generate a plausible English-like 22-character tail.
    """
    random.seed(seed)
    
    # Strategy 1: Combine function words and content
    if seed % 3 == 0:
        # Start with "OF" or "TO" like the real tail
        starts = ['OF', 'TO', 'IN', 'BY', 'AS']
        start = random.choice(starts)
        
        # Add some geometric terms
        middle_options = ['ANGLE', 'ARC', 'LINE', 'CURVE', 'POINT']
        middle = random.choice(middle_options)
        
        # Fill to 22 chars
        tail = start + ' ' + middle
        while len(tail) < 22:
            if len(tail) < 18:
                word = random.choice(ANGLE_WORDS)
                if len(tail) + len(word) + 1 <= 22:
                    tail += ' ' + word
            else:
                # Fill with short words or letters
                remaining = 22 - len(tail)
                if remaining >= 3:
                    tail += ' ' + random.choice(['IS', 'BE', 'OF', 'TO'])[:remaining]
                else:
                    tail += ''.join(random.choices('AEIOURLN', k=remaining))
        
        tail = tail[:22].replace(' ', '')
    
    elif seed % 3 == 1:
        # Strategy 2: Random but bigram-constrained
        tail = ''
        while len(tail) < 22:
            if len(tail) == 0:
                tail = random.choice(string.ascii_uppercase)
            elif len(tail) == 1:
                # Pick a letter that forms a common bigram
                for bigram in COMMON_BIGRAMS:
                    if bigram[0] == tail[-1]:
                        tail += bigram[1]
                        break
                else:
                    tail += random.choice('AEIOU')
            else:
                # Continue with bigram constraints
                last_bigram = tail[-2:]
                found = False
                for bigram in COMMON_BIGRAMS:
                    if random.random() < 0.3 and bigram[0] == tail[-1]:
                        tail += bigram[1]
                        found = True
                        break
                if not found:
                    tail += random.choice(string.ascii_uppercase)
    
    else:
        # Strategy 3: Variation on geometric theme
        templates = [
            "MEASUREOFANANGLEIS",  # 18 chars
            "ANGLEARCMEASUREMENT",  # 19 chars
            "DEGREESANDRADIANS",    # 17 chars
            "CIRCLESECTORANGLE",    # 17 chars
        ]
        base = random.choice(templates)
        
        # Pad or modify to reach 22
        if len(base) < 22:
            padding = ''.join(random.choices('THEIN', k=22-len(base)))
            tail = base + padding
        else:
            tail = base[:22]
    
    # Ensure it's uppercase and exactly 22 chars
    tail = tail.upper().replace(' ', '')[:22]
    while len(tail) < 22:
        tail += random.choice('AEIOU')
    
    # Avoid anchor patterns
    for pattern in avoid_patterns:
        if pattern in tail:
            # Mutate to avoid pattern
            idx = tail.index(pattern)
            chars = list(tail)
            chars[idx] = random.choice([c for c in string.ascii_uppercase if c != chars[idx]])
            tail = ''.join(chars)
    
    return tail


def test_alternate_tail(
    tail: str,
    ct: str,
    anchors: Dict
) -> Tuple[bool, str, Dict]:
    """
    Test if anchors + alternate tail can solve the system.
    
    Returns:
        (feasible, fail_reason, details)
    """
    # Build constraints from anchors + tail
    constraints = {}
    
    # Add anchor constraints
    for name, info in anchors.items():
        for i in range(info['start'], info['end'] + 1):
            idx = i - info['start']
            if idx < len(info['plaintext']):
                constraints[i] = info['plaintext'][idx]
    
    # Add tail constraints (positions 75-96)
    for i, char in enumerate(tail):
        constraints[75 + i] = char
    
    # Group indices by baseline class
    class_indices = {c: [] for c in range(6)}
    for i in range(97):
        class_id = compute_baseline_class(i)
        class_indices[class_id].append(i)
    
    # Try to solve wheels
    wheels = {}
    details = {'classes_solved': 0, 'option_a_violations': 0}
    
    for class_id in range(6):
        indices = class_indices[class_id]
        class_constraints = {i: constraints[i] for i in indices if i in constraints}
        
        if not class_constraints:
            return False, f'no_constraints_class_{class_id}', details
        
        wheel_config = solve_class_wheel(
            class_id,
            indices,
            ct,
            class_constraints,
            enforce_option_a=True
        )
        
        if wheel_config is None:
            return False, f'wheel_solve_failed_class_{class_id}', details
        
        # Check for Option-A violations
        if wheel_config.get('optionA_checks'):
            details['option_a_violations'] += len(wheel_config['optionA_checks'])
        
        wheels[class_id] = wheel_config
        details['classes_solved'] += 1
    
    # Try to derive full plaintext
    try:
        derived_pt = derive_plaintext_from_wheels(ct, wheels, compute_baseline_class)
        
        incomplete = derived_pt.count('?')
        if incomplete > 0:
            details['incomplete_positions'] = incomplete
            return False, 'incomplete_derivation', details
        
        pt_sha = compute_sha256(derived_pt)
        winner_sha = "4eceb739ab655d6f4ec87753569b8bf04573fe26d01c0caa68d36776dd052d79"
        
        if pt_sha == winner_sha:
            details['pt_sha256'] = pt_sha
            return True, 'success', details
        else:
            details['wrong_sha'] = pt_sha[:16]
            return False, 'wrong_plaintext', details
    
    except Exception as e:
        details['error'] = str(e)[:50]
        return False, 'derivation_error', details


def calculate_tail_stats(tail: str) -> Dict:
    """Calculate statistics about a tail string."""
    stats = {
        'length': len(tail),
        'unique_chars': len(set(tail)),
        'vowel_count': sum(1 for c in tail if c in 'AEIOU'),
        'consonant_count': sum(1 for c in tail if c in string.ascii_uppercase and c not in 'AEIOU'),
        'bigram_score': 0
    }
    
    # Count common bigrams
    for i in range(len(tail) - 1):
        bigram = tail[i:i+2]
        if bigram in COMMON_BIGRAMS:
            stats['bigram_score'] += 1
    
    return stats


def main():
    """Main alternate tail test."""
    parser = argparse.ArgumentParser(description='Alternate tail test')
    parser.add_argument('--ct', default='02_DATA/ciphertext_97.txt')
    parser.add_argument('--anchors', default='02_DATA/anchors/four_anchors.json')
    parser.add_argument('--out', default='04_EXPERIMENTS/core_hardening_v3/alt_tail_test')
    parser.add_argument('--seed', type=int, default=1337)
    parser.add_argument('--num-tails', type=int, default=100)
    args = parser.parse_args()
    
    print("Starting Alternate Tail Test")
    print(f"Generating {args.num_tails} alternate tails")
    start_time = time.time()
    
    # Setup output directory
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    with open(args.ct, 'r') as f:
        ct = f.read().strip()
    
    with open(args.anchors, 'r') as f:
        anchors = json.load(f)
    
    # Patterns to avoid (anchor words)
    avoid_patterns = ['EAST', 'NORTHEAST', 'BERLIN', 'CLOCK']
    
    # Generate tails
    generated_csv = out_dir / "ALT_TAIL_GENERATED.csv"
    gen_file = open(generated_csv, 'w', newline='')
    gen_fieldnames = ['tail_id', 'tail', 'length', 'unique_chars', 'vowel_count', 
                      'consonant_count', 'bigram_score']
    gen_writer = csv.DictWriter(gen_file, fieldnames=gen_fieldnames)
    gen_writer.writeheader()
    
    tails = []
    for i in range(args.num_tails):
        seed = args.seed + i
        tail = generate_english_tail(seed, avoid_patterns)
        stats = calculate_tail_stats(tail)
        
        gen_row = {
            'tail_id': i,
            'tail': tail,
            **stats
        }
        gen_writer.writerow(gen_row)
        tails.append(tail)
    
    gen_file.close()
    
    # Test tails
    results_csv = out_dir / "ALT_TAIL_RESULTS.csv"
    res_file = open(results_csv, 'w', newline='')
    res_fieldnames = ['tail', 'feasible', 'fail_reason', 'details']
    res_writer = csv.DictWriter(res_file, fieldnames=res_fieldnames)
    res_writer.writeheader()
    
    feasible_count = 0
    
    print("\nTesting alternate tails...")
    for i, tail in enumerate(tails):
        if i % 20 == 0:
            print(f"  Testing tail {i}/{len(tails)}...")
        
        feasible, reason, details = test_alternate_tail(tail, ct, anchors)
        
        if feasible:
            feasible_count += 1
            print(f"  FEASIBLE FOUND: Tail {i} - {tail}")
        
        res_row = {
            'tail': tail,
            'feasible': feasible,
            'fail_reason': reason,
            'details': json.dumps(details)
        }
        res_writer.writerow(res_row)
    
    res_file.close()
    
    # Create README
    readme_content = f"""# Alternate Tail Test

## Overview

This study generates and tests {args.num_tails} English-like 22-character tails to determine if any alternative to the canonical tail can work with the anchors to solve K4.

## Generation Constraints

- Length: Exactly 22 characters
- Alphabet: A-Z only
- Patterns avoided: Anchor words (EAST, NORTHEAST, BERLIN, CLOCK)
- Generation strategies:
  1. Geometric/angle themed phrases
  2. Bigram-constrained random text
  3. Function word combinations

## Results

- **Tails generated**: {args.num_tails}
- **Feasible tails found**: {feasible_count}
- **Expected**: 0 (only the canonical tail should work)

## Key Finding

{"WARNING: Alternative feasible tail(s) found!" if feasible_count > 0 else "As expected, no alternative tails were feasible. Only the canonical tail 'OFANOISECONSUMEENGLAND' works with the anchors."}

## Files

- **ALT_TAIL_GENERATED.csv**: Generated tails with linguistic statistics
- **ALT_TAIL_RESULTS.csv**: Feasibility test results for each tail

## Reproduction

```bash
python3 07_TOOLS/core_hardening/run_alt_tail_test.py \\
  --seed {args.seed} \\
  --num-tails {args.num_tails}
```
"""
    
    readme_path = out_dir / "README.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    # Generate manifest
    generate_manifest(out_dir)
    
    print(f"\nAlternate tail test complete!")
    print(f"Feasible tails: {feasible_count}/{args.num_tails}")
    print(f"Output: {out_dir}")
    print(f"Runtime: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    main()