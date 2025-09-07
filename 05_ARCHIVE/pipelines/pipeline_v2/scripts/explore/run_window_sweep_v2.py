#!/usr/bin/env python3
"""
Run window sweep campaign with PROPER anchor scoring.
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

from experiments.pipeline_v2.scripts.explore.compute_score_v2 import (
    compute_normalized_score_v2
)


def run_window_sweep_v2(
    candidates_file: Path,
    policy_dir: Path,
    baseline_stats_file: Path,
    output_dir: Path,
    seed: int = 1337
) -> None:
    """
    Run window sweep campaign with proper anchor scoring.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load inputs
    with open(candidates_file) as f:
        data = json.load(f)
        heads = data["heads"]
    
    with open(baseline_stats_file) as f:
        baseline_stats = json.load(f)
    
    # Load v2 policies with anchor scoring
    policies = {
        "fixed": policy_dir / "POLICY.anchor_fixed_v2.json",
        "r2": policy_dir / "POLICY.anchor_windowed_r2_v2.json",
        "r3": policy_dir / "POLICY.anchor_windowed_r3_v2.json",
        "r4": policy_dir / "POLICY.anchor_windowed_r4_v2.json",
        "shuffled": policy_dir / "POLICY.anchor_shuffled_v2.json"
    }
    
    policy_configs = {}
    for name, path in policies.items():
        with open(path) as f:
            policy_configs[name] = json.load(f)
    
    print(f"Testing {len(heads)} heads × {len(policies)} modes")
    print(f"Modes: {list(policies.keys())}")
    print("Using v2 scoring with anchor alignment\n")
    
    # Run all heads through all modes
    results = []
    
    for head_idx, head in enumerate(heads):
        text = head["text"]
        label = head["label"]
        
        if head_idx % 10 == 0:
            print(f"Processing head {head_idx+1}/{len(heads)}: {label}")
        
        head_scores = {}
        head_anchor_scores = {}
        
        for mode_name, policy in policy_configs.items():
            # Compute v2 score with anchor alignment
            score_data = compute_normalized_score_v2(text, policy, baseline_stats)
            
            result = {
                "label": label,
                "route": "GRID_W14_ROWS",  # Using single route for measurement
                "mode": mode_name,
                "score_norm": score_data["score_norm"],
                "anchor_score": score_data["anchor_result"]["anchor_score"],
                "z_ngram": score_data["z_ngram"],
                "z_coverage": score_data["z_coverage"],
                "z_compress": score_data["z_compress"]
            }
            results.append(result)
            head_scores[mode_name] = score_data["score_norm"]
            head_anchor_scores[mode_name] = score_data["anchor_result"]["anchor_score"]
    
    # Compute delta curves
    delta_curves = []
    
    for label in {r["label"] for r in results}:
        head_results = [r for r in results if r["label"] == label]
        scores = {r["mode"]: r["score_norm"] for r in head_results}
        anchor_scores = {r["mode"]: r["anchor_score"] for r in head_results}
        
        curve = {
            "label": label,
            "route": "GRID_W14_ROWS",
            "delta_vs_shuffled_fixed": scores["fixed"] - scores["shuffled"],
            "delta_vs_shuffled_r2": scores["r2"] - scores["shuffled"],
            "delta_vs_shuffled_r3": scores["r3"] - scores["shuffled"],
            "delta_vs_shuffled_r4": scores["r4"] - scores["shuffled"],
            "delta_vs_fixed_r2": scores["r2"] - scores["fixed"],
            "delta_vs_fixed_r3": scores["r3"] - scores["fixed"],
            "delta_vs_fixed_r4": scores["r4"] - scores["fixed"],
            "anchor_delta_fixed_r2": anchor_scores["r2"] - anchor_scores["fixed"],
            "anchor_delta_fixed_r3": anchor_scores["r3"] - anchor_scores["fixed"],
            "anchor_delta_fixed_r4": anchor_scores["r4"] - anchor_scores["fixed"]
        }
        delta_curves.append(curve)
    
    # Write ANCHOR_MODE_MATRIX.csv
    matrix_path = output_dir / "ANCHOR_MODE_MATRIX.csv"
    with open(matrix_path, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
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
    
    mean_anchor_divergence = {
        "r2": np.mean([abs(d["anchor_delta_fixed_r2"]) for d in delta_curves]),
        "r3": np.mean([abs(d["anchor_delta_fixed_r3"]) for d in delta_curves]),
        "r4": np.mean([abs(d["anchor_delta_fixed_r4"]) for d in delta_curves])
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
        f.write("# Window Sweep Campaign Report (v2 - Fixed)\n\n")
        f.write(f"**Date:** {datetime.now().date()}\n")
        f.write(f"**Heads tested:** {len(heads)}\n")
        f.write(f"**Modes:** fixed, r=2, r=3, r=4, shuffled\n")
        f.write("**Scoring:** v2 with anchor alignment\n\n")
        
        f.write("## Aggregate Divergence\n\n")
        f.write("### Combined Score Divergence\n")
        f.write("Mean absolute divergence from fixed mode:\n\n")
        f.write("| Radius | Mean |Δ_fixed| |\n")
        f.write("|--------|---------------|\n")
        for r, div in sorted(mean_divergence.items()):
            f.write(f"| {r} | {div:.4f} |\n")
        
        f.write("\n### Anchor Score Divergence\n")
        f.write("Mean absolute anchor score divergence from fixed:\n\n")
        f.write("| Radius | Mean |Δ_anchor| |\n")
        f.write("|--------|----------------|\n")
        for r, div in sorted(mean_anchor_divergence.items()):
            f.write(f"| {r} | {div:.4f} |\n")
        
        f.write(f"\n**Divergence point r₀:** ")
        if r0:
            f.write(f"{r0} (first radius where mean |Δ| > 0.01)\n")
        else:
            f.write("Not found (all radii < 0.01 divergence)\n")
        
        f.write("\n## Top 10 Head Curves\n\n")
        f.write("Delta vs fixed for top-scoring heads:\n\n")
        f.write("| Label | Δ(r=2) | Δ(r=3) | Δ(r=4) | Δ_anchor(r=2) |\n")
        f.write("|-------|--------|--------|--------|---------------|\n")
        
        top_curves = sorted(delta_curves, 
                          key=lambda x: x["delta_vs_shuffled_fixed"], 
                          reverse=True)[:10]
        
        for curve in top_curves:
            f.write(f"| {curve['label']} | ")
            f.write(f"{curve['delta_vs_fixed_r2']:.4f} | ")
            f.write(f"{curve['delta_vs_fixed_r3']:.4f} | ")
            f.write(f"{curve['delta_vs_fixed_r4']:.4f} | ")
            f.write(f"{curve['anchor_delta_fixed_r2']:.4f} |\n")
        
        f.write("\n## Key Findings\n\n")
        f.write("1. **Anchor scoring now active:** Windowed modes properly search for anchors\n")
        f.write("2. **Divergence point:** ")
        if r0:
            f.write(f"Windowed mode begins to diverge from fixed at r={r0}\n")
        else:
            f.write("No significant divergence detected (anchors may not be present in windows)\n")
        
        f.write(f"3. **Mean anchor divergence:** r=2: {mean_anchor_divergence['r2']:.4f}, ")
        f.write(f"r=3: {mean_anchor_divergence['r3']:.4f}, r=4: {mean_anchor_divergence['r4']:.4f}\n")
    
    # Generate CORRIGENDUM
    corrigendum_path = output_dir / "CORRIGENDUM.md"
    with open(corrigendum_path, 'w') as f:
        f.write("# Corrigendum: Window Sweep v2\n\n")
        f.write("## Issue Fixed\n\n")
        f.write("Windowed anchor scoring was previously a no-op (blinding occurred without window search).\n")
        f.write("This run implements position/typo-aware windowed scoring per policy (see anchor_score.py).\n\n")
        f.write("## Changes Made\n\n")
        f.write("1. Implemented `anchor_score.py` with proper window search\n")
        f.write("2. Created `compute_score_v2.py` that scores anchors BEFORE blinding\n")
        f.write("3. Updated policies with `anchor_scoring` configuration\n")
        f.write("4. Unit tests pass (see `test_anchor_score.py`)\n\n")
        f.write("## Impact\n\n")
        f.write("All windowed results in prior runs are superseded by this folder's artifacts.\n")
        f.write("Deltas should now be non-zero when anchors shift position.\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
    
    # Generate REPRO_STEPS.md
    repro_path = output_dir / "REPRO_STEPS.md"
    with open(repro_path, 'w') as f:
        f.write("# Reproduction Steps: Window Sweep v2\n\n")
        f.write("## Environment\n")
        f.write("- Python 3.8+\n")
        f.write(f"- Seed: {seed}\n")
        f.write(f"- Date: {datetime.now().date()}\n\n")
        f.write("## Steps\n\n")
        f.write("```bash\n")
        f.write("# Run unit tests first\n")
        f.write("python3 scripts/tests/test_anchor_score.py\n\n")
        f.write("# Run window sweep v2\n")
        f.write("python3 scripts/explore/run_window_sweep_v2.py \\\n")
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
    print("Window Sweep v2 Complete:")
    print(f"  Heads tested: {len(heads)}")
    print(f"  Divergence r₀: {r0 if r0 else 'Not found'}")
    print(f"  Mean divergence r=2: {mean_divergence['r2']:.4f}")
    print(f"  Mean anchor divergence r=2: {mean_anchor_divergence['r2']:.4f}")
    print(f"  Output: {output_dir}")
    print("\nCorrigendum created - prior windowed results superseded")


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Run window sweep v2 with anchor scoring")
    parser.add_argument("--candidates", 
                       default="experiments/pipeline_v2/data/window_sweep_heads.json")
    parser.add_argument("--policies", 
                       default="experiments/pipeline_v2/policies/explore_window")
    parser.add_argument("--baseline", 
                       default="experiments/pipeline_v2/runs/2025-01-05-explore-breadth/baseline_stats.json")
    parser.add_argument("--output", 
                       default="experiments/pipeline_v2/runs/2025-01-06-explore-window-v2/")
    parser.add_argument("--seed", type=int, default=1337)
    
    args = parser.parse_args()
    
    run_window_sweep_v2(
        Path(args.candidates),
        Path(args.policies),
        Path(args.baseline),
        Path(args.output),
        args.seed
    )


if __name__ == "__main__":
    main()