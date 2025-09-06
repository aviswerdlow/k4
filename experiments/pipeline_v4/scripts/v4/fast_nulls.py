#!/usr/bin/env python3
"""
Run fast nulls (1k × 2 replicates) on orbit survivors.
"""

import json
import sys
import random
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from scipy import stats

# Add parent directories
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from experiments.pipeline_v4.scripts.v4.score_with_calibration_fixed import CalibratedScorerFixed


class FastNullsRunner:
    """Run fast null hypothesis testing on orbit survivors."""
    
    def __init__(self, seed: int = 1337):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        self.scorer = CalibratedScorerFixed(seed)
        self.output_dir = Path(__file__).parent.parent.parent / "runs" / "track_a_scaled"
        
    def load_orbit_survivors(self) -> List[Dict]:
        """Load orbit survivors from previous analysis."""
        # Load full results to get survivor details
        matrix_file = self.output_dir / "EXPLORE_MATRIX_FIXED.csv"
        orbit_file = self.output_dir / "orbit_analysis.json"
        
        with open(orbit_file, 'r') as f:
            orbit_data = json.load(f)
        
        survivor_labels = [s['label'] for s in orbit_data['survivors']]
        
        # Load the actual head texts
        heads_file = self.output_dir / "blinded_heads_fixed.json"
        with open(heads_file, 'r') as f:
            heads_data = json.load(f)
        
        survivors = []
        for head in heads_data['heads']:
            if head.get('label', '') in survivor_labels:
                survivors.append(head)
        
        print(f"Loaded {len(survivors)} orbit survivors")
        return survivors
    
    def generate_null(self, text: str, null_type: str = 'shuffle') -> str:
        """Generate a null hypothesis sample."""
        if null_type == 'shuffle':
            # Random shuffle of characters
            chars = list(text)
            random.shuffle(chars)
            return ''.join(chars)
        elif null_type == 'mirror':
            # Mirror/reverse the text
            return text[::-1]
        else:
            raise ValueError(f"Unknown null type: {null_type}")
    
    def run_null_test(self, head: Dict, n_nulls: int = 1000, replicate_id: int = 1) -> Dict:
        """Run null hypothesis test for a single head."""
        text = head['text']
        label = head.get('label', 'unknown')
        
        print(f"\n  Testing {label} (replicate {replicate_id})...")
        
        # Score the actual head
        actual_result = self.scorer.score_head(text, label)
        actual_delta_win = actual_result['delta_windowed_best']
        actual_delta_shuf = actual_result['delta_shuffled']
        
        # Generate and score nulls
        null_deltas_win = []
        null_deltas_shuf = []
        
        for i in range(n_nulls):
            # Generate mirrored null (per requirements)
            null_text = self.generate_null(text, 'mirror')
            
            # Score null
            null_result = self.scorer.score_head(null_text, f"NULL_{i}")
            null_deltas_win.append(null_result['delta_windowed_best'])
            null_deltas_shuf.append(null_result['delta_shuffled'])
            
            # Progress
            if (i + 1) % 200 == 0:
                print(f"    Processed {i+1}/{n_nulls} nulls...")
        
        # Compute p-values (one-tailed: actual > null)
        p_windowed = np.mean([d >= actual_delta_win for d in null_deltas_win])
        p_shuffled = np.mean([d >= actual_delta_shuf for d in null_deltas_shuf])
        
        # Statistics
        result = {
            'label': label,
            'replicate': replicate_id,
            'actual': {
                'delta_windowed': actual_delta_win,
                'delta_shuffled': actual_delta_shuf
            },
            'null_stats': {
                'windowed': {
                    'mean': np.mean(null_deltas_win),
                    'std': np.std(null_deltas_win),
                    'max': np.max(null_deltas_win),
                    'percentile_95': np.percentile(null_deltas_win, 95),
                    'percentile_99': np.percentile(null_deltas_win, 99)
                },
                'shuffled': {
                    'mean': np.mean(null_deltas_shuf),
                    'std': np.std(null_deltas_shuf),
                    'max': np.max(null_deltas_shuf),
                    'percentile_95': np.percentile(null_deltas_shuf, 95),
                    'percentile_99': np.percentile(null_deltas_shuf, 99)
                }
            },
            'p_values': {
                'windowed': p_windowed,
                'shuffled': p_shuffled,
                'combined': max(p_windowed, p_shuffled)  # Conservative
            },
            'z_scores': {
                'windowed': (actual_delta_win - np.mean(null_deltas_win)) / max(0.001, np.std(null_deltas_win)),
                'shuffled': (actual_delta_shuf - np.mean(null_deltas_shuf)) / max(0.001, np.std(null_deltas_shuf))
            }
        }
        
        return result
    
    def apply_holm_correction(self, results: List[Dict], alpha: float = 0.01) -> List[Dict]:
        """Apply Holm-Bonferroni correction for multiple testing."""
        print("\n" + "=" * 60)
        print("APPLYING HOLM CORRECTION")
        print("=" * 60)
        
        # Aggregate p-values across replicates
        by_label = {}
        for result in results:
            label = result['label']
            if label not in by_label:
                by_label[label] = []
            by_label[label].append(result)
        
        final_results = []
        
        for label, replicates in by_label.items():
            # Take maximum p-value across replicates (conservative)
            p_windowed = max(r['p_values']['windowed'] for r in replicates)
            p_shuffled = max(r['p_values']['shuffled'] for r in replicates)
            p_combined = max(p_windowed, p_shuffled)
            
            final_results.append({
                'label': label,
                'p_windowed': p_windowed,
                'p_shuffled': p_shuffled,
                'p_combined': p_combined,
                'replicates': replicates
            })
        
        # Sort by p-value for Holm correction
        final_results.sort(key=lambda x: x['p_combined'])
        
        # Apply Holm correction
        m = len(final_results)
        for i, result in enumerate(final_results):
            # Holm threshold for position i
            holm_threshold = alpha / (m - i)
            result['holm_threshold'] = holm_threshold
            result['holm_reject'] = result['p_combined'] < holm_threshold
            
            # Once we fail to reject, all subsequent fail too
            if not result['holm_reject']:
                for j in range(i, m):
                    final_results[j]['holm_threshold'] = alpha / (m - j)  # Ensure all have threshold
                    final_results[j]['holm_reject'] = False
                break
        
        # Summary
        n_significant = sum(r['holm_reject'] for r in final_results)
        print(f"Holm correction with m={m}, α={alpha}")
        print(f"Significant after correction: {n_significant}/{m}")
        
        return final_results
    
    def run_fast_nulls(self, survivors: List[Dict]) -> Dict:
        """Run complete fast nulls analysis."""
        print("=" * 60)
        print("FAST NULLS ANALYSIS")
        print("=" * 60)
        print(f"Testing {len(survivors)} orbit survivors")
        print(f"Configuration: 1000 nulls × 2 replicates")
        
        all_results = []
        
        # Run 2 replicates for each survivor
        for replicate in range(1, 3):
            print(f"\n--- Replicate {replicate} ---")
            
            for head in survivors:
                result = self.run_null_test(head, n_nulls=1000, replicate_id=replicate)
                all_results.append(result)
        
        # Apply Holm correction
        final_results = self.apply_holm_correction(all_results, alpha=0.01)
        
        # Identify survivors
        survivors_after_nulls = [r for r in final_results if r['holm_reject']]
        
        # Save results (convert numpy types for JSON serialization)
        nulls_output = {
            'n_tested': len(survivors),
            'n_replicates': 2,
            'n_nulls_per_test': 1000,
            'alpha': 0.01,
            'correction': 'Holm-Bonferroni',
            'results': [
                {
                    'label': r['label'],
                    'p_windowed': float(r['p_windowed']),
                    'p_shuffled': float(r['p_shuffled']),
                    'p_combined': float(r['p_combined']),
                    'holm_threshold': float(r['holm_threshold']),
                    'holm_reject': bool(r['holm_reject'])
                }
                for r in final_results
            ],
            'survivors': [s['label'] for s in survivors_after_nulls]
        }
        
        nulls_file = self.output_dir / "fast_nulls_results.json"
        with open(nulls_file, 'w') as f:
            json.dump(nulls_output, f, indent=2)
        
        print(f"\nSaved null results to {nulls_file}")
        
        return nulls_output
    
    def generate_summary(self, nulls_results: Dict):
        """Generate summary and decision."""
        print("\n" + "=" * 60)
        print("FAST NULLS SUMMARY")
        print("=" * 60)
        
        n_tested = nulls_results['n_tested']
        n_survivors = len(nulls_results['survivors'])
        
        print(f"Tested: {n_tested} heads")
        print(f"Survivors after Holm correction: {n_survivors}")
        
        if n_survivors > 0:
            print(f"\n✅ SURVIVORS FOUND:")
            for label in nulls_results['survivors']:
                # Find p-values
                for r in nulls_results['results']:
                    if r['label'] == label:
                        print(f"  - {label}: p_combined={r['p_combined']:.4f}")
                        break
            
            print("\n🎯 DECISION: Proceed to Confirm queue")
            print("At least one head survived orbit + fast nulls")
        else:
            print("\n⚠️ NO SURVIVORS")
            print("All heads failed null hypothesis testing")
            print("\n📊 DECISION: Consider scaling to K=200")
        
        return n_survivors > 0


def main():
    """Run fast nulls analysis."""
    runner = FastNullsRunner(seed=1337)
    
    # Load orbit survivors
    survivors = runner.load_orbit_survivors()
    
    if not survivors:
        print("No orbit survivors to test")
        return
    
    # Run fast nulls
    nulls_results = runner.run_fast_nulls(survivors)
    
    # Generate summary
    proceed = runner.generate_summary(nulls_results)
    
    if proceed:
        print("\nNext steps:")
        print("1. Generate mini-bundles for survivors")
        print("2. Submit to Confirm queue")
    else:
        print("\nNext steps:")
        print("1. Review results")
        print("2. Decide whether to scale to K=200")


if __name__ == "__main__":
    main()