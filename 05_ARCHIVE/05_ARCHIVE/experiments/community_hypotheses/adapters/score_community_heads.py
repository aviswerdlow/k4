#!/usr/bin/env python3
"""
Score community hypothesis heads through the Explore pipeline.
Uses the proven v2 scoring with windowed anchor modes.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
import hashlib

# Add pipeline_v2 to path
pipeline_path = Path(__file__).parent.parent.parent / "pipeline_v2"
sys.path.insert(0, str(pipeline_path))

# Now import with correct module paths
from scripts.explore.compute_score_v2 import compute_normalized_score_v2
from scripts.explore.blind_text import blind_text
from scripts.explore.run_anchor_modes import compute_ngram_score, compute_coverage_score, compute_compress_score
import random
import string


def compute_baseline_stats(num_samples: int = 1000, seed: int = 1337) -> Dict:
    """
    Compute baseline statistics from random text.
    
    Args:
        num_samples: Number of random samples
        seed: Random seed
    
    Returns:
        Baseline statistics for normalization
    """
    random.seed(seed)
    
    ngram_scores = []
    coverage_scores = []
    compress_scores = []
    
    for _ in range(num_samples):
        # Generate random text
        text = ''.join(random.choices(string.ascii_uppercase, k=75))
        
        # Blind it
        blinded, _ = blind_text(text, blind_anchors=True, blind_narrative=True)
        
        # Compute scores
        ngram_scores.append(compute_ngram_score(blinded))
        coverage_scores.append(compute_coverage_score(blinded))
        compress_scores.append(compute_compress_score(blinded))
    
    import numpy as np
    
    return {
        "ngram_mean": float(np.mean(ngram_scores)),
        "ngram_std": float(np.std(ngram_scores)),
        "coverage_mean": float(np.mean(coverage_scores)),
        "coverage_std": float(np.std(coverage_scores)),
        "compress_mean": float(np.mean(compress_scores)),
        "compress_std": float(np.std(compress_scores))
    }


def score_campaign_heads(
    heads_file: Path,
    output_dir: Path,
    policies: List[Dict] = None
) -> Dict:
    """
    Score campaign heads through Explore pipeline.
    
    Args:
        heads_file: JSON file with heads to score
        output_dir: Directory for score outputs
        policies: List of window policies to test
    
    Returns:
        Aggregated results
    """
    # Load heads
    with open(heads_file) as f:
        data = json.load(f)
    
    heads = data["heads"]
    campaign = data["campaign"]
    
    print(f"\nScoring {campaign}: {len(heads)} heads")
    
    # Default policies if not provided
    if not policies:
        policies = [
            {"name": "fixed", "window_radius": 0, "typo_budget": 0},
            {"name": "windowed_r2_t0", "window_radius": 2, "typo_budget": 0},
            {"name": "windowed_r5_t1", "window_radius": 5, "typo_budget": 1},
            {"name": "windowed_r10_t2", "window_radius": 10, "typo_budget": 2}
        ]
    
    # Compute baseline once
    print("Computing baseline stats...")
    baseline_stats = compute_baseline_stats(num_samples=1000, seed=1337)
    
    # Score each head
    all_results = []
    promotions = 0
    
    for i, head in enumerate(heads):
        if i % 20 == 0:
            print(f"  Scoring head {i+1}/{len(heads)}...")
        
        text = head["text"]
        label = head["label"]
        
        # Run all anchor modes
        head_results = []
        
        for policy in policies:
            # Score with v2 (anchors before blinding)
            result = compute_normalized_score_v2(text, policy, baseline_stats)
            
            # Compute z-score (average of normalized components)
            z_score = (result["z_ngram"] + result["z_coverage"] + result["z_compress"]) / 3
            
            # For now, we'll use z-score as proxy for deltas
            # (In full pipeline, would compare to windowed/shuffled baselines)
            delta1 = max(0, z_score - 1.0) * 0.02  # Rough approximation
            delta2 = max(0, z_score - 0.5) * 0.05  # Rough approximation
            
            # Store result
            head_result = {
                "label": label,
                "policy": policy["name"],
                "score": result["score_norm"],
                "z_score": z_score,
                "delta1": delta1,
                "delta2": delta2,
                "promoted": delta1 > 0.05 and delta2 > 0.10
            }
            head_results.append(head_result)
            
            if head_result["promoted"]:
                promotions += 1
        
        all_results.extend(head_results)
    
    # Aggregate results
    print(f"\nResults for {campaign}:")
    print(f"  Total heads: {len(heads)}")
    print(f"  Total tests: {len(all_results)}")
    print(f"  Promotions: {promotions}")
    
    # Save results
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results_file = output_dir / f"scores_{campaign.lower()}.json"
    results_data = {
        "campaign": campaign,
        "heads_file": str(heads_file),
        "num_heads": len(heads),
        "policies": policies,
        "baseline_stats": baseline_stats,
        "promotions": promotions,
        "results": all_results
    }
    
    with open(results_file, 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"  Results saved to: {results_file}")
    
    # Create summary
    summary = {
        "campaign": campaign,
        "heads": len(heads),
        "policies": len(policies),
        "tests": len(all_results),
        "promotions": promotions,
        "promotion_rate": promotions / len(all_results) if all_results else 0,
        "file": str(results_file),
        "hash": hashlib.sha256(json.dumps(results_data, sort_keys=True).encode()).hexdigest()[:16]
    }
    
    summary_file = output_dir / f"summary_{campaign.lower()}.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    return summary


def score_all_campaigns(base_dir: Path):
    """
    Score all community hypothesis campaigns.
    
    Args:
        base_dir: Base directory with campaigns
    """
    campaigns = [
        "c1_quagmire",
        "c2_trifid_cube",
        "c3_morse",
        "c4_bigram_polybius",
        "c5_time_key",
        "c6_letter_shape"
    ]
    
    summaries = []
    
    for campaign in campaigns:
        heads_file = base_dir / f"runs/2025-01-06-campaign-{campaign.split('_')[0]}" / f"heads_{campaign}.json"
        
        if not heads_file.exists():
            print(f"Skipping {campaign} - no heads file found")
            continue
        
        output_dir = heads_file.parent
        summary = score_campaign_heads(heads_file, output_dir)
        summaries.append(summary)
    
    # Create aggregate dashboard
    dashboard = {
        "date": "2025-01-06",
        "title": "Community Hypothesis Mining Results",
        "total_campaigns": len(summaries),
        "total_promotions": sum(s["promotions"] for s in summaries),
        "campaigns": summaries
    }
    
    dashboard_file = base_dir / "COMMUNITY_DASHBOARD.json"
    with open(dashboard_file, 'w') as f:
        json.dump(dashboard, f, indent=2)
    
    print(f"\nAggregate dashboard: {dashboard_file}")
    print(f"Total promotions across all campaigns: {dashboard['total_promotions']}")
    
    return dashboard


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Score community hypothesis heads")
    parser.add_argument("--campaign", help="Specific campaign to score (e.g., c1)")
    parser.add_argument("--all", action="store_true", help="Score all campaigns")
    parser.add_argument("--base-dir",
                       default="experiments/community_hypotheses",
                       help="Base directory")
    
    args = parser.parse_args()
    
    base_dir = Path(args.base_dir)
    
    if args.all:
        score_all_campaigns(base_dir)
    elif args.campaign:
        campaign_id = args.campaign.lower()
        if campaign_id == "c1":
            heads_file = base_dir / "runs/2025-01-06-campaign-c1/heads_c1_quagmire.json"
            output_dir = heads_file.parent
            score_campaign_heads(heads_file, output_dir)
        # Add other campaigns as implemented
    else:
        print("Specify --campaign or --all")


if __name__ == "__main__":
    main()