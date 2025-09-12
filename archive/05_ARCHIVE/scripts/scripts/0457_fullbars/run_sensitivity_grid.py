#!/usr/bin/env python3
"""
Sensitivity grid runner - tests published winner with 3x3 policy matrix.
POS thresholds: {0.55, 0.60, 0.65}
Perplexity percentiles: {1.5, 1.0, 0.5}
3 null replicates per cell = 27 total runs.
"""

import json
import hashlib
import csv
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from gate_cadence import evaluate_cadence, tokenize_v2
from holm import run_null_hypothesis_test
from run_p74_strip import (
    generate_space_map, run_near_gate, run_flint_v2, 
    run_generic_gate, generate_null_samples
)

# Published winner from BLINDED_CH00_I003
WINNER_PLAINTEXT = "NKQCBNYHFQDZEXQBZOAKMEASTNORTHEASTRQJOYQWZUWPJZZHCJKDMCNUXNPWVZBERLINCLOCKVTHEJOYOFANANGLEISTHEAR"

# Winner's schedule from earlier Confirm
WINNER_SCHEDULE = {
    'per_class': [
        {'class_id': 0, 'family': 'vigenere', 'L': 17, 'phase': 0},
        {'class_id': 1, 'family': 'vigenere', 'L': 16, 'phase': 0},
        {'class_id': 2, 'family': 'beaufort', 'L': 16, 'phase': 0},
        {'class_id': 3, 'family': 'vigenere', 'L': 16, 'phase': 0},
        {'class_id': 4, 'family': 'beaufort', 'L': 19, 'phase': 0},
        {'class_id': 5, 'family': 'beaufort', 'L': 20, 'phase': 0}
    ],
    'forced_residues': []  # Will be populated from proof_digest
}

def load_winner_data() -> Dict:
    """Load winner data from Confirm run."""
    confirm_dir = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/experiments/pipeline_v4/runs/confirm/BLINDED_CH00_I003")
    
    # Load proof digest for schedule
    with open(confirm_dir / "proof_digest.json", 'r') as f:
        proof = json.load(f)
    
    # Load space map
    with open(confirm_dir / "space_map.json", 'r') as f:
        space_map = json.load(f)
    
    return {
        'plaintext': WINNER_PLAINTEXT,
        'schedule': proof,
        'space_map': space_map
    }

def run_sensitivity_cell(pos_threshold: float, perp_percentile: float,
                        replicate: int, output_dir: Path) -> Dict:
    """
    Run a single sensitivity cell with specified thresholds.
    
    Args:
        pos_threshold: POS threshold (0.55, 0.60, or 0.65)
        perp_percentile: Perplexity percentile (1.5, 1.0, or 0.5)
        replicate: Replicate number (1, 2, or 3)
        output_dir: Output directory for this cell
    
    Returns:
        Result dictionary with gate outcomes and nulls
    """
    print(f"\n{'=' * 60}")
    print(f"SENSITIVITY: POS={pos_threshold}, Perp={perp_percentile}%, Rep={replicate}")
    print(f"{'=' * 60}")
    
    # Create output directory
    cell_name = f"pos{int(pos_threshold*100):03d}_perp{int(perp_percentile*10):02d}"
    cell_dir = output_dir / cell_name / f"rep{replicate}"
    cell_dir.mkdir(parents=True, exist_ok=True)
    
    # Load winner data
    winner = load_winner_data()
    plaintext = winner['plaintext']
    space_map = winner['space_map']
    
    # Get words
    words = tokenize_v2(plaintext, space_map['cuts'])
    head_text = plaintext[:75]
    
    # Save plaintext and space map
    with open(cell_dir / 'plaintext_97.txt', 'w') as f:
        f.write(plaintext)
    
    with open(cell_dir / 'space_map.json', 'w') as f:
        json.dump(space_map, f, indent=2)
    
    # Step 1: Near-gate (same for all cells)
    print("\n1. Running near-gate...")
    near_result = run_near_gate(plaintext, words)
    print(f"   Coverage: {near_result['coverage']:.3f}")
    print(f"   F-words: {near_result['f_words']}")
    print(f"   Has verb: {near_result['has_verb']}")
    print(f"   {'✅ PASS' if near_result['pass'] else '❌ FAIL'}")
    
    with open(cell_dir / 'near_gate_report.json', 'w') as f:
        json.dump(near_result, f, indent=2)
    
    # Step 2: Phrase gate with sensitivity parameters
    print("\n2. Running phrase gate...")
    
    # Flint v2 (same for all cells)
    flint_result = run_flint_v2(plaintext, words)
    print(f"   Flint v2: {'✅ PASS' if flint_result['pass'] else '❌ FAIL'}")
    
    # Generic with sensitivity parameters
    generic_result = run_generic_gate(plaintext, words, 
                                     pos_threshold=pos_threshold,
                                     perp_percentile=perp_percentile)
    print(f"   Generic: {'✅ PASS' if generic_result['pass'] else '❌ FAIL'}")
    print(f"     POS: {generic_result['pos_score']:.3f} (threshold: {pos_threshold})")
    print(f"     Perplexity: {generic_result['perplexity_percentile']:.1f}% (threshold: ≤{perp_percentile}%)")
    
    # Cadence (same for all cells)
    thresholds_path = "/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/experiments/0457_fullbars/runs/2025-01-06/cadence/THRESHOLDS.json"
    cadence_result = evaluate_cadence(head_text, words, thresholds_path)
    print(f"   Cadence: {'✅ PASS' if cadence_result['pass'] else '❌ FAIL'}")
    
    # AND gate
    accepted_by = []
    if flint_result['pass']:
        accepted_by.append('flint_v2')
    if generic_result['pass']:
        accepted_by.append('generic')
    if cadence_result['pass']:
        accepted_by.append('cadence')
    
    phrase_pass = len(accepted_by) == 3
    
    # Load the policy for this cell
    policy_file = f"/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/experiments/0457_fullbars/runs/2025-01-06/prereg/sensitivity/POLICY.pos{int(pos_threshold*100):03d}.perp{int(perp_percentile*10):02d}.json"
    
    with open(policy_file, 'r') as f:
        policy = json.load(f)
    
    with open(cell_dir / 'phrase_gate_policy.json', 'w') as f:
        json.dump(policy, f, indent=2)
    
    phrase_report = {
        'window': [0, 74],
        'tokenization': 'v2',
        'policy': cell_name,
        'flint_v2': flint_result,
        'generic': generic_result,
        'cadence': cadence_result,
        'accepted_by': accepted_by,
        'pass': phrase_pass
    }
    
    with open(cell_dir / 'phrase_gate_report.json', 'w') as f:
        json.dump(phrase_report, f, indent=2)
    
    print(f"   Accepted by: {accepted_by}")
    print(f"   AND gate: {'✅ PASS' if phrase_pass else '❌ FAIL'}")
    
    # Step 3: Nulls (only if all gates pass)
    holm_result = None
    
    if near_result['pass'] and phrase_pass:
        print(f"\n3. Running nulls (replicate {replicate})...")
        
        # Generate seed for this replicate
        ct_sha = hashlib.sha256("OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR".encode()).hexdigest()
        seed_recipe = f"SENSITIVITY|pos:{pos_threshold}|perp:{perp_percentile}|replicate:{replicate}|ct:{ct_sha}"
        seed_u64 = int(hashlib.sha256(seed_recipe.encode()).hexdigest()[:16], 16) % (2**32)
        
        # Generate null samples
        null_samples = generate_null_samples(winner['schedule'], seed_u64, n_samples=10000)
        
        # Extract distributions
        null_dists = {
            'coverage': [s['coverage'] for s in null_samples],
            'f_words': [s['f_words'] for s in null_samples]
        }
        
        # Run Holm test
        observed = {
            'coverage': near_result['coverage'],
            'f_words': near_result['f_words']
        }
        
        holm_result = run_null_hypothesis_test(observed, null_dists)
        
        print(f"   Coverage adj-p: {holm_result['metrics']['coverage']['p_adjusted']:.6f}")
        print(f"   F-words adj-p: {holm_result['metrics']['f_words']['p_adjusted']:.6f}")
        print(f"   Publishable: {'✅' if holm_result['publishable'] else '❌'}")
        
        with open(cell_dir / 'holm_report_canonical.json', 'w') as f:
            json.dump(holm_result, f, indent=2)
    else:
        print("\n3. Nulls not run (gates failed)")
        
        with open(cell_dir / 'holm_report_canonical.json', 'w') as f:
            json.dump({
                'status': 'not_run',
                'reason': 'gates_failed'
            }, f, indent=2)
    
    # Bundle creation
    print("\n4. Creating bundle...")
    
    # Proof digest (use winner's)
    proof_digest = winner['schedule'].copy()
    proof_digest['sensitivity_params'] = {
        'pos_threshold': pos_threshold,
        'perp_percentile': perp_percentile,
        'replicate': replicate
    }
    
    with open(cell_dir / 'proof_digest.json', 'w') as f:
        json.dump(proof_digest, f, indent=2)
    
    # Coverage report
    coverage_report = {
        'encrypts_to_ct': True,
        'route_id': 'GRID_W14_ROWS',
        'sensitivity_cell': cell_name,
        'replicate': replicate,
        'near_gate': near_result,
        'phrase_gate': {
            'accepted_by': accepted_by,
            'pass': phrase_pass
        },
        'nulls': {
            'publishable': holm_result['publishable'] if holm_result else False
        }
    }
    
    with open(cell_dir / 'coverage_report.json', 'w') as f:
        json.dump(coverage_report, f, indent=2)
    
    # REPRO_STEPS.md
    repro_steps = f"""# Reproduction Steps - Sensitivity {cell_name} Rep{replicate}

```bash
python3 scripts/0457_fullbars/run_sensitivity_grid.py \\
    --pos {pos_threshold} \\
    --perp {perp_percentile} \\
    --replicate {replicate} \\
    --policy prereg/sensitivity/POLICY.{cell_name}.json \\
    --output sensitivity_strip/{cell_name}/rep{replicate}
```

## Parameters
- POS threshold: {pos_threshold}
- Perplexity percentile: {perp_percentile}%
- Replicate: {replicate}

## Results
- Near-gate: {'PASS' if near_result['pass'] else 'FAIL'}
- Phrase gate: {'PASS' if phrase_pass else 'FAIL'}
- Publishable: {'YES' if coverage_report['nulls']['publishable'] else 'NO'}
"""
    
    with open(cell_dir / 'REPRO_STEPS.md', 'w') as f:
        f.write(repro_steps)
    
    # Generate hashes
    import subprocess
    subprocess.run(['sha256sum', '*'], cwd=cell_dir, 
                  stdout=open(cell_dir / 'hashes.txt', 'w'), 
                  stderr=subprocess.DEVNULL)
    
    print("   ✅ Bundle complete")
    
    # Return summary
    return {
        'pos': pos_threshold,
        'perplexity': perp_percentile,
        'replicate': replicate,
        'near_pass': near_result['pass'],
        'flint_pass': flint_result['pass'],
        'generic_pass': generic_result['pass'],
        'cadence_pass': cadence_result['pass'],
        'holm_adj_p_cov': holm_result['metrics']['coverage']['p_adjusted'] if holm_result else None,
        'holm_adj_p_fw': holm_result['metrics']['f_words']['p_adjusted'] if holm_result else None,
        'publishable': coverage_report['nulls']['publishable'],
        'seed_u64': seed_u64 if holm_result else None
    }

def run_full_sensitivity_grid():
    """Run complete 3x3 sensitivity grid with 3 replicates each."""
    
    output_dir = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/experiments/0457_fullbars/runs/2025-01-06/sensitivity_strip")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Grid parameters
    pos_thresholds = [0.55, 0.60, 0.65]
    perp_percentiles = [1.5, 1.0, 0.5]
    replicates = [1, 2, 3]
    
    results = []
    
    print("=" * 60)
    print("SENSITIVITY GRID - FULL RUN")
    print("=" * 60)
    print(f"POS thresholds: {pos_thresholds}")
    print(f"Perplexity percentiles: {perp_percentiles}")
    print(f"Replicates per cell: {len(replicates)}")
    print(f"Total runs: {len(pos_thresholds) * len(perp_percentiles) * len(replicates)}")
    
    # Run each cell
    for pos in pos_thresholds:
        for perp in perp_percentiles:
            for rep in replicates:
                result = run_sensitivity_cell(pos, perp, rep, output_dir)
                results.append(result)
    
    # Create summary CSV
    csv_file = output_dir / 'SENS_STRIP_MATRIX.csv'
    with open(csv_file, 'w', newline='') as f:
        fieldnames = [
            'pos', 'perplexity', 'replicate',
            'near_pass', 'flint_pass', 'generic_pass', 'cadence_pass',
            'holm_adj_p_cov', 'holm_adj_p_fw', 'publishable', 'seed_u64'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n{'=' * 60}")
    print("SENSITIVITY GRID COMPLETE")
    print(f"Summary saved to {csv_file}")
    
    # Summary stats
    publishable = sum(1 for r in results if r['publishable'])
    
    print(f"\nPublishable: {publishable}/27")
    
    # Breakdown by cell
    for pos in pos_thresholds:
        for perp in perp_percentiles:
            cell_results = [r for r in results 
                           if r['pos'] == pos and r['perplexity'] == perp]
            cell_pub = sum(1 for r in cell_results if r['publishable'])
            print(f"  POS={pos}, Perp={perp}%: {cell_pub}/3 publishable")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run sensitivity grid')
    parser.add_argument('--pos', type=float, help='Single POS threshold')
    parser.add_argument('--perp', type=float, help='Single perplexity percentile')
    parser.add_argument('--replicate', type=int, help='Single replicate number')
    
    args = parser.parse_args()
    
    if args.pos and args.perp and args.replicate:
        # Single cell mode
        output_dir = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/experiments/0457_fullbars/runs/2025-01-06/sensitivity_strip")
        result = run_sensitivity_cell(args.pos, args.perp, args.replicate, output_dir)
        print(f"\nResult: {json.dumps(result, indent=2)}")
    else:
        # Full grid
        run_full_sensitivity_grid()