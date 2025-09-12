#!/usr/bin/env python3
"""
report_boundary_tie_break.py - Generate boundary v2.1 tie-break report

Report-only analysis showing how boundary-aware tokenization affects function word counts.
Does not change any decision gating - purely informational.
"""

import json
import argparse
import os
from pathlib import Path
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description='Generate boundary v2.1 tie-break report')
    parser.add_argument('--pt', required=True, help='Plaintext file (97 chars)')
    parser.add_argument('--cuts', required=True, help='Canonical cuts JSON')
    parser.add_argument('--fwords', required=True, help='Function words file')
    parser.add_argument('--out', required=True, help='Output directory')
    
    args = parser.parse_args()
    
    # Create output directory
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Load plaintext
    with open(args.pt, 'r') as f:
        plaintext = f.read().strip().upper()
    
    if len(plaintext) != 97:
        print(f"Warning: Plaintext length is {len(plaintext)}, expected 97")
    
    # Get script directory
    script_dir = Path(__file__).parent
    tokenize_script = script_dir / 'tokenize_v21.py'
    
    # Run tokenization analysis
    tokenize_output = out_dir / 'tokenization_analysis.json'
    
    cmd = [
        'python3', str(tokenize_script),
        '--text', args.pt,
        '--cuts', args.cuts,
        '--fwords', args.fwords,
        '--output', str(tokenize_output)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running tokenize_v21.py: {result.stderr}")
        sys.exit(1)
    
    # Load tokenization results
    with open(tokenize_output, 'r') as f:
        tokenization = json.load(f)
    
    # Write individual output files
    
    # 1. head_tokens_v2.json
    with open(out_dir / 'head_tokens_v2.json', 'w') as f:
        json.dump({
            'head_tokens': tokenization['v2']['head_tokens'],
            'head_fword_count': tokenization['v2']['head_fword_count'],
            'head_fwords': tokenization['v2']['head_fwords'],
            'tokenization': 'v2',
            'notes': 'Current decision tokenization (canonical cuts, no inferred splits)'
        }, f, indent=2)
    
    # 2. head_tokens_v21.json
    with open(out_dir / 'head_tokens_v21.json', 'w') as f:
        json.dump({
            'head_tokens': tokenization['v21']['head_tokens'],
            'head_fword_count': tokenization['v21']['head_fword_count'],
            'head_fwords': tokenization['v21']['head_fwords'],
            'tokenization': 'v21',
            'notes': 'Boundary-aware tokenization (splits THEJOY if present at position 74)'
        }, f, indent=2)
    
    # 3. boundary_tie_break.json
    boundary_report = {
        'letters_74_80': tokenization['letters_74_80'],
        'v2': {
            'head_fword_count': tokenization['v2']['head_fword_count'],
            'head_fwords': tokenization['v2']['head_fwords']
        },
        'v21': {
            'head_fword_count': tokenization['v21']['head_fword_count'],
            'head_fwords': tokenization['v21']['head_fwords'],
            'delta': tokenization['v21']['delta']
        },
        'applied': tokenization['boundary_split_applied'],
        'notes': 'Report-only; decision gate remains tokenization v2.'
    }
    
    with open(out_dir / 'boundary_tie_break.json', 'w') as f:
        json.dump(boundary_report, f, indent=2)
    
    # 4. BOUNDARY_TIE_BREAK.md
    with open(out_dir / 'BOUNDARY_TIE_BREAK.md', 'w') as f:
        f.write("# Boundary-Aware Tokenization v2.1 Report\n\n")
        f.write("**Status**: Report-only (does not affect decision gating)\n")
        f.write("**Purpose**: Tie-break analysis for function word counts\n\n")
        
        f.write("## Analysis\n\n")
        f.write(f"**Letters at positions 74-79**: `{tokenization['letters_74_80']}`\n\n")
        
        if tokenization['boundary_split_applied']:
            f.write("**Boundary split applied**: Yes\n\n")
            f.write("The sequence 'THEJOY' at the head boundary (position 74) was split into:\n")
            f.write("- 'THE' (positions 74-76) - counted in head window\n")
            f.write("- 'JOY' (positions 77-79) - excluded from head window\n\n")
        else:
            f.write("**Boundary split applied**: No\n\n")
            f.write(f"The sequence at position 74 is '{tokenization['letters_74_80']}', ")
            f.write("not 'THEJOY', so no boundary split is applied.\n\n")
        
        f.write("## Function Word Counts\n\n")
        f.write("| Tokenization | Head Function Words | List |\n")
        f.write("|--------------|---------------------|------|\n")
        f.write(f"| v2 (decision) | {tokenization['v2']['head_fword_count']} | {', '.join(tokenization['v2']['head_fwords'])} |\n")
        f.write(f"| v2.1 (report) | {tokenization['v21']['head_fword_count']} | {', '.join(tokenization['v21']['head_fwords'])} |\n")
        
        if tokenization['v21']['delta'] != 0:
            f.write(f"\n**Delta**: {tokenization['v21']['delta']:+d} function word(s)\n")
        
        f.write("\n## Implications\n\n")
        f.write("This boundary-aware tokenization (v2.1) is used **only** for reporting ")
        f.write("and potential tie-break analysis. The decision pipeline (phrase gate, ")
        f.write("null hypothesis testing) continues to use standard v2 tokenization.\n\n")
        
        if tokenization['boundary_split_applied']:
            f.write("The presence of 'THEJOY' at the boundary suggests editorial awareness ")
            f.write("of the head/tail division, with 'THE' belonging semantically to the ")
            f.write("head instruction and 'JOY' introducing the tail fragment.\n")
        else:
            f.write("No boundary-aware split is applicable for this plaintext.\n")
    
    print(f"\nBoundary v2.1 Tie-Break Report Generated")
    print(f"Output directory: {out_dir}")
    print(f"  - head_tokens_v2.json")
    print(f"  - head_tokens_v21.json")
    print(f"  - boundary_tie_break.json")
    print(f"  - BOUNDARY_TIE_BREAK.md")
    
    if tokenization['boundary_split_applied']:
        print(f"\nBoundary split WAS applied:")
        print(f"  v2 function words: {tokenization['v2']['head_fword_count']}")
        print(f"  v2.1 function words: {tokenization['v21']['head_fword_count']} (delta: {tokenization['v21']['delta']:+d})")
    else:
        print(f"\nNo boundary split applied (letters 74-79: '{tokenization['letters_74_80']}')")

if __name__ == "__main__":
    main()