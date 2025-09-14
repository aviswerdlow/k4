#!/usr/bin/env python3
"""
Key Scramble Null Control - Test against random key baselines
"""

import json
import random
import string
import argparse
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
import sys


class KeyScrambleNull:
    """Test solutions against scrambled key null hypothesis"""
    
    def __init__(self, manifest_path: str):
        """Load manifest and setup"""
        with open(manifest_path, 'r') as f:
            self.manifest = json.load(f)
        
        # Import zone runner
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / '03_SOLVERS'))
        from zone_mask_v1.scripts.zone_runner import ZoneRunner
        self.ZoneRunner = ZoneRunner
        
        # Load original ciphertext
        ct_path = Path(__file__).parent.parent.parent / '02_DATA' / 'ciphertext_97.txt'
        with open(ct_path, 'r') as f:
            self.ciphertext = f.read().strip().upper()
    
    def generate_random_key(self, length: int) -> str:
        """Generate a random key of specified length"""
        return ''.join(random.choices(string.ascii_uppercase, k=length))
    
    def scramble_manifest_keys(self) -> Dict[str, Any]:
        """Create manifest with scrambled keys"""
        scrambled = json.loads(json.dumps(self.manifest))
        
        if 'cipher' in scrambled and 'keys' in scrambled['cipher']:
            original_keys = scrambled['cipher']['keys']
            
            # Generate random keys of same length
            for zone, key in original_keys.items():
                scrambled['cipher']['keys'][zone] = self.generate_random_key(len(key))
        
        return scrambled
    
    def score_plaintext(self, text: str) -> float:
        """Score plaintext for English-like properties"""
        if not text:
            return -1000
        
        text = text.upper()
        
        # English letter frequencies
        english_freq = {
            'E': 12.7, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0,
            'N': 6.7, 'S': 6.3, 'H': 6.1, 'R': 6.0, 'L': 4.0,
            'D': 4.3, 'C': 2.8, 'U': 2.8, 'M': 2.4, 'W': 2.4,
            'F': 2.2, 'G': 2.0, 'Y': 2.0, 'P': 1.9, 'B': 1.5,
            'V': 1.0, 'K': 0.8, 'J': 0.15, 'X': 0.15, 'Q': 0.10, 'Z': 0.07
        }
        
        # Calculate chi-squared statistic
        chi_squared = 0
        for letter, expected_freq in english_freq.items():
            observed_count = text.count(letter)
            expected_count = (expected_freq / 100) * len(text)
            if expected_count > 0:
                chi_squared += ((observed_count - expected_count) ** 2) / expected_count
        
        # Lower chi-squared is better (closer to English)
        # Convert to a score where higher is better
        score = 1000 - chi_squared
        
        # Bonus for BERLINCLOCK
        if 'BERLINCLOCK' in text.replace(' ', ''):
            score += 500
        
        return score
    
    def run_null_test(self, iterations: int = 100) -> Dict[str, Any]:
        """Run null hypothesis test with scrambled keys"""
        # First, test the original manifest
        runner = self.ZoneRunner()
        runner.manifest = self.manifest
        runner.ciphertext = self.ciphertext
        
        try:
            original_plaintext = runner.decrypt()
            original_score = self.score_plaintext(original_plaintext)
        except:
            original_score = -1000
            original_plaintext = None
        
        # Run null tests with scrambled keys
        null_scores = []
        
        for i in range(iterations):
            if i % 10 == 0:
                print(f"  Iteration {i}/{iterations}...")
            
            scrambled = self.scramble_manifest_keys()
            runner = self.ZoneRunner()
            runner.manifest = scrambled
            runner.ciphertext = self.ciphertext
            
            try:
                plaintext = runner.decrypt()
                score = self.score_plaintext(plaintext)
                null_scores.append(score)
            except:
                null_scores.append(-1000)
        
        # Calculate statistics
        null_scores = np.array(null_scores)
        mean_null = np.mean(null_scores)
        std_null = np.std(null_scores)
        
        # Calculate p-value (how many null scores beat the original)
        better_nulls = np.sum(null_scores >= original_score)
        p_value = better_nulls / iterations
        
        # Z-score
        z_score = (original_score - mean_null) / std_null if std_null > 0 else 0
        
        return {
            'original_score': original_score,
            'null_mean': mean_null,
            'null_std': std_null,
            'null_max': np.max(null_scores),
            'null_min': np.min(null_scores),
            'p_value': p_value,
            'z_score': z_score,
            'iterations': iterations,
            'better_nulls': int(better_nulls),
            'original_plaintext_preview': original_plaintext[:50] if original_plaintext else None
        }


def main():
    parser = argparse.ArgumentParser(description='Key Scramble Null Control Test')
    parser.add_argument('--manifest', required=True, help='Path to manifest')
    parser.add_argument('--iterations', type=int, default=100, help='Number of null iterations')
    parser.add_argument('--output', help='Output file for results')
    
    args = parser.parse_args()
    
    print("Key Scramble Null Control Test")
    print("=" * 60)
    
    # Run null test
    tester = KeyScrambleNull(args.manifest)
    print(f"Running {args.iterations} iterations with scrambled keys...")
    
    results = tester.run_null_test(args.iterations)
    
    # Display results
    print("\nResults:")
    print(f"Original score: {results['original_score']:.2f}")
    print(f"Null mean: {results['null_mean']:.2f} ± {results['null_std']:.2f}")
    print(f"Null range: [{results['null_min']:.2f}, {results['null_max']:.2f}]")
    print(f"Z-score: {results['z_score']:.2f}")
    print(f"P-value: {results['p_value']:.4f}")
    
    # Interpretation
    print("\nInterpretation:")
    if results['p_value'] < 0.01:
        print("✓ PASS: Solution significantly beats random keys (p < 0.01)")
    elif results['p_value'] < 0.05:
        print("⚠ MARGINAL: Solution beats random keys (p < 0.05)")
    else:
        print("✗ FAIL: Solution does not significantly beat random keys")
    
    if results['z_score'] > 3:
        print(f"✓ Strong effect: Z-score = {results['z_score']:.2f} (>3 standard deviations)")
    elif results['z_score'] > 2:
        print(f"⚠ Moderate effect: Z-score = {results['z_score']:.2f}")
    else:
        print(f"✗ Weak effect: Z-score = {results['z_score']:.2f}")
    
    # Save results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    # Return exit code based on test
    sys.exit(0 if results['p_value'] < 0.01 else 1)


if __name__ == '__main__':
    main()