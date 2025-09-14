#!/usr/bin/env python3
"""
Rigorous Geometric Hypothesis Tests for Kryptos K4
Implements scale-invariant tests H1-H7 with empirical p-values
"""

import json
import numpy as np
from typing import List, Dict, Tuple, Optional
import string
from collections import Counter
import random
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import warnings
warnings.filterwarnings('ignore')

# K4 text (97 chars)
K4_TEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

class RigorousGeometricTests:
    """Scale-invariant geometric tests with empirical p-values"""
    
    def __init__(self, positions_file: str = "sample_k4_positions.json"):
        """Initialize with 3D positions"""
        with open(positions_file, 'r') as f:
            self.positions = json.load(f)
        
        # Extract coordinates and normalize
        self.coords = np.array([[p['x'], p['y'], p['z']] for p in self.positions])
        self.letters = [p['char'] for p in self.positions]
        
        # Normalize to unit sphere for scale invariance
        self.center = np.mean(self.coords, axis=0)
        self.centered_coords = self.coords - self.center
        self.radii = np.linalg.norm(self.centered_coords, axis=1)
        self.max_radius = np.max(self.radii)
        self.normalized_coords = self.centered_coords / self.max_radius
        
        # Compute arc-lengths (scale-invariant)
        self.arc_lengths = self._compute_arc_lengths()
        
    def _compute_arc_lengths(self) -> np.ndarray:
        """Compute cumulative arc-length along the sculpture"""
        arc_lengths = [0]
        for i in range(1, len(self.coords)):
            dist = np.linalg.norm(self.coords[i] - self.coords[i-1])
            arc_lengths.append(arc_lengths[-1] + dist)
        arc_lengths = np.array(arc_lengths)
        # Normalize to [0, 1]
        return arc_lengths / arc_lengths[-1]
    
    def _compute_empirical_p(self, test_stat: float, null_stats: List[float], 
                            alternative: str = 'two-sided') -> float:
        """Compute empirical p-value with proper method"""
        null_stats = np.array(null_stats)
        n = len(null_stats)
        
        if alternative == 'greater':
            p = np.sum(null_stats >= test_stat) / n
        elif alternative == 'less':
            p = np.sum(null_stats <= test_stat) / n
        else:  # two-sided
            p = np.sum(np.abs(null_stats) >= np.abs(test_stat)) / n
        
        # Add 1 to numerator and denominator for conservative estimate
        p = (np.sum(null_stats >= test_stat) + 1) / (n + 1)
        return p
    
    def _english_score(self, text: str) -> float:
        """Score text for English-like properties"""
        text = text.upper()
        
        # Common English bigrams
        common_bigrams = ['TH', 'HE', 'IN', 'ER', 'AN', 'ED', 'ND', 'TO', 'EN', 'ES',
                         'OF', 'TE', 'AT', 'ON', 'AR', 'OR', 'IT', 'HA', 'ET', 'NG']
        
        # Common English trigrams
        common_trigrams = ['THE', 'AND', 'ING', 'ION', 'TIO', 'ENT', 'ATI', 'FOR',
                          'HER', 'TER', 'HAT', 'THA', 'ERE', 'ATE', 'HIS', 'CON']
        
        score = 0.0
        
        # Check for common words (3+ letters)
        common_words = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'WITH',
                       'HAVE', 'THIS', 'FROM', 'THAT', 'WHAT', 'WHEN', 'WHO']
        for word in common_words:
            if word in text:
                score += len(word)
        
        # Bigram frequency
        for i in range(len(text) - 1):
            if text[i:i+2] in common_bigrams:
                score += 1
        
        # Trigram frequency
        for i in range(len(text) - 2):
            if text[i:i+3] in common_trigrams:
                score += 2
        
        # Normalize by length
        return score / max(len(text), 1)
    
    def test_h1_arc_length_modulo(self, k_values: List[int] = None, 
                                  num_permutations: int = 10000) -> Dict:
        """
        H1: Arc-length modulo test
        Letters at positions s where (s mod 1/k) < threshold
        """
        if k_values is None:
            k_values = list(range(5, 12)) + [24, 28]
        
        results = {}
        
        for k in k_values:
            # Select letters where arc-length mod (1/k) is small
            threshold = 0.1 / k  # Scale threshold with k
            selected_indices = []
            
            for i, arc_len in enumerate(self.arc_lengths):
                remainder = (arc_len * k) % 1
                if remainder < threshold or remainder > (1 - threshold):
                    selected_indices.append(i)
            
            if len(selected_indices) < 10:  # Need minimum letters
                continue
                
            # Extract selected letters
            selected_text = ''.join([self.letters[i] for i in selected_indices])
            
            # Compute test statistic
            test_stat = self._english_score(selected_text)
            
            # Generate null distribution
            null_stats = []
            for _ in range(num_permutations):
                random_indices = random.sample(range(len(self.letters)), 
                                              len(selected_indices))
                random_text = ''.join([self.letters[i] for i in random_indices])
                null_stats.append(self._english_score(random_text))
            
            # Compute p-value
            p_value = self._compute_empirical_p(test_stat, null_stats, 'greater')
            
            results[f'k={k}'] = {
                'selected_text': selected_text,
                'test_statistic': test_stat,
                'p_value': p_value,
                'num_letters': len(selected_indices),
                'indices': selected_indices
            }
        
        return results
    
    def test_h2_ring_sectors(self, num_sectors: int = 24, step: int = 4,
                            num_permutations: int = 10000) -> Dict:
        """
        H2: Ring-24 sectors test
        Divide cylindrical projection into sectors, extract with step
        """
        # Project to cylinder (use x-z plane, ignore y for now)
        angles = np.arctan2(self.centered_coords[:, 2], self.centered_coords[:, 0])
        angles = (angles + np.pi) / (2 * np.pi)  # Normalize to [0, 1]
        
        # Divide into sectors
        sector_assignments = (angles * num_sectors).astype(int) % num_sectors
        
        # Extract letters with step
        selected_indices = []
        for start in range(step):
            indices = [i for i in range(start, len(self.letters), step)
                      if sector_assignments[i] % step == 0]
            selected_indices.extend(indices)
        
        selected_indices = sorted(set(selected_indices))
        selected_text = ''.join([self.letters[i] for i in selected_indices])
        
        # Compute test statistic
        test_stat = self._english_score(selected_text)
        
        # Generate null distribution
        null_stats = []
        for _ in range(num_permutations):
            random_indices = random.sample(range(len(self.letters)), 
                                          len(selected_indices))
            random_text = ''.join([self.letters[i] for i in random_indices])
            null_stats.append(self._english_score(random_text))
        
        # Compute p-value
        p_value = self._compute_empirical_p(test_stat, null_stats, 'greater')
        
        return {
            'selected_text': selected_text,
            'test_statistic': test_stat,
            'p_value': p_value,
            'num_letters': len(selected_indices),
            'indices': selected_indices,
            'sectors_used': len(set(sector_assignments[selected_indices]))
        }
    
    def test_h3_ne_gradient(self, k_values: List[int] = None,
                           num_permutations: int = 10000) -> Dict:
        """
        H3: NE gradient test
        Select every k-th letter along NE gradient direction
        """
        if k_values is None:
            k_values = [7, 8, 9]
        
        # Define NE direction (45 degrees from north in x-z plane)
        ne_direction = np.array([np.sqrt(2)/2, 0, np.sqrt(2)/2])
        
        # Project positions onto NE direction
        projections = np.dot(self.centered_coords, ne_direction)
        
        # Sort by projection
        sorted_indices = np.argsort(projections)
        
        results = {}
        
        for k in k_values:
            # Select every k-th letter
            selected_indices = sorted_indices[::k]
            selected_text = ''.join([self.letters[i] for i in selected_indices])
            
            # Compute test statistic
            test_stat = self._english_score(selected_text)
            
            # Generate null distribution
            null_stats = []
            for _ in range(num_permutations):
                random_indices = random.sample(range(len(self.letters)), 
                                              len(selected_indices))
                random_text = ''.join([self.letters[i] for i in random_indices])
                null_stats.append(self._english_score(random_text))
            
            # Compute p-value
            p_value = self._compute_empirical_p(test_stat, null_stats, 'greater')
            
            results[f'k={k}'] = {
                'selected_text': selected_text,
                'test_statistic': test_stat,
                'p_value': p_value,
                'num_letters': len(selected_indices),
                'indices': selected_indices.tolist()
            }
        
        return results
    
    def test_h6_anchor_walk(self, offsets: List[int] = None,
                           num_permutations: int = 10000) -> Dict:
        """
        H6: Anchor-walk peel test
        Start from anchor positions, walk with offsets
        """
        if offsets is None:
            offsets = [-2, -1, 1, 2]
        
        # Find anchor positions (OBKR at start)
        anchor_indices = [0, 1, 2, 3]  # O, B, K, R
        
        results = {}
        
        for offset in offsets:
            selected_indices = []
            current = anchor_indices[0]
            
            # Walk through with offset
            while 0 <= current < len(self.letters):
                selected_indices.append(current)
                current += abs(offset) + len(anchor_indices)
            
            if len(selected_indices) < 5:
                continue
            
            selected_text = ''.join([self.letters[i] for i in selected_indices])
            
            # Compute test statistic
            test_stat = self._english_score(selected_text)
            
            # Generate null distribution
            null_stats = []
            for _ in range(num_permutations):
                random_indices = random.sample(range(len(self.letters)), 
                                              len(selected_indices))
                random_text = ''.join([self.letters[i] for i in random_indices])
                null_stats.append(self._english_score(random_text))
            
            # Compute p-value
            p_value = self._compute_empirical_p(test_stat, null_stats, 'greater')
            
            results[f'offset={offset:+d}'] = {
                'selected_text': selected_text,
                'test_statistic': test_stat,
                'p_value': p_value,
                'num_letters': len(selected_indices),
                'indices': selected_indices
            }
        
        return results
    
    def run_priority_tests(self) -> Dict:
        """Run priority tests as specified"""
        print("Running rigorous geometric hypothesis tests...")
        print("=" * 80)
        
        all_results = {
            'H1_arc_length': {},
            'H2_ring_sectors': {},
            'H3_ne_gradient': {},
            'H6_anchor_walk': {}
        }
        
        # H1: Arc-length modulo with k = 24, 28, and 5..11
        print("\n[H1] Arc-length modulo test")
        print("-" * 40)
        h1_results = self.test_h1_arc_length_modulo()
        
        for key, result in h1_results.items():
            if result['p_value'] < 0.05:  # Only show significant results
                print(f"{key}: p={result['p_value']:.4f}, "
                     f"stat={result['test_statistic']:.3f}, "
                     f"n={result['num_letters']}")
                print(f"  Text: {result['selected_text'][:50]}...")
        
        all_results['H1_arc_length'] = h1_results
        
        # H2: Ring-24 sectors with step = 4
        print("\n[H2] Ring-24 sectors test (step=4)")
        print("-" * 40)
        h2_result = self.test_h2_ring_sectors(num_sectors=24, step=4)
        
        print(f"p={h2_result['p_value']:.4f}, "
             f"stat={h2_result['test_statistic']:.3f}, "
             f"n={h2_result['num_letters']}, "
             f"sectors={h2_result['sectors_used']}")
        print(f"Text: {h2_result['selected_text'][:50]}...")
        
        all_results['H2_ring_sectors'] = h2_result
        
        # H3: NE gradient with k = 7, 8, 9
        print("\n[H3] NE gradient test")
        print("-" * 40)
        h3_results = self.test_h3_ne_gradient(k_values=[7, 8, 9])
        
        for key, result in h3_results.items():
            print(f"{key}: p={result['p_value']:.4f}, "
                 f"stat={result['test_statistic']:.3f}, "
                 f"n={result['num_letters']}")
            print(f"  Text: {result['selected_text'][:50]}...")
        
        all_results['H3_ne_gradient'] = h3_results
        
        # H6: Anchor-walk with offsets ±1
        print("\n[H6] Anchor-walk peel test (offsets ±1)")
        print("-" * 40)
        h6_results = self.test_h6_anchor_walk(offsets=[-1, 1])
        
        for key, result in h6_results.items():
            print(f"{key}: p={result['p_value']:.4f}, "
                 f"stat={result['test_statistic']:.3f}, "
                 f"n={result['num_letters']}")
            print(f"  Text: {result['selected_text'][:50]}...")
        
        all_results['H6_anchor_walk'] = h6_results
        
        # Find best results
        print("\n" + "=" * 80)
        print("BEST THREE RESULTS (lowest p-values):")
        print("-" * 40)
        
        # Collect all results with p-values
        all_tests = []
        for test_name, test_results in all_results.items():
            if isinstance(test_results, dict) and 'p_value' in test_results:
                all_tests.append((test_name, 'main', test_results))
            elif isinstance(test_results, dict):
                for sub_key, sub_result in test_results.items():
                    if isinstance(sub_result, dict) and 'p_value' in sub_result:
                        all_tests.append((test_name, sub_key, sub_result))
        
        # Sort by p-value
        all_tests.sort(key=lambda x: x[2]['p_value'])
        
        # Show top 3
        for i, (test_name, sub_key, result) in enumerate(all_tests[:3], 1):
            print(f"\n{i}. {test_name} ({sub_key})")
            print(f"   p-value: {result['p_value']:.6f}")
            print(f"   Test statistic: {result['test_statistic']:.4f}")
            print(f"   Letters selected: {result['num_letters']}")
            print(f"   Text: {result['selected_text'][:60]}...")
            
            # Check for replication
            if test_name == 'H1_arc_length':
                k = int(sub_key.split('=')[1])
                nearby_k = [k-1, k+1]
                print(f"   Replication check (k={k}±1):")
                for nk in nearby_k:
                    if f'k={nk}' in all_results['H1_arc_length']:
                        rep_p = all_results['H1_arc_length'][f'k={nk}']['p_value']
                        print(f"     k={nk}: p={rep_p:.4f}")
        
        # Apply Bonferroni correction
        num_tests = len(all_tests)
        bonferroni_threshold = 0.001 / num_tests
        
        print(f"\nBonferroni correction: α = 0.001 / {num_tests} = {bonferroni_threshold:.6f}")
        
        significant = [t for t in all_tests if t[2]['p_value'] < bonferroni_threshold]
        if significant:
            print(f"Tests passing Bonferroni correction: {len(significant)}")
            for test_name, sub_key, _ in significant:
                print(f"  - {test_name} ({sub_key})")
        else:
            print("No tests pass Bonferroni correction at α = 0.001")
        
        return all_results
    
    def visualize_best_overlays(self, results: Dict, output_dir: str = '.'):
        """Create visualization overlays for the best results"""
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        
        # Find top 3 results
        all_tests = []
        for test_name, test_results in results.items():
            if isinstance(test_results, dict) and 'indices' in test_results:
                all_tests.append((test_name, 'main', test_results))
            elif isinstance(test_results, dict):
                for sub_key, sub_result in test_results.items():
                    if isinstance(sub_result, dict) and 'indices' in sub_result:
                        all_tests.append((test_name, sub_key, sub_result))
        
        all_tests.sort(key=lambda x: x[2].get('p_value', 1.0))
        
        for i, (test_name, sub_key, result) in enumerate(all_tests[:3], 1):
            fig = plt.figure(figsize=(12, 8))
            
            # 3D view
            ax1 = fig.add_subplot(121, projection='3d')
            
            # Plot all letters in gray
            ax1.scatter(self.coords[:, 0], self.coords[:, 1], self.coords[:, 2],
                       c='lightgray', s=20, alpha=0.3)
            
            # Highlight selected letters in red
            selected_indices = result['indices']
            selected_coords = self.coords[selected_indices]
            ax1.scatter(selected_coords[:, 0], selected_coords[:, 1], 
                       selected_coords[:, 2], c='red', s=100, alpha=0.8)
            
            # Add letter labels for selected
            for idx in selected_indices[:20]:  # Limit labels for clarity
                ax1.text(self.coords[idx, 0], self.coords[idx, 1], 
                        self.coords[idx, 2], self.letters[idx],
                        fontsize=8, color='darkred')
            
            ax1.set_title(f'{test_name} ({sub_key})\np={result["p_value"]:.4f}')
            ax1.set_xlabel('X')
            ax1.set_ylabel('Y')
            ax1.set_zlabel('Z')
            
            # 2D projection
            ax2 = fig.add_subplot(122)
            
            # Plot all letters
            ax2.scatter(self.coords[:, 0], self.coords[:, 2],
                       c='lightgray', s=20, alpha=0.3)
            
            # Highlight selected
            ax2.scatter(selected_coords[:, 0], selected_coords[:, 2],
                       c='red', s=100, alpha=0.8)
            
            # Add text preview
            text_preview = result['selected_text'][:40]
            ax2.text(0.02, 0.98, f"Text: {text_preview}...",
                    transform=ax2.transAxes, fontsize=10,
                    verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            ax2.set_title('X-Z Projection')
            ax2.set_xlabel('X')
            ax2.set_ylabel('Z')
            ax2.set_aspect('equal')
            
            plt.suptitle(f'Overlay {i}: {test_name}', fontsize=14, fontweight='bold')
            plt.tight_layout()
            
            # Save figure
            filename = f"{output_dir}/overlay_{i}_{test_name}_{sub_key}.png"
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"Saved overlay: {filename}")
            
            plt.close()


def main():
    """Run all priority tests and generate visualizations"""
    
    tester = RigorousGeometricTests()
    
    # Run tests
    results = tester.run_priority_tests()
    
    # Generate visualizations
    print("\n" + "=" * 80)
    print("Generating overlay visualizations...")
    tester.visualize_best_overlays(results)
    
    # Save results to JSON
    import json
    
    # Convert numpy arrays to lists for JSON serialization
    def convert_for_json(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_for_json(item) for item in obj]
        else:
            return obj
    
    json_results = convert_for_json(results)
    
    with open('rigorous_test_results.json', 'w') as f:
        json.dump(json_results, f, indent=2)
    
    print("\nResults saved to rigorous_test_results.json")
    
    return results


if __name__ == "__main__":
    main()