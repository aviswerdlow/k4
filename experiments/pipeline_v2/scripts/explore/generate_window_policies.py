#!/usr/bin/env python3
"""
Generate window policies for Campaign J elasticity grid.
Creates policies for r ∈ {1,2,3,4,5,6} and typo_budget ∈ {0,1,2}.
"""

import json
from pathlib import Path
import hashlib
from typing import Dict


def generate_windowed_policy(r: int, typo_budget: int) -> Dict:
    """Generate a windowed anchor policy."""
    return {
        "name": f"anchor_windowed_r{r}_tb{typo_budget}_v2",
        "description": f"Windowed anchor mode with radius r={r} and typo_budget={typo_budget}",
        "anchor_mode": "windowed",
        "anchor_scoring": {
            "mode": "windowed",
            "anchors": [
                {"token": "EAST", "start": 21},
                {"token": "NORTHEAST", "start": 25},
                {"token": "BERLINCLOCK", "start": 63}
            ],
            "flexibility": {"r": r, "typo_budget": typo_budget},
            "weights": {
                "bonus": 1.0,
                "penalty_miss": 1.0,
                "lambda_pos": 0.5 / r,  # Scale with radius
                "lambda_typo": 0.3 / (typo_budget + 1),  # Scale with typos
                "w_anchor": 0.15,
                "w_zngram": 0.45,
                "w_coverage": 0.25,
                "w_compress": 0.15
            },
            "mask_after_anchor_eval": True
        },
        "scorer": {
            "ngram_weight": 0.4,
            "coverage_weight": 0.3,
            "compress_weight": 0.3,
            "blind_anchors": True,
            "blind_narrative": True
        },
        "blinding_hash": "e5f6a7b8c9d01234",
        "seed": 1337
    }


def generate_all_policies(output_dir: Path) -> None:
    """Generate all window elasticity policies."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    policies_generated = []
    
    # Generate policies for all combinations
    for r in [1, 2, 3, 4, 5, 6]:
        for tb in [0, 1, 2]:
            policy = generate_windowed_policy(r, tb)
            
            filename = f"POLICY.anchor_windowed_r{r}_tb{tb}_v2.json"
            filepath = output_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(policy, f, indent=2)
            
            policies_generated.append(filename)
            print(f"Generated: {filename}")
    
    # Generate manifest
    manifest = {
        "campaign": "EXPLORE_J_WINDOW_ELASTICITY_GRID",
        "date": "2025-01-06",
        "policies": policies_generated,
        "grid": {
            "radius": [1, 2, 3, 4, 5, 6],
            "typo_budget": [0, 1, 2]
        },
        "total_policies": len(policies_generated)
    }
    
    manifest_path = output_dir / "POLICY_MANIFEST.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Compute hash of all policies
    policy_hashes = {}
    for filename in policies_generated:
        with open(output_dir / filename, 'rb') as f:
            policy_hashes[filename] = hashlib.sha256(f.read()).hexdigest()[:16]
    
    hash_path = output_dir / "POLICY_HASHES.json"
    with open(hash_path, 'w') as f:
        json.dump(policy_hashes, f, indent=2)
    
    print(f"\nGenerated {len(policies_generated)} policies")
    print(f"Output: {output_dir}")
    print(f"Manifest: {manifest_path}")


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Generate window elasticity policies")
    parser.add_argument("--out",
                       default="experiments/pipeline_v2/policies/explore_window",
                       type=Path,
                       help="Output directory")
    
    args = parser.parse_args()
    
    generate_all_policies(args.out)


if __name__ == "__main__":
    main()