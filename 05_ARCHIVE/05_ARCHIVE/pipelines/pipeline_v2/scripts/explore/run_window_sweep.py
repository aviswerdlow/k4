#!/usr/bin/env python3
"""
Run window sweep campaign to measure where windowed diverges from fixed.
Tests r ∈ {2,3,4} to find divergence point r₀.
"""

import json
import csv
import hashlib
import random
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import sys

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from experiments.pipeline_v2.scripts.explore.run_explore_hard import (
    compute_normalized_score
)

def run_window_sweep(
    candidates_file: Path,
    policy_dir: Path,
    baseline_stats_file: Path,
    output_dir: Path,
    seed: int = 1337
) -> None:
    """
    Run window sweep campaign with multiple radius values.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load inputs
    with open(candidates_file) as f:
        data = json.load(f)
        heads = data["heads"]
    
    with open(baseline_stats_file) as f:
        baseline_stats = json.load(f)
    
    # Load policies
    policies = {
        "fixed": policy_dir / "POLICY.anchor_fixed.json",
        "r2": policy_dir / "POLICY.anchor_windowed_r2.json",
        "r3": policy_dir / "POLICY.anchor_windowed_r3.json",
        "r4": policy_dir / "POLICY.anchor_windowed_r4.json",
        "shuffled": policy_dir / "POLICY.anchor_shuffled.json"
    }
    
    policy_configs = {}
    for name, path in policies.items():
        with open(path) as f:
            policy_configs[name] = json.load(f)
    
    print(f"Testing {len(heads)} heads × {len(policies)} modes")
    print(f"Modes: {list(policies.keys())}")
    
    # Run all heads through all modes
    results = []
    
    for head_idx, head in enumerate(heads):
        text = head["text"]
        label = head["label"]
        
        if head_idx % 10 == 0:
            print(f"Processing head {head_idx+1}/{len(heads)}: {label}")
        
        head_scores = {}
        
        for mode_name, policy in policy_configs.items():
            # For shuffled mode, randomize anchor positions
            if mode_name == "shuffled":
                random.seed(seed + head_idx)
                for anchor in policy["anchor_config"]["anchors"]:
                    span = policy["anchor_config"]["anchors"][anchor]["span"]
                    length = span[1] - span[0]
                    new_start = random.randint(0, len(text) - length - 1)
                    policy["anchor_config"]["anchors"][anchor]["span"] = [
                        new_start, new_start + length
                    ]
            
            # Compute normalized score
            score_data = compute_normalized_score(text, policy, baseline_stats)
            
            result = {
                "label": label,
                "route": "GRID_W14_ROWS",  # Using single route for measurement
                "mode": mode_name,
                "score_norm": score_data["score_norm"],
                "z_ngram": score_data["z_ngram"],
                "z_coverage": score_data["z_coverage"],
                "z_compress": score_data["z_compress"]
            }
            results.append(result)
            head_scores[mode_name] = score_data["score_norm"]
        
        # Compute deltas for this head
        delta_result = {
            "label": label,
            "route": "GRID_W14_ROWS",
            "delta_vs_shuffled_fixed": head_scores["fixed"] - head_scores["shuffled"],
            "delta_vs_shuffled_r2": head_scores["r2"] - head_scores["shuffled"],
            "delta_vs_shuffled_r3": head_scores["r3"] - head_scores["shuffled"],
            "delta_vs_shuffled_r4": head_scores["r4"] - head_scores["shuffled"],
            "delta_vs_fixed_r2": head_scores["r2"] - head_scores["fixed"],
            "delta_vs_fixed_r3": head_scores["r3"] - head_scores["fixed"],
            "delta_vs_fixed_r4": head_scores["r4"] - head_scores["fixed"]
        }
    
    # Write ANCHOR_MODE_MATRIX.csv
    matrix_path = output_dir / "ANCHOR_MODE_MATRIX.csv"
    with open(matrix_path, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    # Compute delta curves
    delta_curves = []
    
    for label in {r["label"] for r in results}:
        head_results = [r for r in results if r["label"] == label]
        scores = {r["mode"]: r["score_norm"] for r in head_results}
        
        curve = {
            "label": label,
            "route": "GRID_W14_ROWS",
            "delta_vs_shuffled_fixed": scores["fixed"] - scores["shuffled"],
            "delta_vs_shuffled_r2": scores["r2"] - scores["shuffled"],
            "delta_vs_shuffled_r3": scores["r3"] - scores["shuffled"],
            "delta_vs_shuffled_r4": scores["r4"] - scores["shuffled"],
            "delta_vs_fixed_r2": scores["r2"] - scores["fixed"],
            "delta_vs_fixed_r3": scores["r3"] - scores["fixed"],
            "delta_vs_fixed_r4": scores["r4"] - scores["fixed"]
        }
        delta_curves.append(curve)
    
    # Write DELTA_CURVES.csv
    curves_path = output_dir / "DELTA_CURVES.csv"
    with open(curves_path, 'w', newline='') as f:
        if delta_curves:
            writer = csv.DictWriter(f, fieldnames=delta_curves[0].keys())
            writer.writeheader()
            writer.writerows(delta_curves)
    
    # Compute aggregate statistics
    mean_divergence = {
        "r2": np.mean([abs(d["delta_vs_fixed_r2"]) for d in delta_curves]),
        "r3": np.mean([abs(d["delta_vs_fixed_r3"]) for d in delta_curves]),
        "r4": np.mean([abs(d["delta_vs_fixed_r4"]) for d in delta_curves])
    }
    
    # Find r₀ (divergence point)
    r0 = None
    for r, divergence in sorted(mean_divergence.items()):
        if divergence > 0.01:
            r0 = int(r[1])
            break
    
    # Generate report
    report_path = output_dir / "WINDOW_CURVES.md"
    with open(report_path, 'w') as f:
        f.write("# Window Sweep Campaign Report\n\n")
        f.write(f"**Date:** {datetime.now().date()}\n")
        f.write(f"**Heads tested:** {len(heads)}\n")
        f.write(f"**Modes:** fixed, r=2, r=3, r=4, shuffled\n\n")
        
        f.write("## Aggregate Divergence\n\n")
        f.write("Mean absolute divergence from fixed mode:\n\n")
        f.write("| Radius | Mean |Δ_fixed| |\n")
        f.write("|--------|---------------|\n")
        for r, div in sorted(mean_divergence.items()):
            f.write(f"| {r} | {div:.4f} |\n")
        
        f.write(f"\n**Divergence point r₀:** ")
        if r0:
            f.write(f"{r0} (first radius where mean |Δ| > 0.01)\n")
        else:
            f.write("Not found (all radii < 0.01 divergence)\n")
        
        f.write("\n## Top 10 Head Curves\n\n")
        f.write("Delta vs fixed for top-scoring heads:\n\n")
        f.write("| Label | Δ(r=2) | Δ(r=3) | Δ(r=4) |\n")
        f.write("|-------|--------|--------|--------|\n")
        
        top_curves = sorted(delta_curves, 
                          key=lambda x: x["delta_vs_shuffled_fixed"], 
                          reverse=True)[:10]
        
        for curve in top_curves:
            f.write(f"| {curve['label']} | ")
            f.write(f"{curve['delta_vs_fixed_r2']:.4f} | ")
            f.write(f"{curve['delta_vs_fixed_r3']:.4f} | ")
            f.write(f"{curve['delta_vs_fixed_r4']:.4f} |\n")
        
        f.write("\n## Delta vs Shuffled Patterns\n\n")
        f.write("How different modes compare to shuffled control:\n\n")
        f.write("| Mode | Mean Δ_shuffled | Std Δ_shuffled |\n")
        f.write("|------|-----------------|----------------|\n")
        
        for mode in ["fixed", "r2", "r3", "r4"]:
            mode_key = f"delta_vs_shuffled_{mode}" if mode != "fixed" else "delta_vs_shuffled_fixed"
            deltas = [d[mode_key] for d in delta_curves]
            f.write(f"| {mode} | {np.mean(deltas):.4f} | {np.std(deltas):.4f} |\n")
        
        f.write("\n## Key Findings\n\n")
        f.write("1. **Divergence point:** ")
        if r0:
            f.write(f"Windowed mode begins to diverge from fixed at r={r0}\n")
        else:
            f.write("No significant divergence detected up to r=4\n")
        
        f.write("2. **Fixed vs r=2:** ")
        f.write(f"Mean divergence = {mean_divergence['r2']:.4f}\n")
        
        f.write("3. **Pattern:** ")
        if mean_divergence["r4"] > mean_divergence["r2"]:
            f.write("Divergence increases with radius (expected)\n")
        else:
            f.write("Unexpected pattern in divergence\n")
    
    # Generate REPRO_STEPS.md
    repro_path = output_dir / "REPRO_STEPS.md"
    with open(repro_path, 'w') as f:
        f.write("# Reproduction Steps: Window Sweep\n\n")
        f.write("## Environment\n")
        f.write("- Python 3.8+\n")
        f.write(f"- Seed: {seed}\n")
        f.write(f"- Date: {datetime.now().date()}\n\n")
        f.write("## Steps\n\n")
        f.write("```bash\n")
        f.write("python3 scripts/explore/run_window_sweep.py \\\n")
        f.write(f"  --candidates {candidates_file} \\\n")
        f.write(f"  --policies {policy_dir} \\\n")
        f.write(f"  --baseline {baseline_stats_file} \\\n")
        f.write(f"  --output {output_dir} \\\n")
        f.write(f"  --seed {seed}\n")
        f.write("```\n")
    
    # Generate manifest
    manifest_path = output_dir / "MANIFEST.sha256"
    with open(manifest_path, 'w') as f:
        for file_path in sorted(output_dir.glob("*")):
            if file_path.is_file():
                with open(file_path, 'rb') as fp:
                    hash_val = hashlib.sha256(fp.read()).hexdigest()
                f.write(f"{hash_val}  {file_path.name}\n")
    
    print(f"\n{'='*60}")
    print("Window Sweep Complete:")
    print(f"  Heads tested: {len(heads)}")
    print(f"  Divergence r₀: {r0 if r0 else 'Not found'}")
    print(f"  Mean divergence r=2: {mean_divergence['r2']:.4f}")
    print(f"  Mean divergence r=3: {mean_divergence['r3']:.4f}")
    print(f"  Mean divergence r=4: {mean_divergence['r4']:.4f}")
    print(f"  Output: {output_dir}")

def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Run window sweep campaign")
    parser.add_argument("--candidates", 
                       default="experiments/pipeline_v2/data/window_sweep_heads.json")
    parser.add_argument("--policies", 
                       default="experiments/pipeline_v2/policies/explore_window")
    parser.add_argument("--baseline", 
                       default="experiments/pipeline_v2/runs/2025-01-05-explore-breadth/baseline_stats.json")
    parser.add_argument("--output", 
                       default="experiments/pipeline_v2/runs/2025-01-06-explore-window/")
    parser.add_argument("--seed", type=int, default=1337)
    
    args = parser.parse_args()
    
    run_window_sweep(
        Path(args.candidates),
        Path(args.policies),
        Path(args.baseline),
        Path(args.output),
        args.seed
    )

if __name__ == "__main__":
    main()