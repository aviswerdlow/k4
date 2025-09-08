#!/usr/bin/env python3
"""
Study B - Tail Necessity
Tests whether any single-letter change in the tail (indices 75..96) can produce
a complete, algebraically consistent PT given CT + anchors + baseline skeleton.
"""

import sys
import time
import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
import os

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from core_hardening_utils import *


def test_tail_mutation(
    index: int,
    orig_letter: str,
    mutant_letter: str,
    ciphertext: str,
    baseline_pt: str,
    anchors: Dict[str, Tuple[int, int]]
) -> Dict:
    """
    Test a single tail mutation scenario.
    
    Args:
        index: Position to mutate (75-96)
        orig_letter: Original letter at this position
        mutant_letter: Letter to try as mutation
        ciphertext: Full ciphertext
        baseline_pt: Original plaintext
        anchors: Anchor constraints
    
    Returns:
        Dict with test results
    """
    start_time = time.time()
    seed_u64 = generate_seed("tail_necessity", f"{index}_{mutant_letter}")
    
    # Build plaintext constraints: anchors + mutation
    pt_constraints = get_anchor_plaintext(anchors)
    pt_constraints[index] = mutant_letter  # Add the mutation constraint
    
    # Group indices by baseline class
    class_indices = {c: [] for c in range(6)}
    for i in range(97):
        class_id = compute_baseline_class(i)
        class_indices[class_id].append(i)
    
    # Try to solve wheels with mutation constraint
    wheels = {}
    feasible = False
    failure_reason = ""
    
    # Attempt to solve each class
    for class_id in range(6):
        indices = class_indices[class_id]
        
        # Filter constraints for this class
        class_constraints = {i: pt_constraints[i] for i in indices if i in pt_constraints}
        
        if not class_constraints:
            failure_reason = "solve_fail"
            break
        
        # Attempt to solve wheel
        wheel_config = solve_class_wheel(
            class_id,
            indices,
            ciphertext,
            class_constraints,
            enforce_option_a=True
        )
        
        if wheel_config is None:
            failure_reason = "solve_fail"
            break
        
        # Check Option-A violations
        if wheel_config.get('optionA_checks'):
            failure_reason = "optionA_fail"
            break
        
        wheels[class_id] = wheel_config
    
    # Initialize result
    result = {
        'index': index,
        'orig_letter': orig_letter,
        'mutant_letter': mutant_letter,
        'feasible': False,
        'failure_reason': failure_reason if failure_reason else "",
        'pt_sha256_mutant': "",
        'families_json': "[]",
        'L_json': "[]",
        'phase_json': "[]",
        'seed_u64': seed_u64,
        'runtime_ms': 0
    }
    
    # If all wheels solved, try to derive full PT
    if len(wheels) == 6 and not failure_reason:
        try:
            # Derive full plaintext with wheels
            derived_pt = derive_plaintext_from_wheels(
                ciphertext, 
                wheels, 
                compute_baseline_class
            )
            
            # Check if derivation succeeded
            if '?' not in derived_pt:
                # Verify the mutation is present
                if derived_pt[index] == mutant_letter:
                    # Check if this is the ONLY change (besides potential cascading changes)
                    # For now, we accept it as feasible if mutation is present
                    result['feasible'] = True
                    result['pt_sha256_mutant'] = compute_sha256(derived_pt)
                    
                    # Format wheel info
                    families = [wheels[i]['family'] for i in sorted(wheels.keys())]
                    Ls = [wheels[i]['L'] for i in sorted(wheels.keys())]
                    phases = [wheels[i]['phase'] for i in sorted(wheels.keys())]
                    
                    result['families_json'] = json.dumps(families)
                    result['L_json'] = json.dumps(Ls)
                    result['phase_json'] = json.dumps(phases)
                    
                    # Write proof for feasible mutation
                    proof_dir = Path("04_EXPERIMENTS/core_hardening/tail_necessity/MUTANTS")
                    proof_dir.mkdir(parents=True, exist_ok=True)
                    proof_path = proof_dir / f"mutant_{index}_{mutant_letter}.json"
                    
                    write_proof_json(
                        proof_path,
                        "((i%2)*3)+(i%3)",  # Baseline skeleton
                        anchors,
                        wheels,
                        result['pt_sha256_mutant'],
                        compute_sha256(ciphertext),
                        seed_u64,
                        f"Tail mutation at index {index}: {orig_letter} -> {mutant_letter}"
                    )
                    
                    # Also save the mutant plaintext
                    mutant_pt_path = proof_dir / f"mutant_{index}_{mutant_letter}_plaintext.txt"
                    with open(mutant_pt_path, 'w') as f:
                        f.write(derived_pt)
                else:
                    result['failure_reason'] = "mutation_not_preserved"
            else:
                result['failure_reason'] = "incomplete_derivation"
                
        except Exception as e:
            result['failure_reason'] = f"derivation_error: {str(e)}"
    
    runtime_ms = int((time.time() - start_time) * 1000)
    result['runtime_ms'] = runtime_ms
    
    return result


def run_tail_necessity():
    """Main function to run the tail necessity study."""
    print("Starting Tail Necessity Study...")
    start_time = time.time()
    
    # Setup directories
    study_dir = Path("04_EXPERIMENTS/core_hardening/tail_necessity")
    study_dir.mkdir(parents=True, exist_ok=True)
    mutants_dir = study_dir / "MUTANTS"
    mutants_dir.mkdir(exist_ok=True)
    
    # Load data
    ciphertext = load_ciphertext()
    baseline_pt = load_plaintext()
    print(f"Loaded CT (hash: {compute_sha256(ciphertext)[:16]}...)")
    print(f"Loaded baseline PT (hash: {compute_sha256(baseline_pt)[:16]}...)")
    
    # Generate all mutation scenarios
    scenarios = []
    for index in range(75, 97):  # Indices 75-96 (tail)
        orig_letter = baseline_pt[index]
        for mutant_letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if mutant_letter != orig_letter:
                scenarios.append((index, orig_letter, mutant_letter))
    
    print(f"Generated {len(scenarios)} mutation scenarios to test")
    
    # Prepare CSV
    csv_path = study_dir / "RESULTS.csv"
    csv_file = open(csv_path, 'w', newline='')
    fieldnames = [
        'index', 'orig_letter', 'mutant_letter',
        'feasible', 'failure_reason', 'pt_sha256_mutant',
        'families_json', 'L_json', 'phase_json',
        'seed_u64', 'runtime_ms'
    ]
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()
    
    # Process mutations (with parallelization)
    results = []
    feasible_count = 0
    failure_reasons = {}
    
    with ProcessPoolExecutor(max_workers=min(8, os.cpu_count() or 1)) as executor:
        # Submit all tasks
        future_to_scenario = {}
        for index, orig_letter, mutant_letter in scenarios:
            future = executor.submit(
                test_tail_mutation,
                index,
                orig_letter,
                mutant_letter,
                ciphertext,
                baseline_pt,
                BASELINE_ANCHORS
            )
            future_to_scenario[future] = (index, orig_letter, mutant_letter)
        
        # Process results as they complete
        completed = 0
        for future in as_completed(future_to_scenario):
            index, orig_letter, mutant_letter = future_to_scenario[future]
            try:
                result = future.result(timeout=30)
                results.append(result)
                csv_writer.writerow(result)
                csv_file.flush()
                
                completed += 1
                
                if result['feasible']:
                    feasible_count += 1
                    print(f"  ✓ [{completed}/{len(scenarios)}] Index {index}: {orig_letter}->{mutant_letter} FEASIBLE!")
                else:
                    reason = result['failure_reason']
                    failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
                    if completed % 50 == 0:
                        print(f"  ✗ [{completed}/{len(scenarios)}] Progress... (0 feasible so far)")
                        
            except Exception as e:
                print(f"  ! Index {index}, {orig_letter}->{mutant_letter}: Error - {e}")
                error_result = {
                    'index': index,
                    'orig_letter': orig_letter,
                    'mutant_letter': mutant_letter,
                    'feasible': False,
                    'failure_reason': f"error: {str(e)}",
                    'pt_sha256_mutant': "",
                    'families_json': "[]",
                    'L_json': "[]",
                    'phase_json': "[]",
                    'seed_u64': generate_seed("tail_necessity", f"{index}_{mutant_letter}"),
                    'runtime_ms': 0
                }
                results.append(error_result)
                csv_writer.writerow(error_result)
    
    csv_file.close()
    
    # Create README
    readme_content = f"""# Tail Necessity Study Results

## Overview
This study tested whether any single-letter change in the tail (indices 75-96) could produce a complete, algebraically consistent plaintext given the ciphertext, baseline anchors, and baseline skeleton.

## Test Configuration
- **Tail Indices**: 75-96 (22 positions)
- **Mutations per Position**: 25 (all letters except original)
- **Total Scenarios**: {len(scenarios)}
- **Skeleton**: Baseline `((i%2)*3)+(i%3)`
- **Anchors**: EAST(21-24), NORTHEAST(25-33), BERLIN(63-68), CLOCK(69-73)

## Results Summary
- **Scenarios Tested**: {len(scenarios)}
- **Feasible Mutations**: {feasible_count}
- **Success Rate**: {(feasible_count/len(scenarios)*100):.2f}%

## Failure Analysis
"""
    
    for reason, count in sorted(failure_reasons.items(), key=lambda x: -x[1]):
        percentage = (count/len(scenarios)*100)
        readme_content += f"- `{reason}`: {count} ({percentage:.1f}%)\n"
    
    if feasible_count == 0:
        readme_content += """
## Key Finding
**No single-letter mutations in the tail were feasible.** This strongly supports that:
1. The tail is algebraically locked by the wheel system
2. The plaintext anchors fully determine the tail through the wheels
3. No alternative tail characters can satisfy the algebraic constraints
"""
    else:
        readme_content += f"""
## UNEXPECTED RESULT
**{feasible_count} mutations were found to be feasible!** This requires further investigation:
1. Check the MUTANTS/ directory for proof files
2. Examine the mutant plaintexts to understand the changes
3. Verify the algebraic consistency of these solutions
"""
    
    readme_content += """
## Files
- `RESULTS.csv`: Complete test results for all 550 mutations
- `MUTANTS/`: Proof files for any feasible mutations (if found)
- `RUN_LOG.md`: Execution details and environment info
- `SUMMARY.json`: Machine-readable summary
"""
    
    readme_path = study_dir / "README.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    # Create run log
    end_time = time.time()
    create_run_log(
        study_dir,
        "Tail Necessity Study",
        start_time,
        end_time,
        len(scenarios),
        feasible_count,
        f"Tested {len(scenarios)} single-letter tail mutations"
    )
    
    # Create summary JSON
    create_summary_json(
        study_dir,
        len(scenarios),
        feasible_count,
        0,  # No matching PT in this study
        feasible_count,  # Each feasible mutation is a distinct tail
        "Tail necessity study complete"
    )
    
    # Generate manifest
    generate_manifest(study_dir)
    
    print(f"\nTail necessity study complete!")
    print(f"Results written to {csv_path}")
    print(f"Feasible mutations: {feasible_count}/{len(scenarios)}")
    if feasible_count > 0:
        print(f"⚠️  UNEXPECTED: Found {feasible_count} feasible mutations - check MUTANTS/ directory")


if __name__ == "__main__":
    run_tail_necessity()