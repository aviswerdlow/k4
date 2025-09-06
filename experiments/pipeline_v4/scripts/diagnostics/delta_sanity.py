#!/usr/bin/env python3
"""
Delta scoring diagnostics and sanity tests.
"""

import json
import sys
import random
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directories
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from experiments.pipeline_v2.scripts.explore.run_family import ExplorePipeline
from experiments.pipeline_v4.scripts.v4.gen_blinded_mcmc import BlindedMCMCGenerator


class DeltaDiagnostics:
    """
    Diagnose and fix delta scoring issues.
    """
    
    def __init__(self, seed: int = 1337):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        # Initialize scorers
        self.pipeline = ExplorePipeline(seed)
        self.blinded_scorer = BlindedMCMCGenerator(seed)
        
        # Load or create calibration
        self.calibration = self.load_calibration()
        
    def load_calibration(self) -> Dict:
        """Load calibration stats or create default ones."""
        calibration_path = Path(__file__).parent.parent.parent / "calibration" / "baseline_v4.json"
        
        if calibration_path.exists():
            print(f"Loading calibration from {calibration_path}")
            with open(calibration_path, 'r') as f:
                calib = json.load(f)
            print("Calibration loaded:")
            for policy, stats in calib.items():
                print(f"  {policy}: μ={stats['mu']:.3f}, σ={stats['sigma']:.3f}, N={stats.get('N', 'unknown')}")
            return calib
        else:
            print("⚠️ No calibration found, generating default...")
            return self.generate_calibration()
    
    def generate_calibration(self, n_samples: int = 1000) -> Dict:
        """Generate calibration from random samples."""
        print(f"Generating calibration from {n_samples} random samples...")
        
        policies = [
            {"name": "fixed", "window_radius": 0, "typo_budget": 0},
            {"name": "windowed_r2", "window_radius": 2, "typo_budget": 0},
            {"name": "windowed_r3", "window_radius": 3, "typo_budget": 0},
            {"name": "windowed_r4", "window_radius": 4, "typo_budget": 0},
            {"name": "shuffled", "window_radius": 100, "typo_budget": 2}
        ]
        
        calibration = {}
        
        for policy in policies:
            scores = []
            for i in range(n_samples):
                # Generate random text
                text = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=75))
                
                # Apply anchors according to policy
                if policy["window_radius"] == 0:
                    # Fixed placement
                    text = text[:21] + "EAST" + text[25:25] + "NORTHEAST" + text[34:63] + "BERLINCLOCK" + text[74:]
                elif policy["window_radius"] < 100:
                    # Windowed placement with some randomness
                    offset1 = random.randint(-policy["window_radius"], policy["window_radius"])
                    offset2 = random.randint(-policy["window_radius"], policy["window_radius"])
                    offset3 = random.randint(-policy["window_radius"], policy["window_radius"])
                    
                    pos1 = max(0, min(71, 21 + offset1))
                    pos2 = max(pos1 + 4, min(66, 25 + offset2))
                    pos3 = max(pos2 + 9, min(64, 63 + offset3))
                    
                    text_list = list(text)
                    text_list[pos1:pos1+4] = "EAST"
                    text_list[pos2:pos2+9] = "NORTHEAST"
                    text_list[pos3:pos3+11] = "BERLINCLOCK"
                    text = ''.join(text_list[:75])
                else:
                    # Shuffled - randomly place anchors
                    positions = sorted(random.sample(range(60), 3))
                    text_list = list(text)
                    text_list[positions[0]:positions[0]+4] = "EAST"
                    text_list[positions[1]:positions[1]+9] = "NORTHEAST"
                    text_list[positions[2]:positions[2]+11] = "BERLINCLOCK"
                    text = ''.join(text_list[:75])
                
                # Score with blinded scorer
                score, _ = self.blinded_scorer.compute_blinded_score(text)
                scores.append(score)
            
            mu = np.mean(scores)
            sigma = np.std(scores)
            
            calibration[policy["name"]] = {
                "mu": float(mu),
                "sigma": float(sigma),
                "N": n_samples
            }
            
            print(f"  {policy['name']}: μ={mu:.3f}, σ={sigma:.3f}")
        
        # Save calibration
        calibration_dir = Path(__file__).parent.parent.parent / "calibration"
        calibration_dir.mkdir(exist_ok=True)
        calibration_path = calibration_dir / "baseline_v4.json"
        
        with open(calibration_path, 'w') as f:
            json.dump(calibration, f, indent=2)
        
        print(f"Saved calibration to {calibration_path}")
        return calibration
    
    def compute_z_scores(self, text: str, debug: bool = True) -> Dict:
        """
        Compute z-scores for all policies on given text.
        """
        policies = [
            {"name": "fixed", "window_radius": 0, "typo_budget": 0},
            {"name": "windowed_r2", "window_radius": 2, "typo_budget": 0},
            {"name": "windowed_r3", "window_radius": 3, "typo_budget": 0},
            {"name": "windowed_r4", "window_radius": 4, "typo_budget": 0},
            {"name": "shuffled", "window_radius": 100, "typo_budget": 2}
        ]
        
        results = {}
        
        for policy in policies:
            # Apply anchors
            anchored_text = self.apply_anchors(text, policy)
            
            # Compute blinded score
            score, components = self.blinded_scorer.compute_blinded_score(anchored_text)
            
            # Get calibration stats
            mu = self.calibration[policy["name"]]["mu"]
            sigma = self.calibration[policy["name"]]["sigma"]
            
            # Compute z-score
            z = (score - mu) / max(0.001, sigma)
            
            results[policy["name"]] = {
                "text": anchored_text[:30] + "...",
                "S_blind": score,
                "mu": mu,
                "sigma": sigma,
                "z": z,
                "components": components
            }
            
            if debug:
                print(f"  {policy['name']:12} S={score:6.3f} μ={mu:6.3f} σ={sigma:6.3f} z={z:6.3f}")
        
        # Compute deltas
        z_fixed = results["fixed"]["z"]
        z_win_r2 = results["windowed_r2"]["z"]
        z_win_r3 = results["windowed_r3"]["z"]
        z_win_r4 = results["windowed_r4"]["z"]
        z_shuffled = results["shuffled"]["z"]
        
        delta_windowed_best = max(z_fixed - z_win_r2, z_fixed - z_win_r3, z_fixed - z_win_r4)
        delta_shuffled = z_fixed - z_shuffled
        
        if debug:
            print(f"  delta_windowed_best = {delta_windowed_best:.3f}")
            print(f"  delta_shuffled = {delta_shuffled:.3f}")
        
        results["deltas"] = {
            "delta_windowed_best": delta_windowed_best,
            "delta_shuffled": delta_shuffled,
            "pass_windowed": delta_windowed_best >= 0.05,
            "pass_shuffled": delta_shuffled >= 0.10,
            "candidate": delta_windowed_best >= 0.05 and delta_shuffled >= 0.10
        }
        
        return results
    
    def apply_anchors(self, text: str, policy: Dict) -> str:
        """Apply anchors to text according to policy."""
        if len(text) != 75:
            text = (text + "X" * 75)[:75]
        
        text_list = list(text)
        
        if policy["window_radius"] == 0:
            # Fixed placement
            text_list[21:25] = "EAST"
            text_list[25:34] = "NORTHEAST"
            text_list[63:74] = "BERLINCLOCK"
        elif policy["window_radius"] < 100:
            # Windowed placement
            offset1 = random.randint(-policy["window_radius"], policy["window_radius"])
            offset2 = random.randint(-policy["window_radius"], policy["window_radius"])
            offset3 = random.randint(-policy["window_radius"], policy["window_radius"])
            
            pos1 = max(0, min(71, 21 + offset1))
            pos2 = max(pos1 + 4, min(66, 25 + offset2))
            pos3 = max(pos2 + 9, min(64, 63 + offset3))
            
            text_list[pos1:pos1+4] = "EAST"
            text_list[pos2:pos2+9] = "NORTHEAST"
            text_list[pos3:pos3+11] = "BERLINCLOCK"
        else:
            # Shuffled - randomly place
            positions = sorted(random.sample(range(60), 3))
            text_list[positions[0]:positions[0]+4] = "EAST"
            text_list[positions[1]:positions[1]+9] = "NORTHEAST"
            text_list[positions[2]:positions[2]+11] = "BERLINCLOCK"
        
        return ''.join(text_list[:75])
    
    def sanity_test_1_reference(self):
        """Test 1: High-probability reference head."""
        print("\n" + "="*60)
        print("SANITY TEST 1: Reference Head (common bigrams)")
        print("="*60)
        
        # Build from common bigrams
        common_bigrams = ["TH", "HE", "ER", "AN", "ED", "ND", "TO", "EN", "ES", "OF", "TE", "AT", "ON", "IN", "IT", "AL", "AR", "OU", "RE", "NG", "ST", "NT", "IS", "OR", "ET"]
        
        text = ""
        for _ in range(37):
            bigram = random.choice(common_bigrams)
            text += bigram
        text = text[:75]
        
        print(f"Text: {text[:30]}...")
        results = self.compute_z_scores(text)
        
        print("\nExpectation: z_fixed > 0, delta_shuffled > 0")
        print(f"Result: z_fixed={results['fixed']['z']:.3f}, delta_shuffled={results['deltas']['delta_shuffled']:.3f}")
        
        return results
    
    def sanity_test_2_worst(self):
        """Test 2: Worst-case random head."""
        print("\n" + "="*60)
        print("SANITY TEST 2: Worst-case Head (uniform random)")
        print("="*60)
        
        # Completely random
        text = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=75))
        
        print(f"Text: {text[:30]}...")
        results = self.compute_z_scores(text)
        
        print("\nExpectation: z_fixed ≈ 0, delta_shuffled ≤ 0")
        print(f"Result: z_fixed={results['fixed']['z']:.3f}, delta_shuffled={results['deltas']['delta_shuffled']:.3f}")
        
        return results
    
    def sanity_test_3_policy_separation(self):
        """Test 3: Policy separation."""
        print("\n" + "="*60)
        print("SANITY TEST 3: Policy Separation")
        print("="*60)
        
        # Use a real generated head
        heads_file = Path(__file__).parent.parent.parent / "runs" / "track_a_scaled" / "blinded_heads_scaled_review.json"
        
        if heads_file.exists():
            with open(heads_file, 'r') as f:
                data = json.load(f)
            text = data['heads'][0]['text']
        else:
            # Fallback to generated
            text = ''.join(random.choices("ETAOINSHRDLCUMWFGYPBVKJXQZ", k=75))
        
        print(f"Text: {text[:30]}...")
        results = self.compute_z_scores(text)
        
        # Check separation
        z_vals = [results[p]["z"] for p in ["fixed", "windowed_r2", "windowed_r3", "windowed_r4"]]
        all_equal = len(set(z_vals)) == 1
        
        print(f"\nExpectation: z-scores should differ across policies")
        print(f"Result: z_fixed={z_vals[0]:.3f}, z_r2={z_vals[1]:.3f}, z_r3={z_vals[2]:.3f}, z_r4={z_vals[3]:.3f}")
        print(f"All equal? {all_equal} (should be False)")
        
        return results
    
    def debug_25_heads(self):
        """Debug the 25 review heads."""
        print("\n" + "="*60)
        print("DEBUG: 25 Review Heads")
        print("="*60)
        
        # Load heads
        heads_file = Path(__file__).parent.parent.parent / "runs" / "track_a_scaled" / "blinded_heads_scaled_review.json"
        
        if not heads_file.exists():
            print(f"❌ Heads file not found: {heads_file}")
            return
        
        with open(heads_file, 'r') as f:
            data = json.load(f)
        
        heads = data['heads'][:5]  # First 5 for debug
        
        print(f"\nProcessing {len(heads)} heads...")
        print(f"{'Label':<20} {'S_pre':>7} {'S_post':>7} {'S_rep':>7} {'δ_win':>7} {'δ_shuf':>7} {'Pass?':>6}")
        print("-" * 80)
        
        results = []
        for head in heads:
            text = head['text']
            label = head['label']
            
            # Original score
            s_pre, _ = self.blinded_scorer.compute_blinded_score(text)
            
            # With fixed anchors
            text_fixed = self.apply_anchors(text, {"window_radius": 0})
            s_post, _ = self.blinded_scorer.compute_blinded_score(text_fixed)
            
            # After repair (simulate)
            s_rep = s_post  # Would be from repair
            
            # Compute z-scores and deltas
            z_results = self.compute_z_scores(text, debug=False)
            
            delta_win = z_results['deltas']['delta_windowed_best']
            delta_shuf = z_results['deltas']['delta_shuffled']
            candidate = z_results['deltas']['candidate']
            
            print(f"{label:<20} {s_pre:7.3f} {s_post:7.3f} {s_rep:7.3f} {delta_win:7.3f} {delta_shuf:7.3f} {'YES' if candidate else 'NO':>6}")
            
            results.append({
                'label': label,
                's_blind_pre': s_pre,
                's_blind_post': s_post,
                's_blind_repair': s_rep,
                'delta_windowed': delta_win,
                'delta_shuffled': delta_shuf,
                'candidate': candidate
            })
        
        return results


def main():
    """Run all diagnostics."""
    diag = DeltaDiagnostics(seed=1337)
    
    # Ensure calibration exists
    if not diag.calibration:
        print("⚠️ Generating calibration first...")
        diag.calibration = diag.generate_calibration()
    
    # Run sanity tests
    test1 = diag.sanity_test_1_reference()
    test2 = diag.sanity_test_2_worst()
    test3 = diag.sanity_test_3_policy_separation()
    
    # Debug real heads
    head_results = diag.debug_25_heads()
    
    # Save results
    output = {
        'sanity_tests': {
            'test1_reference': test1,
            'test2_worst': test2,
            'test3_separation': test3
        },
        'head_debug': head_results
    }
    
    output_file = Path(__file__).parent / "delta_diagnostics.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, default=lambda x: float(x) if isinstance(x, np.floating) else x)
    
    print(f"\n✅ Diagnostics saved to {output_file}")


if __name__ == "__main__":
    main()