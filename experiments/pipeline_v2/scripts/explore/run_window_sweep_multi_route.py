#!/usr/bin/env python3
"""
Run window sweep with multiple routes and comprehensive tracking.
Supports all campaigns (H/I/J/K/L) with alignment columns.
"""

import json
import csv
import hashlib
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import sys

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from experiments.pipeline_v2.scripts.explore.compute_score_v2 import (
    compute_normalized_score_v2
)


def check_corridor_alignment(text: str) -> Dict:
    """
    Check if anchors are at expected corridor positions.
    """
    east_idx = -1
    ne_idx = -1
    berlin_idx = -1
    
    # Check for EAST at position 21
    if len(text) >= 25 and text[21:25] == "EAST":
        east_idx = 21
    
    # Check for NORTHEAST at position 25
    if len(text) >= 34 and text[25:34] == "NORTHEAST":
        ne_idx = 25
    
    # Check for BERLINCLOCK at position 63
    if len(text) >= 74 and text[63:74] == "BERLINCLOCK":
        berlin_idx = 63
    
    corridor_ok = (east_idx == 21 and ne_idx == 25 and berlin_idx == 63)
    
    return {
        "anchor_found_east_idx": east_idx,
        "anchor_found_ne_idx": ne_idx,
        "anchor_found_berlin_idx": berlin_idx,
        "corridor_ok": corridor_ok
    }


def run_multi_route_sweep(
    candidates_file: Path,
    policy_dir: Path,
    baseline_stats_file: Path,
    routes: List[str],
    output_dir: Path,
    seed: int = 1337,
    run_nulls: bool = False
) -> None:
    """
    Run window sweep across multiple routes with comprehensive tracking.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load inputs
    with open(candidates_file) as f:
        data = json.load(f)
        heads = data["heads"]
    
    with open(baseline_stats_file) as f:
        baseline_stats = json.load(f)
    
    # Load all policies
    policy_files = list(policy_dir.glob("POLICY.anchor_*.json"))
    policies = {}
    policy_configs = {}
    
    for policy_file in policy_files:
        # Extract mode from filename
        if "fixed" in policy_file.name:
            mode = "fixed"
        elif "shuffled" in policy_file.name:
            mode = "shuffled"
        elif "windowed" in policy_file.name:
            # Extract r and tb values
            parts = policy_file.stem.split("_")
            if "r1" in policy_file.name:
                mode = "r1"
            elif "r2" in policy_file.name:
                mode = "r2"
            elif "r3" in policy_file.name:
                mode = "r3"
            elif "r4" in policy_file.name:
                mode = "r4"
            elif "r5" in policy_file.name:
                mode = "r5"
            elif "r6" in policy_file.name:
                mode = "r6"
            else:
                continue
            
            # Check for typo budget
            if "tb" in policy_file.name:
                tb_part = [p for p in parts if p.startswith("tb")]
                if tb_part:
                    mode += f"_{tb_part[0]}"
        else:
            continue
        
        policies[mode] = policy_file
        with open(policy_file) as f:
            policy_configs[mode] = json.load(f)
    
    print(f"Testing {len(heads)} heads × {len(policies)} modes × {len(routes)} routes")
    print(f"Routes: {', '.join(routes)}")
    print(f"Modes: {', '.join(sorted(policies.keys()))}")
    print(f"Seed: {seed}\n")
    
    # Run all combinations
    all_results = []
    explore_results = []
    
    total_evaluations = len(heads) * len(policies) * len(routes)
    current_eval = 0
    
    for route in routes:
        print(f"\nProcessing route: {route}")
        
        for head_idx, head in enumerate(heads):
            text = head["text"]
            label = head["label"]
            
            # Check corridor alignment
            alignment = check_corridor_alignment(text)
            
            if head_idx % 20 == 0:
                print(f"  Head {head_idx+1}/{len(heads)}: {label}")
            
            head_scores = {}
            head_anchor_scores = {}
            
            for mode_name, policy in policy_configs.items():
                current_eval += 1
                
                if current_eval % 1000 == 0:
                    print(f"  Progress: {current_eval}/{total_evaluations} evaluations")
                
                # Compute v2 score with anchor alignment
                score_data = compute_normalized_score_v2(text, policy, baseline_stats)
                
                result = {
                    "label": label,
                    "route": route,
                    "mode": mode_name,
                    "score_norm": score_data["score_norm"],
                    "anchor_score": score_data["anchor_result"]["anchor_score"],
                    "z_ngram": score_data["z_ngram"],
                    "z_coverage": score_data["z_coverage"],
                    "z_compress": score_data["z_compress"],
                    "anchor_found_east_idx": alignment["anchor_found_east_idx"],
                    "anchor_found_ne_idx": alignment["anchor_found_ne_idx"],
                    "anchor_found_berlin_idx": alignment["anchor_found_berlin_idx"],
                    "corridor_ok": alignment["corridor_ok"]
                }
                all_results.append(result)
                head_scores[mode_name] = score_data["score_norm"]
                head_anchor_scores[mode_name] = score_data["anchor_result"]["anchor_score"]
            
            # Calculate deltas for explore decision
            if "fixed" in head_scores and "shuffled" in head_scores:
                # Find best windowed mode
                windowed_modes = [m for m in head_scores.keys() if m.startswith("r")]
                if windowed_modes:
                    best_windowed_score = max(head_scores[m] for m in windowed_modes)
                    best_windowed_mode = [m for m in windowed_modes 
                                        if head_scores[m] == best_windowed_score][0]
                else:
                    best_windowed_score = head_scores["fixed"]
                    best_windowed_mode = "fixed"
                
                delta_vs_shuffled = head_scores["fixed"] - head_scores["shuffled"]
                delta_vs_windowed = head_scores["fixed"] - best_windowed_score
                
                # Check explore thresholds
                pass_explore = (delta_vs_windowed > 0.05 and delta_vs_shuffled > 0.10)
                
                explore_result = {
                    "label": label,
                    "route": route,
                    "score_fixed": head_scores["fixed"],
                    "score_best_windowed": best_windowed_score,
                    "best_windowed_mode": best_windowed_mode,
                    "score_shuffled": head_scores["shuffled"],
                    "delta_vs_shuffled": delta_vs_shuffled,
                    "delta_vs_windowed": delta_vs_windowed,
                    "pass_explore": pass_explore,
                    "corridor_ok": alignment["corridor_ok"]
                }
                explore_results.append(explore_result)
    
    # Write ANCHOR_MODE_MATRIX.csv
    matrix_path = output_dir / "ANCHOR_MODE_MATRIX.csv"
    with open(matrix_path, 'w', newline='') as f:
        if all_results:
            writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
            writer.writeheader()
            writer.writerows(all_results)
    
    # Write EXPLORE_MATRIX.csv
    explore_path = output_dir / "EXPLORE_MATRIX.csv"
    with open(explore_path, 'w', newline='') as f:
        if explore_results:
            writer = csv.DictWriter(f, fieldnames=explore_results[0].keys())
            writer.writeheader()
            writer.writerows(explore_results)
    
    # Calculate delta curves
    delta_curves = []
    unique_combinations = set((r["label"], r["route"]) for r in all_results)
    
    for label, route in unique_combinations:
        combo_results = [r for r in all_results 
                        if r["label"] == label and r["route"] == route]
        
        if not combo_results:
            continue
            
        scores = {r["mode"]: r["score_norm"] for r in combo_results}
        anchor_scores = {r["mode"]: r["anchor_score"] for r in combo_results}
        
        if "fixed" not in scores or "shuffled" not in scores:
            continue
        
        curve = {
            "label": label,
            "route": route,
            "corridor_ok": combo_results[0]["corridor_ok"],
            "delta_vs_shuffled": scores["fixed"] - scores["shuffled"]
        }
        
        # Add deltas for each windowed mode
        for mode in sorted(scores.keys()):
            if mode.startswith("r"):
                curve[f"delta_vs_fixed_{mode}"] = scores[mode] - scores["fixed"]
                curve[f"anchor_delta_{mode}"] = anchor_scores[mode] - anchor_scores["fixed"]
        
        delta_curves.append(curve)
    
    # Write DELTA_CURVES.csv
    curves_path = output_dir / "DELTA_CURVES.csv"
    with open(curves_path, 'w', newline='') as f:
        if delta_curves:
            writer = csv.DictWriter(f, fieldnames=delta_curves[0].keys())
            writer.writeheader()
            writer.writerows(delta_curves)
    
    # Generate report
    report_path = output_dir / "EXPLORE_REPORT.md"
    
    # Calculate statistics
    total_evaluated = len(explore_results)
    passed_explore = sum(1 for r in explore_results if r["pass_explore"])
    corridor_aligned = sum(1 for r in explore_results if r["corridor_ok"])
    
    # Group by route
    by_route = {}
    for result in explore_results:
        route = result["route"]
        if route not in by_route:
            by_route[route] = {"total": 0, "passed": 0}
        by_route[route]["total"] += 1
        if result["pass_explore"]:
            by_route[route]["passed"] += 1
    
    with open(report_path, 'w') as f:
        f.write(f"# Explore Campaign Report\n\n")
        f.write(f"**Date:** {datetime.now().date()}\n")
        f.write(f"**Campaign:** {candidates_file.stem}\n")
        f.write(f"**Seed:** {seed}\n\n")
        
        f.write(f"## Summary Statistics\n\n")
        f.write(f"- Total evaluations: {total_evaluated}\n")
        f.write(f"- Passed explore thresholds: {passed_explore} ({100*passed_explore/total_evaluated:.1f}%)\n")
        f.write(f"- Corridor aligned: {corridor_aligned} ({100*corridor_aligned/total_evaluated:.1f}%)\n\n")
        
        f.write(f"## Results by Route\n\n")
        f.write("| Route | Total | Passed | Pass Rate |\n")
        f.write("|-------|-------|--------|----------|\n")
        for route in sorted(by_route.keys()):
            stats = by_route[route]
            pass_rate = 100 * stats["passed"] / stats["total"] if stats["total"] > 0 else 0
            f.write(f"| {route} | {stats['total']} | {stats['passed']} | {pass_rate:.1f}% |\n")
        
        f.write(f"\n## Death Points\n\n")
        f.write(f"- Failed δ₁ (vs windowed): {sum(1 for r in explore_results if r['delta_vs_windowed'] <= 0.05)}\n")
        f.write(f"- Failed δ₂ (vs shuffled): {sum(1 for r in explore_results if r['delta_vs_shuffled'] <= 0.10)}\n")
        f.write(f"- Failed both thresholds: {total_evaluated - passed_explore}\n")
        
        if passed_explore > 0:
            f.write(f"\n## Top Survivors (NOT promoted)\n\n")
            f.write("| Label | Route | δ vs shuffled | δ vs windowed |\n")
            f.write("|-------|-------|--------------|---------------|\n")
            
            survivors = [r for r in explore_results if r["pass_explore"]]
            survivors.sort(key=lambda x: x["delta_vs_shuffled"], reverse=True)
            
            for survivor in survivors[:10]:
                f.write(f"| {survivor['label']} | {survivor['route']} | ")
                f.write(f"{survivor['delta_vs_shuffled']:.4f} | ")
                f.write(f"{survivor['delta_vs_windowed']:.4f} |\n")
        
        f.write(f"\n## Conclusion\n\n")
        f.write(f"Campaign complete. ")
        if passed_explore == 0:
            f.write(f"No heads passed explore thresholds. Confirm lane remains idle.\n")
        else:
            f.write(f"{passed_explore} heads passed thresholds but are NOT promoted (Explore discipline maintained).\n")
    
    # Generate REPRO_STEPS.md
    repro_path = output_dir / "REPRO_STEPS.md"
    with open(repro_path, 'w') as f:
        f.write("# Reproduction Steps\n\n")
        f.write(f"**Date:** {datetime.now().date()}\n")
        f.write(f"**Seed:** {seed}\n\n")
        f.write("```bash\n")
        f.write("# Generate heads\n")
        f.write(f"python3 scripts/explore/generate_heads_registers.py \\\n")
        f.write(f"  --out {candidates_file} --seed {seed}\n\n")
        f.write("# Run sweep\n")
        f.write(f"python3 scripts/explore/run_window_sweep_multi_route.py \\\n")
        f.write(f"  --candidates {candidates_file} \\\n")
        f.write(f"  --policies {policy_dir} \\\n")
        f.write(f"  --baseline {baseline_stats_file} \\\n")
        f.write(f"  --routes {','.join(routes)} \\\n")
        f.write(f"  --out {output_dir} \\\n")
        f.write(f"  --seed {seed}\n")
        f.write("```\n")
    
    # Generate MANIFEST.sha256
    manifest_path = output_dir / "MANIFEST.sha256"
    with open(manifest_path, 'w') as f:
        for file_path in sorted(output_dir.glob("*")):
            if file_path.is_file() and file_path.name != "MANIFEST.sha256":
                with open(file_path, 'rb') as fp:
                    hash_val = hashlib.sha256(fp.read()).hexdigest()
                f.write(f"{hash_val}  {file_path.name}\n")
    
    print(f"\n{'='*60}")
    print(f"Campaign Complete:")
    print(f"  Total evaluated: {total_evaluated}")
    print(f"  Passed explore: {passed_explore}")
    print(f"  Corridor aligned: {100*corridor_aligned/total_evaluated:.1f}%")
    print(f"  Output: {output_dir}")
    print(f"  Confirm lane: IDLE (no promotions)")


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Run multi-route window sweep")
    parser.add_argument("--candidates",
                       default="experiments/pipeline_v2/data/heads_registers.json")
    parser.add_argument("--policies",
                       default="experiments/pipeline_v2/policies/explore_window",
                       type=Path)
    parser.add_argument("--baseline",
                       default="experiments/pipeline_v2/runs/2025-01-05-explore-breadth/baseline_stats.json")
    parser.add_argument("--routes",
                       default="GRID_W14_ROWS,GRID_W14_NE,GRID_W14_NW,GRID_W14_BOU",
                       help="Comma-separated list of routes")
    parser.add_argument("--out",
                       default="experiments/pipeline_v2/runs/2025-01-06-explore-H/",
                       type=Path)
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--run-nulls", action="store_true",
                       help="Run 1k nulls for passers")
    
    args = parser.parse_args()
    
    routes = args.routes.split(",")
    
    run_multi_route_sweep(
        Path(args.candidates),
        args.policies,
        Path(args.baseline),
        routes,
        args.out,
        args.seed,
        args.run_nulls
    )


if __name__ == "__main__":
    main()