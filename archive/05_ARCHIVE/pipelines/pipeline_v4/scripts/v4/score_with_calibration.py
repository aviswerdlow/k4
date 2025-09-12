#!/usr/bin/env python3
"""
Fixed scoring pipeline with proper calibration-based delta computation.
"""

import json
import csv
import sys
import random
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directories
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from experiments.pipeline_v4.scripts.v4.gen_blinded_mcmc import BlindedMCMCGenerator


class CalibratedScorer:
    """
    Score heads with proper calibration and delta computation.
    """
    
    def __init__(self, seed: int = 1337):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        # Initialize blinded scorer
        self.blinded_scorer = BlindedMCMCGenerator(seed)
        
        # Load calibration
        self.calibration = self.load_calibration()
        
    def load_calibration(self) -> Dict:
        """Load calibration stats."""
        calibration_path = Path(__file__).parent.parent.parent / "calibration" / "baseline_v4.json"
        
        if not calibration_path.exists():
            raise FileNotFoundError(f"Calibration not found at {calibration_path}")
        
        with open(calibration_path, 'r') as f:
            return json.load(f)
    
    def apply_anchors(self, text: str, policy: str, window_radius: int = 0) -> str:
        """Apply anchors to text according to policy."""
        if len(text) != 75:
            text = (text + "X" * 75)[:75]
        
        text_list = list(text)
        
        if policy == "fixed" or window_radius == 0:
            # Fixed placement
            text_list[21:25] = "EAST"
            text_list[25:34] = "NORTHEAST"
            text_list[63:74] = "BERLINCLOCK"
        elif policy == "shuffled" or window_radius >= 100:
            # Shuffled - randomly place
            positions = sorted(random.sample(range(60), 3))
            text_list[positions[0]:positions[0]+4] = "EAST"
            text_list[positions[1]:positions[1]+9] = "NORTHEAST"
            text_list[positions[2]:positions[2]+11] = "BERLINCLOCK"
        else:
            # Windowed placement
            offset1 = random.randint(-window_radius, window_radius)
            offset2 = random.randint(-window_radius, window_radius)
            offset3 = random.randint(-window_radius, window_radius)
            
            pos1 = max(0, min(71, 21 + offset1))
            pos2 = max(pos1 + 4, min(66, 25 + offset2))
            pos3 = max(pos2 + 9, min(64, 63 + offset3))
            
            text_list[pos1:pos1+4] = "EAST"
            text_list[pos2:pos2+9] = "NORTHEAST"
            text_list[pos3:pos3+11] = "BERLINCLOCK"
        
        return ''.join(text_list[:75])
    
    def score_head(self, text: str, label: str = "unknown") -> Dict:
        """
        Score a single head with all policies and compute deltas.
        """
        policies = [
            ("fixed", 0),
            ("windowed_r2", 2),
            ("windowed_r3", 3),
            ("windowed_r4", 4),
            ("shuffled", 100)
        ]
        
        results = {}
        z_scores = {}
        
        # Score original (no anchors)
        original_score, _ = self.blinded_scorer.compute_blinded_score(text)
        
        # Score with each policy
        for policy_name, radius in policies:
            # Apply anchors
            anchored_text = self.apply_anchors(text, policy_name, radius)
            
            # Compute blinded score
            score, components = self.blinded_scorer.compute_blinded_score(anchored_text)
            
            # Get calibration stats
            mu = self.calibration[policy_name]["mu"]
            sigma = self.calibration[policy_name]["sigma"]
            
            # Compute z-score
            z = (score - mu) / max(0.001, sigma)
            
            results[policy_name] = {
                "S_blind": score,
                "z": z,
                "mu": mu,
                "sigma": sigma
            }
            z_scores[policy_name] = z
        
        # Compute deltas (NO CLAMPING!)
        z_fixed = z_scores["fixed"]
        delta_windowed_best = max(
            z_fixed - z_scores["windowed_r2"],
            z_fixed - z_scores["windowed_r3"],
            z_fixed - z_scores["windowed_r4"]
        )
        delta_shuffled = z_fixed - z_scores["shuffled"]
        
        # Check thresholds
        pass_windowed = delta_windowed_best >= 0.05
        pass_shuffled = delta_shuffled >= 0.10
        candidate = pass_windowed and pass_shuffled
        
        return {
            "label": label,
            "original_score": original_score,
            "policies": results,
            "z_scores": z_scores,
            "delta_windowed_best": delta_windowed_best,
            "delta_shuffled": delta_shuffled,
            "pass_windowed": pass_windowed,
            "pass_shuffled": pass_shuffled,
            "candidate": candidate
        }
    
    def score_batch(self, heads: List[Dict], output_csv: Path = None) -> List[Dict]:
        """
        Score a batch of heads and optionally save to CSV.
        """
        results = []
        
        print(f"Scoring {len(heads)} heads...")
        print(f"{'Label':<25} {'S_orig':>7} {'z_fix':>7} {'δ_win':>7} {'δ_shuf':>7} {'Pass?':>6}")
        print("-" * 70)
        
        for i, head in enumerate(heads):
            if isinstance(head, dict):
                text = head.get('repaired_text', head.get('text', ''))
                label = head.get('label', f'head_{i}')
            else:
                text = head
                label = f'head_{i}'
            
            result = self.score_head(text, label)
            results.append(result)
            
            # Print summary
            print(f"{label:<25} {result['original_score']:7.3f} "
                  f"{result['z_scores']['fixed']:7.3f} "
                  f"{result['delta_windowed_best']:7.3f} "
                  f"{result['delta_shuffled']:7.3f} "
                  f"{'YES' if result['candidate'] else 'NO':>6}")
        
        # Summary stats
        n_pass_win = sum(1 for r in results if r['pass_windowed'])
        n_pass_shuf = sum(1 for r in results if r['pass_shuffled'])
        n_candidates = sum(1 for r in results if r['candidate'])
        
        print("-" * 70)
        print(f"Pass windowed: {n_pass_win}/{len(heads)} ({100*n_pass_win/len(heads):.1f}%)")
        print(f"Pass shuffled: {n_pass_shuf}/{len(heads)} ({100*n_pass_shuf/len(heads):.1f}%)")
        print(f"Candidates: {n_candidates}/{len(heads)} ({100*n_candidates/len(heads):.1f}%)")
        
        # Save to CSV if requested
        if output_csv:
            with open(output_csv, 'w', newline='') as f:
                fieldnames = [
                    'label', 'grid', 'anchor_mode',
                    'S_blind_orig', 'S_blind_fixed',
                    'z_fixed', 'z_win_r2', 'z_win_r3', 'z_win_r4', 'z_shuffled',
                    'delta_vs_windowed', 'delta_vs_shuffled',
                    'pass_windowed', 'pass_shuffled', 'candidate'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for r in results:
                    writer.writerow({
                        'label': r['label'],
                        'grid': 'v4_track_a_scaled',
                        'anchor_mode': 'fixed',
                        'S_blind_orig': f"{r['original_score']:.3f}",
                        'S_blind_fixed': f"{r['policies']['fixed']['S_blind']:.3f}",
                        'z_fixed': f"{r['z_scores']['fixed']:.3f}",
                        'z_win_r2': f"{r['z_scores']['windowed_r2']:.3f}",
                        'z_win_r3': f"{r['z_scores']['windowed_r3']:.3f}",
                        'z_win_r4': f"{r['z_scores']['windowed_r4']:.3f}",
                        'z_shuffled': f"{r['z_scores']['shuffled']:.3f}",
                        'delta_vs_windowed': f"{r['delta_windowed_best']:.3f}",
                        'delta_vs_shuffled': f"{r['delta_shuffled']:.3f}",
                        'pass_windowed': r['pass_windowed'],
                        'pass_shuffled': r['pass_shuffled'],
                        'candidate': r['candidate']
                    })
            
            print(f"\nSaved results to {output_csv}")
        
        return results


def main():
    """Score the 25 review heads with fixed pipeline."""
    scorer = CalibratedScorer(seed=1337)
    
    # Load processed heads
    heads_file = Path(__file__).parent.parent.parent / "runs" / "track_a_scaled" / "processed_heads_review.json"
    
    if not heads_file.exists():
        print(f"❌ Processed heads not found at {heads_file}")
        return
    
    with open(heads_file, 'r') as f:
        data = json.load(f)
    
    heads = data['heads']
    print(f"Loaded {len(heads)} processed heads")
    
    # Score with fixed pipeline
    output_csv = Path(__file__).parent.parent.parent / "runs" / "track_a_scaled" / "EXPLORE_MATRIX_FIXED.csv"
    results = scorer.score_batch(heads, output_csv)
    
    # Save detailed results
    output_json = Path(__file__).parent.parent.parent / "runs" / "track_a_scaled" / "scoring_results_fixed.json"
    with open(output_json, 'w') as f:
        # Convert numpy types for JSON serialization
        clean_results = []
        for r in results:
            clean_r = {
                'label': r['label'],
                'original_score': float(r['original_score']),
                'delta_windowed_best': float(r['delta_windowed_best']),
                'delta_shuffled': float(r['delta_shuffled']),
                'pass_windowed': bool(r['pass_windowed']),
                'pass_shuffled': bool(r['pass_shuffled']),
                'candidate': bool(r['candidate']),
                'z_scores': {k: float(v) for k, v in r['z_scores'].items()}
            }
            clean_results.append(clean_r)
        
        json.dump({
            'n_heads': len(heads),
            'n_candidates': sum(1 for r in results if r['candidate']),
            'results': clean_results
        }, f, indent=2)
    
    print(f"Saved detailed results to {output_json}")


if __name__ == "__main__":
    main()