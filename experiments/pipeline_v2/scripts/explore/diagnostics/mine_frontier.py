#!/usr/bin/env python3
"""
Mine near-miss candidates from C7-C16 campaigns.
Find heads that are close to passing delta thresholds.
"""

import json
import csv
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np

# Add pipeline modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.explore.run_family import ExplorePipeline


def load_campaign_results(campaign_id: str, base_dir: Path) -> List[Dict]:
    """Load results from a campaign."""
    campaign_dir = base_dir / f"runs/2025-01-06-explore-ideas-{campaign_id}"
    
    # Find heads file
    heads_files = list(campaign_dir.glob("heads_*.json"))
    if not heads_files:
        return []
    
    with open(heads_files[0]) as f:
        data = json.load(f)
    
    # Check for scoring results
    matrix_file = campaign_dir / "EXPLORE_MATRIX.csv"
    if matrix_file.exists():
        # Load existing scores
        scores = {}
        with open(matrix_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                label = row.get("label", "")
                if label:
                    scores[label] = {
                        "delta_vs_windowed": float(row.get("delta_vs_windowed", 0)),
                        "delta_vs_shuffled": float(row.get("delta_vs_shuffled", 0))
                    }
        
        # Attach scores to heads
        for head in data["heads"]:
            if head["label"] in scores:
                head["scores"] = scores[head["label"]]
    
    return data.get("heads", [])


def mine_near_misses(
    epsilon: float = 0.02,
    delta_thresholds: Dict[str, float] = None
) -> List[Dict]:
    """
    Mine candidates that are within epsilon of passing thresholds.
    
    Args:
        epsilon: Distance from threshold to consider
        delta_thresholds: Delta requirements (default 0.05, 0.10)
    
    Returns:
        List of near-miss candidates
    """
    if delta_thresholds is None:
        delta_thresholds = {
            "windowed": 0.05,
            "shuffled": 0.10
        }
    
    base_dir = Path("experiments/pipeline_v2")
    pipeline = ExplorePipeline(seed=1337)
    
    near_misses = []
    
    # Process each campaign
    for campaign_id in ["C7", "C8", "C9", "C10", "C11", "C12", "C13", "C14", "C15", "C16"]:
        print(f"Processing {campaign_id}...")
        
        heads = load_campaign_results(campaign_id, base_dir)
        
        for head in heads:
            text = head["text"]
            label = head["label"]
            
            # Score if not already scored
            if "scores" not in head:
                # Run scoring
                policies = [
                    {"name": "fixed", "window_radius": 0, "typo_budget": 0},
                    {"name": "windowed_r2", "window_radius": 2, "typo_budget": 0},
                    {"name": "shuffled", "window_radius": 100, "typo_budget": 2}
                ]
                
                mode_results = pipeline.run_anchor_modes(text, policies)
                head["scores"] = {
                    "delta_vs_windowed": mode_results["delta_vs_windowed"],
                    "delta_vs_shuffled": mode_results["delta_vs_shuffled"]
                }
            
            # Check if near miss
            delta_w = head["scores"]["delta_vs_windowed"]
            delta_s = head["scores"]["delta_vs_shuffled"]
            
            # Distance from passing both thresholds
            dist_w = delta_thresholds["windowed"] - delta_w
            dist_s = delta_thresholds["shuffled"] - delta_s
            
            # Check if within epsilon of BOTH thresholds
            if dist_w <= epsilon and dist_s <= epsilon:
                # Calculate combined distance metric
                combined_distance = np.sqrt(dist_w**2 + dist_s**2)
                
                near_misses.append({
                    "campaign": campaign_id,
                    "label": label,
                    "text": text,
                    "delta_vs_windowed": delta_w,
                    "delta_vs_shuffled": delta_s,
                    "distance_windowed": dist_w,
                    "distance_shuffled": dist_s,
                    "combined_distance": combined_distance,
                    "metadata": head.get("metadata", {})
                })
    
    # Sort by combined distance (closest first)
    near_misses.sort(key=lambda x: x["combined_distance"])
    
    return near_misses


def main():
    """Run frontier mining."""
    print("="*60)
    print("NEAR-MISS MINING")
    print("="*60)
    
    # Mine with different epsilon values
    epsilons = [0.02, 0.05, 0.10]
    
    for epsilon in epsilons:
        print(f"\nMining with epsilon = {epsilon}...")
        
        near_misses = mine_near_misses(epsilon=epsilon)
        
        print(f"Found {len(near_misses)} near-misses within {epsilon} of both thresholds")
        
        if near_misses:
            # Save results
            output_dir = Path("experiments/pipeline_v2/runs/2025-01-06-explore-diagnostics")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Take top 100
            top_misses = near_misses[:100]
            
            # Save CSV
            csv_file = output_dir / f"FRONTIER_eps{epsilon:.2f}.csv"
            with open(csv_file, 'w', newline='') as f:
                fieldnames = [
                    "campaign", "label", "delta_vs_windowed", "delta_vs_shuffled",
                    "distance_windowed", "distance_shuffled", "combined_distance"
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for miss in top_misses:
                    writer.writerow({k: miss[k] for k in fieldnames})
            
            print(f"Saved top {len(top_misses)} to {csv_file}")
            
            # Show top 5
            print("\nTop 5 closest:")
            for i, miss in enumerate(top_misses[:5]):
                print(f"  {i+1}. {miss['campaign']}/{miss['label']}")
                print(f"     Deltas: windowed={miss['delta_vs_windowed']:.4f}, shuffled={miss['delta_vs_shuffled']:.4f}")
                print(f"     Distance: {miss['combined_distance']:.4f}")
    
    # Create report
    report_file = output_dir / "FRONTIER_REPORT.md"
    with open(report_file, 'w') as f:
        f.write("# Near-Miss Mining Report\n\n")
        f.write("## Summary\n\n")
        
        if len(near_misses) == 0:
            f.write("**No near-misses found within epsilon=0.10 of both thresholds.**\n\n")
            f.write("This suggests the hypothesis space is far from the delta requirements.\n")
        else:
            f.write(f"Found {len(near_misses)} candidates within epsilon=0.10 of both thresholds.\n\n")
            f.write("### Closest Candidates\n\n")
            
            for i, miss in enumerate(near_misses[:10]):
                f.write(f"{i+1}. **{miss['campaign']}/{miss['label']}**\n")
                f.write(f"   - Delta vs windowed: {miss['delta_vs_windowed']:.4f} (need >0.05)\n")
                f.write(f"   - Delta vs shuffled: {miss['delta_vs_shuffled']:.4f} (need >0.10)\n")
                f.write(f"   - Combined distance: {miss['combined_distance']:.4f}\n\n")
    
    print(f"\nReport saved to {report_file}")
    
    return near_misses


if __name__ == "__main__":
    near_misses = main()