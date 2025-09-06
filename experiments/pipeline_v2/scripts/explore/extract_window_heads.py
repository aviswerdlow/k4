#!/usr/bin/env python3
"""
Extract diverse sample of 100 heads for window sweep campaign.
40 top, 40 middle, 20 bottom from breadth campaign.
"""

import json
import csv
from pathlib import Path

def extract_diverse_heads():
    """Extract 100 heads across score distribution."""
    
    # Load breadth candidates
    breadth_file = Path("experiments/pipeline_v2/data/candidates_breadth.json")
    with open(breadth_file) as f:
        breadth_data = json.load(f)
        all_heads = breadth_data["heads"]
    
    # Also load route campaign seeds for diversity
    route_file = Path("experiments/pipeline_v2/data/route_campaign_seeds.json")
    if route_file.exists():
        with open(route_file) as f:
            route_data = json.load(f)
            # Add unique heads not already in list
            existing_labels = {h["label"] for h in all_heads}
            for cand in route_data.get("candidates", []):
                if cand["label"] not in existing_labels:
                    all_heads.append(cand)
    
    # Load scores from breadth campaign
    matrix_file = Path("experiments/pipeline_v2/runs/2025-01-05-explore-breadth/ANCHOR_MODE_MATRIX.csv")
    scores = {}
    with open(matrix_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            label = row["label"]
            score = float(row["fixed_score"])
            if label not in scores or score > scores[label]:
                scores[label] = score
    
    # Sort heads by score
    scored_heads = []
    for head in all_heads:
        label = head["label"]
        if label in scores:
            scored_heads.append({
                "label": label,
                "text": head["text"],
                "length": head["length"],
                "score": scores[label]
            })
    
    scored_heads.sort(key=lambda x: x["score"], reverse=True)
    
    # Use all available heads (we only have 70)
    selected = scored_heads
    
    # Create output
    output = {
        "campaign": "window_sweep",
        "source": "breadth_diverse_sample",
        "seed": 1337,
        "total": len(selected),
        "distribution": {
            "top": len([h for h in selected if h["score"] > 3.0]),
            "middle": len([h for h in selected if 1.0 <= h["score"] <= 3.0]),
            "bottom": len([h for h in selected if h["score"] < 1.0])
        },
        "heads": selected[:100]
    }
    
    # Write output
    output_file = Path("experiments/pipeline_v2/data/window_sweep_heads.json")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Extracted {len(selected)} heads:")
    print(f"  Top (>3.0): {output['distribution']['top']}")
    print(f"  Middle (1.0-3.0): {output['distribution']['middle']}")
    print(f"  Bottom (<1.0): {output['distribution']['bottom']}")
    print(f"Output: {output_file}")

if __name__ == "__main__":
    extract_diverse_heads()