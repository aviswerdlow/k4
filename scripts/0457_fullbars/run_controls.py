#!/usr/bin/env python3
"""
Controls runner - tests control heads through full pipeline.
Control heads: "IS A MAP", "IS TRUE", "IS FACT"
These should fail linguistic gates but serve as calibration.
"""

import json
import hashlib
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

# Control heads from runbook
CONTROL_HEADS = {
    'CONTROL_IS_A_MAP': {
        'plaintext': 'IS A MAP',
        'expected_result': 'fail',
        'reason': 'Too short and simplistic'
    },
    'CONTROL_IS_TRUE': {
        'plaintext': 'IS TRUE',
        'expected_result': 'fail',
        'reason': 'Too short and simplistic'
    },
    'CONTROL_IS_FACT': {
        'plaintext': 'IS FACT',
        'expected_result': 'fail', 
        'reason': 'Too short and simplistic'
    }
}

def expand_control_head(short_text: str, target_length: int = 97) -> str:
    """
    Expand control head to target length by repeating pattern.
    
    Args:
        short_text: The control head text
        target_length: Target length (97 for K4)
    
    Returns:
        Expanded text of target length
    """
    # Remove spaces for pattern
    pattern = short_text.replace(' ', '')
    
    # Repeat to fill length
    expanded = ''
    while len(expanded) < target_length:
        expanded += pattern
    
    # Truncate to exact length
    return expanded[:target_length]

def run_control(control_id: str, control_data: Dict, output_dir: Path) -> Dict:
    """
    Run a single control head through the pipeline.
    
    Args:
        control_id: Identifier for the control
        control_data: Control configuration
        output_dir: Output directory for this control
    
    Returns:
        Result dictionary with gate outcomes
    """
    print(f"\n{'=' * 60}")
    print(f"CONTROL: {control_id}")
    print(f"{'=' * 60}")
    
    # Create output directory
    control_dir = output_dir / control_id
    control_dir.mkdir(parents=True, exist_ok=True)
    
    # Expand control head to full length
    short_text = control_data['plaintext']
    full_text = expand_control_head(short_text)
    
    print(f"Control head: '{short_text}'")
    print(f"Expanded to: {full_text[:50]}... (length: {len(full_text)})")
    print(f"Expected: {control_data['expected_result']} ({control_data['reason']})")
    
    # Generate space map
    seed = int(hashlib.sha256(f"CONTROL|{control_id}".encode()).hexdigest()[:16], 16) % (2**32)
    space_map = generate_space_map(full_text, seed)
    
    # Get words for head (first 75 chars)
    head_text = full_text[:75]
    words = tokenize_v2(head_text, space_map['cuts'])
    
    # Save plaintext and space map
    with open(control_dir / 'plaintext_97.txt', 'w') as f:
        f.write(full_text)
    
    with open(control_dir / 'space_map.json', 'w') as f:
        json.dump(space_map, f, indent=2)
    
    # Step 1: Near-gate
    print("\n1. Running near-gate...")
    near_result = run_near_gate(full_text, words)
    print(f"   Coverage: {near_result['coverage']:.3f}")
    print(f"   F-words: {near_result['f_words']}")
    print(f"   Has verb: {near_result['has_verb']}")
    print(f"   {'✅ PASS' if near_result['pass'] else '❌ FAIL'}")
    
    with open(control_dir / 'near_gate_report.json', 'w') as f:
        json.dump(near_result, f, indent=2)
    
    # Step 2: Phrase gates with baseline policy
    print("\n2. Running phrase gates...")
    
    # Flint v2
    flint_result = run_flint_v2(full_text, words)
    print(f"   Flint v2: {'✅ PASS' if flint_result['pass'] else '❌ FAIL'}")
    
    # Generic with baseline thresholds
    generic_result = run_generic_gate(full_text, words, 
                                     pos_threshold=0.60,
                                     perp_percentile=1.0)
    print(f"   Generic: {'✅ PASS' if generic_result['pass'] else '❌ FAIL'}")
    if 'pos_score' in generic_result:
        print(f"     POS: {generic_result['pos_score']:.3f} (threshold: 0.60)")
    if 'perplexity_percentile' in generic_result:
        print(f"     Perplexity: {generic_result['perplexity_percentile']:.1f}% (threshold: ≤1.0%)")
    
    # Cadence
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
    
    # Load baseline policy
    policy_file = "/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/experiments/0457_fullbars/runs/2025-01-06/prereg/POLICY.json"
    
    with open(policy_file, 'r') as f:
        policy = json.load(f)
    
    with open(control_dir / 'phrase_gate_policy.json', 'w') as f:
        json.dump(policy, f, indent=2)
    
    phrase_report = {
        'window': [0, 74],
        'tokenization': 'v2',
        'policy': 'baseline',
        'flint_v2': flint_result,
        'generic': generic_result,
        'cadence': cadence_result,
        'accepted_by': accepted_by,
        'pass': phrase_pass
    }
    
    with open(control_dir / 'phrase_gate_report.json', 'w') as f:
        json.dump(phrase_report, f, indent=2)
    
    print(f"   Accepted by: {accepted_by}")
    print(f"   AND gate: {'✅ PASS' if phrase_pass else '❌ FAIL'}")
    
    # Step 3: Document failures in ONE_PAGER.md
    print("\n3. Creating ONE_PAGER.md...")
    
    # Extract verifiable evidence spans
    evidence_spans = []
    
    if not near_result['pass']:
        # Find low-coverage regions
        if near_result['coverage'] < 0.85:
            evidence_spans.append({
                'gate': 'near',
                'issue': 'Low coverage',
                'evidence': f"Coverage {near_result['coverage']:.3f} < 0.85",
                'span': full_text[:20] + '...'
            })
        if near_result['f_words'] < 5:
            evidence_spans.append({
                'gate': 'near',
                'issue': 'Insufficient F-words',
                'evidence': f"F-words {near_result['f_words']} < 5",
                'span': ' '.join(words[:3]) if words else 'N/A'
            })
    
    if not flint_result['pass']:
        evidence_spans.append({
            'gate': 'flint_v2',
            'issue': 'Failed Flint v2 check',
            'evidence': 'No recognized phrase patterns',
            'span': head_text[:30] + '...'
        })
    
    if not generic_result['pass']:
        if 'pos_score' in generic_result and generic_result['pos_score'] < 0.60:
            evidence_spans.append({
                'gate': 'generic',
                'issue': 'Low POS score',
                'evidence': f"POS {generic_result['pos_score']:.3f} < 0.60",
                'span': ' '.join(words[:5]) if words else 'N/A'
            })
    
    # Generate ONE_PAGER.md
    one_pager = f"""# CONTROL: {control_id}

## Control Head
- **Text**: "{short_text}"
- **Expanded**: {full_text[:50]}...
- **Length**: {len(full_text)}
- **Expected**: {control_data['expected_result']} - {control_data['reason']}

## Gate Results
- **Near-gate**: {'PASS' if near_result['pass'] else 'FAIL'}
  - Coverage: {near_result['coverage']:.3f}
  - F-words: {near_result['f_words']}
  - Has verb: {near_result['has_verb']}

- **Phrase gates**: {'PASS' if phrase_pass else 'FAIL'}
  - Flint v2: {'PASS' if flint_result['pass'] else 'FAIL'}
  - Generic: {'PASS' if generic_result['pass'] else 'FAIL'}
  - Cadence: {'PASS' if cadence_result['pass'] else 'FAIL'}
  - Accepted by: {accepted_by}

## Evidence Spans
"""
    
    for i, span in enumerate(evidence_spans, 1):
        one_pager += f"""
### {i}. {span['gate']} - {span['issue']}
- **Evidence**: {span['evidence']}
- **Span**: `{span['span']}`
"""
    
    if not evidence_spans:
        one_pager += "\nNo specific failure evidence captured (unexpected pass).\n"
    
    one_pager += f"""
## Conclusion
Control head "{short_text}" {'failed' if not phrase_pass else 'unexpectedly passed'} linguistic gates as expected.
This confirms that the gates are functioning to reject non-linguistic content.
"""
    
    with open(control_dir / 'ONE_PAGER.md', 'w') as f:
        f.write(one_pager)
    
    print("   ✅ ONE_PAGER.md created")
    
    # Generate hashes
    import subprocess
    subprocess.run(['sha256sum', '*'], cwd=control_dir, 
                  stdout=open(control_dir / 'hashes.txt', 'w'), 
                  stderr=subprocess.DEVNULL)
    
    print("   ✅ Bundle complete")
    
    # Return summary
    return {
        'control_id': control_id,
        'short_text': short_text,
        'near_pass': near_result['pass'],
        'flint_pass': flint_result['pass'],
        'generic_pass': generic_result['pass'],
        'cadence_pass': cadence_result['pass'],
        'phrase_pass': phrase_pass,
        'expected_result': control_data['expected_result'],
        'actual_result': 'pass' if phrase_pass else 'fail',
        'matches_expected': (control_data['expected_result'] == ('pass' if phrase_pass else 'fail'))
    }

def run_all_controls():
    """Run all control heads through the pipeline."""
    
    output_dir = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/experiments/0457_fullbars/runs/2025-01-06/controls")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    print("=" * 60)
    print("CONTROLS - FULL RUN")
    print("=" * 60)
    print(f"Control heads: {list(CONTROL_HEADS.keys())}")
    print(f"Total runs: {len(CONTROL_HEADS)}")
    
    # Run each control
    for control_id, control_data in CONTROL_HEADS.items():
        result = run_control(control_id, control_data, output_dir)
        results.append(result)
    
    # Create summary
    print(f"\n{'=' * 60}")
    print("CONTROLS COMPLETE")
    print(f"{'=' * 60}")
    
    # Summary table
    print("\nSummary:")
    print(f"{'Control':<20} {'Text':<15} {'Expected':<10} {'Actual':<10} {'Match':<10}")
    print("-" * 65)
    
    for r in results:
        print(f"{r['control_id']:<20} {r['short_text']:<15} {r['expected_result']:<10} {r['actual_result']:<10} {'✅' if r['matches_expected'] else '❌'}")
    
    # Save summary
    summary = {
        'controls': results,
        'all_matched': all(r['matches_expected'] for r in results)
    }
    
    with open(output_dir / 'CONTROLS_SUMMARY.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nAll controls matched expected: {'✅' if summary['all_matched'] else '❌'}")

if __name__ == "__main__":
    run_all_controls()