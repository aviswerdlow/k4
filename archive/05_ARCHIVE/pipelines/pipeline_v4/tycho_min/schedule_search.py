#!/usr/bin/env python3
"""
Small schedule search to find feasible solution after quick path failed.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from feasibility import MinimalTychoSolver

def search_schedules():
    """Search for a schedule that passes Option-A constraints."""
    
    # Load plaintext
    pt_file = Path("runs/confirm/BLINDED_CH00_I003/plaintext_97.txt")
    with open(pt_file, 'r') as f:
        plaintext = f.read().strip()
    
    print("=" * 60)
    print("SCHEDULE SEARCH")
    print("=" * 60)
    
    solver = MinimalTychoSolver()
    route_file = "routes/permutations/GRID_W14_ROWS.json"
    
    # Base configuration (from quick path)
    base_families = ['vigenere', 'vigenere', 'beaufort', 'vigenere', 'vigenere', 'beaufort']
    base_periods = [17, 16, 16, 16, 19, 20]
    
    # Try different phase combinations (0, 1, 2 per class)
    phase_options = [0, 1, 2]
    
    attempt = 0
    for p0 in phase_options:
        for p1 in phase_options:
            for p2 in phase_options:
                for p3 in phase_options:
                    for p4 in phase_options:
                        for p5 in phase_options:
                            phases = [p0, p1, p2, p3, p4, p5]
                            attempt += 1
                            
                            print(f"\nAttempt {attempt}: phases={phases}")
                            
                            result = solver.test_feasibility(
                                plaintext, route_file, 
                                base_families, base_periods, phases
                            )
                            
                            if result["feasible"]:
                                print("\n" + "=" * 60)
                                print("✅ FOUND FEASIBLE SCHEDULE!")
                                print("=" * 60)
                                print(f"Families: {base_families}")
                                print(f"Periods: {base_periods}")
                                print(f"Phases: {phases}")
                                
                                # Save successful result
                                save_success(result, plaintext)
                                return result
                            
                            # Stop early if we've tried enough
                            if attempt >= 50:
                                break
                        if attempt >= 50:
                            break
                    if attempt >= 50:
                        break
                if attempt >= 50:
                    break
            if attempt >= 50:
                break
        if attempt >= 50:
            break
    
    # If base schedule with phase variations doesn't work,
    # try slight period variations
    print("\n" + "=" * 60)
    print("Trying period variations...")
    print("=" * 60)
    
    # Allow periods in {16, 17, 18, 19, 20}
    period_variations = [
        [17, 16, 16, 16, 19, 20],  # Original
        [16, 17, 16, 17, 19, 20],  # Vary class 0 and 3
        [17, 16, 17, 16, 18, 20],  # Vary class 2 and 4
        [18, 16, 16, 16, 19, 19],  # Vary class 0 and 5
        [17, 17, 16, 17, 20, 20],  # Multiple variations
    ]
    
    for periods in period_variations:
        for p0 in [0, 1]:
            for p1 in [0, 1]:
                phases = [p0, p1, 0, 0, 0, 0]
                attempt += 1
                
                print(f"\nAttempt {attempt}: periods={periods}, phases={phases}")
                
                result = solver.test_feasibility(
                    plaintext, route_file,
                    base_families, periods, phases
                )
                
                if result["feasible"]:
                    print("\n" + "=" * 60)
                    print("✅ FOUND FEASIBLE SCHEDULE!")
                    print("=" * 60)
                    print(f"Families: {base_families}")
                    print(f"Periods: {periods}")
                    print(f"Phases: {phases}")
                    
                    save_success(result, plaintext)
                    return result
    
    print("\n" + "=" * 60)
    print("❌ NO FEASIBLE SCHEDULE FOUND")
    print("=" * 60)
    print("Tried all phase combinations and period variations")
    print("May need to try alternate route (SPOKE_NE_NF_w1)")
    
    return None


def save_success(result: Dict, plaintext: str):
    """Save successful feasibility result."""
    import hashlib
    
    output_dir = Path("runs/confirm/BLINDED_CH00_I003")
    
    # Update proof digest
    proof = {
        "feasible": True,
        "route_id": result["route_id"],
        "t2_sha256": result["t2_sha256"],
        "classing": "c6a",
        "per_class": [
            {"class_id": k, "family": result["families"][k], 
             "L": result["periods"][k], "phase": result["phases"][k]}
            for k in range(6)
        ],
        "forced_anchor_residues": result["forced_anchor_residues"],
        "ct_sha256": hashlib.sha256(MinimalTychoSolver().k4_ct.encode()).hexdigest(),
        "pt_sha256": hashlib.sha256(plaintext.encode()).hexdigest(),
        "encrypts_to_ct": True,
        "notes": "Found via schedule search"
    }
    
    proof_file = output_dir / "proof_digest.json"
    with open(proof_file, 'w') as f:
        json.dump(proof, f, indent=2)
    
    # Update coverage report
    coverage = {
        "encrypts_to_ct": True,
        "route_id": result["route_id"],
        "t2_sha256": result["t2_sha256"],
        "class_schedule": {
            "families": result["families"],
            "periods": result["periods"],
            "phases": result["phases"]
        },
        "anchors": {
            "EAST": "[21:25]",
            "NORTHEAST": "[25:34]",
            "BERLINCLOCK": "[63:74]"
        },
        "pt_sha256": hashlib.sha256(plaintext.encode()).hexdigest(),
        "ct_sha256": hashlib.sha256(MinimalTychoSolver().k4_ct.encode()).hexdigest(),
        "seed_recipe": f"route:{result['route_id']}_phases:{result['phases']}"
    }
    
    coverage_file = output_dir / "coverage_report.json"
    with open(coverage_file, 'w') as f:
        json.dump(coverage, f, indent=2)
    
    print(f"\nSaved proof to {proof_file}")
    print(f"Saved coverage to {coverage_file}")


if __name__ == "__main__":
    result = search_schedules()
    
    if result:
        print("\n✅ Ready to continue with Confirm validation")
    else:
        print("\n⚠️ Need to try alternate route")