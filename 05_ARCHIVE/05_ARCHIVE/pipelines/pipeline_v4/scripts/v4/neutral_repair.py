#!/usr/bin/env python3
"""
Track A4: Neutral-move repair.
Apply saliency-preserving transforms to recover score after anchor placement.
"""

import json
import random
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set
import numpy as np

# Import dependencies
from gen_blinded_mcmc import BlindedMCMCGenerator


class NeutralMoveRepairer:
    """
    Apply neutral moves to repair score after anchor placement.
    """
    
    def __init__(self, seed: int = 1337):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        # Initialize scorer
        self.scorer = BlindedMCMCGenerator(seed)
        
        # Anchor positions (to protect during repair)
        self.anchor_spans = []
    
    def identify_anchor_spans(self, text: str) -> Set[int]:
        """
        Identify positions occupied by anchors.
        
        Returns:
            Set of protected positions
        """
        protected = set()
        
        # Look for anchor patterns
        anchors = [
            ('EAST', 4),
            ('NORTHEAST', 9),
            ('BERLINCLOCK', 11)
        ]
        
        for anchor_text, length in anchors:
            # Find all occurrences
            for i in range(len(text) - length + 1):
                if text[i:i+length] == anchor_text:
                    for j in range(i, i + length):
                        protected.add(j)
        
        return protected
    
    def apply_adjacent_swap(self, text: str, protected: Set[int]) -> List[str]:
        """
        Generate variants with adjacent character swaps.
        
        Args:
            text: Input text
            protected: Positions that cannot be modified
            
        Returns:
            List of swap variants
        """
        variants = []
        text_list = list(text)
        
        for i in range(len(text) - 1):
            # Check if both positions are unprotected
            if i not in protected and (i + 1) not in protected:
                # Create swap variant
                variant = text_list.copy()
                variant[i], variant[i+1] = variant[i+1], variant[i]
                variants.append(''.join(variant))
        
        return variants
    
    def apply_2opt_swap(
        self, 
        text: str, 
        protected: Set[int],
        low_saliency_positions: List[int]
    ) -> List[str]:
        """
        Apply 2-opt swaps on low-saliency positions.
        
        Args:
            text: Input text
            protected: Protected positions
            low_saliency_positions: Positions with low saliency
            
        Returns:
            List of 2-opt variants
        """
        variants = []
        text_list = list(text)
        
        # Filter to unprotected low-saliency positions
        valid_positions = [p for p in low_saliency_positions 
                          if p not in protected and p < len(text)]
        
        # Try swapping pairs of low-saliency positions
        for i in range(len(valid_positions)):
            for j in range(i + 1, min(i + 10, len(valid_positions))):
                pos1 = valid_positions[i]
                pos2 = valid_positions[j]
                
                # Create swap variant
                variant = text_list.copy()
                variant[pos1], variant[pos2] = variant[pos2], variant[pos1]
                variants.append(''.join(variant))
        
        return variants
    
    def apply_trigram_improvement(
        self,
        text: str,
        protected: Set[int]
    ) -> List[str]:
        """
        Try to improve trigram scores by selective character changes.
        
        Args:
            text: Input text
            protected: Protected positions
            
        Returns:
            List of improved variants
        """
        variants = []
        text_list = list(text)
        
        # Identify problematic trigrams (not in model)
        for i in range(len(text) - 2):
            # Skip if any position is protected
            if any(p in protected for p in range(i, i+3)):
                continue
            
            trigram = text[i:i+3]
            prefix = trigram[:2]
            
            # Check if trigram is rare
            if prefix in self.scorer.trigram_model['trigram_probs']:
                probs = self.scorer.trigram_model['trigram_probs'][prefix]
                current_char = trigram[2]
                
                if current_char not in probs or probs[current_char] < 0.01:
                    # Try to improve by sampling better character
                    if probs:
                        # Sample from distribution
                        chars = list(probs.keys())
                        weights = list(probs.values())
                        better_char = random.choices(chars, weights=weights)[0]
                        
                        # Create variant
                        variant = text_list.copy()
                        variant[i+2] = better_char
                        variants.append(''.join(variant))
        
        return variants
    
    def hill_climb_repair(
        self,
        text: str,
        max_iterations: int = 200,
        epsilon: float = 0.001,
        low_saliency_positions: List[int] = None
    ) -> Tuple[str, float, Dict]:
        """
        Hill-climb to repair score using neutral moves.
        
        Args:
            text: Anchored text to repair
            max_iterations: Maximum repair iterations
            epsilon: Minimum improvement threshold
            low_saliency_positions: Optional low-saliency positions
            
        Returns:
            (repaired_text, final_score, repair_stats)
        """
        # Identify protected positions
        protected = self.identify_anchor_spans(text)
        
        # Get initial score
        current_text = text
        current_score, current_components = self.scorer.compute_blinded_score(current_text)
        initial_score = current_score
        
        best_text = current_text
        best_score = current_score
        
        improvements = []
        no_improvement_count = 0
        
        for iteration in range(max_iterations):
            # Generate variants
            variants = []
            
            # Adjacent swaps
            variants.extend(self.apply_adjacent_swap(current_text, protected))
            
            # 2-opt swaps if low saliency positions provided
            if low_saliency_positions:
                variants.extend(self.apply_2opt_swap(
                    current_text, protected, low_saliency_positions
                ))
            
            # Trigram improvements
            variants.extend(self.apply_trigram_improvement(current_text, protected))
            
            # Evaluate variants
            best_variant = None
            best_variant_score = current_score
            
            for variant in variants:
                score, _ = self.scorer.compute_blinded_score(variant)
                if score > best_variant_score:
                    best_variant = variant
                    best_variant_score = score
            
            # Check for improvement
            if best_variant and best_variant_score > current_score + epsilon:
                current_text = best_variant
                current_score = best_variant_score
                improvements.append({
                    'iteration': iteration,
                    'score': current_score,
                    'improvement': current_score - initial_score
                })
                no_improvement_count = 0
                
                if current_score > best_score:
                    best_text = current_text
                    best_score = current_score
            else:
                no_improvement_count += 1
                
                # Stop if no improvement for many iterations
                if no_improvement_count >= 50:
                    break
        
        # Compute final statistics
        repair_stats = {
            'initial_score': initial_score,
            'final_score': best_score,
            'improvement': best_score - initial_score,
            'iterations': iteration + 1,
            'successful_improvements': len(improvements),
            'protected_positions': len(protected),
            'improvements_log': improvements
        }
        
        return best_text, best_score, repair_stats
    
    def repair_head(self, placement_result: Dict, saliency_data: Dict = None) -> Dict:
        """
        Repair a head after anchor placement.
        
        Args:
            placement_result: Result from Pareto placement
            saliency_data: Optional saliency information
            
        Returns:
            Dictionary with repair results
        """
        anchored_text = placement_result['anchored_text']
        
        # Get low saliency positions if available
        low_saliency_positions = None
        if saliency_data and 'low_saliency_positions' in saliency_data:
            low_saliency_positions = saliency_data['low_saliency_positions']
        
        # Run hill-climb repair
        repaired_text, final_score, repair_stats = self.hill_climb_repair(
            anchored_text,
            low_saliency_positions=low_saliency_positions
        )
        
        # Verify anchors are preserved
        anchors_preserved = all([
            'EAST' in repaired_text,
            'NORTHEAST' in repaired_text,
            'BERLINCLOCK' in repaired_text
        ])
        
        return {
            'original_text': placement_result['original_text'],
            'anchored_text': anchored_text,
            'repaired_text': repaired_text,
            'anchors_preserved': anchors_preserved,
            'pre_repair_score': placement_result['new_score'],
            'post_repair_score': final_score,
            'repair_improvement': repair_stats['improvement'],
            'repair_stats': repair_stats,
            'total_score_recovery': final_score - placement_result['new_score'],
            'final_vs_original': final_score - placement_result['original_score']
        }


def process_heads_with_repair(placement_file: Path, saliency_file: Path, output_dir: Path, n_heads: int = None):
    """
    Process heads with neutral-move repair.
    """
    # Load placement results
    with open(placement_file, 'r') as f:
        placement_data = json.load(f)
    
    # Load saliency data
    with open(saliency_file, 'r') as f:
        saliency_data = json.load(f)
    
    placement_results = placement_data['results']
    saliency_results = saliency_data['results']
    
    if n_heads:
        placement_results = placement_results[:n_heads]
        saliency_results = saliency_results[:n_heads]
    
    print(f"Repairing {len(placement_results)} heads...")
    
    repairer = NeutralMoveRepairer(seed=1337)
    repair_results = []
    
    for i, (placement, saliency) in enumerate(zip(placement_results, saliency_results)):
        if i % 10 == 0:
            print(f"  Repairing head {i+1}/{len(placement_results)}...")
        
        # Repair head
        repair_result = repairer.repair_head(
            placement,
            saliency['saliency_data']
        )
        
        # Add metadata
        repair_result['label'] = placement['label']
        repair_result['placement'] = placement['placement']
        repair_result['window_radius'] = placement['window_radius']
        
        repair_results.append(repair_result)
        
        # Print details for first few
        if i < 3:
            print(f"    Head {i}: Repair improvement={repair_result['repair_improvement']:.3f}, "
                  f"Total recovery={repair_result['total_score_recovery']:.3f}")
    
    # Save results
    output_file = output_dir / "repaired_heads.json"
    with open(output_file, 'w') as f:
        json.dump({
            'total_heads': len(repair_results),
            'results': repair_results
        }, f, indent=2)
    
    print(f"\nSaved repair results to {output_file}")
    
    # Statistics
    improvements = [r['repair_improvement'] for r in repair_results]
    recoveries = [r['total_score_recovery'] for r in repair_results]
    final_vs_original = [r['final_vs_original'] for r in repair_results]
    
    print("\nRepair Statistics:")
    print(f"  Mean repair improvement: {np.mean(improvements):.3f}")
    print(f"  Mean total recovery:     {np.mean(recoveries):.3f}")
    print(f"  Mean final vs original:  {np.mean(final_vs_original):.3f}")
    print(f"  Heads with net gain:     {sum(1 for x in final_vs_original if x > 0)}/{len(final_vs_original)}")
    
    return repair_results


def main():
    """Run neutral-move repair."""
    # Setup paths
    output_dir = Path(__file__).parent.parent.parent / "runs" / "track_a"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    placement_file = output_dir / "pareto_placements.json"
    saliency_file = output_dir / "SALIENCY.json"
    
    if not placement_file.exists():
        print("Running placement first...")
        from place_anchors_pareto import main as place_anchors
        place_anchors()
    
    # Process heads
    repair_results = process_heads_with_repair(
        placement_file, 
        saliency_file, 
        output_dir, 
        n_heads=50
    )
    
    return repair_results


if __name__ == "__main__":
    results = main()