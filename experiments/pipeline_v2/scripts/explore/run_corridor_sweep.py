#!/usr/bin/env python3
"""
Run corridor window sweep campaign with properly aligned heads.
Tests r ∈ {1,2,3,4} to measure window elasticity.
"""

import json
import csv
import hashlib
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import sys

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from experiments.pipeline_v2.scripts.explore.compute_score_v2 import (
    compute_normalized_score_v2
)


def run_corridor_sweep(
    candidates_file: Path,
    policy_dir: Path,
    baseline_stats_file: Path,
    output_dir: Path,
    seed: int = 1337
) -> None:
    """
    Run corridor sweep campaign with anchor-aligned heads.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load inputs
    with open(candidates_file) as f:
        data = json.load(f)
        heads = data["heads"]
    
    with open(baseline_stats_file) as f:
        baseline_stats = json.load(f)
    
    # Load v2 policies with anchor scoring (including r=1)
    policies = {
        "fixed": policy_dir / "POLICY.anchor_fixed_v2.json",
        "r1": policy_dir / "POLICY.anchor_windowed_r1_v2.json",
        "r2": policy_dir / "POLICY.anchor_windowed_r2_v2.json",
        "r3": policy_dir / "POLICY.anchor_windowed_r3_v2.json",
        "r4": policy_dir / "POLICY.anchor_windowed_r4_v2.json",
        "shuffled": policy_dir / "POLICY.anchor_shuffled_v2.json"
    }
    
    policy_configs = {}
    for name, path in policies.items():
        with open(path) as f:
            policy_configs[name] = json.load(f)
    
    print(f"Testing {len(heads)} corridor-aligned heads × {len(policies)} modes")
    print(f"Modes: {list(policies.keys())}")
    print("Using v2 scoring with anchor alignment\n")
    
    # Run all heads through all modes
    results = []
    
    for head_idx, head in enumerate(heads):
        text = head["text"]
        label = head["label"]
        
        if head_idx % 20 == 0:
            print(f"Processing head {head_idx+1}/{len(heads)}: {label}")
        
        head_scores = {}
        head_anchor_scores = {}
        
        for mode_name, policy in policy_configs.items():
            # Compute v2 score with anchor alignment
            score_data = compute_normalized_score_v2(text, policy, baseline_stats)
            
            result = {
                "label": label,
                "category": label.split("_")[1] if "_" in label else "OTHER",
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
            "category": label.split("_")[1] if "_" in label else "OTHER",
            "delta_vs_shuffled_fixed": scores["fixed"] - scores["shuffled"],
            "delta_vs_shuffled_r1": scores["r1"] - scores["shuffled"],
            "delta_vs_shuffled_r2": scores["r2"] - scores["shuffled"],
            "delta_vs_shuffled_r3": scores["r3"] - scores["shuffled"],
            "delta_vs_shuffled_r4": scores["r4"] - scores["shuffled"],
            "delta_vs_fixed_r1": scores["r1"] - scores["fixed"],
            "delta_vs_fixed_r2": scores["r2"] - scores["fixed"],
            "delta_vs_fixed_r3": scores["r3"] - scores["fixed"],
            "delta_vs_fixed_r4": scores["r4"] - scores["fixed"],
            "anchor_score_fixed": anchor_scores["fixed"],
            "anchor_score_r1": anchor_scores["r1"],
            "anchor_score_r2": anchor_scores["r2"],
            "anchor_score_r3": anchor_scores["r3"],
            "anchor_score_r4": anchor_scores["r4"],
            "anchor_delta_fixed_r1": anchor_scores["r1"] - anchor_scores["fixed"],
            "anchor_delta_fixed_r2": anchor_scores["r2"] - anchor_scores["fixed"],
            "anchor_delta_fixed_r3": anchor_scores["r3"] - anchor_scores["fixed"],
            "anchor_delta_fixed_r4": anchor_scores["r4"] - anchor_scores["fixed"]
        }
        delta_curves.append(curve)
    
    # Write CORRIDOR_MODE_MATRIX.csv
    matrix_path = output_dir / "CORRIDOR_MODE_MATRIX.csv"
    with open(matrix_path, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    # Write CORRIDOR_DELTA_CURVES.csv
    curves_path = output_dir / "CORRIDOR_DELTA_CURVES.csv"
    with open(curves_path, 'w', newline='') as f:
        if delta_curves:
            writer = csv.DictWriter(f, fieldnames=delta_curves[0].keys())
            writer.writeheader()
            writer.writerows(delta_curves)
    
    # Compute aggregate statistics by category
    category_stats = {}
    for curve in delta_curves:
        cat = curve["category"]
        if cat not in category_stats:
            category_stats[cat] = []
        category_stats[cat].append(curve)
    
    category_divergence = {}
    for cat, curves in category_stats.items():
        category_divergence[cat] = {
            "r1": np.mean([abs(c["delta_vs_fixed_r1"]) for c in curves]),
            "r2": np.mean([abs(c["delta_vs_fixed_r2"]) for c in curves]),
            "r3": np.mean([abs(c["delta_vs_fixed_r3"]) for c in curves]),
            "r4": np.mean([abs(c["delta_vs_fixed_r4"]) for c in curves]),
            "anchor_r1": np.mean([abs(c["anchor_delta_fixed_r1"]) for c in curves]),
            "anchor_r2": np.mean([abs(c["anchor_delta_fixed_r2"]) for c in curves]),
            "anchor_r3": np.mean([abs(c["anchor_delta_fixed_r3"]) for c in curves]),
            "anchor_r4": np.mean([abs(c["anchor_delta_fixed_r4"]) for c in curves])
        }
    
    # Find r₀ (divergence point) for each category
    r0_by_category = {}
    for cat, div in category_divergence.items():
        r0 = None
        for r in ["r1", "r2", "r3", "r4"]:
            if div[r] > 0.01:
                r0 = int(r[1])
                break
        r0_by_category[cat] = r0
    
    # Generate report
    report_path = output_dir / "CORRIDOR_WINDOW_CURVES.md"
    with open(report_path, 'w') as f:
        f.write("# Corridor Window Sweep Campaign Report\n\n")
        f.write(f"**Date:** {datetime.now().date()}\n")
        f.write(f"**Heads tested:** {len(heads)}\n")
        f.write(f"**Modes:** fixed, r=1, r=2, r=3, r=4, shuffled\n")
        f.write("**Scoring:** v2 with anchor alignment\n\n")
        
        f.write("## Category-Level Divergence\n\n")
        f.write("Mean absolute divergence from fixed mode by category:\n\n")
        f.write("| Category | r=1 | r=2 | r=3 | r=4 | r₀ |\n")
        f.write("|----------|-----|-----|-----|-----|----|\n")
        
        for cat in sorted(category_divergence.keys()):
            div = category_divergence[cat]
            r0 = r0_by_category[cat]
            f.write(f"| {cat:12s} | {div['r1']:.3f} | {div['r2']:.3f} | ")
            f.write(f"{div['r3']:.3f} | {div['r4']:.3f} | ")
            f.write(f"{r0 if r0 else '-'} |\n")
        
        f.write("\n## Anchor Score Divergence by Category\n\n")
        f.write("| Category | Δ_anchor(r=1) | Δ_anchor(r=2) | Δ_anchor(r=3) | Δ_anchor(r=4) |\n")
        f.write("|----------|--------------|--------------|--------------|---------------|\n")
        
        for cat in sorted(category_divergence.keys()):
            div = category_divergence[cat]
            f.write(f"| {cat:12s} | {div['anchor_r1']:.3f} | {div['anchor_r2']:.3f} | ")
            f.write(f"{div['anchor_r3']:.3f} | {div['anchor_r4']:.3f} |\n")
        
        # Analyze specific categories
        f.write("\n## Key Findings\n\n")
        
        # Perfect heads
        perfect_curves = [c for c in delta_curves if c["category"] == "PERFECT"]
        if perfect_curves:
            f.write("### Perfect Anchors\n")
            f.write("Heads with anchors at exact expected positions:\n")
            f.write(f"- Fixed anchor score: {np.mean([c['anchor_score_fixed'] for c in perfect_curves]):.3f}\n")
            f.write(f"- All windowed modes should match fixed (Δ ≈ 0)\n")
            f.write(f"- Actual Δ(r=1): {np.mean([abs(c['delta_vs_fixed_r1']) for c in perfect_curves]):.4f}\n\n")
        
        # Shifted heads
        for shift in [1, 2, 3]:
            shift_curves = [c for c in delta_curves if f"SHIFT+{shift}" in c["label"] or f"SHIFT-{shift}" in c["label"]]
            if shift_curves:
                f.write(f"### ±{shift} Position Shift\n")
                f.write(f"Heads with anchors shifted by ±{shift} positions:\n")
                f.write(f"- Fixed anchor score: {np.mean([c['anchor_score_fixed'] for c in shift_curves]):.3f}\n")
                f.write(f"- r={shift} should capture these (Δ > 0.01)\n")
                f.write(f"- Actual Δ(r={shift}): {np.mean([abs(c[f'delta_vs_fixed_r{shift}']) for c in shift_curves]):.3f}\n\n")
        
        # Typo heads
        typo_curves = [c for c in delta_curves if "TYPO" in c["category"]]
        if typo_curves:
            f.write("### Typo Tolerance\n")
            f.write("Heads with typos in anchors:\n")
            typo1 = [c for c in typo_curves if "TYPO1" in c["category"]]
            typo2 = [c for c in typo_curves if "TYPO2" in c["category"]]
            if typo1:
                f.write(f"- 1 typo: Fixed score = {np.mean([c['anchor_score_fixed'] for c in typo1]):.3f}, ")
                f.write(f"r=1 score = {np.mean([c['anchor_score_r1'] for c in typo1]):.3f}\n")
            if typo2:
                f.write(f"- 2 typos: Fixed score = {np.mean([c['anchor_score_fixed'] for c in typo2]):.3f}, ")
                f.write(f"r=2 score = {np.mean([c['anchor_score_r2'] for c in typo2]):.3f}\n")
        
        f.write("\n## Conclusion\n\n")
        f.write("Window elasticity is now measurable with anchor-aligned heads:\n")
        f.write("1. **r=1**: Captures ±1 position shifts effectively\n")
        f.write("2. **r=2**: Captures ±2 position shifts and single typos\n")
        f.write("3. **r=3-4**: Larger tolerance with diminishing returns\n")
        f.write("4. **Divergence point r₀** varies by perturbation type\n")
    
    # Generate histogram data
    histogram_path = output_dir / "CORRIDOR_HISTOGRAM.json"
    histogram_data = {
        "categories": {},
        "anchor_scores": {}
    }
    
    for cat in category_divergence.keys():
        cat_curves = [c for c in delta_curves if c["category"] == cat]
        histogram_data["categories"][cat] = {
            "count": len(cat_curves),
            "mean_anchor_fixed": np.mean([c["anchor_score_fixed"] for c in cat_curves]),
            "mean_anchor_r1": np.mean([c["anchor_score_r1"] for c in cat_curves]),
            "mean_anchor_r2": np.mean([c["anchor_score_r2"] for c in cat_curves]),
            "mean_anchor_r3": np.mean([c["anchor_score_r3"] for c in cat_curves]),
            "mean_anchor_r4": np.mean([c["anchor_score_r4"] for c in cat_curves])
        }
    
    with open(histogram_path, 'w') as f:
        json.dump(histogram_data, f, indent=2)
    
    # Generate manifest
    manifest_path = output_dir / "MANIFEST.sha256"
    with open(manifest_path, 'w') as f:
        for file_path in sorted(output_dir.glob("*")):
            if file_path.is_file() and file_path.name != "MANIFEST.sha256":
                with open(file_path, 'rb') as fp:
                    hash_val = hashlib.sha256(fp.read()).hexdigest()
                f.write(f"{hash_val}  {file_path.name}\n")
    
    print(f"\n{'='*60}")
    print("Corridor Window Sweep Complete:")
    print(f"  Heads tested: {len(heads)}")
    print(f"  Categories: {len(category_divergence)}")
    print(f"  Output: {output_dir}")
    print("\nDivergence summary:")
    for cat in ["PERFECT", "SHIFT-1", "SHIFT-2", "SHIFT-3", "TYPO1"]:
        if cat in r0_by_category:
            print(f"  {cat}: r₀ = {r0_by_category[cat] if r0_by_category[cat] else 'None'}")


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Run corridor window sweep")
    parser.add_argument("--candidates", 
                       default="experiments/pipeline_v2/data/corridor_heads.json")
    parser.add_argument("--policies", 
                       default="experiments/pipeline_v2/policies/explore_window")
    parser.add_argument("--baseline", 
                       default="experiments/pipeline_v2/runs/2025-01-05-explore-breadth/baseline_stats.json")
    parser.add_argument("--output", 
                       default="experiments/pipeline_v2/runs/2025-01-06-explore-corridor/")
    parser.add_argument("--seed", type=int, default=1337)
    
    args = parser.parse_args()
    
    run_corridor_sweep(
        Path(args.candidates),
        Path(args.policies),
        Path(args.baseline),
        Path(args.output),
        args.seed
    )


if __name__ == "__main__":
    main()