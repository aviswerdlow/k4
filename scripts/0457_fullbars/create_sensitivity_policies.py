#!/usr/bin/env python3
"""
Create 9 sensitivity policy JSONs for the 3x3 grid.
"""

import json
import os
from pathlib import Path

def create_sensitivity_policies():
    """Create 9 sensitivity policy JSONs."""
    
    base_dir = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/experiments/0457_fullbars/runs/2025-01-06/prereg/sensitivity")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Grid parameters
    pos_thresholds = [0.55, 0.60, 0.65]
    perp_percentiles = [1.5, 1.0, 0.5]
    
    # Common policy structure
    base_policy = {
        "program": "phrase_gate",
        "combine": "AND",
        "window": [0, 74],
        "tokenization": "v2",
        "flint_v2": {
            "declination_patterns": [
                ["SET", "COURSE"], ["ADJUST", "HEADING"],
                ["CORRECT", "FOR"], ["TRUE", "NORTH"]
            ],
            "instrument_verbs": ["READ", "SEE", "NOTE", "SIGHT", "OBSERVE"],
            "directions": ["EAST", "NORTHEAST"],
            "nouns": ["BERLIN", "CLOCK", "BERLINCLOCK", "DIAL"],
            "min_content": 6,
            "max_repeat": 2
        },
        "cadence_ref": {
            "thresholds_sha256": "<sha256 of cadence/THRESHOLDS.json>",
            "policy_sha256": "<sha256 of POLICY.cadence.json>"
        }
    }
    
    # Create each policy variant
    for pos in pos_thresholds:
        for perp in perp_percentiles:
            policy = base_policy.copy()
            policy["generic"] = {
                "perplexity_top_percent": perp,
                "pos_threshold": pos,
                "calibration_hashes": {
                    "calib_97_perplexity.json": "<sha256>",
                    "pos_trigrams.json": "<sha256>",
                    "pos_threshold.txt": "<sha256>"
                }
            }
            
            # Filename format
            filename = f"POLICY.pos{int(pos*100):03d}.perp{int(perp*10):02d}.json"
            filepath = base_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(policy, f, indent=2)
            
            print(f"Created {filename}")
    
    print(f"\nCreated 9 sensitivity policies in {base_dir}")

if __name__ == "__main__":
    create_sensitivity_policies()