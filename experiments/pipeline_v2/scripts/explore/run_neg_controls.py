#!/usr/bin/env python3
"""
Run negative controls for Explore lane validation.
Tests scrambled anchors, permuted seam, and anchor-free decodes.
"""

import json
import random
import csv
from pathlib import Path
from typing import Dict, List
import sys

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from experiments.pipeline_v2.scripts.explore.run_anchor_modes import explore_score

def scramble_anchors(plaintext: str, anchor_positions: Dict[str, List[int]], seed: int) -> str:
    """
    Scramble anchor letters within each span.
    """
    random.seed(seed)
    result = list(plaintext)
    
    for anchor, positions in anchor_positions.items():
        if len(positions) != 2:
            continue
        start, end = positions
        
        if start < len(result) and end < len(result):
            # Extract anchor letters
            anchor_chars = result[start:end+1]
            # Scramble them
            random.shuffle(anchor_chars)
            # Put back
            result[start:end+1] = anchor_chars
    
    return ''.join(result)

def permute_seam(plaintext: str, seam_position: int, seed: int) -> str:
    """
    Permute tokens around seam position.
    """
    if seam_position <= 0 or seam_position >= len(plaintext):
        return plaintext
    
    random.seed(seed)
    
    # Split at seam
    left = list(plaintext[:seam_position])
    right = list(plaintext[seam_position:])
    
    # Permute last 10 chars of left and first 10 of right
    if len(left) > 10:
        segment = left[-10:]
        random.shuffle(segment)
        left[-10:] = segment
    
    if len(right) > 10:
        segment = right[:10]
        random.shuffle(segment)
        right[:10] = segment
    
    return ''.join(left + right)

def anchor_free_decode(plaintext: str, policy: Dict) -> Dict:
    """
    Decode without any anchor scoring/masks.
    """
    # Create policy without anchor scoring
    no_anchor_policy = json.loads(json.dumps(policy))  # Deep copy
    no_anchor_policy["scorer"]["blind_anchors"] = False
    no_anchor_policy["scorer"]["blind_narrative"] = False
    no_anchor_policy["anchor_config"]["anchors"] = {}
    
    return explore_score(plaintext, no_anchor_policy, blinded=False)

def run_negative_controls(plaintext: str, policy_path: Path, output_dir: Path, seed: int = 1337):
    """
    Run all negative control experiments.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load policy
    with open(policy_path) as f:
        policy = json.load(f)
    
    results = []
    
    print("Running negative controls...")
    
    # 1. Original (baseline)
    print("  Original baseline...")
    original_score = explore_score(plaintext, policy, blinded=True)
    results.append({
        "control_type": "original",
        "modification": "none",
        "score": original_score["final_score"],
        "coverage": original_score["coverage_score"],
        "ngram": original_score["ngram_score"],
        "compress": original_score["compress_score"]
    })
    
    # 2. Scrambled anchors
    print("  Scrambled anchors...")
    anchor_positions = {
        "EAST": [21, 24],
        "NORTHEAST": [25, 33],
        "BERLINCLOCK": [63, 73]
    }
    scrambled = scramble_anchors(plaintext, anchor_positions, seed)
    scrambled_score = explore_score(scrambled, policy, blinded=True)
    results.append({
        "control_type": "scrambled_anchors",
        "modification": "anchors_permuted",
        "score": scrambled_score["final_score"],
        "coverage": scrambled_score["coverage_score"],
        "ngram": scrambled_score["ngram_score"],
        "compress": scrambled_score["compress_score"]
    })
    
    # 3. Permuted seam
    print("  Permuted seam...")
    seam_pos = 74  # Position 74
    seam_permuted = permute_seam(plaintext, seam_pos, seed + 1)
    seam_score = explore_score(seam_permuted, policy, blinded=True)
    results.append({
        "control_type": "permuted_seam",
        "modification": f"seam_at_{seam_pos}",
        "score": seam_score["final_score"],
        "coverage": seam_score["coverage_score"],
        "ngram": seam_score["ngram_score"],
        "compress": seam_score["compress_score"]
    })
    
    # 4. Anchor-free
    print("  Anchor-free decode...")
    free_score = anchor_free_decode(plaintext, policy)
    results.append({
        "control_type": "anchor_free",
        "modification": "no_anchor_scoring",
        "score": free_score["final_score"],
        "coverage": free_score["coverage_score"],
        "ngram": free_score["ngram_score"],
        "compress": free_score["compress_score"]
    })
    
    # 5. Random shuffle (complete negative control)
    print("  Random shuffle...")
    random.seed(seed + 2)
    shuffled = list(plaintext)
    random.shuffle(shuffled)
    shuffled_text = ''.join(shuffled)
    shuffle_score = explore_score(shuffled_text, policy, blinded=True)
    results.append({
        "control_type": "random_shuffle",
        "modification": "complete_shuffle",
        "score": shuffle_score["final_score"],
        "coverage": shuffle_score["coverage_score"],
        "ngram": shuffle_score["ngram_score"],
        "compress": shuffle_score["compress_score"]
    })
    
    # Compute deltas
    baseline = original_score["final_score"]
    for result in results:
        result["delta_from_original"] = result["score"] - baseline
        result["ratio_to_original"] = result["score"] / max(0.001, baseline)
    
    # Write results
    csv_path = output_dir / "NEG_CONTROL_SUMMARY.csv"
    with open(csv_path, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    # Write detailed report
    report = {
        "timestamp": Path(output_dir).name,
        "seed": seed,
        "baseline_score": baseline,
        "controls": results,
        "summary": {
            "scrambled_degrades": results[1]["delta_from_original"] < -0.05,
            "seam_affects": abs(results[2]["delta_from_original"]) > 0.02,
            "anchors_matter": abs(results[3]["delta_from_original"]) > 0.01,
            "random_worst": results[4]["score"] < baseline * 0.5
        }
    }
    
    json_path = output_dir / "neg_control_report.json"
    with open(json_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nNegative control results:")
    for r in results:
        print(f"  {r['control_type']}: {r['score']:.3f} (Δ={r['delta_from_original']:+.3f})")
    
    return csv_path

def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Run negative controls")
    parser.add_argument("--plaintext", default="WECANSEETHETEXTISCODEEASTNORTHEASTWESETTHECOURSETRUEREADTHENSEEBERLINCLOCKTHEJOYOFANANGLEISTHEARC")
    parser.add_argument("--policy", default="experiments/pipeline_v2/policies/explore/POLICY.neg_controls.json")
    parser.add_argument("--output", default="experiments/pipeline_v2/runs/2025-01-05/explore/neg_controls/")
    parser.add_argument("--seed", type=int, default=1337)
    
    args = parser.parse_args()
    
    # Create policy if needed
    if not Path(args.policy).exists():
        print(f"Creating negative control policy: {args.policy}")
        policy = {
            "name": "negative_controls",
            "random_seeds": {
                "scramble": 42,
                "seam": 43,
                "shuffle": 44
            },
            "anchor_config": {
                "anchors": {
                    "EAST": {"span": [21, 24], "weight": 0.1},
                    "NORTHEAST": {"span": [25, 33], "weight": 0.1},
                    "BERLINCLOCK": {"span": [63, 73], "weight": 0.1}
                }
            },
            "scorer": {
                "ngram_weight": 0.4,
                "coverage_weight": 0.3,
                "compress_weight": 0.3,
                "blind_anchors": True,
                "blind_narrative": True
            }
        }
        Path(args.policy).parent.mkdir(parents=True, exist_ok=True)
        with open(args.policy, 'w') as f:
            json.dump(policy, f, indent=2)
    
    run_negative_controls(args.plaintext, Path(args.policy), Path(args.output), args.seed)

if __name__ == "__main__":
    main()