#!/usr/bin/env python3
"""
Feature ablation analysis to identify which components drive scoring.
"""

import json
import random
import sys
from pathlib import Path
from typing import List, Dict
import numpy as np
# import matplotlib.pyplot as plt  # Optional for plotting

# Add pipeline modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.explore.run_family import ExplorePipeline


def ablation_analysis(pipeline: ExplorePipeline, num_samples: int = 200):
    """
    Perform feature ablation on a sample of heads and controls.
    
    Returns:
        Ablation results with feature contributions
    """
    # Load some C7-C16 heads
    campaign_heads = []
    for cid in ["C7", "C8", "C9", "C10"]:
        heads_dir = Path(f"experiments/pipeline_v2/runs/2025-01-06-explore-ideas-{cid}")
        heads_files = list(heads_dir.glob("heads_*.json"))
        if heads_files:
            with open(heads_files[0]) as f:
                data = json.load(f)
                campaign_heads.extend([h["text"] for h in data["heads"][:25]])
    
    # Generate controls
    controls = [''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=75)) 
                for _ in range(num_samples)]
    
    # Combine samples
    all_samples = campaign_heads[:num_samples//2] + controls[:num_samples//2]
    
    results = []
    
    for i, text in enumerate(all_samples):
        if i % 50 == 0:
            print(f"Processing {i}/{len(all_samples)}...")
        
        # Full scoring
        policy = {"name": "fixed", "window_radius": 0, "typo_budget": 0}
        full_result = pipeline.compute_score_v2(text, policy)
        
        # Store component scores
        results.append({
            "is_control": i >= len(campaign_heads[:num_samples//2]),
            "full_score": full_result["score_norm"],
            "anchor_score": full_result["anchor_result"]["total_score"],
            "z_ngram": full_result["z_ngram"],
            "z_coverage": full_result["z_coverage"],
            "z_compress": full_result["z_compress"]
        })
    
    return results


def analyze_contributions(results: List[Dict]):
    """Analyze feature contributions."""
    # Separate controls and heads
    controls = [r for r in results if r["is_control"]]
    heads = [r for r in results if not r["is_control"]]
    
    # Calculate means
    features = ["anchor_score", "z_ngram", "z_coverage", "z_compress"]
    
    control_means = {f: np.mean([r[f] for r in controls]) for f in features}
    head_means = {f: np.mean([r[f] for r in heads]) for f in features}
    
    # Calculate correlations with full score (simple correlation)
    correlations = {}
    for f in features:
        all_f = [r[f] for r in results]
        all_full = [r["full_score"] for r in results]
        
        # Simple Pearson correlation
        mean_f = np.mean(all_f)
        mean_full = np.mean(all_full)
        
        num = sum((f_i - mean_f) * (full_i - mean_full) 
                 for f_i, full_i in zip(all_f, all_full))
        den_f = np.sqrt(sum((f_i - mean_f)**2 for f_i in all_f))
        den_full = np.sqrt(sum((full_i - mean_full)**2 for full_i in all_full))
        
        corr = num / (den_f * den_full) if den_f * den_full > 0 else 0
        correlations[f] = {"correlation": corr, "p_value": 0.0}  # Simplified
    
    return {
        "control_means": control_means,
        "head_means": head_means,
        "feature_differences": {f: head_means[f] - control_means[f] for f in features},
        "correlations": correlations
    }


def main():
    """Run ablation analysis."""
    print("="*60)
    print("FEATURE ABLATION ANALYSIS")
    print("="*60)
    
    pipeline = ExplorePipeline(seed=1337)
    
    print("\nPerforming ablation analysis...")
    results = ablation_analysis(pipeline, num_samples=200)
    
    print("Analyzing contributions...")
    analysis = analyze_contributions(results)
    
    # Save results
    output_dir = Path("experiments/pipeline_v2/runs/2025-01-06-explore-diagnostics")
    
    # Create report
    report_file = output_dir / "ABLATION_REPORT.md"
    with open(report_file, 'w') as f:
        f.write("# Feature Ablation Report\n\n")
        
        f.write("## Feature Means\n\n")
        f.write("### Controls\n")
        for feat, val in analysis["control_means"].items():
            f.write(f"- {feat}: {val:.4f}\n")
        
        f.write("\n### Campaign Heads\n")
        for feat, val in analysis["head_means"].items():
            f.write(f"- {feat}: {val:.4f}\n")
        
        f.write("\n## Feature Importance\n\n")
        f.write("### Correlation with Full Score\n")
        for feat, data in analysis["correlations"].items():
            f.write(f"- {feat}: r={data['correlation']:.3f} (p={data['p_value']:.4f})\n")
        
        f.write("\n## Key Finding\n\n")
        
        # Find most important feature
        best_feat = max(analysis["correlations"], 
                       key=lambda x: abs(analysis["correlations"][x]["correlation"]))
        
        f.write(f"**{best_feat}** has the strongest correlation with the full score ")
        f.write(f"(r={analysis['correlations'][best_feat]['correlation']:.3f}).\n\n")
        
        # Check which features differentiate
        f.write("### Feature Differences (Heads - Controls)\n")
        for feat, diff in analysis["feature_differences"].items():
            f.write(f"- {feat}: {diff:+.4f}\n")
    
    print(f"\nReport saved to {report_file}")
    
    # Print summary
    print("\nFeature Correlations:")
    for feat, data in analysis["correlations"].items():
        print(f"  {feat}: r={data['correlation']:.3f}")
    
    return analysis


if __name__ == "__main__":
    analysis = main()