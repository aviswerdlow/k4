#!/usr/bin/env python3
"""
run_frame_variant.py - Test adjacent frame variants

Tests frames adjacent to the claim boundary (GRID-only + AND + nulls):
- AND with POS 0.80 (stricter Generic)
- Full deck with AND (expanded routes)
- OR with strict Generic (different gate logic)

Usage:
    python3 run_frame_variant.py \
        --variant pos080 \
        --output_dir runs/2025-09-05/
"""

import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

VARIANTS = {
    'pos080': {
        'policy': 'policies/POLICY.seamfree.and_pos080.json',
        'name': 'AND with POS 0.80',
        'description': 'Stricter Generic threshold (0.80 vs 0.60)'
    },
    'full_deck': {
        'policy': 'policies/POLICY.seamfree.full_deck.json',
        'name': 'Full Deck with AND',
        'description': 'All routes enabled (GRID + SPOKE + RAILFENCE + HALF)'
    },
    'or_strict': {
        'policy': 'policies/POLICY.seamfree.or_strict.json',
        'name': 'OR with Strict Generic',
        'description': 'OR gate with top-0.5% perplexity'
    }
}

def run_command(cmd, verbose=False):
    """Run a command and capture output."""
    if verbose:
        print(f"Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running command: {' '.join(cmd)}")
        print(f"stderr: {result.stderr}")
        return None
    
    return result.stdout

def test_variant(variant_key, output_dir, seed=1337, verbose=False):
    """Test a specific frame variant."""
    
    variant = VARIANTS[variant_key]
    print(f"\n=== Testing Variant: {variant['name']} ===")
    print(f"Description: {variant['description']}")
    
    # Setup output directory
    variant_dir = output_dir / f'frame_{variant_key}'
    variant_dir.mkdir(parents=True, exist_ok=True)
    
    # Get paths
    scripts_dir = Path(__file__).parent
    data_dir = scripts_dir.parent / 'data'
    policy_path = scripts_dir.parent / variant['policy']
    
    # Step 1: Generate candidates
    print("\nGenerating candidates...")
    candidates_file = variant_dir / 'candidates.txt'
    
    cmd = [
        'python3', str(scripts_dir / 'generate_candidates.py'),
        '--policy', str(policy_path),
        '--permutations', str(data_dir / 'permutations.txt'),
        '--candidates', str(candidates_file)
    ]
    
    output = run_command(cmd, verbose)
    if output is None:
        return False
    
    # Step 2: Confirm and run nulls
    print("Running confirmations and nulls...")
    confirmations_file = variant_dir / 'confirmations.json'
    
    cmd = [
        'python3', str(scripts_dir / 'confirm_and_nulls.py'),
        '--candidates', str(candidates_file),
        '--policy', str(policy_path),
        '--cuts', str(data_dir / 'canonical_cuts.json'),
        '--fwords', str(data_dir / 'function_words.txt'),
        '--output', str(confirmations_file),
        '--seed', str(seed)
    ]
    
    output = run_command(cmd, verbose)
    if output is None:
        return False
    
    # Load results
    with open(confirmations_file, 'r') as f:
        results = json.load(f)
    
    # Generate summary
    summary_file = variant_dir / 'SUMMARY.md'
    
    with open(summary_file, 'w') as f:
        f.write(f"# Frame Variant: {variant['name']}\n\n")
        f.write(f"**Policy**: {variant['policy']}\n")
        f.write(f"**Description**: {variant['description']}\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        
        f.write("## Results\n\n")
        f.write(f"- Candidates tested: {results['n_candidates']}\n")
        f.write(f"- Passing phrase gate: {results['n_passing_gate']}\n")
        f.write(f"- Passing nulls: {results['n_passing_nulls']}\n\n")
        
        if results['n_passing_nulls'] > 0:
            f.write("## Interpretation\n\n")
            f.write("This frame variant produces alternate results, ")
            f.write("demonstrating behavior outside the claim boundary.\n")
        else:
            f.write("## Interpretation\n\n")
            f.write("This frame variant produces no alternate results, ")
            f.write("similar to the published frame.\n")
    
    print(f"Results: {results['n_passing_gate']} pass gate, {results['n_passing_nulls']} pass nulls")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Test frame variants')
    parser.add_argument('--variant', choices=list(VARIANTS.keys()),
                       help='Specific variant to test')
    parser.add_argument('--all', action='store_true',
                       help='Test all variants')
    parser.add_argument('--output_dir', required=True,
                       help='Output directory')
    parser.add_argument('--seed', type=int, default=1337,
                       help='Random seed')
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    if not args.variant and not args.all:
        parser.error("Must specify either --variant or --all")
    
    output_dir = Path(args.output_dir)
    
    # Test specified variant(s)
    variants_to_test = list(VARIANTS.keys()) if args.all else [args.variant]
    
    results_summary = []
    
    for variant_key in variants_to_test:
        success = test_variant(variant_key, output_dir, args.seed, args.verbose)
        results_summary.append({
            'variant': variant_key,
            'name': VARIANTS[variant_key]['name'],
            'success': success
        })
    
    # Create overall summary
    print("\n=== Frame Variants Summary ===")
    summary_file = output_dir / 'FRAME_VARIANTS_SUMMARY.md'
    
    with open(summary_file, 'w') as f:
        f.write("# Adjacent Frame Variants Analysis\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"**Seed**: {args.seed}\n\n")
        
        f.write("## Variants Tested\n\n")
        f.write("| Variant | Description | Status |\n")
        f.write("|---------|-------------|--------|\n")
        
        for result in results_summary:
            status = "✓" if result['success'] else "✗"
            f.write(f"| {result['name']} | {VARIANTS[result['variant']]['description']} | {status} |\n")
        
        f.write("\n## Claim Boundary\n\n")
        f.write("The published result uses:\n")
        f.write("- GRID-only routes (W14_ROWS, W10_NW)\n")
        f.write("- AND gate (Flint v2 ∧ Generic)\n")
        f.write("- Head-only decision (positions 0-74)\n")
        f.write("- Null hypothesis testing with Holm correction\n\n")
        
        f.write("These adjacent frames test variations outside this boundary.\n")
    
    print(f"\nSummary written to: {summary_file}")
    
    return 0

if __name__ == "__main__":
    exit(main())