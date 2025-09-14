#!/usr/bin/env python3
"""
Segment Shuffle Null Control - Test against shuffled segment baselines
"""

import json
import random
import argparse
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
import sys


class SegmentShuffleNull:
    """Test solutions against shuffled segment null hypothesis"""
    
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
    
    def shuffle_segments(self, text: str, segment_size: int = 10) -> str:
        """Shuffle text in segments"""
        segments = []
        
        # Split into segments
        for i in range(0, len(text), segment_size):
            segments.append(text[i:i+segment_size])
        
        # Shuffle segments
        shuffled_segments = segments.copy()
        random.shuffle(shuffled_segments)
        
        return ''.join(shuffled_segments)
    
    def score_plaintext(self, text: str) -> float:
        """Score plaintext for English-like properties"""
        if not text:
            return -1000
        
        text = text.upper()
        
        # Bigram frequencies (common English bigrams)
        common_bigrams = [
            'TH', 'HE', 'IN', 'ER', 'AN', 'ED', 'ND', 'TO', 'EN', 'ES',
            'ST', 'RE', 'NT', 'ON', 'AT', 'OU', 'IT', 'TE', 'ET', 'NG',
            'AR', 'AL', 'OR', 'AS', 'IS', 'HA', 'ET', 'SE', 'EA', 'LE'
        ]
        
        # Count bigrams
        bigram_score = 0
        for bigram in common_bigrams:
            bigram_score += text.count(bigram) * 10
        
        # Trigram frequencies
        common_trigrams = [
            'THE', 'AND', 'ING', 'HER', 'HAT', 'HIS', 'THA', 'ERE', 'FOR', 'ENT',
            'ION', 'TER', 'WAS', 'YOU', 'ITH', 'VER', 'ALL', 'WIT', 'THI', 'TIO'
        ]
        
        trigram_score = 0
        for trigram in common_trigrams:
            trigram_score += text.count(trigram) * 20
        
        # Letter frequency score
        english_freq = {
            'E': 12.7, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0,
            'N': 6.7, 'S': 6.3, 'H': 6.1, 'R': 6.0, 'L': 4.0
        }
        
        freq_score = 0
        for letter, expected_freq in english_freq.items():
            actual_freq = (text.count(letter) / len(text)) * 100
            freq_score -= abs(actual_freq - expected_freq)
        
        # Combined score
        total_score = bigram_score + trigram_score + freq_score * 10
        
        # Bonus for BERLINCLOCK
        if 'BERLINCLOCK' in text.replace(' ', ''):
            total_score += 1000
        
        return total_score
    
    def run_null_test(self, iterations: int = 100, segment_sizes: List[int] = None) -> Dict[str, Any]:
        """Run null hypothesis test with shuffled segments"""
        if segment_sizes is None:
            segment_sizes = [5, 10, 15]
        
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
        
        # Run null tests for each segment size
        results_by_segment = {}
        
        for segment_size in segment_sizes:
            print(f"\nTesting segment size {segment_size}...")
            null_scores = []
            
            for i in range(iterations):
                if i % 10 == 0:
                    print(f"  Iteration {i}/{iterations}...")
                
                # Shuffle ciphertext segments
                shuffled_ct = self.shuffle_segments(self.ciphertext, segment_size)
                
                # Try to decrypt shuffled ciphertext
                runner = self.ZoneRunner()
                runner.manifest = self.manifest
                runner.ciphertext = shuffled_ct
                
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
            
            # Calculate p-value
            better_nulls = np.sum(null_scores >= original_score)
            p_value = better_nulls / iterations
            
            # Z-score
            z_score = (original_score - mean_null) / std_null if std_null > 0 else 0
            
            results_by_segment[segment_size] = {
                'null_mean': mean_null,
                'null_std': std_null,
                'null_max': np.max(null_scores),
                'null_min': np.min(null_scores),
                'p_value': p_value,
                'z_score': z_score,
                'better_nulls': int(better_nulls)
            }
        
        # Find best segment size (highest z-score)
        best_segment = max(results_by_segment.keys(), 
                          key=lambda k: results_by_segment[k]['z_score'])
        
        return {
            'original_score': original_score,
            'iterations': iterations,
            'segment_results': results_by_segment,
            'best_segment_size': best_segment,
            'best_p_value': results_by_segment[best_segment]['p_value'],
            'best_z_score': results_by_segment[best_segment]['z_score'],
            'original_plaintext_preview': original_plaintext[:50] if original_plaintext else None
        }


def holm_correction(p_values: List[float], alpha: float = 0.05) -> Dict[str, Any]:
    """Apply Holm-Bonferroni correction for multiple comparisons"""
    n = len(p_values)
    
    # Sort p-values and keep track of original indices
    sorted_pairs = sorted(enumerate(p_values), key=lambda x: x[1])
    
    # Apply Holm correction
    corrected = []
    for i, (orig_idx, p_val) in enumerate(sorted_pairs):
        adjusted_alpha = alpha / (n - i)
        reject = p_val < adjusted_alpha
        corrected.append({
            'original_index': orig_idx,
            'p_value': p_val,
            'adjusted_alpha': adjusted_alpha,
            'reject_null': reject
        })
        
        # If we fail to reject, stop (Holm's step-down procedure)
        if not reject:
            break
    
    return {
        'corrected_results': corrected,
        'any_significant': any(c['reject_null'] for c in corrected),
        'num_significant': sum(c['reject_null'] for c in corrected)
    }


def main():
    parser = argparse.ArgumentParser(description='Segment Shuffle Null Control Test')
    parser.add_argument('--manifest', required=True, help='Path to manifest')
    parser.add_argument('--iterations', type=int, default=100, help='Number of null iterations')
    parser.add_argument('--segments', help='Comma-separated segment sizes (default: 5,10,15)')
    parser.add_argument('--output', help='Output file for results')
    
    args = parser.parse_args()
    
    print("Segment Shuffle Null Control Test")
    print("=" * 60)
    
    # Parse segment sizes
    if args.segments:
        segment_sizes = [int(s) for s in args.segments.split(',')]
    else:
        segment_sizes = [5, 10, 15]
    
    # Run null test
    tester = SegmentShuffleNull(args.manifest)
    print(f"Running {args.iterations} iterations with segment sizes: {segment_sizes}")
    
    results = tester.run_null_test(args.iterations, segment_sizes)
    
    # Display results
    print("\nResults:")
    print(f"Original score: {results['original_score']:.2f}")
    
    for seg_size, seg_results in results['segment_results'].items():
        print(f"\nSegment size {seg_size}:")
        print(f"  Null mean: {seg_results['null_mean']:.2f} ± {seg_results['null_std']:.2f}")
        print(f"  Z-score: {seg_results['z_score']:.2f}")
        print(f"  P-value: {seg_results['p_value']:.4f}")
    
    # Apply Holm correction
    p_values = [r['p_value'] for r in results['segment_results'].values()]
    holm_results = holm_correction(p_values)
    
    print("\nHolm-Bonferroni Correction:")
    if holm_results['any_significant']:
        print(f"✓ PASS: {holm_results['num_significant']} tests significant after correction")
    else:
        print("✗ FAIL: No tests significant after multiple comparison correction")
    
    # Best result
    print(f"\nBest result (segment size {results['best_segment_size']}):")
    print(f"  Z-score: {results['best_z_score']:.2f}")
    print(f"  P-value: {results['best_p_value']:.4f}")
    
    # Interpretation
    print("\nInterpretation:")
    if results['best_p_value'] < 0.01 and holm_results['any_significant']:
        print("✓ PASS: Solution significantly beats shuffled segments")
    elif results['best_p_value'] < 0.05:
        print("⚠ MARGINAL: Solution marginally beats shuffled segments")
    else:
        print("✗ FAIL: Solution does not significantly beat shuffled segments")
    
    # Save results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    # Return exit code based on test
    sys.exit(0 if results['best_p_value'] < 0.01 and holm_results['any_significant'] else 1)


if __name__ == '__main__':
    main()