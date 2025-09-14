#!/usr/bin/env python3
"""
Generate mock light_sweep_results.json for testing the scoring pipeline
"""

import json
import random

def generate_mock_light_sweep():
    """Generate mock light sweep results"""
    
    results = {
        "timestamp": "2025-09-13T00:00:00",
        "method": "cylindrical_projection",
        "selections": {
            "M_15": [],
            "M_20": [],
            "M_24": []
        }
    }
    
    # Generate selections for different angles
    for angle in range(0, 360, 10):  # Every 10 degrees
        # M=15 selections
        indices_15 = sorted(random.sample(range(97), 15))
        results["selections"]["M_15"].append({
            "angle": angle,
            "indices": indices_15,
            "method": "top_illuminated"
        })
        
        # M=20 selections
        indices_20 = sorted(random.sample(range(97), 20))
        results["selections"]["M_20"].append({
            "angle": angle,
            "indices": indices_20,
            "method": "top_illuminated"
        })
        
        # M=24 selections
        indices_24 = sorted(random.sample(range(97), 24))
        results["selections"]["M_24"].append({
            "angle": angle,
            "indices": indices_24,
            "method": "top_illuminated"
        })
    
    # Save as JSON
    with open('light_sweep_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Generated mock light_sweep_results.json")
    print(f"  - Angles: {len(results['selections']['M_15'])} (every 10°)")
    print(f"  - M values: 15, 20, 24")
    print(f"  - Total tests: {len(results['selections']['M_15']) * 3}")
    print("\nThis is a MOCK file for testing only.")
    print("Replace with real projection results when available.")

if __name__ == "__main__":
    generate_mock_light_sweep()