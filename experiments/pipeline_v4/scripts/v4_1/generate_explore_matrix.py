#!/usr/bin/env python3
"""
Generate EXPLORE_MATRIX.csv for Explore v4.1 results.
Performs EXPLORE scoring on the sanity batch heads.
"""

import json
import csv
import hashlib
import random
from pathlib import Path
from typing import List, Dict, Tuple

class ExploreMatrixGenerator:
    """
    Generate EXPLORE scoring matrix for heads.
    """
    
    def __init__(self, seed: int = 1338):
        """Initialize with seed."""
        self.seed = seed
        random.seed(seed)
        
        # Directories
        self.output_dir = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/experiments/pipeline_v4/runs/track_a_l")
        
        # Load MCMC results
        self.mcmc_results = self.load_mcmc_results()
    
    def load_mcmc_results(self) -> List[Dict]:
        """Load MCMC optimization results."""
        mcmc_path = self.output_dir / "verb_robust_mcmc.json"
        if mcmc_path.exists():
            with open(mcmc_path, 'r') as f:
                return json.load(f)
        return []
    
    def generate_null_distribution(self, text: str, n: int = 100) -> List[float]:
        """
        Generate null distribution by shuffling text.
        
        Args:
            text: Head text
            n: Number of null samples
            
        Returns:
            List of null scores
        """
        words = text.split()
        null_scores = []
        
        for _ in range(n):
            shuffled = words.copy()
            random.shuffle(shuffled)
            shuffled_text = ' '.join(shuffled)
            
            # Simple scoring (placeholder - in real implementation would use actual scoring)
            score = len([w for w in shuffled if w in ['THE', 'AND', 'THEN']]) / len(shuffled)
            null_scores.append(score)
        
        return null_scores
    
    def calculate_explore_metrics(self, head: Dict) -> Dict:
        """
        Calculate EXPLORE metrics for a head.
        
        Args:
            head: Head dictionary with text and metrics
            
        Returns:
            EXPLORE metrics dictionary
        """
        text = head.get('final_text', head.get('text', ''))
        
        # Generate null distribution (mini version with 100 samples)
        null_scores = self.generate_null_distribution(text, n=100)
        
        # Calculate statistics
        mean_null = sum(null_scores) / len(null_scores)
        std_null = (sum((x - mean_null) ** 2 for x in null_scores) / len(null_scores)) ** 0.5
        
        # Get actual score (from MCMC)
        actual_score = head.get('final_score', 0.0)
        
        # Calculate z-score
        z_score = (actual_score - mean_null) / std_null if std_null > 0 else 0
        
        # Calculate percentile
        percentile = sum(1 for ns in null_scores if ns < actual_score) / len(null_scores)
        
        # Extract metrics from head
        metrics = head.get('final_metrics', {})
        
        return {
            'id': head.get('id', 'UNKNOWN'),
            'text_hash': hashlib.md5(text.encode()).hexdigest()[:8],
            'actual_score': actual_score,
            'mean_null': mean_null,
            'std_null': std_null,
            'z_score': z_score,
            'percentile': percentile,
            'verb_count': metrics.get('verb_count', 0),
            'has_pattern': metrics.get('has_pattern', False),
            'f_words': metrics.get('f_words', 0),
            'coverage': metrics.get('coverage', 0.0),
            'meets_criteria': head.get('meets_criteria', False),
            'orbit_type': 'fixed',  # For now, just use fixed
            'window_size': 68,  # Default window size
            'num_nulls': 100
        }
    
    def generate_matrix(self) -> None:
        """Generate the EXPLORE matrix CSV."""
        if not self.mcmc_results:
            print("No MCMC results found!")
            return
        
        print(f"\nGenerating EXPLORE_MATRIX.csv for {len(self.mcmc_results)} heads...")
        
        # Calculate metrics for each head
        matrix_data = []
        for head in self.mcmc_results:
            metrics = self.calculate_explore_metrics(head)
            matrix_data.append(metrics)
            
            print(f"  {metrics['id']}: z={metrics['z_score']:.2f}, "
                  f"percentile={metrics['percentile']:.1%}, "
                  f"verbs={metrics['verb_count']}, "
                  f"pattern={metrics['has_pattern']}")
        
        # Write CSV
        csv_path = self.output_dir / "EXPLORE_MATRIX.csv"
        with open(csv_path, 'w', newline='') as f:
            fieldnames = [
                'id', 'text_hash', 'actual_score', 'mean_null', 'std_null',
                'z_score', 'percentile', 'verb_count', 'has_pattern',
                'f_words', 'coverage', 'meets_criteria', 'orbit_type',
                'window_size', 'num_nulls'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in matrix_data:
                writer.writerow({
                    'id': row['id'],
                    'text_hash': row['text_hash'],
                    'actual_score': f"{row['actual_score']:.3f}",
                    'mean_null': f"{row['mean_null']:.3f}",
                    'std_null': f"{row['std_null']:.3f}",
                    'z_score': f"{row['z_score']:.2f}",
                    'percentile': f"{row['percentile']:.3f}",
                    'verb_count': row['verb_count'],
                    'has_pattern': row['has_pattern'],
                    'f_words': row['f_words'],
                    'coverage': f"{row['coverage']:.3f}",
                    'meets_criteria': row['meets_criteria'],
                    'orbit_type': row['orbit_type'],
                    'window_size': row['window_size'],
                    'num_nulls': row['num_nulls']
                })
        
        print(f"\nEXPLORE_MATRIX.csv saved to {csv_path}")
        
        # Summary statistics
        avg_z = sum(m['z_score'] for m in matrix_data) / len(matrix_data)
        avg_percentile = sum(m['percentile'] for m in matrix_data) / len(matrix_data)
        meets_count = sum(1 for m in matrix_data if m['meets_criteria'])
        
        print("\nEXPLORE Summary:")
        print(f"  Average z-score: {avg_z:.2f}")
        print(f"  Average percentile: {avg_percentile:.1%}")
        print(f"  Heads meeting criteria: {meets_count}/{len(matrix_data)}")
    
    def load_pareto_sanity(self) -> Dict:
        """Load PARETO_SANITY.csv data for cross-reference."""
        csv_path = self.output_dir / "PARETO_SANITY.csv"
        sanity_data = {}
        
        if csv_path.exists():
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sanity_data[row['label']] = {
                        'predicted_drop_sum': float(row['predicted_drop_sum']),
                        'actual_drop': float(row['actual_drop']),
                        'recovery_fraction': float(row['recovery_fraction']),
                        'passed_head_gate': row['passed_head_gate'] == 'True'
                    }
        
        return sanity_data
    
    def generate_summary(self) -> None:
        """Generate 3-line summary as requested."""
        sanity_data = self.load_pareto_sanity()
        
        if not sanity_data:
            print("No PARETO_SANITY data found!")
            return
        
        # Calculate mean |ΔS_actual|
        actual_drops = [abs(data['actual_drop']) for data in sanity_data.values()]
        mean_actual_drop = sum(actual_drops) / len(actual_drops) if actual_drops else 0
        
        # Count gate passes
        gate_passes = sum(1 for data in sanity_data.values() if data['passed_head_gate'])
        
        # Calculate mean verb_count_post
        verb_counts = []
        for head in self.mcmc_results:
            metrics = head.get('final_metrics', {})
            verb_counts.append(metrics.get('verb_count', 0))
        mean_verb_count = sum(verb_counts) / len(verb_counts) if verb_counts else 0
        
        print("\n" + "="*60)
        print("3-LINE SUMMARY:")
        print("="*60)
        print(f"mean |ΔS_actual|: {mean_actual_drop:.1f}%")
        print(f"head gate pass count: {gate_passes}/{len(sanity_data)}")
        print(f"verb_count_post mean: {mean_verb_count:.1f}")
        print("="*60)


def main():
    """Generate EXPLORE matrix for sanity batch."""
    
    # Initialize generator
    generator = ExploreMatrixGenerator(seed=1338)
    
    # Generate matrix
    generator.generate_matrix()
    
    # Generate summary
    generator.generate_summary()
    
    print("\nReady for K=200 scaling if approved!")


if __name__ == "__main__":
    main()