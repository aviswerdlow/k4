#!/usr/bin/env python3
"""
Improved anchor placement with token-boundary insertion.
Preserves function words and linguistic structure.
"""

import json
import numpy as np
from typing import List, Dict, Tuple, Optional, Set
from pathlib import Path
import itertools
import hashlib

class ImprovedAnchorPlacer:
    """
    Token-aware anchor placement that preserves linguistic structure.
    """
    
    def __init__(self, alpha: float = 0.6, beta: float = 0.2, gamma: float = 0.3):
        """
        Initialize improved placer.
        
        Args:
            alpha: Weight for predicted drop sum
            beta: Weight for f-word retention 
            gamma: Weight for verb preservation
        """
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        
        # Anchor strings
        self.anchor_texts = ['EAST', 'NORTHEAST', 'BERLIN', 'CLOCK']
        
        self.function_words = {
            'THE', 'A', 'AN', 'IS', 'ARE', 'WAS', 'BE', 'TO', 'OF', 'AND',
            'IN', 'FOR', 'ON', 'WITH', 'AS', 'BY', 'AT', 'FROM', 'BUT', 'OR',
            'IF', 'THEN', 'SO', 'ALL', 'WOULD', 'THERE', 'THEIR', 'WHAT',
            'THAT', 'THIS', 'THESE', 'THOSE', 'WHERE', 'WHEN', 'WHY', 'HOW'
        }
        
        self.verbs = {
            'SET', 'READ', 'SEE', 'FIND', 'SEEK', 'LOOK', 'APPLY', 'USE',
            'TAKE', 'MAKE', 'TURN', 'CHECK', 'MARK', 'NOTE', 'KEEP', 'HOLD',
            'LEAD', 'LEADS', 'MOVE', 'THINK', 'KNOW', 'BELIEVE', 'WATCH'
        }
        
        # Common padding words for grammar-aware insertion
        self.padding_words = {
            'connectors': ['THE', 'AND', 'TO', 'OF', 'IN', 'FOR', 'WITH'],
            'determiners': ['THE', 'A', 'AN', 'THIS', 'THAT', 'THESE'],
            'prepositions': ['IN', 'ON', 'AT', 'BY', 'FOR', 'WITH', 'FROM']
        }
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        return text.split()
    
    def find_token_boundaries(self, text: str) -> List[Tuple[int, int]]:
        """
        Find word boundaries in text.
        
        Args:
            text: Input text
            
        Returns:
            List of (start, end) positions for each token
        """
        boundaries = []
        tokens = self.tokenize(text)
        
        pos = 0
        for token in tokens:
            # Find token in remaining text
            idx = text[pos:].find(token)
            if idx >= 0:
                start = pos + idx
                end = start + len(token)
                boundaries.append((start, end))
                pos = end
                
                # Skip any spaces
                while pos < len(text) and text[pos] == ' ':
                    pos += 1
        
        return boundaries
    
    def insert_at_token_boundary(self, text: str, anchor: str, 
                                position: int) -> Tuple[str, int]:
        """
        Insert anchor at nearest token boundary.
        
        Args:
            text: Original text
            anchor: Anchor to insert
            position: Target position
            
        Returns:
            (Modified text, actual insertion position)
        """
        boundaries = self.find_token_boundaries(text)
        
        # Find nearest boundary
        best_boundary = 0
        min_dist = float('inf')
        
        for i, (start, end) in enumerate(boundaries):
            # Can insert before this token
            if abs(start - position) < min_dist:
                min_dist = abs(start - position)
                best_boundary = start
                
            # Can insert after this token (if not last)
            if i < len(boundaries) - 1:
                next_start = boundaries[i + 1][0]
                space_pos = end + (next_start - end) // 2
                if abs(space_pos - position) < min_dist:
                    min_dist = abs(space_pos - position)
                    best_boundary = space_pos
        
        # Insert anchor
        if best_boundary <= len(text):
            modified = text[:best_boundary] + anchor + ' ' + text[best_boundary:]
        else:
            modified = text + ' ' + anchor
            
        return modified, best_boundary
    
    def compute_linguistic_metrics(self, text: str) -> Dict:
        """
        Compute linguistic metrics.
        
        Args:
            text: Text to analyze
            
        Returns:
            Metrics dictionary
        """
        words = self.tokenize(text)
        
        f_words = sum(1 for w in words if w in self.function_words)
        has_verb = any(w in self.verbs for w in words)
        
        # Compute f-word positions
        f_word_positions = []
        for i, w in enumerate(words):
            if w in self.function_words:
                f_word_positions.append(i)
        
        return {
            'f_words': f_words,
            'has_verb': has_verb,
            'f_word_positions': f_word_positions,
            'total_words': len(words)
        }
    
    def predict_metrics_after_insertion(self, text: str, 
                                       anchor_configs: List[Dict]) -> Dict:
        """
        Predict metrics after token-boundary insertion.
        
        Args:
            text: Original text
            anchor_configs: List of {anchor, position} dicts
            
        Returns:
            Predicted metrics
        """
        # Apply insertions at token boundaries
        modified = text
        offset = 0
        
        # Sort by position
        sorted_configs = sorted(anchor_configs, key=lambda x: x['position'])
        
        for config in sorted_configs:
            anchor = config['anchor']
            target_pos = config['position'] + offset
            
            # Insert at token boundary
            modified, actual_pos = self.insert_at_token_boundary(
                modified, anchor, target_pos
            )
            
            # Update offset for next insertion
            offset = len(modified) - len(text)
        
        # Compute metrics
        metrics = self.compute_linguistic_metrics(modified)
        metrics['text'] = modified
        
        return metrics
    
    def compute_enhanced_cost(self, drop_predictions: List[float],
                            original_metrics: Dict,
                            predicted_metrics: Dict) -> float:
        """
        Compute enhanced Pareto cost with f-word retention.
        
        Args:
            drop_predictions: Predicted drops for each anchor
            original_metrics: Metrics before insertion
            predicted_metrics: Metrics after insertion
            
        Returns:
            Combined cost
        """
        # Drop component
        drop_sum = sum(drop_predictions)
        
        # F-word retention component
        f_word_loss = 0.0
        if original_metrics['f_words'] > 0:
            f_word_retention = predicted_metrics['f_words'] / original_metrics['f_words']
            f_word_loss = max(0, 1.0 - f_word_retention)
        
        # Verb preservation component  
        verb_loss = 0.0
        if original_metrics['has_verb'] and not predicted_metrics['has_verb']:
            verb_loss = 1.0
        
        # Combined cost
        cost = (self.alpha * drop_sum + 
               self.beta * f_word_loss + 
               self.gamma * verb_loss)
        
        return cost
    
    def beam_search_padding(self, text: str, anchor_configs: List[Dict],
                          beam_width: int = 3) -> str:
        """
        Use beam search to find optimal padding.
        
        Args:
            text: Text with anchors inserted
            anchor_configs: Anchor configurations
            beam_width: Beam width for search
            
        Returns:
            Text with optimal padding
        """
        # Start with base text
        beams = [(text, 0.0)]  # (text, score)
        
        # Try adding padding around each anchor
        for config in anchor_configs:
            anchor = config['anchor']
            new_beams = []
            
            for beam_text, beam_score in beams:
                # Try different padding options
                padding_options = [
                    '',  # No padding
                    'THE ',  # Common determiner
                    'AND ',  # Common connector
                    'TO ',   # Common preposition
                ]
                
                for pad in padding_options:
                    # Find anchor in text
                    idx = beam_text.find(anchor)
                    if idx >= 0:
                        # Try padding before
                        padded = beam_text[:idx] + pad + beam_text[idx:]
                        metrics = self.compute_linguistic_metrics(padded)
                        
                        # Score based on f-words and naturalness
                        score = metrics['f_words'] * 0.7 + (1.0 if metrics['has_verb'] else 0) * 0.3
                        new_beams.append((padded, beam_score + score))
            
            # Keep top beams
            new_beams.sort(key=lambda x: x[1], reverse=True)
            beams = new_beams[:beam_width]
        
        # Return best
        if beams:
            return beams[0][0]
        return text
    
    def find_optimal_placement(self, text: str, saliency_map: Dict,
                              drop_predictor) -> Dict:
        """
        Find optimal anchor placement with token awareness.
        
        Args:
            text: Head text
            saliency_map: Precomputed saliency map
            drop_predictor: Drop prediction model
            
        Returns:
            Optimal placement configuration
        """
        # Get original metrics
        original_metrics = self.compute_linguistic_metrics(text)
        
        # Get token boundaries
        boundaries = self.find_token_boundaries(text)
        words = self.tokenize(text)
        
        # Find verb positions to protect (with wider protection zone)
        verb_positions = []
        verb_tokens = []
        for i, word in enumerate(words):
            if word in self.verbs:
                if i < len(boundaries):
                    verb_positions.append(boundaries[i])
                    verb_tokens.append(i)
        
        # Generate candidate positions at token boundaries
        candidate_positions = []
        for i, (start, end) in enumerate(boundaries):
            # Skip if within ±2 tokens of any verb
            is_near_verb_token = any(abs(i - vt) <= 2 for vt in verb_tokens)
            
            # Skip if within ±15 chars of verb position
            is_near_verb_pos = any(abs(start - vp[0]) < 15 for vp in verb_positions)
            
            # Prefer positions after first 10 chars and before last 10
            if start > 10 and not is_near_verb_token and not is_near_verb_pos:
                candidate_positions.append(start)  # Before token
            if end < len(text) - 10 and not is_near_verb_token and not is_near_verb_pos:
                candidate_positions.append(end)  # After token
        
        # Remove duplicates and sort
        candidate_positions = sorted(list(set(candidate_positions)))
        
        # Ensure we have enough positions
        if len(candidate_positions) < 8:
            # Add more positions if needed
            text_len = len(text)
            for pos in [text_len // 4, text_len // 3, text_len // 2, 2 * text_len // 3]:
                if pos not in candidate_positions:
                    candidate_positions.append(pos)
            candidate_positions = sorted(candidate_positions)
        
        # Try different combinations
        best_config = None
        best_cost = float('inf')
        
        # Sample positions for each anchor
        max_candidates = min(12, len(candidate_positions))
        
        for east_idx in range(0, max_candidates, 2):
            east_pos = candidate_positions[east_idx]
            
            for ne_idx in range(east_idx + 2, min(east_idx + 10, max_candidates), 2):
                ne_pos = candidate_positions[ne_idx]
                
                for berlin_idx in range(ne_idx + 2, min(ne_idx + 10, max_candidates), 2):
                    berlin_pos = candidate_positions[berlin_idx]
                    
                    for clock_idx in range(berlin_idx + 2, min(berlin_idx + 10, max_candidates), 2):
                        if clock_idx < len(candidate_positions):
                            clock_pos = candidate_positions[clock_idx]
                            
                            # Create configuration
                            anchor_configs = [
                                {'anchor': 'EAST', 'position': east_pos},
                                {'anchor': 'NORTHEAST', 'position': ne_pos},
                                {'anchor': 'BERLIN', 'position': berlin_pos},
                                {'anchor': 'CLOCK', 'position': clock_pos}
                            ]
                            
                            # Predict metrics
                            predicted_metrics = self.predict_metrics_after_insertion(
                                text, anchor_configs
                            )
                            
                            # Compute drops
                            drops = []
                            for config in anchor_configs:
                                drop = drop_predictor.predict_drop(
                                    text, config['position'], saliency_map
                                )
                                drops.append(drop)
                            
                            # Compute cost
                            cost = self.compute_enhanced_cost(
                                drops, original_metrics, predicted_metrics
                            )
                            
                            if cost < best_cost:
                                best_cost = cost
                                best_config = {
                                    'configs': anchor_configs,
                                    'drops': drops,
                                    'metrics': predicted_metrics,
                                    'cost': cost
                                }
        
        # Fallback if no good config found
        if best_config is None:
            # Use evenly spaced positions
            text_len = len(text)
            anchor_configs = [
                {'anchor': 'EAST', 'position': text_len // 5},
                {'anchor': 'NORTHEAST', 'position': 2 * text_len // 5},
                {'anchor': 'BERLIN', 'position': 3 * text_len // 5},
                {'anchor': 'CLOCK', 'position': 4 * text_len // 5}
            ]
            
            predicted_metrics = self.predict_metrics_after_insertion(text, anchor_configs)
            
            best_config = {
                'configs': anchor_configs,
                'drops': [0.2, 0.2, 0.2, 0.2],
                'metrics': predicted_metrics,
                'cost': 0.8
            }
        
        return best_config
    
    def place_anchors_with_padding(self, text: str, optimal_config: Dict) -> str:
        """
        Place anchors with grammar-aware padding.
        
        Args:
            text: Original text
            optimal_config: Optimal placement configuration
            
        Returns:
            Text with anchors and padding
        """
        # Insert anchors at token boundaries
        modified = text
        offset = 0
        
        # Sort by position
        sorted_configs = sorted(optimal_config['configs'], key=lambda x: x['position'])
        
        for config in sorted_configs:
            anchor = config['anchor']
            target_pos = config['position'] + offset
            
            # Insert at token boundary
            modified, actual_pos = self.insert_at_token_boundary(
                modified, anchor, target_pos
            )
            
            # Update offset
            offset = len(modified) - len(text)
        
        # Apply beam search padding
        padded = self.beam_search_padding(modified, sorted_configs)
        
        return padded


class EnhancedNeutralRepairer:
    """
    Enhanced neutral repair with verb recovery moves.
    """
    
    def __init__(self, repair_budget: int = 30):
        """
        Initialize enhanced repairer.
        
        Args:
            repair_budget: Max moves per anchor (up to 6 per head)
        """
        self.repair_budget = min(repair_budget, 6)  # Cap at 6 moves per head
        
        # Core verbs for recovery
        self.recovery_verbs = ['READ', 'SEE', 'NOTE']
        
        # All verbs for counting
        self.all_verbs = [
            'SET', 'READ', 'SEE', 'NOTE', 'SIGHT', 'OBSERVE',
            'FIND', 'APPLY', 'CORRECT', 'REDUCE', 'ALIGN',
            'BRING', 'MARK', 'TRACE', 'FOLLOW', 'CHECK',
            'TURN', 'MOVE', 'WAIT', 'STOP', 'START', 'BEGIN'
        ]
        
        # Expanded neutral moves
        self.neutral_swaps = [
            ('AND', 'THEN'),
            ('THEN', 'AND'),
            ('THAT', 'WHICH'),
            ('WHICH', 'THAT'),
            ('THE', 'A'),
            ('A', 'THE'),
            ('IS', 'ARE'),
            ('ARE', 'IS'),
            ('WAS', 'WERE'),
            ('WERE', 'WAS'),
            ('HAS', 'HAVE'),
            ('HAVE', 'HAS')
        ]
        
        self.neutral_insertions = [
            'THE', 'A', 'AND', 'OF', 'TO', 'IN', 'FOR', 'WITH'
        ]
        
        self.neutral_deletions = [
            'VERY', 'QUITE', 'REALLY', 'JUST', 'ONLY'
        ]
        
        # Vacuous tokens that can be replaced with verbs
        self.vacuous_tokens = ['SO', 'ALL', 'ITS', 'VERY', 'JUST']
    
    def find_repair_positions(self, text: str, anchor_texts: List[str]) -> List[int]:
        """
        Find positions for repair near anchors.
        
        Args:
            text: Text with anchors
            anchor_texts: List of anchor strings
            
        Returns:
            List of word positions for repair
        """
        words = text.split()
        repair_positions = set()
        
        # Find positions near each anchor
        for anchor in anchor_texts:
            # Find anchor in word list
            for i, word in enumerate(words):
                if anchor in word:
                    # Add positions within ±3 words
                    for offset in range(-3, 4):
                        pos = i + offset
                        if 0 <= pos < len(words):
                            repair_positions.add(pos)
        
        return sorted(repair_positions)
    
    def apply_swap(self, words: List[str], position: int) -> Optional[List[str]]:
        """
        Apply neutral swap at position.
        
        Args:
            words: Word list
            position: Position to swap
            
        Returns:
            Modified words or None
        """
        if position >= len(words):
            return None
        
        for old, new in self.neutral_swaps:
            if words[position] == old:
                modified = words.copy()
                modified[position] = new
                return modified
        
        return None
    
    def apply_insertion(self, words: List[str], position: int) -> Optional[List[str]]:
        """
        Apply neutral insertion at position.
        
        Args:
            words: Word list
            position: Position to insert
            
        Returns:
            Modified words or None
        """
        if position > len(words):
            return None
        
        # Don't insert if already has too many function words nearby
        nearby_count = 0
        for i in range(max(0, position - 2), min(len(words), position + 2)):
            if i < len(words) and words[i] in self.neutral_insertions:
                nearby_count += 1
        
        if nearby_count >= 2:
            return None
        
        # Choose appropriate insertion based on context
        if position > 0 and position < len(words):
            prev_word = words[position - 1] if position > 0 else ''
            next_word = words[position] if position < len(words) else ''
            
            # Don't insert THE before THE
            if next_word == 'THE':
                return None
                
            # Smart insertion choice
            if prev_word in ['SET', 'READ', 'FIND']:
                insert_word = 'THE'
            elif prev_word in ['THE', 'A']:
                return None  # Don't double articles
            else:
                import random
                random.seed(position)  # Deterministic choice
                insert_word = random.choice(self.neutral_insertions[:3])
        else:
            return None
        
        modified = words[:position] + [insert_word] + words[position:]
        return modified
    
    def count_verbs(self, text: str) -> int:
        """Count verbs in text."""
        words = text.split()
        verb_count = 0
        for word in words:
            if word in self.all_verbs:
                verb_count += 1
        return verb_count
    
    def apply_verb_recovery(self, words: List[str], position: int) -> Optional[List[str]]:
        """
        Apply verb recovery move.
        
        Args:
            words: Word list
            position: Position for recovery
            
        Returns:
            Modified words or None
        """
        if position > len(words):
            return None
        
        # Strategy 1: Insert verb after connector
        if position > 0 and words[position - 1] in ['THEN', 'AND']:
            # Insert recovery verb
            import random
            random.seed(position)
            verb = random.choice(self.recovery_verbs)
            modified = words[:position] + [verb] + words[position:]
            return modified
        
        # Strategy 2: Replace vacuous token with verb
        if position < len(words) and words[position] in self.vacuous_tokens:
            import random
            random.seed(position)
            verb = random.choice(self.recovery_verbs)
            modified = words.copy()
            modified[position] = verb
            return modified
        
        # Strategy 3: Insert connector + verb
        if position < len(words) - 1:
            # Check if good position for "THEN READ" pattern
            import random
            random.seed(position)
            verb = random.choice(self.recovery_verbs)
            modified = words[:position] + ['THEN', verb] + words[position:]
            return modified
        
        return None
    
    def apply_deletion(self, words: List[str], position: int) -> Optional[List[str]]:
        """
        Apply neutral deletion at position.
        
        Args:
            words: Word list
            position: Position to delete
            
        Returns:
            Modified words or None
        """
        if position >= len(words):
            return None
        
        # Check if word can be deleted
        if words[position] in self.neutral_deletions:
            modified = words[:position] + words[position + 1:]
            return modified
        
        return None
    
    def repair(self, original_text: str, anchored_text: str,
              anchor_texts: List[str], scorer) -> Dict:
        """
        Apply enhanced neutral repairs.
        
        Args:
            original_text: Text before anchors
            anchored_text: Text with anchors
            anchor_texts: List of anchor strings
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
        repair_positions = self.find_repair_positions(anchored_text, anchor_texts)
        
        for iteration in range(self.repair_budget):
            if moves_made >= self.repair_budget:
                break
            
            words = current_text.split()
            best_repair = None
            best_score = current_score
            
            # Check if we need verb recovery
            verb_count = self.count_verbs(current_text)
            need_verb_recovery = verb_count < 2
            
            # Try different repair types at each position
            for pos in repair_positions:
                # Prioritize verb recovery if needed
                if need_verb_recovery:
                    # Try verb recovery first
                    verb_recovered = self.apply_verb_recovery(words, pos)
                    if verb_recovered:
                        repaired_text = ' '.join(verb_recovered)
                        repaired_score = scorer(repaired_text)
                        if repaired_score > best_score:
                            best_repair = {
                                'text': repaired_text,
                                'position': pos,
                                'type': 'verb_recovery',
                                'score': repaired_score
                            }
                            best_score = repaired_score
                # Try swap
                swapped = self.apply_swap(words, pos)
                if swapped:
                    repaired_text = ' '.join(swapped)
                    repaired_score = scorer(repaired_text)
                    if repaired_score > best_score:
                        best_repair = {
                            'text': repaired_text,
                            'position': pos,
                            'type': 'swap',
                            'score': repaired_score
                        }
                        best_score = repaired_score
                
                # Try insertion
                inserted = self.apply_insertion(words, pos)
                if inserted:
                    repaired_text = ' '.join(inserted)
                    repaired_score = scorer(repaired_text)
                    if repaired_score > best_score:
                        best_repair = {
                            'text': repaired_text,
                            'position': pos,
                            'type': 'insert',
                            'score': repaired_score
                        }
                        best_score = repaired_score
                
                # Try deletion
                deleted = self.apply_deletion(words, pos)
                if deleted:
                    repaired_text = ' '.join(deleted)
                    repaired_score = scorer(repaired_text)
                    if repaired_score > best_score:
                        best_repair = {
                            'text': repaired_text,
                            'position': pos,
                            'type': 'delete',
                            'score': repaired_score
                        }
                        best_score = repaired_score
            
            if best_repair:
                current_text = best_repair['text']
                current_score = best_repair['score']
                moves_made += 1
                
                recovery = 0.0
                if initial_drop > 0:
                    recovery = (current_score - scorer(anchored_text)) / initial_drop
                
                repair_trace.append({
                    'move': moves_made,
                    'position': best_repair['position'],
                    'type': best_repair['type'],
                    'score': current_score,
                    'recovery': recovery
                })
                
                # Check if recovered enough
                if recovery >= 0.5:  # Lower threshold for better recovery
                    break
            else:
                # No improvement possible
                break
        
        final_recovery = 0.0
        if initial_drop > 0:
            final_recovery = (current_score - scorer(anchored_text)) / initial_drop
        
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
    """Test improved placement and repair."""
    
    # Load test data
    import sys
    sys.path.append(str(Path(__file__).parent))
    from saliency_map import SaliencyMapper, DropPredictor
    
    # Example text
    text = "SET THE COURSE TRUE AND READ THE SIGN WHERE THE PATH LEADS TO MORE"
    
    print(f"Original text: {text}")
    
    # Compute saliency
    mapper = SaliencyMapper()
    saliency_map = mapper.generate_saliency_map(text)
    
    # Initialize drop predictor
    predictor = DropPredictor()
    
    # Initialize improved placer
    placer = ImprovedAnchorPlacer(alpha=0.7, beta=0.3, gamma=0.15)
    
    # Get original metrics
    original_metrics = placer.compute_linguistic_metrics(text)
    print(f"\nOriginal metrics:")
    print(f"  F-words: {original_metrics['f_words']}")
    print(f"  Has verb: {original_metrics['has_verb']}")
    
    # Find optimal placement
    print("\nFinding optimal anchor placement...")
    optimal = placer.find_optimal_placement(text, saliency_map, predictor)
    
    print(f"\nOptimal configuration:")
    for config in optimal['configs']:
        print(f"  {config['anchor']}: position {config['position']}")
    print(f"  Predicted drops: {[f'{d:.3f}' for d in optimal['drops']]}")
    print(f"  Total drop: {sum(optimal['drops']):.3f}")
    print(f"  Cost: {optimal['cost']:.3f}")
    
    # Place anchors with padding
    anchored_text = placer.place_anchors_with_padding(text, optimal)
    print(f"\nAnchored text: {anchored_text}")
    
    # Check metrics after insertion
    anchored_metrics = placer.compute_linguistic_metrics(anchored_text)
    print(f"\nAnchored metrics:")
    print(f"  F-words: {anchored_metrics['f_words']}")
    print(f"  Has verb: {anchored_metrics['has_verb']}")
    
    # Apply enhanced repair
    repairer = EnhancedNeutralRepairer(repair_budget=30)
    
    # Simple scorer for testing
    def scorer(t):
        return mapper.compute_base_score(t)
    
    repair_result = repairer.repair(
        text, anchored_text, 
        ['EAST', 'NORTHEAST', 'BERLIN', 'CLOCK'],
        scorer
    )
    
    print(f"\nRepair results:")
    print(f"  Original score: {repair_result['original_score']:.3f}")
    print(f"  Anchored score: {repair_result['anchored_score']:.3f}")
    print(f"  Repaired score: {repair_result['repaired_score']:.3f}")
    print(f"  Recovery: {repair_result['final_recovery']*100:.1f}%")
    print(f"  Moves made: {repair_result['moves_made']}")
    
    print(f"\nFinal text: {repair_result['repaired_text']}")
    
    # Final metrics
    final_metrics = placer.compute_linguistic_metrics(repair_result['repaired_text'])
    print(f"\nFinal metrics:")
    print(f"  F-words: {final_metrics['f_words']}")
    print(f"  Has verb: {final_metrics['has_verb']}")
    
    # Save results
    output_dir = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/experiments/pipeline_v4/runs/track_a_l")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "improved_placement_test.json", 'w') as f:
        json.dump({
            'original': text,
            'original_metrics': original_metrics,
            'optimal_placement': {
                'configs': optimal['configs'],
                'drops': optimal['drops'],
                'cost': optimal['cost']
            },
            'anchored': anchored_text,
            'anchored_metrics': anchored_metrics,
            'repair': repair_result,
            'final_metrics': final_metrics
        }, f, indent=2)
    
    print(f"\nResults saved to {output_dir / 'improved_placement_test.json'}")


if __name__ == "__main__":
    main()