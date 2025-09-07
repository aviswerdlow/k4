#!/usr/bin/env python3
"""
Campaign C8: Corridor Drift & Elastic Anchors (CDEA)
Test smooth drift in expected anchor indices across the head.
"""

import random
import hashlib
import string
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
import numpy as np

# Expected anchor positions (baseline)
ANCHOR_BASELINE = {
    "EAST": 21,
    "NORTHEAST": 25,
    "BERLINCLOCK": 63
}


def drift_function(index: int, a: float, b: float, drift_type: str = "linear") -> float:
    """
    Calculate drift at given index.
    
    Args:
        index: Position in head (0-74)
        a: Linear coefficient
        b: Constant offset
        drift_type: "linear" or "quadratic"
    
    Returns:
        Drift amount (capped at ±4)
    """
    if drift_type == "linear":
        drift = a * index + b
    else:  # quadratic
        drift = a * index**2 / 100 + b  # Scale down quadratic term
    
    # Cap drift at ±4
    return max(-4, min(4, drift))


def generate_drifted_head(
    base_text: str,
    a: float,
    b: float,
    drift_type: str,
    seed: int
) -> Dict:
    """
    Generate a head with drifted anchor positions.
    
    Args:
        base_text: Base text to modify
        a: Drift coefficient
        b: Drift offset
        drift_type: Type of drift function
        seed: Random seed
    
    Returns:
        Head dictionary with metadata
    """
    random.seed(seed)
    
    # Start with random base or pattern
    if base_text == "random":
        text = list(''.join(random.choices(string.ascii_uppercase, k=75)))
    else:
        text = list(base_text[:75].ljust(75, 'X'))
    
    # Apply drift to anchor positions
    drifted_positions = {}
    
    for anchor, base_pos in ANCHOR_BASELINE.items():
        drift = drift_function(base_pos, a, b, drift_type)
        new_pos = int(base_pos + drift)
        
        # Ensure within bounds
        if anchor == "EAST":
            new_pos = max(4, min(new_pos, 71))  # Leave room for "EAST"
        elif anchor == "NORTHEAST":
            new_pos = max(9, min(new_pos, 66))  # Leave room for "NORTHEAST"
        else:  # BERLINCLOCK
            new_pos = max(11, min(new_pos, 64))  # Leave room for "BERLINCLOCK"
        
        drifted_positions[anchor] = new_pos
        
        # Place anchor at drifted position
        anchor_text = anchor
        for i, char in enumerate(anchor_text):
            if new_pos + i < 75:
                text[new_pos + i] = char
    
    # Fill gaps with plausible text
    for i in range(75):
        if text[i] == 'X' or text[i] not in string.ascii_uppercase:
            # Sample from common letters
            text[i] = random.choice("ETAOINSHRDLCUMWFGYPBVKJXQZ")
    
    return {
        "text": ''.join(text),
        "drift_a": a,
        "drift_b": b,
        "drift_type": drift_type,
        "drifted_positions": drifted_positions,
        "seed": seed
    }


def generate_cdea_heads(
    num_heads: int = 100,
    a_range: Tuple[float, float] = (-0.05, 0.05),
    b_range: Tuple[float, float] = (-2, 2),
    steps: int = 10,
    seed: int = 1337
) -> List[Dict]:
    """
    Generate CDEA heads with corridor drift.
    
    Args:
        num_heads: Target number of heads
        a_range: Range for linear coefficient
        b_range: Range for constant offset
        steps: Number of steps in grid
        seed: Random seed
    
    Returns:
        List of candidate heads
    """
    random.seed(seed)
    heads = []
    
    # Create grid of parameters
    a_values = np.linspace(a_range[0], a_range[1], steps)
    b_values = np.linspace(b_range[0], b_range[1], steps)
    
    head_idx = 0
    for a in a_values:
        for b in b_values:
            if head_idx >= num_heads:
                break
                
            for drift_type in ["linear", "quadratic"]:
                if head_idx >= num_heads:
                    break
                
                # Generate head with this drift
                result = generate_drifted_head(
                    "random",
                    a, b, drift_type,
                    seed + head_idx
                )
                
                head = {
                    "label": f"CDEA_{head_idx:03d}",
                    "text": result["text"],
                    "metadata": {
                        "drift_a": float(a),
                        "drift_b": float(b),
                        "drift_type": drift_type,
                        "drifted_positions": result["drifted_positions"],
                        "max_drift": max(abs(drift_function(i, a, b, drift_type)) 
                                       for i in range(75)),
                        "seed": result["seed"]
                    }
                }
                heads.append(head)
                head_idx += 1
    
    return heads[:num_heads]


def run_campaign_c8(output_dir: Path, seed: int = 1337):
    """
    Run Campaign C8: CDEA testing.
    
    Args:
        output_dir: Directory for output files
        seed: Random seed
    """
    print("Campaign C8: Corridor Drift & Elastic Anchors (CDEA)")
    print(f"  Drift types: linear, quadratic")
    print(f"  a range: -0.05 to 0.05")
    print(f"  b range: -2 to 2")
    print(f"  Max drift: ±4")
    
    # Generate heads
    heads = generate_cdea_heads(
        num_heads=100,
        a_range=(-0.05, 0.05),
        b_range=(-2, 2),
        steps=10,
        seed=seed
    )
    
    # Analyze drift statistics
    drift_stats = {
        "linear": 0,
        "quadratic": 0,
        "max_drifts": []
    }
    
    for head in heads:
        drift_stats[head["metadata"]["drift_type"]] += 1
        drift_stats["max_drifts"].append(head["metadata"]["max_drift"])
    
    print(f"\nGenerated {len(heads)} heads:")
    print(f"  Linear drift: {drift_stats['linear']}")
    print(f"  Quadratic drift: {drift_stats['quadratic']}")
    print(f"  Max drift range: {min(drift_stats['max_drifts']):.2f} to {max(drift_stats['max_drifts']):.2f}")
    
    # Create output structure
    output = {
        "campaign": "C8_CDEA",
        "date": "2025-01-06",
        "description": "Corridor Drift & Elastic Anchors",
        "hypothesis": "Smooth drift in anchor indices reveals corridor-consistent heads",
        "parameters": {
            "a_range": [-0.05, 0.05],
            "b_range": [-2, 2],
            "drift_types": ["linear", "quadratic"],
            "max_drift": 4
        },
        "seed": seed,
        "total_heads": len(heads),
        "drift_distribution": {
            "linear": drift_stats["linear"],
            "quadratic": drift_stats["quadratic"]
        },
        "heads": heads
    }
    
    # Save output
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "heads_c8_cdea.json"
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nOutput saved to: {output_file}")
    
    # Create manifest
    manifest = {
        "campaign": "C8",
        "file": str(output_file),
        "hash": hashlib.sha256(json.dumps(output, sort_keys=True).encode()).hexdigest()[:16],
        "heads": len(heads)
    }
    
    manifest_file = output_dir / "MANIFEST.sha256"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return heads


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Generate CDEA heads")
    parser.add_argument("--output",
                       default="experiments/pipeline_v2/runs/2025-01-06-explore-ideas-C8",
                       help="Output directory")
    parser.add_argument("--seed", type=int, default=1337,
                       help="Random seed")
    
    args = parser.parse_args()
    
    run_campaign_c8(Path(args.output), args.seed)


if __name__ == "__main__":
    main()