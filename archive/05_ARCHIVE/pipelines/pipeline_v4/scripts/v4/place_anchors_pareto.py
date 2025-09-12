#!/usr/bin/env python3
"""
Track A3: Pareto anchor placement.
Optimize (anchor_cost, score_drop) jointly using ε-Pareto optimization.
"""

import json
import random
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

# Import dependencies
from gen_blinded_mcmc import BlindedMCMCGenerator
from saliency_map import SaliencyMapper


class ParetoAnchorPlacer:
    """
    Place anchors using Pareto optimization of anchor cost vs score drop.
    """
    
    def __init__(self, seed: int = 1337):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        # Initialize components
        self.scorer = BlindedMCMCGenerator(seed)
        self.saliency_mapper = SaliencyMapper(seed)
        
        # Anchor definitions
        self.anchors = {
            'EAST': {
                'text': 'EAST',
                'corridor_start': 21,
                'corridor_end': 25,
                'length': 4
            },
            'NORTHEAST': {
                'text': 'NORTHEAST',
                'corridor_start': 25,
                'corridor_end': 34,
                'length': 9
            },
            'BERLINCLOCK': {
                'text': 'BERLINCLOCK',
                'corridor_start': 63,
                'corridor_end': 74,
                'length': 11
            }
        }
    
    def compute_placement_cost(
        self, 
        placement: Dict[str, int],
        window_radius: int = 0,
        typo_budget: int = 0
    ) -> Tuple[float, float]:
        """
        Compute cost vector for an anchor placement.
        
        Args:
            placement: Dict mapping anchor names to start positions
            window_radius: Allowed window for placement
            typo_budget: Allowed typos (for windowed mode)
            
        Returns:
            (C_anchor, C_drop) tuple
        """
        C_anchor = 0.0
        
        for anchor_name, pos in placement.items():
            anchor_info = self.anchors[anchor_name]
            corridor_start = anchor_info['corridor_start']
            
            # Distance from exact corridor position
            distance = abs(pos - corridor_start)
            
            # Cost based on distance and window
            if distance == 0:
                cost = 0
            elif distance <= window_radius:
                cost = distance * 0.5  # Reduced cost within window
            else:
                cost = distance * 2  # High cost outside window
            
            C_anchor += cost
        
        # C_drop computed separately with saliency
        return C_anchor
    
    def compute_score_drop(
        self,
        text: str,
        placement: Dict[str, int],
        saliency: List[float]
    ) -> float:
        """
        Estimate score drop from placing anchors.
        
        Args:
            text: Original text
            placement: Anchor positions
            saliency: Per-position saliency values
            
        Returns:
            Estimated score drop
        """
        C_drop = 0.0
        
        for anchor_name, pos in placement.items():
            anchor_info = self.anchors[anchor_name]
            length = anchor_info['length']
            
            # Sum saliency for positions that will be overwritten
            for i in range(pos, min(pos + length, 75)):
                if i < len(saliency):
                    C_drop += saliency[i]
        
        return C_drop
    
    def generate_placement_candidates(
        self,
        text: str,
        saliency: List[float],
        window_radii: List[int] = [0, 2, 3, 4]
    ) -> List[Dict]:
        """
        Generate candidate anchor placements.
        
        Returns:
            List of placement dictionaries with costs
        """
        candidates = []
        
        for window_radius in window_radii:
            # For each window radius, try various placements
            for _ in range(10):  # Generate multiple candidates per radius
                placement = {}
                
                for anchor_name, anchor_info in self.anchors.items():
                    corridor_start = anchor_info['corridor_start']
                    corridor_end = anchor_info['corridor_end']
                    length = anchor_info['length']
                    
                    if window_radius == 0:
                        # Fixed placement
                        pos = corridor_start
                    else:
                        # Find best position within window
                        best_pos = corridor_start
                        best_saliency = float('inf')
                        
                        for test_pos in range(
                            max(0, corridor_start - window_radius),
                            min(75 - length, corridor_start + window_radius + 1)
                        ):
                            # Check if position is valid
                            if test_pos + length <= 75:
                                # Sum saliency for this placement
                                sal_sum = sum(saliency[test_pos:test_pos+length])
                                if sal_sum < best_saliency:
                                    best_saliency = sal_sum
                                    best_pos = test_pos
                        
                        pos = best_pos
                    
                    placement[anchor_name] = pos
                
                # Compute costs
                C_anchor = self.compute_placement_cost(placement, window_radius)
                C_drop = self.compute_score_drop(text, placement, saliency)
                
                candidates.append({
                    'placement': placement,
                    'window_radius': window_radius,
                    'C_anchor': C_anchor,
                    'C_drop': C_drop,
                    'total_cost': C_anchor + C_drop  # For sorting
                })
        
        return candidates
    
    def find_pareto_front(self, candidates: List[Dict], epsilon: float = 0.01) -> List[Dict]:
        """
        Find ε-Pareto optimal placements.
        
        Args:
            candidates: List of placement candidates
            epsilon: Dominance threshold
            
        Returns:
            Non-dominated placements
        """
        pareto_front = []
        
        for i, cand in enumerate(candidates):
            is_dominated = False
            
            for j, other in enumerate(candidates):
                if i == j:
                    continue
                
                # Check if other dominates cand (with epsilon tolerance)
                if (other['C_anchor'] <= cand['C_anchor'] - epsilon and
                    other['C_drop'] <= cand['C_drop'] - epsilon):
                    is_dominated = True
                    break
            
            if not is_dominated:
                pareto_front.append(cand)
        
        # Sort by total cost
        pareto_front.sort(key=lambda x: x['total_cost'])
        
        return pareto_front
    
    def apply_placement(self, text: str, placement: Dict[str, int]) -> str:
        """
        Apply anchor placement to text.
        
        Args:
            text: Original text
            placement: Anchor positions
            
        Returns:
            Text with anchors placed
        """
        text_list = list(text)
        
        # Apply each anchor
        for anchor_name, pos in placement.items():
            anchor_text = self.anchors[anchor_name]['text']
            
            # Overwrite positions with anchor text
            for i, char in enumerate(anchor_text):
                if pos + i < 75:
                    text_list[pos + i] = char
        
        return ''.join(text_list)
    
    def place_anchors_on_head(self, head_data: Dict) -> Dict:
        """
        Place anchors on a single head using Pareto optimization.
        
        Args:
            head_data: Dictionary with text and saliency data
            
        Returns:
            Dictionary with placement results
        """
        text = head_data['text']
        saliency = head_data['saliency_data']['saliency']
        
        # Generate placement candidates
        candidates = self.generate_placement_candidates(text, saliency)
        
        # Find Pareto front
        pareto_front = self.find_pareto_front(candidates)
        
        # Select best from Pareto front (lowest total cost)
        if pareto_front:
            best_placement = pareto_front[0]
        else:
            # Fallback to exact corridor placement
            best_placement = {
                'placement': {
                    'EAST': 21,
                    'NORTHEAST': 25,
                    'BERLINCLOCK': 63
                },
                'window_radius': 0,
                'C_anchor': 0,
                'C_drop': sum(saliency[21:25]) + sum(saliency[25:34]) + sum(saliency[63:74])
            }
        
        # Apply placement
        anchored_text = self.apply_placement(text, best_placement['placement'])
        
        # Compute new score
        new_score, new_components = self.scorer.compute_blinded_score(anchored_text)
        original_score = head_data['blinded_score']
        actual_drop = original_score - new_score
        
        return {
            'original_text': text,
            'anchored_text': anchored_text,
            'placement': best_placement['placement'],
            'window_radius': best_placement['window_radius'],
            'C_anchor': best_placement['C_anchor'],
            'C_drop': best_placement['C_drop'],
            'predicted_drop': best_placement['C_drop'],
            'actual_drop': actual_drop,
            'original_score': original_score,
            'new_score': new_score,
            'pareto_front_size': len(pareto_front),
            'total_candidates': len(candidates)
        }


def process_heads_with_placement(saliency_file: Path, output_dir: Path, n_heads: int = None):
    """
    Process heads with Pareto anchor placement.
    """
    # Load saliency results
    with open(saliency_file, 'r') as f:
        data = json.load(f)
    
    results = data['results']
    if n_heads:
        results = results[:n_heads]
    
    print(f"Processing {len(results)} heads for anchor placement...")
    
    placer = ParetoAnchorPlacer(seed=1337)
    placement_results = []
    
    for i, head_data in enumerate(results):
        if i % 10 == 0:
            print(f"  Processing head {i+1}/{len(results)}...")
        
        # Place anchors
        placement_result = placer.place_anchors_on_head(head_data)
        
        # Add metadata
        placement_result['label'] = head_data['label']
        placement_result['saliency_stats'] = head_data['saliency_data']['statistics']
        
        placement_results.append(placement_result)
        
        # Print details for first few
        if i < 3:
            print(f"    Head {i}: C_anchor={placement_result['C_anchor']:.2f}, "
                  f"C_drop={placement_result['C_drop']:.2f}, "
                  f"Actual drop={placement_result['actual_drop']:.3f}")
    
    # Save results
    output_file = output_dir / "pareto_placements.json"
    with open(output_file, 'w') as f:
        json.dump({
            'total_heads': len(placement_results),
            'results': placement_results
        }, f, indent=2)
    
    print(f"\nSaved placement results to {output_file}")
    
    # Statistics
    drops = [r['actual_drop'] for r in placement_results]
    recoveries = [r['original_score'] - r['actual_drop'] for r in placement_results]
    
    print("\nPlacement Statistics:")
    print(f"  Mean score drop: {np.mean(drops):.3f}")
    print(f"  Std score drop:  {np.std(drops):.3f}")
    print(f"  Min score drop:  {np.min(drops):.3f}")
    print(f"  Max score drop:  {np.max(drops):.3f}")
    print(f"  Mean recovery:   {np.mean(recoveries):.3f}")
    
    return placement_results


def main():
    """Run Pareto anchor placement."""
    # Setup paths
    output_dir = Path(__file__).parent.parent.parent / "runs" / "track_a"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    saliency_file = output_dir / "SALIENCY.json"
    
    if not saliency_file.exists():
        print("Running saliency analysis first...")
        from saliency_map import main as compute_saliency
        compute_saliency()
    
    # Process heads
    placement_results = process_heads_with_placement(saliency_file, output_dir, n_heads=50)
    
    return placement_results


if __name__ == "__main__":
    results = main()