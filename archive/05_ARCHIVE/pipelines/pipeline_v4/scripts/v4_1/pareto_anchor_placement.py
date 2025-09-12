#!/usr/bin/env python3
"""
Pareto-optimal anchor placement with neutral repair.
Minimizes score drop while maintaining linguistic quality.
"""

import json
import numpy as np
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import itertools
import hashlib

class ParetoAnchorPlacer:
    """
    Place anchors optimally using Pareto optimization.
    """
    
    def __init__(self, alpha: float = 1.0, beta: float = 1.0):
        """
        Initialize Pareto placer.
        
        Args:
            alpha: Weight for predicted drop sum
            beta: Weight for post-gate penalty
        """
        self.alpha = alpha
        self.beta = beta
        
        # Anchor strings
        self.anchors = {
            'EAST': (21, 24),      # Positions 21-24
            'NORTHEAST': (25, 33), # Positions 25-33
            'BERLINCLOCK': (63, 73) # Positions 63-73
        }
        
        # Simplified anchors for initial implementation
        self.anchor_texts = ['EAST', 'NORTHEAST', 'BERLIN', 'CLOCK']
        
        self.function_words = {
            'THE', 'A', 'AN', 'IS', 'ARE', 'WAS', 'BE', 'TO', 'OF', 'AND',
            'IN', 'FOR', 'ON', 'WITH', 'AS', 'BY', 'AT', 'FROM', 'BUT', 'OR',
            'IF', 'THEN', 'SO', 'ALL', 'WOULD', 'THERE', 'THEIR', 'WHAT'
        }
        
        self.verbs = {
            'SET', 'READ', 'SEE', 'FIND', 'SEEK', 'LOOK', 'APPLY', 'USE',
            'TAKE', 'MAKE', 'TURN', 'CHECK', 'MARK', 'NOTE', 'KEEP', 'HOLD'
        }
    
    def find_valid_positions(self, text: str, anchor_length: int, 
                            existing_positions: List[Tuple[int, int]]) -> List[int]:
        """
        Find valid positions for anchor placement.
        
        Args:
            text: Head text
            anchor_length: Length of anchor to place
            existing_positions: Already placed anchors (start, end)
            
        Returns:
            List of valid starting positions
        """
        valid = []
        text_len = len(text)
        
        for pos in range(text_len - anchor_length + 1):
            # Check position is valid
            end_pos = pos + anchor_length
            
            # Don't go past text boundary
            if end_pos > text_len:
                continue
            
            # Check no overlap with existing anchors
            overlaps = False
            for existing_start, existing_end in existing_positions:
                # Check for overlap or too close (min spacing = 2)
                if not (end_pos + 2 <= existing_start or pos >= existing_end + 2):
                    overlaps = True
                    break
            
            if not overlaps:
                valid.append(pos)
        
        return valid
    
    def predict_metrics_after_insertion(self, text: str, positions: Dict[str, int]) -> Dict:
        """
        Predict metrics after anchor insertion.
        
        Args:
            text: Original text
            positions: Anchor positions {anchor_text: position}
            
        Returns:
            Predicted metrics
        """
        # Insert anchors into text
        modified = list(text)
        
        # Sort by position (reverse) to maintain indices
        sorted_insertions = sorted(positions.items(), key=lambda x: x[1], reverse=True)
        
        for anchor_text, pos in sorted_insertions:
            # Simple insertion (in real implementation would be more sophisticated)
            if pos < len(modified):
                # Replace characters at position
                for i, char in enumerate(anchor_text):
                    if pos + i < len(modified):
                        modified[pos + i] = char
        
        modified_text = ''.join(modified)
        
        # Predict metrics
        words = modified_text.split()
        f_words = sum(1 for w in words if w in self.function_words)
        has_verb = any(w in self.verbs for w in words)
        
        return {
            'text': modified_text,
            'f_words': f_words,
            'has_verb': has_verb
        }
    
    def compute_cost(self, drop_predictions: List[float], 
                     predicted_metrics: Dict) -> float:
        """
        Compute Pareto cost.
        
        Args:
            drop_predictions: Predicted drops for each anchor
            predicted_metrics: Predicted metrics after insertion
            
        Returns:
            Combined cost
        """
        # Drop component
        drop_sum = sum(drop_predictions)
        
        # Gate penalty component
        penalty = 0.0
        if predicted_metrics['f_words'] < 8:
            penalty += 1.0
        if not predicted_metrics['has_verb']:
            penalty += 1.0
        
        # Combined cost
        cost = self.alpha * drop_sum + self.beta * penalty
        
        return cost
    
    def find_optimal_placement(self, text: str, saliency_map: Dict, 
                              drop_predictor) -> Dict:
        """
        Find optimal anchor placement using Pareto optimization.
        
        Args:
            text: Head text
            saliency_map: Precomputed saliency map
            drop_predictor: Drop prediction model
            
        Returns:
            Optimal placement configuration
        """
        # Generate candidate placements
        candidates = []
        
        # For simplified version, try a grid of positions
        # In real implementation, would use more sophisticated search
        
        # Try different position combinations
        text_len = len(text)
        
        # Sample positions for each anchor
        anchor_configs = []
        
        # EAST (length 4)
        east_positions = self.find_valid_positions(text, 4, [])
        
        for east_pos in east_positions[::3]:  # Sample every 3rd position
            # NORTHEAST (length 9)
            ne_positions = self.find_valid_positions(
                text, 9, [(east_pos, east_pos + 4)]
            )
            
            for ne_pos in ne_positions[::3]:
                # BERLIN (length 6)
                berlin_positions = self.find_valid_positions(
                    text, 6, 
                    [(east_pos, east_pos + 4), (ne_pos, ne_pos + 9)]
                )
                
                for berlin_pos in berlin_positions[::3]:
                    # CLOCK (length 5)
                    clock_positions = self.find_valid_positions(
                        text, 5,
                        [(east_pos, east_pos + 4), 
                         (ne_pos, ne_pos + 9),
                         (berlin_pos, berlin_pos + 6)]
                    )
                    
                    for clock_pos in clock_positions[::3]:
                        config = {
                            'EAST': east_pos,
                            'NORTHEAST': ne_pos,
                            'BERLIN': berlin_pos,
                            'CLOCK': clock_pos
                        }
                        
                        # Compute drops
                        drops = []
                        for anchor, pos in config.items():
                            drop = drop_predictor.predict_drop(
                                text, pos, saliency_map
                            )
                            drops.append(drop)
                        
                        # Predict metrics
                        metrics = self.predict_metrics_after_insertion(text, config)
                        
                        # Compute cost
                        cost = self.compute_cost(drops, metrics)
                        
                        candidates.append({
                            'config': config,
                            'drops': drops,
                            'metrics': metrics,
                            'cost': cost
                        })
                        
                        # Limit candidates for efficiency
                        if len(candidates) >= 100:
                            break
                    if len(candidates) >= 100:
                        break
                if len(candidates) >= 100:
                    break
            if len(candidates) >= 100:
                break
        
        # Find optimal (minimum cost)
        if not candidates:
            # Fallback to simple placement
            config = {
                'EAST': 10,
                'NORTHEAST': 20,
                'BERLIN': 35,
                'CLOCK': 45
            }
            return {
                'config': config,
                'drops': [0.2, 0.2, 0.2, 0.2],
                'metrics': self.predict_metrics_after_insertion(text, config),
                'cost': 0.8
            }
        
        optimal = min(candidates, key=lambda x: x['cost'])
        return optimal
    
    def place_anchors(self, text: str, optimal_config: Dict) -> str:
        """
        Place anchors in text according to optimal configuration.
        
        Args:
            text: Original text
            optimal_config: Optimal placement configuration
            
        Returns:
            Text with anchors inserted
        """
        # Convert text to list for easier manipulation
        chars = list(text)
        
        # Sort insertions by position (reverse) to maintain indices
        insertions = sorted(
            optimal_config['config'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        for anchor_text, pos in insertions:
            # Insert anchor at position
            # For simplicity, replace characters
            for i, char in enumerate(anchor_text):
                if pos + i < len(chars):
                    chars[pos + i] = char
        
        return ''.join(chars)


class NeutralRepairer:
    """
    Apply neutral repairs to recover score after anchor insertion.
    """
    
    def __init__(self, repair_budget: int = 30):
        """
        Initialize repairer.
        
        Args:
            repair_budget: Max moves per anchor
        """
        self.repair_budget = repair_budget
        
        self.neutral_swaps = [
            ('AND', 'THEN'),
            ('THEN', 'AND'),
            ('THAT', 'WHICH'),
            ('WHICH', 'THAT'),
            ('THE', 'A'),
            ('A', 'THE'),
            ('IS', 'ARE'),
            ('ARE', 'IS')
        ]
    
    def find_repair_positions(self, text: str, anchor_positions: Dict) -> List[int]:
        """
        Find positions near anchors for repair.
        
        Args:
            text: Text with anchors
            anchor_positions: Anchor configuration
            
        Returns:
            List of positions within ±2 tokens of anchors
        """
        repair_positions = set()
        words = text.split()
        
        # Map word positions to character positions
        char_pos = 0
        word_to_char = []
        for word in words:
            word_to_char.append(char_pos)
            char_pos += len(word) + 1  # +1 for space
        
        # Find words near anchors
        for anchor, pos in anchor_positions.items():
            # Find word containing this position
            for i, word_pos in enumerate(word_to_char):
                if word_pos <= pos < word_pos + len(words[i]):
                    # Add ±2 word positions
                    for offset in range(-2, 3):
                        if 0 <= i + offset < len(words):
                            repair_positions.add(i + offset)
                    break
        
        return sorted(repair_positions)
    
    def apply_repair(self, text: str, position: int, repair_type: str) -> str:
        """
        Apply a single repair.
        
        Args:
            text: Current text
            position: Word position for repair
            repair_type: Type of repair
            
        Returns:
            Repaired text
        """
        words = text.split()
        
        if position >= len(words):
            return text
        
        if repair_type == 'swap':
            # Try neutral swaps
            for old, new in self.neutral_swaps:
                if words[position] == old:
                    words[position] = new
                    break
        
        return ' '.join(words)
    
    def repair(self, original_text: str, anchored_text: str, 
              anchor_positions: Dict, scorer) -> Dict:
        """
        Apply neutral repairs to recover score.
        
        Args:
            original_text: Text before anchors
            anchored_text: Text with anchors
            anchor_positions: Anchor configuration
            scorer: Function to compute score
            
        Returns:
            Repair results
        """
        original_score = scorer(original_text)
        current_score = scorer(anchored_text)
        initial_drop = original_score - current_score
        
        current_text = anchored_text
        repair_trace = []
        moves_made = 0
        
        # Find repair positions
        repair_positions = self.find_repair_positions(anchored_text, anchor_positions)
        
        for _ in range(self.repair_budget):
            if moves_made >= self.repair_budget:
                break
            
            # Try repairs at each position
            best_repair = None
            best_score = current_score
            
            for pos in repair_positions:
                # Try swap
                repaired = self.apply_repair(current_text, pos, 'swap')
                repaired_score = scorer(repaired)
                
                if repaired_score > best_score:
                    best_repair = {
                        'text': repaired,
                        'position': pos,
                        'type': 'swap',
                        'score': repaired_score
                    }
                    best_score = repaired_score
            
            if best_repair:
                current_text = best_repair['text']
                current_score = best_repair['score']
                moves_made += 1
                
                repair_trace.append({
                    'move': moves_made,
                    'position': best_repair['position'],
                    'type': best_repair['type'],
                    'score': current_score,
                    'recovery': (current_score - scorer(anchored_text)) / initial_drop
                        if initial_drop > 0 else 0
                })
                
                # Check if we've recovered enough
                recovery = (current_score - scorer(anchored_text)) / initial_drop \
                    if initial_drop > 0 else 0
                if recovery >= 0.8:
                    break
            else:
                # No improvement possible
                break
        
        final_recovery = (current_score - scorer(anchored_text)) / initial_drop \
            if initial_drop > 0 else 0
        
        return {
            'original_text': original_text,
            'anchored_text': anchored_text,
            'repaired_text': current_text,
            'original_score': original_score,
            'anchored_score': scorer(anchored_text),
            'repaired_score': current_score,
            'initial_drop': initial_drop,
            'final_recovery': final_recovery,
            'moves_made': moves_made,
            'repair_trace': repair_trace
        }


def main():
    """Test Pareto placement and repair."""
    
    # Load test data
    import sys
    sys.path.append(str(Path(__file__).parent))
    from saliency_map import SaliencyMapper, DropPredictor
    
    # Example text
    text = "SET THE COURSE TRUE AND READ THE SIGN WHERE THE PATH LEADS TO MORE"
    
    # Compute saliency
    mapper = SaliencyMapper()
    saliency_map = mapper.generate_saliency_map(text)
    
    # Initialize drop predictor
    predictor = DropPredictor()
    
    # Initialize Pareto placer
    placer = ParetoAnchorPlacer(alpha=1.0, beta=1.0)
    
    # Find optimal placement
    print("Finding optimal anchor placement...")
    optimal = placer.find_optimal_placement(text, saliency_map, predictor)
    
    print(f"\nOptimal configuration:")
    print(f"  Positions: {optimal['config']}")
    print(f"  Predicted drops: {[f'{d:.3f}' for d in optimal['drops']]}")
    print(f"  Total drop: {sum(optimal['drops']):.3f}")
    print(f"  Cost: {optimal['cost']:.3f}")
    
    # Place anchors
    anchored_text = placer.place_anchors(text, optimal)
    print(f"\nAnchored text: {anchored_text}")
    
    # Apply repair
    repairer = NeutralRepairer(repair_budget=30)
    
    # Simple scorer for testing
    def scorer(t):
        return mapper.compute_base_score(t)
    
    repair_result = repairer.repair(text, anchored_text, optimal['config'], scorer)
    
    print(f"\nRepair results:")
    print(f"  Original score: {repair_result['original_score']:.3f}")
    print(f"  Anchored score: {repair_result['anchored_score']:.3f}")
    print(f"  Repaired score: {repair_result['repaired_score']:.3f}")
    print(f"  Recovery: {repair_result['final_recovery']*100:.1f}%")
    print(f"  Moves made: {repair_result['moves_made']}")
    
    # Save results
    output_dir = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/experiments/pipeline_v4/runs/track_a_l")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "pareto_test.json", 'w') as f:
        json.dump({
            'original': text,
            'optimal_placement': optimal,
            'anchored': anchored_text,
            'repair': repair_result
        }, f, indent=2)
    
    print(f"\nResults saved to {output_dir / 'pareto_test.json'}")


if __name__ == "__main__":
    main()