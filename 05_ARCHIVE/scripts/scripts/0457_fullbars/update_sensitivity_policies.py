#!/usr/bin/env python3
"""
Update sensitivity policies with cadence SHA references.
"""

import json
from pathlib import Path

def update_policies():
    """Update all sensitivity policies with cadence SHAs."""
    
    base_dir = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/experiments/0457_fullbars/runs/2025-01-06/prereg/sensitivity")
    
    thresholds_sha = "0d6ba5c3c3134e23a080653ef5b083bdd34737ab9ff1d54e728ba20d197e36c1"
    policy_sha = "2161a32ee615f34823cb45b917bc51c6d4e0967fd5c2fb40829901adfbb4defc"
    
    # Update each policy file
    for policy_file in base_dir.glob("POLICY.*.json"):
        with open(policy_file, 'r') as f:
            policy = json.load(f)
        
        # Update cadence_ref
        policy["cadence_ref"] = {
            "thresholds_sha256": thresholds_sha,
            "policy_sha256": policy_sha
        }
        
        with open(policy_file, 'w') as f:
            json.dump(policy, f, indent=2)
        
        print(f"Updated {policy_file.name}")
    
    print("\nAll sensitivity policies updated with cadence SHAs")

if __name__ == "__main__":
    update_policies()