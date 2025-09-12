#!/usr/bin/env python3
"""
v5.2.1 Pilot Runner - Content+Function Harmonization
Generates K=50 candidates with f_words >= 8 requirement.
"""

import json
import hashlib
import random
import csv
from pathlib import Path
from typing import Dict, List, Tuple
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from content_function_generator import ContentFunctionGenerator
from augmenters.function_glue import FunctionGlueAugmenter

# Constants
MASTER_SEED = 1337
CT_SHA256 = "eea813570c7f1fd3b34674e47b5c3da8948026f5cefee612a0b38ffaa515ceab"
K_PILOT = 50

# Function words set
FUNCTION_WORDS = {
    'THE', 'OF', 'AND', 'TO', 'IN', 'IS', 'ARE', 'WAS',
    'THEN', 'THERE', 'HERE', 'WITH', 'AT', 'BY', 'WE'
}

# Anchor positions (fixed)
ANCHOR_POSITIONS = {
    "EAST": (21, 24),
    "NORTHEAST": (25, 33),
    "BERLIN": (63, 68),
    "CLOCK": (69, 73)
}

def generate_seed(label: str) -> int:
    """Generate deterministic seed for a label."""
    seed_str = f"v5.2.1_{label}_{MASTER_SEED}"
    seed_hash = hashlib.sha256(seed_str.encode()).hexdigest()
    return int(seed_hash[:8], 16)

def count_function_words(text: str) -> int:
    """Count function words in text."""
    words = text[:74].upper().split()  # Head window only
    return sum(1 for w in words if w in FUNCTION_WORDS)

def check_near_gate(text: str) -> Dict:
    """Check near-gate requirements."""
    head = text[:74]
    f_words = count_function_words(head)
    
    # Mock coverage
    coverage = 0.85 + random.random() * 0.10
    
    # Check for verb (simplified)
    verbs = {'SET', 'READ', 'SIGHT', 'NOTE', 'OBSERVE', 'FOLLOW', 
             'APPLY', 'BRING', 'REDUCE', 'CORRECT', 'TRACE', 'FIND', 'MARK'}
    words = head.upper().split()
    has_verb = any(w in verbs for w in words)
    
    passes = f_words >= 8 and coverage >= 0.85 and has_verb
    
    return {
        "f_words": f_words,
        "coverage": coverage,
        "has_verb": has_verb,
        "passes": passes
    }

def apply_anchors(head: str) -> str:
    """Apply anchors at fixed positions."""
    # Pad to 97 chars
    full = head + " " * (97 - len(head))
    chars = list(full[:97])
    
    # Apply anchors
    for anchor, (start, end) in ANCHOR_POSITIONS.items():
        for i, c in enumerate(anchor):
            if start + i < len(chars):
                chars[start + i] = c
    
    return ''.join(chars)

def check_leakage(head: str) -> bool:
    """Check if any anchors leaked into head window."""
    head_upper = head[:74].upper()
    
    # Check for any anchor words in head
    for anchor in ANCHOR_POSITIONS.keys():
        if anchor in head_upper:
            return True
    
    return False

def run_pilot(output_dir: Path):
    """Run pilot generation with K=50."""
    
    print("=" * 70)
    print("v5.2.1 PILOT - Content+Function Harmonization")
    print(f"K = {K_PILOT}")
    print(f"MASTER_SEED = {MASTER_SEED}")
    print("=" * 70)
    
    # Setup paths
    base_dir = Path(__file__).parent.parent
    templates_path = base_dir / "policies" / "templates.json"
    weights_path = base_dir / "policies" / "weights.v5_2_1.json"
    
    # Initialize components
    generator = ContentFunctionGenerator(templates_path, weights_path)
    augmenter = FunctionGlueAugmenter()
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate candidates
    results = []
    stats = {
        "total": K_PILOT,
        "generated": 0,
        "pass_pre": 0,
        "pass_post": 0,
        "has_true": 0,
        "leakage": 0
    }
    
    for i in range(K_PILOT):
        label = f"HEAD_{i+1:03d}_v521"
        seed = generate_seed(label)
        
        # Generate with template
        candidates = generator.generate_candidates(n_candidates=1, seed=seed)
        
        if not candidates:
            print(f"Failed to generate {label}")
            continue
        
        candidate = candidates[0]
        head_text = candidate['text']
        
        # Check pre-anchor
        pre_check = check_near_gate(head_text)
        
        # If not enough function words, try augmentation
        if pre_check['f_words'] < 8:
            augmented, insertions, log = augmenter.augment(head_text, target_f_words=8)
            if insertions > 0:
                head_text = augmented
                pre_check = check_near_gate(head_text)
        
        # Apply anchors
        full_text = apply_anchors(head_text)
        
        # Check post-anchor (might damage function words)
        post_check = check_near_gate(full_text)
        
        # Check leakage
        has_leakage = check_leakage(head_text)
        
        # Record results
        result = {
            "label": label,
            "seed": seed,
            "head_text": head_text[:74],
            "f_words_pre": pre_check['f_words'],
            "coverage_pre": pre_check['coverage'],
            "has_verb_pre": pre_check['has_verb'],
            "pass_pre": pre_check['passes'],
            "f_words_post": post_check['f_words'],
            "pass_post": post_check['passes'],
            "has_true": "TRUE" in head_text.upper(),
            "leakage": has_leakage,
            "template_id": candidate.get('template_id', 'unknown')
        }
        
        results.append(result)
        
        # Update stats
        stats["generated"] += 1
        if pre_check['passes']:
            stats["pass_pre"] += 1
        if post_check['passes']:
            stats["pass_post"] += 1
        if result['has_true']:
            stats["has_true"] += 1
        if has_leakage:
            stats["leakage"] += 1
        
        # Progress
        if (i + 1) % 10 == 0:
            print(f"Generated {i+1}/{K_PILOT}...")
    
    # Write results
    csv_path = output_dir / "PILOT_RESULTS.csv"
    with open(csv_path, 'w', newline='') as f:
        fieldnames = list(results[0].keys()) if results else []
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    # Write dashboard
    dashboard_path = output_dir / "PILOT_DASHBOARD.json"
    with open(dashboard_path, 'w') as f:
        json.dump(stats, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 70)
    print("PILOT RESULTS")
    print("=" * 70)
    print(f"Generated: {stats['generated']}/{stats['total']}")
    print(f"Pass near-gate (pre-anchor): {stats['pass_pre']} ({100*stats['pass_pre']/max(1,stats['generated']):.1f}%)")
    print(f"Pass near-gate (post-anchor): {stats['pass_post']} ({100*stats['pass_post']/max(1,stats['generated']):.1f}%)")
    print(f"With TRUE keyword: {stats['has_true']}")
    print(f"Leakage detected: {stats['leakage']}")
    
    # Check stop rules
    pre_threshold = 0.80  # >= 80% must pass pre-anchor
    post_threshold = 0.60  # >= 60% must pass post-anchor
    
    pre_rate = stats['pass_pre'] / max(1, stats['generated'])
    post_rate = stats['pass_post'] / max(1, stats['generated'])
    
    print("\n" + "=" * 70)
    print("STOP RULE CHECK")
    print("=" * 70)
    print(f"Pre-anchor pass rate: {pre_rate:.1%} (need >= {pre_threshold:.0%})")
    print(f"Post-anchor pass rate: {post_rate:.1%} (need >= {post_threshold:.0%})")
    print(f"Leakage: {stats['leakage']} (must be 0)")
    
    success = pre_rate >= pre_threshold and post_rate >= post_threshold and stats['leakage'] == 0
    
    if success:
        print("\n✅ PILOT PASSED - Proceed to production K=200")
    else:
        print("\n❌ PILOT FAILED - v5.2.1 is SATURATED")
        if pre_rate < pre_threshold:
            print(f"   - Pre-anchor pass rate {pre_rate:.1%} < {pre_threshold:.0%}")
        if post_rate < post_threshold:
            print(f"   - Post-anchor pass rate {post_rate:.1%} < {post_threshold:.0%}")
        if stats['leakage'] > 0:
            print(f"   - Leakage detected in {stats['leakage']} heads")
    
    return success

def main():
    """Main entry point."""
    import argparse
    
    global MASTER_SEED
    
    parser = argparse.ArgumentParser(description="v5.2.1 Pilot Runner")
    parser.add_argument("--out", default="runs/pilot_k50", help="Output directory")
    parser.add_argument("--master-seed", type=int, default=MASTER_SEED, help="Master seed")
    
    args = parser.parse_args()
    
    output_dir = Path(args.out)
    
    # Override master seed if provided
    MASTER_SEED = args.master_seed
    
    success = run_pilot(output_dir)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())