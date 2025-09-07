#!/usr/bin/env python3
"""
Saliency mapping for understanding position importance.
Computes token-level contributions to blinded trigram score.
"""

import json
import numpy as np
from typing import List, Dict, Tuple
from pathlib import Path

class SaliencyMapper:
    """
    Compute saliency maps showing token importance.
    """
    
    def __init__(self):
        """Initialize saliency mapper."""
        self.function_words = {
            'THE', 'A', 'AN', 'IS', 'ARE', 'WAS', 'BE', 'TO', 'OF', 'AND',
            'IN', 'FOR', 'ON', 'WITH', 'AS', 'BY', 'AT', 'FROM', 'BUT', 'OR',
            'IF', 'THEN', 'SO', 'ALL', 'WOULD', 'THERE', 'THEIR', 'WHAT'
        }
        
        self.narrative_tokens = {
            'EAST', 'NORTHEAST', 'NORTHWEST', 'SOUTHEAST', 'SOUTHWEST',
            'NORTH', 'SOUTH', 'WEST', 'BERLIN', 'CLOCK', 'ANGLE', 'JOY'
        }
    
    def compute_base_score(self, text: str, blinded: bool = True) -> float:
        """
        Compute base trigram score.
        
        Args:
            text: Input text
            blinded: Whether to mask narrative tokens
            
        Returns:
            Base score
        """
        if blinded:
            for token in self.narrative_tokens:
                text = text.replace(token, 'XXX')
        
        words = text.split()
        
        # Simple trigram scoring
        score = 0.0
        for i in range(len(words) - 2):
            trigram = (words[i], words[i+1], words[i+2])
            
            # Reward common patterns
            if trigram[0] in self.function_words and trigram[2] in self.function_words:
                score += 1.0
            if trigram[1] not in self.narrative_tokens:
                score += 0.5
        
        return score
    
    def compute_leave_one_out(self, text: str) -> List[float]:
        """
        Compute leave-one-out saliency.
        
        Args:
            text: Input text
            
        Returns:
            List of saliency scores per position
        """
        words = text.split()
        base_score = self.compute_base_score(text)
        
        saliency = []
        
        for i in range(len(words)):
            # Create text with word i removed
            modified = words[:i] + words[i+1:]
            modified_text = ' '.join(modified)
            
            # Compute score difference
            modified_score = self.compute_base_score(modified_text)
            importance = base_score - modified_score
            
            saliency.append(importance)
        
        return saliency
    
    def compute_char_level_saliency(self, text: str) -> List[float]:
        """
        Map word-level saliency to character positions.
        
        Args:
            text: Input text
            
        Returns:
            Character-level saliency scores
        """
        words = text.split()
        word_saliency = self.compute_leave_one_out(text)
        
        char_saliency = []
        word_idx = 0
        in_word = False
        
        for char in text:
            if char == ' ':
                char_saliency.append(0.0)  # Spaces have no saliency
                in_word = False
            else:
                if not in_word:
                    in_word = True
                    if word_idx < len(word_saliency):
                        current_saliency = word_saliency[word_idx]
                    else:
                        current_saliency = 0.0
                char_saliency.append(current_saliency)
                
                # Check if end of word
                next_idx = len(char_saliency)
                if next_idx < len(text) and text[next_idx] == ' ':
                    word_idx += 1
        
        return char_saliency
    
    def find_low_saliency_windows(self, saliency: List[float], 
                                 window_size: int = 10) -> List[Tuple[int, int]]:
        """
        Find windows with low average saliency.
        
        Args:
            saliency: Character-level saliency scores
            window_size: Size of window to consider
            
        Returns:
            List of (start, end) positions for low-saliency windows
        """
        if len(saliency) < window_size:
            return [(0, len(saliency))]
        
        # Compute windowed averages
        windows = []
        for i in range(len(saliency) - window_size + 1):
            window_avg = sum(saliency[i:i+window_size]) / window_size
            windows.append((i, i + window_size, window_avg))
        
        # Sort by saliency
        windows.sort(key=lambda x: x[2])
        
        # Return top low-saliency windows
        return [(w[0], w[1]) for w in windows[:5]]
    
    def generate_saliency_map(self, text: str) -> Dict:
        """
        Generate comprehensive saliency map.
        
        Args:
            text: Input text
            
        Returns:
            Saliency map dictionary
        """
        words = text.split()
        word_saliency = self.compute_leave_one_out(text)
        char_saliency = self.compute_char_level_saliency(text)
        low_windows = self.find_low_saliency_windows(char_saliency)
        
        # Normalize saliency scores
        if max(char_saliency) > 0:
            char_saliency_norm = [s / max(char_saliency) for s in char_saliency]
        else:
            char_saliency_norm = char_saliency
        
        # Find best anchor positions (lowest saliency)
        anchor_positions = []
        for window in low_windows:
            mid = (window[0] + window[1]) // 2
            anchor_positions.append({
                'position': mid,
                'window': window,
                'avg_saliency': sum(char_saliency[window[0]:window[1]]) / (window[1] - window[0])
            })
        
        return {
            'text': text,
            'base_score': self.compute_base_score(text),
            'word_saliency': word_saliency,
            'char_saliency': char_saliency_norm,
            'low_saliency_windows': low_windows,
            'suggested_anchor_positions': anchor_positions,
            'stats': {
                'mean_saliency': np.mean(char_saliency),
                'std_saliency': np.std(char_saliency),
                'min_saliency': min(char_saliency),
                'max_saliency': max(char_saliency)
            }
        }


class DropPredictor:
    """
    Predict score drop when inserting anchors.
    """
    
    def __init__(self, seed: int = 1338):
        """Initialize drop predictor."""
        np.random.seed(seed)
        
        # Simple linear model weights (would be trained in real implementation)
        self.weights = {
            'position_normalized': -0.2,  # Position in text (0 to 1)
            'local_saliency_mean': 0.8,   # Mean saliency in ±2 window
            'local_saliency_std': 0.3,    # Std saliency in ±2 window
            'is_function_word': -0.1,     # Whether replacing function word
            'bigram_disruption': 0.5,     # Whether breaking common bigram
            'bias': 0.1
        }
    
    def extract_features(self, text: str, position: int, 
                        saliency_map: Dict) -> np.ndarray:
        """
        Extract features for drop prediction.
        
        Args:
            text: Head text
            position: Insertion position
            saliency_map: Precomputed saliency map
            
        Returns:
            Feature vector
        """
        char_saliency = saliency_map['char_saliency']
        
        # Position feature
        pos_norm = position / len(text)
        
        # Local saliency window
        window_start = max(0, position - 2)
        window_end = min(len(char_saliency), position + 3)
        local_saliency = char_saliency[window_start:window_end]
        
        if local_saliency:
            local_mean = np.mean(local_saliency)
            local_std = np.std(local_saliency)
        else:
            local_mean = 0.0
            local_std = 0.0
        
        # Token class features
        words = text.split()
        char_count = 0
        word_at_pos = None
        for word in words:
            if char_count <= position < char_count + len(word):
                word_at_pos = word
                break
            char_count += len(word) + 1  # +1 for space
        
        is_fw = 1.0 if word_at_pos in {'THE', 'A', 'AN', 'TO', 'OF'} else 0.0
        
        # Bigram disruption (simplified)
        bigram_disruption = 0.5 if position > 5 and position < len(text) - 5 else 0.0
        
        features = np.array([
            pos_norm,
            local_mean,
            local_std,
            is_fw,
            bigram_disruption,
            1.0  # Bias term
        ])
        
        return features
    
    def predict_drop(self, text: str, position: int, 
                     saliency_map: Dict) -> float:
        """
        Predict score drop for anchor insertion.
        
        Args:
            text: Head text
            position: Insertion position
            saliency_map: Precomputed saliency map
            
        Returns:
            Predicted drop (0 to 1)
        """
        features = self.extract_features(text, position, saliency_map)
        
        # Linear model prediction
        drop = 0.0
        weight_names = ['position_normalized', 'local_saliency_mean', 
                       'local_saliency_std', 'is_function_word',
                       'bigram_disruption', 'bias']
        
        for i, name in enumerate(weight_names):
            drop += self.weights[name] * features[i]
        
        # Sigmoid to bound between 0 and 1
        drop = 1.0 / (1.0 + np.exp(-drop))
        
        return drop
    
    def predict_multi_anchor_drop(self, text: str, positions: List[int],
                                 saliency_map: Dict) -> Dict:
        """
        Predict cumulative drop for multiple anchors.
        
        Args:
            text: Head text
            positions: List of insertion positions
            saliency_map: Precomputed saliency map
            
        Returns:
            Drop prediction results
        """
        individual_drops = []
        
        for pos in positions:
            drop = self.predict_drop(text, pos, saliency_map)
            individual_drops.append(drop)
        
        # Cumulative drop (not just sum - interactions matter)
        cumulative = 1.0 - np.prod([1.0 - d for d in individual_drops])
        
        return {
            'positions': positions,
            'individual_drops': individual_drops,
            'cumulative_drop': cumulative,
            'expected_retention': 1.0 - cumulative
        }
    
    def save_model(self, path: Path):
        """Save model weights."""
        with open(path, 'w') as f:
            json.dump(self.weights, f, indent=2)
    
    def load_model(self, path: Path):
        """Load model weights."""
        with open(path, 'r') as f:
            self.weights = json.load(f)


def main():
    """Test saliency mapping and drop prediction."""
    
    # Example text
    text = "SET THE COURSE TRUE AND READ THE SIGN WHERE THE PATH LEADS"
    
    # Compute saliency
    mapper = SaliencyMapper()
    saliency_map = mapper.generate_saliency_map(text)
    
    print("Saliency Map:")
    print(f"  Text: {text}")
    print(f"  Base score: {saliency_map['base_score']:.3f}")
    print(f"  Low saliency windows: {saliency_map['low_saliency_windows']}")
    print(f"  Suggested positions: {[p['position'] for p in saliency_map['suggested_anchor_positions']]}")
    
    # Test drop predictor
    predictor = DropPredictor()
    
    # Test positions for anchors
    test_positions = [10, 25, 40]
    drop_result = predictor.predict_multi_anchor_drop(text, test_positions, saliency_map)
    
    print(f"\nDrop Predictions:")
    print(f"  Positions: {drop_result['positions']}")
    print(f"  Individual drops: {[f'{d:.3f}' for d in drop_result['individual_drops']]}")
    print(f"  Cumulative drop: {drop_result['cumulative_drop']:.3f}")
    print(f"  Expected retention: {drop_result['expected_retention']:.3f}")
    
    # Save model
    model_path = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/experiments/pipeline_v4/runs/track_a_l/drop_model.json")
    predictor.save_model(model_path)
    print(f"\nModel saved to {model_path}")


if __name__ == "__main__":
    main()