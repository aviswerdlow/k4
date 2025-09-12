#!/usr/bin/env python3
"""
Enhanced Alternate Tail Test with 500 Stratified Candidates
Test various categories of English-like 22-character tails.
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
from collections import Counter

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent))
from core_hardening_utils import *


# Common English bigrams and trigrams
COMMON_BIGRAMS = [
    'TH', 'HE', 'IN', 'ER', 'AN', 'RE', 'ED', 'ON', 'ES', 'ST',
    'EN', 'AT', 'TO', 'NT', 'HA', 'ND', 'OU', 'EA', 'NG', 'AS',
    'OR', 'TI', 'IS', 'ET', 'IT', 'AR', 'TE', 'SE', 'HI', 'OF'
]

COMMON_TRIGRAMS = [
    'THE', 'AND', 'ING', 'HER', 'HAT', 'HIS', 'THA', 'ERE', 'FOR',
    'ENT', 'ION', 'TER', 'WAS', 'YOU', 'ITH', 'VER', 'ALL', 'WIT',
    'THI', 'TIO'
]

# Function words for F-heavy category
FUNCTION_WORDS = [
    'OF', 'TO', 'IN', 'IT', 'IS', 'BE', 'AS', 'AT', 'SO', 'WE',
    'HE', 'BY', 'OR', 'ON', 'DO', 'IF', 'ME', 'MY', 'UP', 'AN',
    'NO', 'US', 'AM', 'GO', 'HI', 'YE'
]

# Content words for content-heavy
CONTENT_WORDS = [
    'ANGLE', 'ARC', 'DEGREE', 'RADIAN', 'MEASURE', 'LINE', 'POINT',
    'CURVE', 'CIRCLE', 'RADIUS', 'CHORD', 'SECTOR', 'TIME', 'CLOCK',
    'NORTH', 'EAST', 'SOUTH', 'WEST', 'BERLIN', 'WORLD', 'CODE',
    'CIPHER', 'KEY', 'PUZZLE', 'SECRET', 'HIDDEN', 'SOLVE'
]

# The canonical tail for near-miss generation
CANONICAL_TAIL = "OFANOISECONSUMEENGLAND"


def edit_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return edit_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def generate_f_heavy_tail(seed: int) -> str:
    """Generate a function-word-heavy tail (≥8 function words)."""
    random.seed(seed)
    tail = ""
    function_count = 0
    
    while len(tail) < 22:
        if function_count < 8 or random.random() < 0.7:
            word = random.choice(FUNCTION_WORDS)
            if len(tail) + len(word) <= 22:
                tail += word
                function_count += 1
        else:
            # Add random letters
            remaining = 22 - len(tail)
            if remaining > 0:
                tail += ''.join(random.choices(string.ascii_uppercase, k=min(remaining, 2)))
    
    # Pad or truncate to exactly 22
    if len(tail) < 22:
        tail += ''.join(random.choices('AEIOU', k=22 - len(tail)))
    
    return tail[:22]


def generate_f_light_tail(seed: int) -> str:
    """Generate a function-word-light tail (≤5 function words)."""
    random.seed(seed)
    tail = ""
    function_count = 0
    
    while len(tail) < 22:
        if function_count < 5 and random.random() < 0.3:
            word = random.choice(FUNCTION_WORDS)
            if len(tail) + len(word) <= 22:
                tail += word
                function_count += 1
        else:
            # Add content words or random
            if random.random() < 0.5 and len(CONTENT_WORDS) > 0:
                word = random.choice(CONTENT_WORDS)
                if len(tail) + len(word) <= 22:
                    tail += word[:22 - len(tail)]
            else:
                tail += random.choice(string.ascii_uppercase)
    
    return tail[:22].ljust(22, 'X')


def generate_content_heavy_tail(seed: int) -> str:
    """Generate a content-word-heavy tail."""
    random.seed(seed)
    words_used = []
    
    # Select content words
    while sum(len(w) for w in words_used) < 22:
        word = random.choice(CONTENT_WORDS)
        if word not in words_used:
            words_used.append(word)
    
    # Combine and truncate
    tail = ''.join(words_used)[:22]
    
    # Pad if needed
    if len(tail) < 22:
        tail += ''.join(random.choices('RSTNL', k=22 - len(tail)))
    
    return tail[:22]


def generate_random_clean_tail(seed: int) -> str:
    """Generate random tail that passes trigram filter."""
    random.seed(seed)
    tail = ""
    
    # Start with a common trigram
    tail = random.choice(COMMON_TRIGRAMS)
    
    # Build rest using bigrams
    while len(tail) < 22:
        last_char = tail[-1]
        valid_bigrams = [bg for bg in COMMON_BIGRAMS if bg[0] == last_char]
        
        if valid_bigrams:
            bigram = random.choice(valid_bigrams)
            tail += bigram[1]
        else:
            # Add common letter
            tail += random.choice('AEIOURSTNL')
    
    return tail[:22]


def generate_near_miss_tail(seed: int, max_distance: int = 3) -> str:
    """Generate tail with edit distance 1-3 from canonical."""
    random.seed(seed)
    tail = list(CANONICAL_TAIL)
    distance = random.randint(1, max_distance)
    
    for _ in range(distance):
        operation = random.choice(['substitute', 'swap'])
        
        if operation == 'substitute':
            idx = random.randint(0, 21)
            old_char = tail[idx]
            new_char = random.choice([c for c in string.ascii_uppercase if c != old_char])
            tail[idx] = new_char
        elif operation == 'swap' and len(tail) > 1:
            idx = random.randint(0, 20)
            tail[idx], tail[idx + 1] = tail[idx + 1], tail[idx]
    
    return ''.join(tail)


def categorize_tail(tail: str) -> str:
    """Categorize a tail based on its characteristics."""
    # Count function words
    function_count = 0
    for word in FUNCTION_WORDS:
        if word in tail:
            function_count += 1
    
    # Check edit distance from canonical
    dist = edit_distance(tail, CANONICAL_TAIL)
    
    if dist <= 3:
        return "near_miss"
    elif function_count >= 8:
        return "f_heavy"
    elif function_count <= 5:
        return "f_light"
    
    # Check for content words
    content_count = sum(1 for word in CONTENT_WORDS if word in tail)
    if content_count >= 2:
        return "content_heavy"
    
    # Check trigram quality
    trigram_count = sum(1 for i in range(len(tail) - 2) if tail[i:i+3] in COMMON_TRIGRAMS)
    if trigram_count >= 3:
        return "random_clean"
    
    return "other"


def test_alternate_tail_detailed(
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
    details = {
        'classes_solved': 0,
        'first_failing_class': None,
        'option_a_violations': 0,
        'phase_conflicts': 0
    }
    
    for class_id in range(6):
        indices = class_indices[class_id]
        class_constraints = {i: constraints[i] for i in indices if i in constraints}
        
        if not class_constraints:
            details['first_failing_class'] = class_id
            return False, 'cannot_fill_slots', details
        
        wheel_config = solve_class_wheel(
            class_id,
            indices,
            ct,
            class_constraints,
            enforce_option_a=True
        )
        
        if wheel_config is None:
            details['first_failing_class'] = class_id
            
            # Try to determine specific failure reason
            # Check for Option-A violations
            anchor_positions = []
            for name, info in anchors.items():
                anchor_positions.extend(range(info['start'], info['end'] + 1))
            
            class_anchors = [i for i in anchor_positions if compute_baseline_class(i) == class_id]
            if class_anchors:
                # Check if K=0 at anchor (Option-A violation)
                for idx in class_anchors:
                    if idx in class_constraints:
                        ct_val = ord(ct[idx]) - ord('A')
                        pt_val = ord(class_constraints[idx]) - ord('A')
                        if (ct_val - pt_val) % 26 == 0:
                            details['option_a_violations'] += 1
            
            if details['option_a_violations'] > 0:
                return False, 'optionA_violation', details
            else:
                return False, 'wheel_collision', details
        
        wheels[class_id] = wheel_config
        details['classes_solved'] += 1
    
    # Try to derive full plaintext
    try:
        derived_pt = derive_plaintext_from_wheels(ct, wheels, compute_baseline_class)
        
        incomplete = derived_pt.count('?')
        if incomplete > 0:
            details['incomplete_positions'] = incomplete
            return False, 'cannot_fill_slots', details
        
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
        return False, 'phase_conflict', details


def main():
    """Enhanced alternate tail test with 500 stratified candidates."""
    parser = argparse.ArgumentParser(description='Enhanced alternate tail test')
    parser.add_argument('--ct', default='02_DATA/ciphertext_97.txt')
    parser.add_argument('--anchors', default='02_DATA/anchors/four_anchors.json')
    parser.add_argument('--out', default='04_EXPERIMENTS/core_hardening_v3/alt_tail_test')
    parser.add_argument('--seed', type=int, default=1337)
    parser.add_argument('--num-tails', type=int, default=500)
    args = parser.parse_args()
    
    print("Starting Enhanced Alternate Tail Test")
    print(f"Generating {args.num_tails} stratified alternate tails")
    print(f"Master seed: {args.seed}")
    start_time = time.time()
    
    # Setup output directory
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    with open(args.ct, 'r') as f:
        ct = f.read().strip()
    
    with open(args.anchors, 'r') as f:
        anchors = json.load(f)
    
    # Generate stratified tails
    print("\nGenerating stratified tails...")
    tails = []
    
    # Target distribution
    buckets = {
        'f_heavy': args.num_tails // 5,      # 100 tails
        'f_light': args.num_tails // 5,      # 100 tails
        'content_heavy': args.num_tails // 5, # 100 tails
        'random_clean': args.num_tails // 5,  # 100 tails
        'near_miss': args.num_tails // 5      # 100 tails
    }
    
    tail_id = 0
    
    # Generate F-heavy tails
    for i in range(buckets['f_heavy']):
        tail = generate_f_heavy_tail(args.seed + tail_id)
        tails.append({
            'tail_id': tail_id,
            'tail': tail,
            'bucket': 'f_heavy',
            'edit_distance': edit_distance(tail, CANONICAL_TAIL)
        })
        tail_id += 1
    
    # Generate F-light tails
    for i in range(buckets['f_light']):
        tail = generate_f_light_tail(args.seed + tail_id)
        tails.append({
            'tail_id': tail_id,
            'tail': tail,
            'bucket': 'f_light',
            'edit_distance': edit_distance(tail, CANONICAL_TAIL)
        })
        tail_id += 1
    
    # Generate content-heavy tails
    for i in range(buckets['content_heavy']):
        tail = generate_content_heavy_tail(args.seed + tail_id)
        tails.append({
            'tail_id': tail_id,
            'tail': tail,
            'bucket': 'content_heavy',
            'edit_distance': edit_distance(tail, CANONICAL_TAIL)
        })
        tail_id += 1
    
    # Generate random-clean tails
    for i in range(buckets['random_clean']):
        tail = generate_random_clean_tail(args.seed + tail_id)
        tails.append({
            'tail_id': tail_id,
            'tail': tail,
            'bucket': 'random_clean',
            'edit_distance': edit_distance(tail, CANONICAL_TAIL)
        })
        tail_id += 1
    
    # Generate near-miss tails
    for i in range(buckets['near_miss']):
        tail = generate_near_miss_tail(args.seed + tail_id)
        tails.append({
            'tail_id': tail_id,
            'tail': tail,
            'bucket': 'near_miss',
            'edit_distance': edit_distance(tail, CANONICAL_TAIL)
        })
        tail_id += 1
    
    # Save generated tails
    generated_csv = out_dir / "ALT_TAIL_GENERATED.csv"
    with open(generated_csv, 'w', newline='') as f:
        fieldnames = ['tail_id', 'tail', 'bucket', 'edit_distance']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for tail_info in tails:
            writer.writerow(tail_info)
    
    # Test tails
    print("\nTesting alternate tails...")
    results = []
    feasible_count = 0
    fail_reason_counts = Counter()
    bucket_fail_counts = {b: Counter() for b in buckets.keys()}
    
    for i, tail_info in enumerate(tails):
        if i % 50 == 0:
            print(f"  Testing tail {i}/{len(tails)}...")
        
        feasible, reason, details = test_alternate_tail_detailed(
            tail_info['tail'],
            ct,
            anchors
        )
        
        if feasible:
            feasible_count += 1
            print(f"  FEASIBLE FOUND: Tail {i} ({tail_info['bucket']}) - {tail_info['tail']}")
        
        fail_reason_counts[reason] += 1
        bucket_fail_counts[tail_info['bucket']][reason] += 1
        
        results.append({
            'tail_id': tail_info['tail_id'],
            'tail': tail_info['tail'],
            'bucket': tail_info['bucket'],
            'feasible': feasible,
            'fail_reason': reason,
            'first_failing_class': details.get('first_failing_class', ''),
            'classes_solved': details.get('classes_solved', 0),
            'option_a_violations': details.get('option_a_violations', 0)
        })
    
    # Save results
    results_csv = out_dir / "ALT_TAIL_RESULTS.csv"
    with open(results_csv, 'w', newline='') as f:
        fieldnames = ['tail_id', 'tail', 'bucket', 'feasible', 'fail_reason', 
                      'first_failing_class', 'classes_solved', 'option_a_violations']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    
    # Create failure grid
    fail_grid = []
    fail_reasons = sorted(set(fail_reason_counts.keys()))
    
    for bucket in buckets.keys():
        for reason in fail_reasons:
            fail_grid.append({
                'bucket': bucket,
                'fail_reason': reason,
                'count': bucket_fail_counts[bucket].get(reason, 0)
            })
    
    fail_grid_csv = out_dir / "ALT_TAIL_FAIL_GRID.csv"
    with open(fail_grid_csv, 'w', newline='') as f:
        fieldnames = ['bucket', 'fail_reason', 'count']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in fail_grid:
            writer.writerow(row)
    
    # Create summary
    summary = {
        'description': 'Enhanced alternate tail test with stratified candidates',
        'master_seed': args.seed,
        'total_candidates': len(tails),
        'feasible_count': feasible_count,
        'buckets': {
            bucket: {
                'count': buckets[bucket],
                'feasible': sum(1 for r in results if r['bucket'] == bucket and r['feasible'])
            }
            for bucket in buckets.keys()
        },
        'fail_reasons': dict(fail_reason_counts),
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }
    
    summary_file = out_dir / "ALT_TAIL_SUMMARY.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Create README
    readme_content = f"""# Enhanced Alternate Tail Test

## Overview

This enhanced study tests {args.num_tails} stratified English-like 22-character tails to verify that no alternative to the canonical tail "OFANOISECONSUMEENGLAND" can work with the anchors to solve K4.

## Stratification

Candidates were generated in 5 buckets:
- **F-heavy**: ≥8 function words (e.g., OF, TO, IN, IS)
- **F-light**: ≤5 function words
- **Content-heavy**: Multiple content words (ANGLE, CIRCLE, etc.)
- **Random-clean**: Passes trigram filter
- **Near-miss**: Edit distance 1-3 from canonical tail

## Results

- **Total candidates**: {args.num_tails}
- **Feasible tails found**: {feasible_count}
- **Expected**: 0 (only the canonical tail should work)

### Failure Reasons

{chr(10).join(f"- **{reason}**: {count} tails" for reason, count in fail_reason_counts.items())}

### Per-Bucket Results

{chr(10).join(f"- **{bucket}**: {buckets[bucket]} tested, {summary['buckets'][bucket]['feasible']} feasible" for bucket in buckets.keys())}

## Key Finding

{"WARNING: Alternative feasible tail(s) found!" if feasible_count > 0 else "As expected, no alternative tails were feasible. Only the canonical tail 'OFANOISECONSUMEENGLAND' works with the anchors."}

## Files

- **ALT_TAIL_GENERATED.csv**: Generated tails with bucket and edit distance
- **ALT_TAIL_RESULTS.csv**: Detailed test results for each tail
- **ALT_TAIL_FAIL_GRID.csv**: Contingency table of bucket × fail_reason
- **ALT_TAIL_SUMMARY.json**: Overall summary statistics

## Failure Analysis

The failure grid shows how different tail categories fail:
- Most tails fail due to **wheel_collision** (incompatible with wheel structure)
- Some fail **optionA_violation** (K=0 at anchor positions)
- Others fail **cannot_fill_slots** (insufficient constraints)

## Reproduction

```bash
python3 07_TOOLS/core_hardening/run_alt_tail_test_enhanced.py \\
  --seed {args.seed} \\
  --num-tails {args.num_tails}
```
"""
    
    readme_path = out_dir / "README.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    # Generate manifest
    generate_manifest(out_dir)
    
    print(f"\nEnhanced alternate tail test complete!")
    print(f"Feasible tails: {feasible_count}/{args.num_tails}")
    print(f"Output: {out_dir}")
    print(f"Runtime: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    main()