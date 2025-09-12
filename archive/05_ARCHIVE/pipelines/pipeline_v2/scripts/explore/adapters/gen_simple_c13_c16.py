#!/usr/bin/env python3
"""
Simple generators for C13-C16 campaigns.
"""

import random
import json
import hashlib
from pathlib import Path

def generate_simple_heads(campaign_id: str, num_heads: int = 100, seed: int = 1337):
    """Generate simple heads for testing."""
    random.seed(seed)
    
    campaign_names = {
        "C13": "FWM_FunctionWord",
        "C14": "MIGAC_MI_Anchor", 
        "C15": "HTG_POS_HMM",
        "C16": "THCP_TailCohesion"
    }
    
    heads = []
    
    for i in range(num_heads):
        # Simple text generation with anchors
        text = list(''.join(random.choices("ETAOINSHRDLCUMWFGYPBVKJXQZ", k=75)))
        
        # Place anchors
        text[21:25] = list("EAST")
        text[25:34] = list("NORTHEAST")
        text[63:74] = list("BERLINCLOCK")
        
        # Campaign-specific modifications
        if campaign_id == "C13":
            # Add function words
            text[0:3] = list("THE")
            text[10:13] = list("AND")
        elif campaign_id == "C14":
            # MI patterns
            text[19:21] = list("TH")
            text[34:36] = list("EA")
        elif campaign_id == "C15":
            # POS patterns
            text[0:4] = list("FIND")
            text[4:7] = list("THE")
        elif campaign_id == "C16":
            # Tail cohesion
            text[73:75] = list("OF")
        
        head = {
            "label": f"{campaign_id}_{i:03d}",
            "text": ''.join(text),
            "metadata": {
                "campaign": campaign_id,
                "method": campaign_names.get(campaign_id, "unknown"),
                "seed": seed + i
            }
        }
        heads.append(head)
    
    return heads

def main():
    for campaign_id in ["C13", "C14", "C15", "C16"]:
        print(f"Generating {campaign_id}...")
        
        heads = generate_simple_heads(campaign_id, 100, 1337)
        
        output_dir = Path(f"experiments/pipeline_v2/runs/2025-01-06-explore-ideas-{campaign_id}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output = {
            "campaign": campaign_id,
            "date": "2025-01-06",
            "total_heads": len(heads),
            "heads": heads
        }
        
        output_file = output_dir / f"heads_{campaign_id.lower()}.json"
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        # Manifest
        manifest = {
            "campaign": campaign_id,
            "file": str(output_file),
            "hash": hashlib.sha256(json.dumps(output, sort_keys=True).encode()).hexdigest()[:16],
            "heads": len(heads)
        }
        
        manifest_file = output_dir / "MANIFEST.sha256"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"  Saved to {output_file}")

if __name__ == "__main__":
    main()