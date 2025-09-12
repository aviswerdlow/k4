#!/usr/bin/env python3
"""
Sanity check for windowed anchor scoring with synthetic heads.
"""

import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from experiments.pipeline_v2.scripts.explore.compute_score_v2 import (
    compute_normalized_score_v2
)


def run_sanity_check():
    """Run sanity checks with synthetic heads."""
    
    # Create synthetic heads
    heads = [
        # Perfect anchors at expected positions
        {
            "label": "SYNTH_PERFECT",
            "text": "X" * 21 + "EAST" + "NORTHEAST" + "X" * 29 + "BERLINCLOCK" + "X"
        },
        # EAST shifted by +1
        {
            "label": "SYNTH_SHIFT1",
            "text": "X" * 22 + "EAST" + "NORTHEAST" + "X" * 28 + "BERLINCLOCK" + "X"
        },
        # EAST shifted by +2
        {
            "label": "SYNTH_SHIFT2", 
            "text": "X" * 23 + "EAST" + "NORTHEAST" + "X" * 27 + "BERLINCLOCK" + "X"
        },
        # No anchors
        {
            "label": "SYNTH_NONE",
            "text": "X" * 75
        }
    ]
    
    # Create mock baseline stats
    baseline_stats = {
        "ngram_mean": 0.5,
        "ngram_std": 0.2,
        "coverage_mean": 0.3,
        "coverage_std": 0.1,
        "compress_mean": 0.4,
        "compress_std": 0.15
    }
    
    # Load policies
    policy_dir = Path("experiments/pipeline_v2/policies/explore_window")
    policies = {
        "fixed": policy_dir / "POLICY.anchor_fixed_v2.json",
        "r2": policy_dir / "POLICY.anchor_windowed_r2_v2.json",
        "shuffled": policy_dir / "POLICY.anchor_shuffled_v2.json"
    }
    
    policy_configs = {}
    for name, path in policies.items():
        with open(path) as f:
            policy_configs[name] = json.load(f)
    
    print("Sanity Check Results")
    print("=" * 60)
    
    for head in heads:
        print(f"\n{head['label']}:")
        print("-" * 40)
        
        scores = {}
        anchor_scores = {}
        
        for mode_name, policy in policy_configs.items():
            result = compute_normalized_score_v2(head["text"], policy, baseline_stats)
            scores[mode_name] = result["score_norm"]
            anchor_scores[mode_name] = result["anchor_result"]["anchor_score"]
            
            print(f"  {mode_name:8} - Score: {result['score_norm']:.4f}, Anchor: {result['anchor_result']['anchor_score']:.4f}")
        
        # Compute deltas
        delta_fixed_r2 = scores.get("r2", 0) - scores["fixed"]
        delta_fixed_shuffled = scores["fixed"] - scores["shuffled"]
        
        print(f"\n  Deltas:")
        print(f"    fixed vs r2:       {delta_fixed_r2:.4f}")
        print(f"    fixed vs shuffled: {delta_fixed_shuffled:.4f}")
        
        # Validate expectations
        if head["label"] == "SYNTH_PERFECT":
            assert abs(delta_fixed_r2) < 0.01, f"Perfect anchors should have ~0 delta, got {delta_fixed_r2}"
            assert delta_fixed_shuffled > 0.05, f"Fixed should beat shuffled, got {delta_fixed_shuffled}"
            print("    ✓ Perfect anchors behave as expected")
            
        elif head["label"] == "SYNTH_SHIFT1":
            assert delta_fixed_r2 > 0.01, f"Shifted anchor should cause r2 > fixed, got {delta_fixed_r2}"
            print("    ✓ Shifted anchor detected by r2")
            
        elif head["label"] == "SYNTH_NONE":
            assert anchor_scores["fixed"] == 0.0, "No anchors should score 0"
            print("    ✓ Missing anchors score 0")
    
    print("\n" + "=" * 60)
    print("✅ All sanity checks passed!")


if __name__ == "__main__":
    run_sanity_check()