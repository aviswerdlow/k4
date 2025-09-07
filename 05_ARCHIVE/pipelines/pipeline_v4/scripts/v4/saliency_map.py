#!/usr/bin/env python3
"""
Track A2: Saliency map computation.
Determines which positions contribute most to blinded score.
"""

import json
import random
import sys
from pathlib import Path
from typing import Dict, List
import numpy as np

# Import blinded generator
from gen_blinded_mcmc import BlindedMCMCGenerator


class SaliencyMapper:
    """
    Compute per-position saliency for heads.
    """
    
    def __init__(self, seed: int = 1337):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        # Initialize scorer
        self.generator = BlindedMCMCGenerator(seed)
    
    def compute_saliency(self, text: str, n_samples: int = 5) -> Dict:
        """
        Compute saliency map for a head.
        
        For each position, measure how much the blinded score drops
        when that position is changed.
        
        Args:
            text: 75-character head
            n_samples: Number of random alternatives to average over
            
        Returns:
            Dictionary with saliency data
        """
        # Get baseline score
        baseline_score, baseline_components = self.generator.compute_blinded_score(text)
        
        saliency = []
        position_impacts = []
        
        for pos in range(len(text)):
            # Try multiple random alternatives
            deltas = []
            
            for _ in range(n_samples):
                # Create variant with position flipped
                text_list = list(text)
                original_char = text_list[pos]
                
                # Sample alternative (not equal to original)
                alternatives = [c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c != original_char]
                new_char = random.choice(alternatives)
                text_list[pos] = new_char
                
                # Compute score change
                variant = ''.join(text_list)
                variant_score, _ = self.generator.compute_blinded_score(variant)
                delta = variant_score - baseline_score
                deltas.append(delta)
            
            # Saliency = negative median delta (higher = more harmful to change)
            median_delta = np.median(deltas)
            saliency_value = -median_delta
            
            saliency.append(saliency_value)
            position_impacts.append({
                'position': pos,
                'char': text[pos],
                'saliency': saliency_value,
                'median_delta': median_delta,
                'std_delta': np.std(deltas)
            })
        
        # Normalize saliency to [0, 1]
        min_sal = min(saliency)
        max_sal = max(saliency)
        if max_sal > min_sal:
            normalized_saliency = [(s - min_sal) / (max_sal - min_sal) for s in saliency]
        else:
            normalized_saliency = [0.5] * len(saliency)
        
        # Identify high/low saliency regions
        threshold_high = np.percentile(saliency, 75)
        threshold_low = np.percentile(saliency, 25)
        
        high_saliency_positions = [i for i, s in enumerate(saliency) if s >= threshold_high]
        low_saliency_positions = [i for i, s in enumerate(saliency) if s <= threshold_low]
        
        return {
            'text': text,
            'baseline_score': baseline_score,
            'baseline_components': baseline_components,
            'saliency': saliency,
            'normalized_saliency': normalized_saliency,
            'position_impacts': position_impacts,
            'high_saliency_positions': high_saliency_positions,
            'low_saliency_positions': low_saliency_positions,
            'statistics': {
                'mean_saliency': np.mean(saliency),
                'std_saliency': np.std(saliency),
                'max_saliency': max_sal,
                'min_saliency': min_sal,
                'threshold_high': threshold_high,
                'threshold_low': threshold_low
            }
        }
    
    def visualize_saliency(self, saliency_data: Dict) -> str:
        """
        Create ASCII visualization of saliency map.
        """
        text = saliency_data['text']
        normalized = saliency_data['normalized_saliency']
        
        # Create visual representation
        lines = []
        lines.append("Saliency Map Visualization:")
        lines.append("=" * 75)
        
        # Text with position markers
        lines.append("Position: " + ''.join(str(i % 10) for i in range(75)))
        lines.append("Text:     " + text)
        
        # Saliency bars
        saliency_chars = []
        for val in normalized:
            if val >= 0.75:
                saliency_chars.append('█')  # High saliency
            elif val >= 0.5:
                saliency_chars.append('▓')  # Medium-high
            elif val >= 0.25:
                saliency_chars.append('▒')  # Medium-low
            else:
                saliency_chars.append('░')  # Low saliency
        
        lines.append("Saliency: " + ''.join(saliency_chars))
        
        # Mark corridor positions
        corridor_marks = [' '] * 75
        # EAST: 21-24
        for i in range(21, 25):
            corridor_marks[i] = 'E'
        # NORTHEAST: 25-33
        for i in range(25, 34):
            corridor_marks[i] = 'N'
        # BERLINCLOCK: 63-73
        for i in range(63, 74):
            corridor_marks[i] = 'B'
        
        lines.append("Corridor: " + ''.join(corridor_marks))
        lines.append("=" * 75)
        
        # Statistics
        stats = saliency_data['statistics']
        lines.append(f"Mean saliency: {stats['mean_saliency']:.3f}")
        lines.append(f"Std saliency:  {stats['std_saliency']:.3f}")
        lines.append(f"Max saliency:  {stats['max_saliency']:.3f} at positions {saliency_data['high_saliency_positions'][:5]}")
        lines.append(f"Min saliency:  {stats['min_saliency']:.3f} at positions {saliency_data['low_saliency_positions'][:5]}")
        
        return '\n'.join(lines)
    
    def find_best_anchor_positions(self, saliency_data: Dict) -> Dict:
        """
        Identify best positions for anchor placement based on saliency.
        
        Returns:
            Dictionary with recommended positions for each anchor
        """
        saliency = saliency_data['saliency']
        
        # Define corridors
        corridors = {
            'EAST': (21, 25, 4),  # start, end, length
            'NORTHEAST': (25, 34, 9),
            'BERLINCLOCK': (63, 74, 11)
        }
        
        recommendations = {}
        
        for anchor_name, (start, end, length) in corridors.items():
            # Find position within corridor with lowest total saliency
            best_pos = None
            best_saliency_sum = float('inf')
            
            for pos in range(start, min(end - length + 1, 75 - length + 1)):
                # Sum saliency for this placement
                saliency_sum = sum(saliency[pos:pos+length])
                
                if saliency_sum < best_saliency_sum:
                    best_saliency_sum = saliency_sum
                    best_pos = pos
            
            recommendations[anchor_name] = {
                'best_position': best_pos,
                'saliency_cost': best_saliency_sum,
                'corridor_start': start,
                'corridor_end': end,
                'length': length
            }
        
        return recommendations


def process_heads(heads_file: Path, output_dir: Path, n_heads: int = None):
    """
    Process heads and compute saliency maps.
    """
    # Load heads
    with open(heads_file, 'r') as f:
        data = json.load(f)
    
    heads = data['heads']
    if n_heads:
        heads = heads[:n_heads]
    
    print(f"Processing {len(heads)} heads for saliency analysis...")
    
    mapper = SaliencyMapper(seed=1337)
    saliency_results = []
    
    for i, head in enumerate(heads):
        if i % 10 == 0:
            print(f"  Processing head {i+1}/{len(heads)}...")
        
        # Compute saliency
        saliency_data = mapper.compute_saliency(head['text'])
        
        # Find best anchor positions
        anchor_recommendations = mapper.find_best_anchor_positions(saliency_data)
        
        # Add to results
        result = {
            'label': head['label'],
            'text': head['text'],
            'blinded_score': head['score'],
            'saliency_data': saliency_data,
            'anchor_recommendations': anchor_recommendations
        }
        
        saliency_results.append(result)
        
        # Save visualization for first few
        if i < 3:
            viz = mapper.visualize_saliency(saliency_data)
            viz_file = output_dir / f"saliency_viz_{i:03d}.txt"
            with open(viz_file, 'w') as f:
                f.write(viz)
            print(f"    Saved visualization to {viz_file}")
    
    # Save all results
    output_file = output_dir / "SALIENCY.json"
    with open(output_file, 'w') as f:
        json.dump({
            'total_heads': len(saliency_results),
            'results': saliency_results
        }, f, indent=2)
    
    print(f"\nSaved saliency analysis to {output_file}")
    
    # Summary statistics
    all_saliencies = []
    for result in saliency_results:
        all_saliencies.extend(result['saliency_data']['saliency'])
    
    print("\nOverall Saliency Statistics:")
    print(f"  Mean: {np.mean(all_saliencies):.3f}")
    print(f"  Std:  {np.std(all_saliencies):.3f}")
    print(f"  Min:  {np.min(all_saliencies):.3f}")
    print(f"  Max:  {np.max(all_saliencies):.3f}")
    
    return saliency_results


def main():
    """Run saliency analysis on blinded heads."""
    # Setup paths
    output_dir = Path(__file__).parent.parent.parent / "runs" / "track_a"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    heads_file = output_dir / "blinded_heads.json"
    
    if not heads_file.exists():
        print("Generating blinded heads first...")
        from gen_blinded_mcmc import main as gen_heads
        gen_heads()
    
    # Process heads
    saliency_results = process_heads(heads_file, output_dir, n_heads=50)
    
    return saliency_results


if __name__ == "__main__":
    results = main()