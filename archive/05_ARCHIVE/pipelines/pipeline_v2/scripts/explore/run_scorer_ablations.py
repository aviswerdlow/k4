#!/usr/bin/env python3
"""
Run Campaign C: Scorer Ablations and Weight Calibration.
Tests different scorer weight configurations to find optimal settings.
"""

import json
import csv
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import sys
from itertools import product

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from experiments.pipeline_v2.scripts.explore.run_anchor_modes import (
    compute_ngram_score, compute_coverage_score, compute_compress_score
)
from experiments.pipeline_v2.scripts.explore.blind_text import blind_text

def compute_ablation_score(
    text: str,
    weights: Tuple[float, float, float],
    baseline_stats: Dict,
    blind: bool = True
) -> Dict:
    """
    Compute score with specific weight configuration.
    """
    # Blind if requested
    if blind:
        blinded_text, mask_report = blind_text(text, blind_anchors=True, blind_narrative=True)
    else:
        blinded_text = text
        mask_report = None
    
    # Raw scores
    ngram_raw = compute_ngram_score(blinded_text)
    coverage_raw = compute_coverage_score(blinded_text)
    compress_raw = compute_compress_score(blinded_text)
    
    # Normalize
    z_ngram = (ngram_raw - baseline_stats["ngram_mean"]) / max(0.001, baseline_stats["ngram_std"])
    z_coverage = (coverage_raw - baseline_stats["coverage_mean"]) / max(0.001, baseline_stats["coverage_std"])
    z_compress = (compress_raw - baseline_stats["compress_mean"]) / max(0.001, baseline_stats["compress_std"])
    
    # Weighted combination
    w_ngram, w_coverage, w_compress = weights
    score = w_ngram * z_ngram + w_coverage * z_coverage + w_compress * z_compress
    
    return {
        "score": score,
        "weights": weights,
        "components": {
            "ngram": {"raw": ngram_raw, "z": z_ngram, "weighted": w_ngram * z_ngram},
            "coverage": {"raw": coverage_raw, "z": z_coverage, "weighted": w_coverage * z_coverage},
            "compress": {"raw": compress_raw, "z": z_compress, "weighted": w_compress * z_compress}
        },
        "mask_report": mask_report
    }

def generate_weight_configs() -> List[Tuple[str, Tuple[float, float, float]]]:
    """
    Generate all weight configurations to test.
    """
    configs = []
    
    # 1. Component Ablations (single component)
    configs.append(("ngram_only", (1.0, 0.0, 0.0)))
    configs.append(("coverage_only", (0.0, 1.0, 0.0)))
    configs.append(("compress_only", (0.0, 0.0, 1.0)))
    
    # 2. Pairwise Ablations
    configs.append(("ngram_coverage", (0.5, 0.5, 0.0)))
    configs.append(("ngram_compress", (0.5, 0.0, 0.5)))
    configs.append(("coverage_compress", (0.0, 0.5, 0.5)))
    
    # 3. Weight Sweeps (constrained to sum to 1.0)
    ngram_weights = [0.2, 0.3, 0.4, 0.5, 0.6]
    coverage_weights = [0.2, 0.3, 0.4]
    
    for w_ng in ngram_weights:
        for w_cov in coverage_weights:
            w_comp = 1.0 - w_ng - w_cov
            if 0.1 <= w_comp <= 0.5:  # Valid compress weight
                configs.append((f"sweep_{w_ng:.1f}_{w_cov:.1f}_{w_comp:.1f}", 
                              (w_ng, w_cov, w_comp)))
    
    # 4. Extreme Configurations
    configs.append(("ngram_heavy", (0.7, 0.15, 0.15)))
    configs.append(("coverage_heavy", (0.15, 0.7, 0.15)))
    configs.append(("compress_heavy", (0.15, 0.15, 0.7)))
    configs.append(("balanced", (0.333, 0.333, 0.334)))
    
    # 5. Current baseline
    configs.append(("baseline", (0.4, 0.3, 0.3)))
    
    return configs

def compute_deltas(
    text: str,
    weights: Tuple[float, float, float],
    baseline_stats: Dict,
    seed: int = 1337
) -> Tuple[float, float]:
    """
    Compute delta margins for a weight configuration.
    Simulates windowed and shuffled modes.
    """
    import random
    random.seed(seed)
    
    # Fixed score
    fixed_score = compute_ablation_score(text, weights, baseline_stats, blind=True)["score"]
    
    # Windowed score (simulate by adding small noise)
    windowed_score = fixed_score + random.gauss(0, 0.01)
    
    # Shuffled score (simulate by shuffling and rescoring)
    shuffled = list(text)
    random.shuffle(shuffled)
    shuffled_text = ''.join(shuffled)
    shuffled_score = compute_ablation_score(shuffled_text, weights, baseline_stats, blind=True)["score"]
    
    delta_windowed = fixed_score - windowed_score
    delta_shuffled = fixed_score - shuffled_score
    
    return delta_windowed, delta_shuffled

def run_threshold_calibration(
    texts: List[str],
    weights: Tuple[float, float, float],
    baseline_stats: Dict,
    thresholds: List[float] = [0.03, 0.04, 0.05, 0.06, 0.07]
) -> Dict:
    """
    Test different delta thresholds to calibrate acceptance rates.
    """
    results = {}
    
    for threshold in thresholds:
        passers = 0
        for text in texts:
            delta_w, delta_s = compute_deltas(text, weights, baseline_stats)
            if delta_w >= threshold and delta_s >= threshold:
                passers += 1
        
        results[threshold] = {
            "pass_rate": passers / len(texts),
            "passers": passers,
            "total": len(texts)
        }
    
    return results

def run_scorer_ablations(
    candidates_file: Path,
    baseline_stats_file: Path,
    output_dir: Path,
    seed: int = 1337
) -> None:
    """
    Run Campaign C: Scorer ablations and calibration.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load inputs
    with open(candidates_file) as f:
        data = json.load(f)
        candidates = data.get("heads", data.get("candidates", []))[:10]  # Top 10
    
    with open(baseline_stats_file) as f:
        baseline_stats = json.load(f)
    
    # Generate weight configurations
    weight_configs = generate_weight_configs()
    print(f"Testing {len(weight_configs)} weight configurations on {len(candidates)} candidates")
    
    # Test each configuration
    ablation_results = []
    
    for config_name, weights in weight_configs:
        print(f"\nTesting {config_name}: {weights}")
        
        for candidate in candidates:
            text = candidate["text"]
            
            # Compute scores and deltas
            score_data = compute_ablation_score(text, weights, baseline_stats)
            delta_w, delta_s = compute_deltas(text, weights, baseline_stats, seed)
            
            result = {
                "config": config_name,
                "weights": f"{weights[0]:.2f},{weights[1]:.2f},{weights[2]:.2f}",
                "candidate": candidate["label"],
                "score": score_data["score"],
                "delta_windowed": delta_w,
                "delta_shuffled": delta_s,
                "pass_deltas": delta_w >= 0.05 and delta_s >= 0.05,
                "ngram_contrib": score_data["components"]["ngram"]["weighted"],
                "coverage_contrib": score_data["components"]["coverage"]["weighted"],
                "compress_contrib": score_data["components"]["compress"]["weighted"]
            }
            ablation_results.append(result)
    
    # Write ablation matrix
    ablation_path = output_dir / "ABLATION_MATRIX.csv"
    with open(ablation_path, 'w', newline='') as f:
        if ablation_results:
            writer = csv.DictWriter(f, fieldnames=ablation_results[0].keys())
            writer.writeheader()
            writer.writerows(ablation_results)
    
    # Analyze best configurations
    config_performance = {}
    for config_name, _ in weight_configs:
        config_results = [r for r in ablation_results if r["config"] == config_name]
        config_performance[config_name] = {
            "avg_score": np.mean([r["score"] for r in config_results]),
            "avg_delta_s": np.mean([r["delta_shuffled"] for r in config_results]),
            "pass_rate": sum(1 for r in config_results if r["pass_deltas"]) / len(config_results)
        }
    
    # Sort by delta_shuffled performance
    sorted_configs = sorted(config_performance.items(), 
                          key=lambda x: x[1]["avg_delta_s"], 
                          reverse=True)
    
    # Run threshold calibration on best config
    best_config_name = sorted_configs[0][0]
    best_weights = next(w for n, w in weight_configs if n == best_config_name)
    
    print(f"\nRunning threshold calibration with {best_config_name}")
    texts = [c["text"] for c in candidates]
    threshold_results = run_threshold_calibration(texts, best_weights, baseline_stats)
    
    # Write calibration report
    report_path = output_dir / "CALIBRATION_REPORT.md"
    with open(report_path, 'w') as f:
        f.write("# Campaign C: Scorer Ablations Report\n\n")
        f.write(f"**Date:** {datetime.now().date()}\n")
        f.write(f"**Configurations tested:** {len(weight_configs)}\n")
        f.write(f"**Candidates tested:** {len(candidates)}\n\n")
        
        f.write("## Top Configurations by Delta Performance\n\n")
        f.write("| Config | Weights (N,C,P) | Avg Score | Avg δ_shuffled | Pass Rate |\n")
        f.write("|--------|-----------------|-----------|----------------|----------|\n")
        for config_name, perf in sorted_configs[:10]:
            weights_str = next(w for n, w in weight_configs if n == config_name)
            f.write(f"| {config_name} | {weights_str} | {perf['avg_score']:.3f} | ")
            f.write(f"{perf['avg_delta_s']:.3f} | {perf['pass_rate']:.1%} |\n")
        
        f.write("\n## Threshold Calibration\n\n")
        f.write(f"Best config: {best_config_name}\n\n")
        f.write("| Threshold | Pass Rate | Passers |\n")
        f.write("|-----------|-----------|----------|\n")
        for threshold, results in sorted(threshold_results.items()):
            f.write(f"| {threshold:.2f} | {results['pass_rate']:.1%} | ")
            f.write(f"{results['passers']}/{results['total']} |\n")
        
        f.write("\n## Key Findings\n\n")
        f.write("1. **Best configuration:** " + best_config_name + "\n")
        f.write("2. **Optimal weights:** " + str(best_weights) + "\n")
        f.write("3. **Delta improvement:** " + 
               f"{config_performance[best_config_name]['avg_delta_s']:.3f} vs " +
               f"{config_performance['baseline']['avg_delta_s']:.3f} (baseline)\n")
        f.write("4. **Recommended threshold:** Based on calibration results\n")
    
    # Save optimal weights
    optimal_path = output_dir / "optimal_weights.json"
    with open(optimal_path, 'w') as f:
        json.dump({
            "config_name": best_config_name,
            "weights": {
                "ngram": best_weights[0],
                "coverage": best_weights[1],
                "compress": best_weights[2]
            },
            "performance": config_performance[best_config_name],
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Campaign C Complete:")
    print(f"  Configurations tested: {len(weight_configs)}")
    print(f"  Best config: {best_config_name}")
    print(f"  Best weights: {best_weights}")
    print(f"  Output: {output_dir}")

def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Run Campaign C: Scorer Ablations")
    parser.add_argument("--candidates", 
                       default="experiments/pipeline_v2/data/candidates_breadth.json")
    parser.add_argument("--baseline", 
                       default="experiments/pipeline_v2/runs/2025-01-05-explore-breadth/baseline_stats.json")
    parser.add_argument("--output", 
                       default="experiments/pipeline_v2/runs/2025-01-06-scorer-ablations/")
    parser.add_argument("--seed", type=int, default=1337)
    
    args = parser.parse_args()
    
    run_scorer_ablations(
        Path(args.candidates),
        Path(args.baseline),
        Path(args.output),
        args.seed
    )

if __name__ == "__main__":
    main()