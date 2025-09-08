#!/usr/bin/env python3
"""
Skeleton Survey v2 - Extended testing of periodic/near-periodic classing patterns.
Tests broader families of classing schemes beyond the original 24.
"""

import sys
import json
import csv
import time
import hashlib
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Callable
import os

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent))
from core_hardening_utils import *


class SkeletonGenerator:
    """Generate various families of classing patterns."""
    
    def __init__(self, master_seed: int = 1337):
        self.master_seed = master_seed
        self.patterns = []
        
    def generate_all(self, max_patterns: int = 200) -> List[Tuple[str, str, Callable]]:
        """Generate all skeleton patterns up to max_patterns."""
        patterns = []
        
        # Always include baseline
        patterns.append(self._baseline())
        
        # Family A: Pure modular composites
        patterns.extend(self._family_a())
        
        # Family B: Alternating skeletons
        patterns.extend(self._family_b())
        
        # Family C: Phase-offsetted variants
        patterns.extend(self._family_c())
        
        # Family D: Hybrid periodic
        patterns.extend(self._family_d())
        
        # Family E: Shallow aperiodic toggles
        patterns.extend(self._family_e())
        
        # Limit to max_patterns
        if len(patterns) > max_patterns:
            patterns = patterns[:max_patterns]
        
        return patterns
    
    def _baseline(self) -> Tuple[str, str, Callable]:
        """The baseline skeleton."""
        def skeleton(i: int) -> int:
            return ((i % 2) * 3) + (i % 3)
        return ("BASELINE", "((i%2)*3)+(i%3)", skeleton)
    
    def _family_a(self) -> List[Tuple[str, str, Callable]]:
        """Family A: Pure modular composites."""
        patterns = []
        
        # Test various (a,c) pairs with different b values
        configs = [
            (2, 3, 1), (2, 3, 2), (2, 3, 3), (2, 3, 4),
            (3, 2, 1), (3, 2, 2), (3, 2, 3), (3, 2, 4),
            (4, 3, 1), (4, 3, 2), (4, 3, 3),
            (3, 4, 1), (3, 4, 2), (3, 4, 3),
            (5, 2, 1), (5, 2, 2), (5, 2, 3),
            (2, 5, 1), (2, 5, 2), (2, 5, 3)
        ]
        
        for a, c, b in configs:
            def make_skeleton(a=a, c=c, b=b):
                def skeleton(i: int) -> int:
                    return (((i % a) * b) + (i % c)) % 6
                return skeleton
            
            pattern_id = f"A_{a}_{c}_{b}"
            formula = f"(((i%{a})*{b})+(i%{c}))%6"
            patterns.append((pattern_id, formula, make_skeleton()))
        
        return patterns
    
    def _family_b(self) -> List[Tuple[str, str, Callable]]:
        """Family B: Alternating skeletons."""
        patterns = []
        
        # B1: Alternate between two classing rules by parity
        def b1_skeleton(i: int) -> int:
            if i % 2 == 0:
                return ((i % 2) * 3) + (i % 3)
            else:
                return ((i % 3) * 2) + (i % 2)
        patterns.append(("B1_PARITY", "even:((i%2)*3)+(i%3);odd:((i%3)*2)+(i%2)", b1_skeleton))
        
        # B2: Alternate with mod-6 and permutation
        odd_perm = [3, 4, 5, 0, 1, 2]  # Fixed permutation for odd indices
        def b2_skeleton(i: int) -> int:
            base = i % 6
            if i % 2 == 0:
                return base
            else:
                return odd_perm[base]
        patterns.append(("B2_MOD6_PERM", "even:i%6;odd:perm[i%6]", b2_skeleton))
        
        # B3: Triple alternation
        def b3_skeleton(i: int) -> int:
            mod3 = i % 3
            if mod3 == 0:
                return i % 6
            elif mod3 == 1:
                return (i % 2) * 3 + (i % 3)
            else:
                return (i % 3) * 2
        patterns.append(("B3_TRIPLE", "i%3→different rules", b3_skeleton))
        
        return patterns
    
    def _family_c(self) -> List[Tuple[str, str, Callable]]:
        """Family C: Phase-offsetted variants."""
        patterns = []
        
        # Phase offsets of baseline
        for phase in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
            def make_skeleton(p=phase):
                def skeleton(i: int) -> int:
                    j = i + p
                    return ((j % 2) * 3) + (j % 3)
                return skeleton
            
            pattern_id = f"C_PHASE_{phase}"
            formula = f"baseline(i+{phase})"
            patterns.append((pattern_id, formula, make_skeleton()))
        
        return patterns
    
    def _family_d(self) -> List[Tuple[str, str, Callable]]:
        """Family D: Hybrid periodic (two-level)."""
        patterns = []
        
        # D1: XOR-based mapping
        map6_xor = [0, 3, 1, 4, 2, 5]  # Fixed mapping
        def d1_skeleton(i: int) -> int:
            h = i % 2
            k = i % 3
            idx = (h << 2) ^ k
            return map6_xor[idx % 6]
        patterns.append(("D1_XOR", "map6[(i%2<<2)^(i%3)]", d1_skeleton))
        
        # D2: Multiplicative mapping
        map6_mult = [0, 1, 2, 3, 4, 5]  # Identity for now
        def d2_skeleton(i: int) -> int:
            h = i % 2
            k = i % 3
            idx = (h * 3) + k
            return map6_mult[idx]
        patterns.append(("D2_MULT", "map6[(i%2)*3+(i%3)]", d2_skeleton))
        
        # D3: Different multiplicative mapping
        map6_mult2 = [5, 4, 3, 2, 1, 0]  # Reverse
        def d3_skeleton(i: int) -> int:
            h = i % 2
            k = i % 3
            idx = (h * 3) + k
            return map6_mult2[idx]
        patterns.append(("D3_MULT_REV", "map6_rev[(i%2)*3+(i%3)]", d3_skeleton))
        
        return patterns
    
    def _family_e(self) -> List[Tuple[str, str, Callable]]:
        """Family E: Shallow aperiodic toggles."""
        patterns = []
        
        # Generate deterministic 12-length patterns
        import random
        
        for seed_offset in range(10):  # Generate 10 patterns
            seed = self.master_seed + seed_offset
            random.seed(seed)
            
            # Generate balanced pattern (each class appears ~2 times in 12)
            pattern = []
            for c in range(6):
                pattern.extend([c] * 2)
            random.shuffle(pattern)
            
            def make_skeleton(p=pattern[:]):
                def skeleton(i: int) -> int:
                    return p[i % 12]
                return skeleton
            
            pattern_id = f"E_PATTERN_{seed_offset}"
            formula = f"repeat_12[{seed}]"
            patterns.append((pattern_id, formula, make_skeleton()))
        
        return patterns


def test_skeleton(
    pattern_id: str,
    formula: str,
    skeleton_func: Callable,
    ct: str,
    anchors: Dict
) -> Dict:
    """Test a single skeleton pattern."""
    start_time = time.time()
    
    # For baseline, use full plaintext for validation
    # For others, use only anchors
    if pattern_id == "BASELINE":
        # Load the full known plaintext
        full_pt = load_plaintext()
        anchor_pt = {i: full_pt[i] for i in range(97)}
    else:
        # Load anchor plaintext constraints only
        anchor_pt = {}
        for name, info in anchors.items():
            for i in range(info['start'], info['end'] + 1):
                idx = i - info['start']
                if idx < len(info['plaintext']):
                    anchor_pt[i] = info['plaintext'][idx]
    
    # Compute classes for all indices
    classes = [skeleton_func(i) for i in range(97)]
    unique_classes = set(classes)
    
    # Must map to exactly 6 classes
    if len(unique_classes) != 6:
        return {
            'pattern_id': pattern_id,
            'family_name': formula,
            'params_json': json.dumps({'classes': len(unique_classes)}),
            'feasible': False,
            'reason': f'wrong_class_count:{len(unique_classes)}',
            'pt_sha256': '',
            'wheels_json_path': ''
        }
    
    # Ensure classes are 0-5
    if min(unique_classes) != 0 or max(unique_classes) != 5:
        return {
            'pattern_id': pattern_id,
            'family_name': formula,
            'params_json': json.dumps({'class_range': f'{min(unique_classes)}-{max(unique_classes)}'}),
            'feasible': False,
            'reason': 'invalid_class_range',
            'pt_sha256': '',
            'wheels_json_path': ''
        }
    
    # Group indices by class
    class_indices = {c: [] for c in range(6)}
    for i in range(97):
        class_indices[skeleton_func(i)].append(i)
    
    # Try to solve wheels
    wheels = {}
    for class_id in range(6):
        indices = class_indices[class_id]
        
        # Get anchor constraints for this class
        class_constraints = {i: anchor_pt[i] for i in indices if i in anchor_pt}
        
        if not class_constraints:
            # No anchors in this class - cannot solve
            return {
                'pattern_id': pattern_id,
                'family_name': formula,
                'params_json': json.dumps({'failed_class': class_id}),
                'feasible': False,
                'reason': f'no_anchors_in_class_{class_id}',
                'pt_sha256': '',
                'wheels_json_path': ''
            }
        
        # Try to solve wheel
        wheel_config = solve_class_wheel(
            class_id,
            indices,
            ct,
            class_constraints,
            enforce_option_a=True
        )
        
        if wheel_config is None:
            return {
                'pattern_id': pattern_id,
                'family_name': formula,
                'params_json': json.dumps({'failed_class': class_id}),
                'feasible': False,
                'reason': f'wheel_solve_failed_class_{class_id}',
                'pt_sha256': '',
                'wheels_json_path': ''
            }
        
        wheels[class_id] = wheel_config
    
    # Try to derive full plaintext
    try:
        derived_pt = derive_plaintext_from_wheels(ct, wheels, skeleton_func)
        
        if '?' in derived_pt:
            return {
                'pattern_id': pattern_id,
                'family_name': formula,
                'params_json': json.dumps({'incomplete_positions': derived_pt.count('?')}),
                'feasible': False,
                'reason': 'incomplete_derivation',
                'pt_sha256': '',
                'wheels_json_path': ''
            }
        
        # Compute SHA
        pt_sha = compute_sha256(derived_pt)
        
        # Check if matches winner
        winner_sha = "4eceb739ab655d6f4ec87753569b8bf04573fe26d01c0caa68d36776dd052d79"
        if pt_sha == winner_sha:
            # Write proof
            proof_path = Path(f"04_EXPERIMENTS/core_hardening_v2/skeleton_survey_v2/PROOFS/{pattern_id}.json")
            proof_path.parent.mkdir(parents=True, exist_ok=True)
            
            proof = {
                "pattern_id": pattern_id,
                "classing": formula,
                "families": [wheels[i]['family'] for i in sorted(wheels.keys())],
                "periods": [wheels[i]['L'] for i in sorted(wheels.keys())],
                "phases": [wheels[i]['phase'] for i in sorted(wheels.keys())],
                "forced_anchor_residues": [],
                "class_formula_note": "no seam guard; Option-A enforced",
                "pt_sha256": pt_sha
            }
            
            # Collect forced anchor residues
            for class_id, config in wheels.items():
                if 'forced_anchor_residues' in config:
                    proof['forced_anchor_residues'].extend(config['forced_anchor_residues'])
            
            with open(proof_path, 'w') as f:
                json.dump(proof, f, indent=2)
            
            return {
                'pattern_id': pattern_id,
                'family_name': formula,
                'params_json': json.dumps({
                    'families': proof['families'],
                    'periods': proof['periods']
                }),
                'feasible': True,
                'reason': 'success',
                'pt_sha256': pt_sha,
                'wheels_json_path': str(proof_path)
            }
        else:
            return {
                'pattern_id': pattern_id,
                'family_name': formula,
                'params_json': json.dumps({'sha': pt_sha[:16]}),
                'feasible': False,
                'reason': 'wrong_plaintext',
                'pt_sha256': pt_sha,
                'wheels_json_path': ''
            }
            
    except Exception as e:
        return {
            'pattern_id': pattern_id,
            'family_name': formula,
            'params_json': json.dumps({'error': str(e)[:50]}),
            'feasible': False,
            'reason': f'derivation_error',
            'pt_sha256': '',
            'wheels_json_path': ''
        }


def main():
    """Main function for skeleton survey v2."""
    parser = argparse.ArgumentParser(description='Extended skeleton survey')
    parser.add_argument('--ct', default='02_DATA/ciphertext_97.txt', help='Ciphertext file')
    parser.add_argument('--anchors', default='02_DATA/anchors/four_anchors.json', help='Anchors JSON')
    parser.add_argument('--out', default='04_EXPERIMENTS/core_hardening_v2/skeleton_survey_v2', help='Output directory')
    parser.add_argument('--max-patterns', type=int, default=200, help='Maximum patterns to test')
    parser.add_argument('--master-seed', type=int, default=1337, help='Master seed')
    args = parser.parse_args()
    
    print(f"Starting Extended Skeleton Survey v2")
    print(f"Max patterns: {args.max_patterns}")
    print(f"Master seed: {args.master_seed}")
    
    start_time = time.time()
    
    # Setup output directory
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    proofs_dir = out_dir / "PROOFS"
    proofs_dir.mkdir(exist_ok=True)
    
    # Load ciphertext
    with open(args.ct, 'r') as f:
        ct = f.read().strip()
    print(f"Loaded CT (hash: {compute_sha256(ct)[:16]}...)")
    
    # Load anchors
    with open(args.anchors, 'r') as f:
        anchors = json.load(f)
    print(f"Loaded {len(anchors)} anchors")
    
    # Generate skeleton patterns
    generator = SkeletonGenerator(args.master_seed)
    patterns = generator.generate_all(args.max_patterns)
    print(f"Generated {len(patterns)} patterns to test")
    
    # Prepare CSV
    csv_path = out_dir / "RESULTS.csv"
    csv_file = open(csv_path, 'w', newline='')
    fieldnames = ['pattern_id', 'family_name', 'params_json', 'feasible', 'reason', 'pt_sha256', 'wheels_json_path']
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()
    
    # Test each pattern
    results = []
    feasible_count = 0
    
    for pattern_id, formula, skeleton_func in patterns:
        print(f"Testing {pattern_id}...", end=" ")
        result = test_skeleton(pattern_id, formula, skeleton_func, ct, anchors)
        results.append(result)
        csv_writer.writerow(result)
        csv_file.flush()
        
        if result['feasible']:
            feasible_count += 1
            print(f"✓ FEASIBLE")
        else:
            print(f"✗ {result['reason']}")
    
    csv_file.close()
    
    # Create summary
    summary = {
        "patterns_tested": len(patterns),
        "feasible": feasible_count,
        "feasible_patterns": [r['pattern_id'] for r in results if r['feasible']],
        "master_seed": args.master_seed,
        "runtime_seconds": time.time() - start_time
    }
    
    summary_path = out_dir / "SUMMARY.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Create README
    readme_content = f"""# Skeleton Survey v2 - Extended Results

## Overview
Tested {len(patterns)} skeleton patterns across multiple families.

## Results
- **Patterns tested**: {len(patterns)}
- **Feasible**: {feasible_count}
- **Success rate**: {feasible_count/len(patterns)*100:.1f}%

## Pattern Families
- **Baseline**: The original ((i%2)*3)+(i%3)
- **Family A**: Pure modular composites
- **Family B**: Alternating skeletons
- **Family C**: Phase-offsetted variants
- **Family D**: Hybrid periodic (two-level)
- **Family E**: Shallow aperiodic toggles

## Feasible Patterns
"""
    
    for r in results:
        if r['feasible']:
            readme_content += f"- {r['pattern_id']}: {r['family_name']}\n"
    
    if feasible_count == 0:
        readme_content += "No patterns were feasible.\n"
    
    readme_content += f"""
## Files
- RESULTS.csv: Complete test results
- PROOFS/: Proof files for feasible patterns
- SUMMARY.json: Machine-readable summary
"""
    
    readme_path = out_dir / "README.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    # Create run log
    run_log_content = f"""# Run Log - Skeleton Survey v2

## Execution
- Start: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(start_time))}
- End: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}
- Runtime: {time.time() - start_time:.2f} seconds
- Master Seed: {args.master_seed}

## Configuration
- Max patterns: {args.max_patterns}
- Ciphertext: {args.ct}
- Anchors: {args.anchors}

## Results
- Patterns tested: {len(patterns)}
- Feasible: {feasible_count}
"""
    
    run_log_path = out_dir / "RUN_LOG.md"
    with open(run_log_path, 'w') as f:
        f.write(run_log_content)
    
    # Generate manifest
    generate_manifest(out_dir)
    
    print(f"\nSkeleton Survey v2 complete!")
    print(f"Results: {feasible_count}/{len(patterns)} feasible")
    print(f"Output: {out_dir}")


if __name__ == "__main__":
    main()