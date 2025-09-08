#!/usr/bin/env python3
"""
Study C - Anchor Perturbations
Tests how "tight" the four plaintext anchors are by shifting their indices ±1
and/or toggling BERLIN/CLOCK split vs combined.
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


def generate_perturbation_scenarios() -> List[Dict]:
    """
    Generate all anchor perturbation scenarios to test.
    
    Returns:
        List of scenario dictionaries
    """
    scenarios = []
    scenario_id = 0
    
    # Baseline anchor starts
    baseline_starts = {
        'EAST': 21,
        'NORTHEAST': 25,
        'BERLIN': 63,
        'CLOCK': 69
    }
    
    # Anchor lengths
    anchor_lengths = {
        'EAST': 4,
        'NORTHEAST': 9,
        'BERLIN': 6,
        'CLOCK': 5
    }
    
    # Test each anchor with ±1 perturbation, keeping others fixed
    for anchor_to_perturb in ['EAST', 'NORTHEAST', 'BERLIN', 'CLOCK']:
        for delta in [-1, 0, 1]:
            # Test both split and combined modes for BERLIN/CLOCK
            for mode in ['SPLIT', 'COMBINED']:
                scenario = {
                    'scenario_id': f"PERT_{scenario_id:03d}",
                    'east_start': baseline_starts['EAST'],
                    'ne_start': baseline_starts['NORTHEAST'],
                    'berlin_start': baseline_starts['BERLIN'],
                    'clock_start': baseline_starts['CLOCK'],
                    'berlin_clock_mode': mode,
                    'description': f"Perturb {anchor_to_perturb} by {delta:+d}, mode={mode}"
                }
                
                # Apply perturbation
                if anchor_to_perturb == 'EAST':
                    scenario['east_start'] += delta
                elif anchor_to_perturb == 'NORTHEAST':
                    scenario['ne_start'] += delta
                elif anchor_to_perturb == 'BERLIN':
                    scenario['berlin_start'] += delta
                elif anchor_to_perturb == 'CLOCK':
                    scenario['clock_start'] += delta
                
                scenarios.append(scenario)
                scenario_id += 1
    
    # Add a few additional interesting scenarios
    # All anchors shifted +1
    scenarios.append({
        'scenario_id': f"PERT_{scenario_id:03d}",
        'east_start': 22,
        'ne_start': 26,
        'berlin_start': 64,
        'clock_start': 70,
        'berlin_clock_mode': 'SPLIT',
        'description': "All anchors +1, split"
    })
    scenario_id += 1
    
    # All anchors shifted -1
    scenarios.append({
        'scenario_id': f"PERT_{scenario_id:03d}",
        'east_start': 20,
        'ne_start': 24,
        'berlin_start': 62,
        'clock_start': 68,
        'berlin_clock_mode': 'SPLIT',
        'description': "All anchors -1, split"
    })
    scenario_id += 1
    
    # Baseline with combined mode only
    scenarios.append({
        'scenario_id': f"PERT_{scenario_id:03d}",
        'east_start': 21,
        'ne_start': 25,
        'berlin_start': 63,
        'clock_start': 69,
        'berlin_clock_mode': 'COMBINED',
        'description': "Baseline positions, combined mode"
    })
    
    return scenarios


def build_anchor_constraints(scenario: Dict) -> Tuple[Dict[str, Tuple[int, int]], Dict[int, str]]:
    """
    Build anchor constraints from a scenario.
    
    Returns:
        (anchors dict, plaintext constraints dict)
    """
    anchors = {}
    pt_constraints = {}
    
    # EAST
    start = scenario['east_start']
    anchors['EAST'] = (start, start + 3)  # Length 4
    for i, char in enumerate('EAST'):
        pt_constraints[start + i] = char
    
    # NORTHEAST
    start = scenario['ne_start']
    anchors['NORTHEAST'] = (start, start + 8)  # Length 9
    for i, char in enumerate('NORTHEAST'):
        pt_constraints[start + i] = char
    
    # BERLIN/CLOCK handling
    if scenario['berlin_clock_mode'] == 'COMBINED':
        # Combined BERLINCLOCK
        start = scenario['berlin_start']
        anchors['BERLINCLOCK'] = (start, start + 10)  # Length 11
        for i, char in enumerate('BERLINCLOCK'):
            pt_constraints[start + i] = char
    else:
        # Split BERLIN and CLOCK
        # BERLIN
        start = scenario['berlin_start']
        anchors['BERLIN'] = (start, start + 5)  # Length 6
        for i, char in enumerate('BERLIN'):
            pt_constraints[start + i] = char
        
        # CLOCK
        start = scenario['clock_start']
        anchors['CLOCK'] = (start, start + 4)  # Length 5
        for i, char in enumerate('CLOCK'):
            pt_constraints[start + i] = char
    
    return anchors, pt_constraints


def test_anchor_perturbation(
    scenario: Dict,
    ciphertext: str
) -> Dict:
    """
    Test a single anchor perturbation scenario.
    
    Args:
        scenario: Scenario configuration
        ciphertext: Full ciphertext
    
    Returns:
        Dict with test results
    """
    start_time = time.time()
    seed_u64 = generate_seed("anchor_perturbations", scenario['scenario_id'])
    
    # Build anchor constraints
    anchors, pt_constraints = build_anchor_constraints(scenario)
    
    # Group indices by baseline class
    class_indices = {c: [] for c in range(6)}
    for i in range(97):
        class_id = compute_baseline_class(i)
        class_indices[class_id].append(i)
    
    # Try to solve wheels
    wheels = {}
    feasible = False
    optionA_ok = True
    
    # Attempt to solve each class
    for class_id in range(6):
        indices = class_indices[class_id]
        
        # Filter constraints for this class
        class_constraints = {i: pt_constraints[i] for i in indices if i in pt_constraints}
        
        if not class_constraints:
            # No anchors in this class - can't solve
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
            break
        
        # Check Option-A violations
        if wheel_config.get('optionA_checks'):
            optionA_ok = False
        
        wheels[class_id] = wheel_config
    
    # Initialize result
    result = {
        'scenario_id': scenario['scenario_id'],
        'east_start': scenario['east_start'],
        'ne_start': scenario['ne_start'],
        'berlin_start': scenario['berlin_start'],
        'clock_start': scenario['clock_start'],
        'berlin_clock_mode': scenario['berlin_clock_mode'],
        'feasible': False,
        'optionA_ok': optionA_ok,
        'wheels_solved': len(wheels) == 6,
        'pt_sha256': "",
        'matches_winner_pt': False,
        'tail_str': "",
        'families_json': "[]",
        'L_json': "[]",
        'phase_json': "[]",
        'seed_u64': seed_u64,
        'runtime_ms': 0
    }
    
    # If all wheels solved, try to derive full PT
    if len(wheels) == 6:
        try:
            # Derive full plaintext with wheels
            derived_pt = derive_plaintext_from_wheels(
                ciphertext,
                wheels,
                compute_baseline_class
            )
            
            # Check if derivation succeeded
            if '?' not in derived_pt:
                result['feasible'] = True
                result['pt_sha256'] = compute_sha256(derived_pt)
                result['tail_str'] = derived_pt[75:]
                
                # Check if matches winner PT
                winner_pt = load_plaintext()
                result['matches_winner_pt'] = (derived_pt == winner_pt)
                
                # Format wheel info
                families = [wheels[i]['family'] for i in sorted(wheels.keys())]
                Ls = [wheels[i]['L'] for i in sorted(wheels.keys())]
                phases = [wheels[i]['phase'] for i in sorted(wheels.keys())]
                
                result['families_json'] = json.dumps(families)
                result['L_json'] = json.dumps(Ls)
                result['phase_json'] = json.dumps(phases)
                
                # Write proof for feasible scenario
                proof_dir = Path("04_EXPERIMENTS/core_hardening/anchor_perturbations/PROOFS")
                proof_dir.mkdir(parents=True, exist_ok=True)
                proof_path = proof_dir / f"perturbation_{scenario['scenario_id']}.json"
                
                write_proof_json(
                    proof_path,
                    "((i%2)*3)+(i%3)",  # Baseline skeleton
                    anchors,
                    wheels,
                    result['pt_sha256'],
                    compute_sha256(ciphertext),
                    seed_u64,
                    scenario['description']
                )
                
        except Exception as e:
            print(f"Error deriving PT for {scenario['scenario_id']}: {e}")
    
    runtime_ms = int((time.time() - start_time) * 1000)
    result['runtime_ms'] = runtime_ms
    
    return result


def run_anchor_perturbations():
    """Main function to run the anchor perturbation study."""
    print("Starting Anchor Perturbation Study...")
    start_time = time.time()
    
    # Setup directories
    study_dir = Path("04_EXPERIMENTS/core_hardening/anchor_perturbations")
    study_dir.mkdir(parents=True, exist_ok=True)
    proofs_dir = study_dir / "PROOFS"
    proofs_dir.mkdir(exist_ok=True)
    
    # Load ciphertext
    ciphertext = load_ciphertext()
    print(f"Loaded CT (hash: {compute_sha256(ciphertext)[:16]}...)")
    
    # Generate perturbation scenarios
    scenarios = generate_perturbation_scenarios()
    print(f"Generated {len(scenarios)} perturbation scenarios to test")
    
    # Prepare CSV
    csv_path = study_dir / "RESULTS.csv"
    csv_file = open(csv_path, 'w', newline='')
    fieldnames = [
        'scenario_id',
        'east_start', 'ne_start', 'berlin_start', 'clock_start', 'berlin_clock_mode',
        'feasible', 'optionA_ok', 'wheels_solved',
        'pt_sha256', 'matches_winner_pt', 'tail_str',
        'families_json', 'L_json', 'phase_json',
        'seed_u64', 'runtime_ms'
    ]
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()
    
    # Process scenarios (with parallelization)
    results = []
    feasible_count = 0
    matching_count = 0
    distinct_tails = set()
    
    with ProcessPoolExecutor(max_workers=min(4, os.cpu_count() or 1)) as executor:
        # Submit all tasks
        future_to_scenario = {}
        for scenario in scenarios:
            future = executor.submit(
                test_anchor_perturbation,
                scenario,
                ciphertext
            )
            future_to_scenario[future] = scenario
        
        # Process results as they complete
        for future in as_completed(future_to_scenario):
            scenario = future_to_scenario[future]
            try:
                result = future.result(timeout=60)
                results.append(result)
                csv_writer.writerow(result)
                csv_file.flush()
                
                if result['feasible']:
                    feasible_count += 1
                    distinct_tails.add(result['tail_str'])
                    if result['matches_winner_pt']:
                        matching_count += 1
                    print(f"  ✓ {scenario['scenario_id']}: FEASIBLE (matches winner: {result['matches_winner_pt']})")
                    print(f"    {scenario['description']}")
                else:
                    print(f"  ✗ {scenario['scenario_id']}: Not feasible ({scenario['description']})")
                    
            except Exception as e:
                print(f"  ! {scenario['scenario_id']}: Error - {e}")
    
    csv_file.close()
    
    # Analyze results for patterns
    baseline_feasible = False
    perturbation_feasible = []
    
    for result in results:
        if result['feasible']:
            # Check if this is baseline configuration
            if (result['east_start'] == 21 and 
                result['ne_start'] == 25 and 
                result['berlin_start'] == 63 and 
                result['clock_start'] == 69):
                baseline_feasible = True
            else:
                perturbation_feasible.append(result)
    
    # Create README
    readme_content = f"""# Anchor Perturbation Study Results

## Overview
This study tested the sensitivity of the four plaintext anchors by shifting their indices ±1 and testing both split and combined modes for BERLIN/CLOCK.

## Test Configuration
- **Base Anchors**: EAST(21), NORTHEAST(25), BERLIN(63), CLOCK(69)
- **Perturbations**: ±1 index shifts per anchor
- **Modes**: SPLIT (BERLIN + CLOCK) vs COMBINED (BERLINCLOCK)
- **Skeleton**: Baseline `((i%2)*3)+(i%3)`

## Results Summary
- **Scenarios Tested**: {len(scenarios)}
- **Feasible Solutions**: {feasible_count}
- **Matching Winner PT**: {matching_count}
- **Distinct Tails Found**: {len(distinct_tails)}

## Key Findings
"""
    
    if baseline_feasible and len(perturbation_feasible) == 0:
        readme_content += """- **Only the baseline anchor positions are feasible**
- No ±1 perturbations produced valid solutions
- This demonstrates the anchors are "tight" - exact positioning is required
- The algebraic constraints are highly sensitive to anchor placement
"""
    elif len(perturbation_feasible) > 0:
        readme_content += f"""- **{len(perturbation_feasible)} perturbations were feasible beyond baseline**
- This suggests some flexibility in anchor positioning
- Feasible perturbations:
"""
        for pert in perturbation_feasible[:5]:  # Show first 5
            readme_content += f"  - {pert['scenario_id']}: EAST={pert['east_start']}, NE={pert['ne_start']}, "
            readme_content += f"BERLIN={pert['berlin_start']}, CLOCK={pert['clock_start']}, mode={pert['berlin_clock_mode']}\n"
        
        if len(perturbation_feasible) > 5:
            readme_content += f"  - ... and {len(perturbation_feasible)-5} more\n"
    
    # Add mode analysis
    split_feasible = sum(1 for r in results if r['feasible'] and r['berlin_clock_mode'] == 'SPLIT')
    combined_feasible = sum(1 for r in results if r['feasible'] and r['berlin_clock_mode'] == 'COMBINED')
    
    readme_content += f"""
## Mode Analysis
- **SPLIT mode feasible**: {split_feasible}
- **COMBINED mode feasible**: {combined_feasible}
"""
    
    if split_feasible > 0 and combined_feasible == 0:
        readme_content += "- Only SPLIT mode (separate BERLIN and CLOCK) produces valid solutions\n"
    elif combined_feasible > 0 and split_feasible == 0:
        readme_content += "- Only COMBINED mode (BERLINCLOCK) produces valid solutions\n"
    elif split_feasible > 0 and combined_feasible > 0:
        readme_content += "- Both SPLIT and COMBINED modes can produce valid solutions\n"
    
    readme_content += """
## Files
- `RESULTS.csv`: Complete test results for all perturbation scenarios
- `PROOFS/`: Proof files for feasible perturbations
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
        "Anchor Perturbation Study",
        start_time,
        end_time,
        len(scenarios),
        feasible_count,
        f"Tested {len(scenarios)} anchor perturbation scenarios"
    )
    
    # Create summary JSON
    create_summary_json(
        study_dir,
        len(scenarios),
        feasible_count,
        matching_count,
        len(distinct_tails),
        "Anchor perturbation study complete"
    )
    
    # Generate manifest
    generate_manifest(study_dir)
    
    print(f"\nAnchor perturbation study complete!")
    print(f"Results written to {csv_path}")
    print(f"Feasible solutions: {feasible_count}/{len(scenarios)}")
    print(f"Matching winner PT: {matching_count}")


if __name__ == "__main__":
    run_anchor_perturbations()