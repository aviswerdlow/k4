#!/usr/bin/env python3
"""
Create 9 sensitivity policies + publication baseline for 04:57 execution.
"""

import json
import hashlib
from pathlib import Path

def create_policy(pos_threshold, perplexity_percentile):
    """Create a policy with specified POS and perplexity thresholds."""
    return {
        "rails": {
            "anchors_0idx": { 
                "EAST": [21, 24], 
                "NORTHEAST": [25, 33], 
                "BERLINCLOCK": [63, 73] 
            },
            "head_lock": [0, 74],
            "tail_guard": None,  # Seam ignored for decision
            "na_only": True,
            "option_A": True,
            "ct_sha256": "eea813570c7f1fd3b34674e47b5c3da8948026f5cefee612a0b38ffaa515ceab"
        },
        "model_class": "GRID_ONLY",
        "routes_whitelist": ["GRID_W14_ROWS", "GRID_W10_NW"],  # Two GRID routes
        "phrase_gate": {
            "combine": "AND",
            "tokenization_v2": True,
            "flint_v2": { 
                "directions": ["EAST", "NORTHEAST"], 
                "instrument_verbs": ["READ", "SEE", "NOTE", "SIGHT", "OBSERVE"],
                "instrument_nouns": ["BERLIN", "CLOCK", "BERLINCLOCK", "DIAL"], 
                "min_content": 6, 
                "max_repeat": 2 
            },
            "generic": { 
                "percentile_top": perplexity_percentile, 
                "pos_threshold": pos_threshold, 
                "min_content": 6, 
                "max_repeat": 2,
                "calibration_hashes": {
                    "calib_97_perplexity.json": "9bbcf015635ccf5b1a3b225f9732d9a587c32eb97ab1eaeb3f52742aecdc45db",
                    "pos_trigrams.json": "a5fad7d87294b1c968e58e43e0106bbb49b377e952cdb420db92ce65cdfda3b9", 
                    "pos_threshold.txt": "7d680231e9793ecd6ad7252404e91c726e564cd57fcbf140289b9256e077143d"
                }
            }
        },
        "nulls": { 
            "K": 10000, 
            "holm_m": 2, 
            "metric_order": ["coverage", "f_words"], 
            "adj_p_threshold": 0.01 
        }
    }

def main():
    base_dir = Path("experiments/0457_exec/policies/sensitivity")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Define the 3x3 grid
    pos_values = [0.55, 0.60, 0.65]
    ppct_values = [1.5, 1.0, 0.5]
    
    policy_hashes = {}
    
    # Create 9 sensitivity policies
    for pos in pos_values:
        for ppct in ppct_values:
            policy = create_policy(pos, ppct)
            
            # Format filename
            pos_str = f"{int(pos * 100):03d}"
            ppct_str = f"{int(ppct * 10):02d}" if ppct >= 1.0 else f"0{int(ppct * 10)}"
            filename = f"POLICY.pos{pos_str}_pp{ppct_str}.json"
            filepath = base_dir / filename
            
            # Write policy
            with open(filepath, 'w') as f:
                json.dump(policy, f, indent=2)
            
            # Calculate SHA-256
            with open(filepath, 'rb') as f:
                sha256 = hashlib.sha256(f.read()).hexdigest()
            policy_hashes[filename] = sha256
            
            print(f"Created {filename} - SHA256: {sha256}")
    
    # Create publication baseline (pos=0.60, ppct=1.0)
    pub_policy = create_policy(0.60, 1.0)
    pub_path = Path("experiments/0457_exec/policies/POLICY.publication.json")
    with open(pub_path, 'w') as f:
        json.dump(pub_policy, f, indent=2)
    
    with open(pub_path, 'rb') as f:
        pub_sha = hashlib.sha256(f.read()).hexdigest()
    policy_hashes["POLICY.publication.json"] = pub_sha
    print(f"Created POLICY.publication.json - SHA256: {pub_sha}")
    
    # Save hashes for receipts
    with open("experiments/0457_exec/docs/policy_hashes.json", 'w') as f:
        json.dump(policy_hashes, f, indent=2)
    
    print(f"\nAll policies created. Hashes saved to policy_hashes.json")

if __name__ == "__main__":
    main()