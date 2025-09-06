#!/usr/bin/env python3
"""
Common scoring module for v3 generation tracks.
Inherits from v2 pipeline with focus on n-gram quality.
"""

import sys
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple

# Add v2 pipeline to path
sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline_v2"))
from scripts.explore.run_family import ExplorePipeline
from scripts.explore.anchor_score import score_anchors


class V3ScoringPipeline(ExplorePipeline):
    """
    Enhanced scoring pipeline for v3 with generation quality focus.
    """
    
    def __init__(self, seed: int = 1337):
        super().__init__(seed)
        
        # Load trigram model
        model_path = Path(__file__).parent / "trigram_model.json"
        with open(model_path, 'r') as f:
            self.trigram_model = json.load(f)
    
    def score_generation_quality(self, text: str) -> Dict:
        """
        Score generation quality before blinding.
        Focus on n-gram coherence that will survive blinding.
        
        Returns:
            Dictionary with generation quality metrics
        """
        # Clean text
        clean = ''.join(c if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' else '' for c in text.upper())
        
        # Trigram score
        trigram_score = self._score_trigram(clean)
        
        # Bigram entropy
        bigram_entropy = self._compute_bigram_entropy(clean)
        
        # Character distribution
        char_dist = self._compute_char_distribution(clean)
        
        # Repetition penalty
        repetition = self._compute_repetition(clean)
        
        return {
            'trigram_score': trigram_score,
            'bigram_entropy': bigram_entropy,
            'char_distribution': char_dist,
            'repetition_penalty': repetition,
            'quality_score': trigram_score * (1 - repetition) * bigram_entropy
        }
    
    def _score_trigram(self, text: str) -> float:
        """Score text using trigram model."""
        if len(text) < 3:
            return 0.0
        
        score = 0.0
        smoothing = 1e-6
        
        for i in range(2, len(text)):
            trigram = text[i-2:i+1]
            prefix = trigram[:2]
            char = trigram[2]
            
            # Get probability from model
            if prefix in self.trigram_model['trigram_probs']:
                if char in self.trigram_model['trigram_probs'][prefix]:
                    prob = self.trigram_model['trigram_probs'][prefix][char]
                else:
                    prob = smoothing
            else:
                # Fallback to bigram
                if prefix[1] in self.trigram_model['bigram_probs']:
                    if char in self.trigram_model['bigram_probs'][prefix[1]]:
                        prob = self.trigram_model['bigram_probs'][prefix[1]][char] * 0.1
                    else:
                        prob = smoothing
                else:
                    prob = smoothing
            
            score += max(-10, min(0, -abs(prob)))
        
        return score / max(1, len(text) - 2)
    
    def _compute_bigram_entropy(self, text: str) -> float:
        """Compute bigram entropy."""
        if len(text) < 2:
            return 0.0
        
        bigrams = {}
        for i in range(len(text) - 1):
            bigram = text[i:i+2]
            bigrams[bigram] = bigrams.get(bigram, 0) + 1
        
        total = sum(bigrams.values())
        entropy = 0.0
        for count in bigrams.values():
            p = count / total
            if p > 0:
                entropy -= p * (p if p > 0 else 0)
        
        # Normalize to [0, 1]
        max_entropy = min(len(text) - 1, 26 * 26)
        return min(1.0, entropy / max(1, max_entropy ** 0.5))
    
    def _compute_char_distribution(self, text: str) -> float:
        """Score character distribution against English."""
        english_freq = {
            'E': 0.127, 'T': 0.091, 'A': 0.082, 'O': 0.075, 'I': 0.070,
            'N': 0.067, 'S': 0.063, 'H': 0.061, 'R': 0.060, 'D': 0.043,
            'L': 0.040, 'C': 0.028, 'U': 0.028, 'M': 0.024, 'W': 0.024,
            'F': 0.022, 'G': 0.020, 'Y': 0.020, 'P': 0.019, 'B': 0.015,
            'V': 0.010, 'K': 0.008, 'J': 0.002, 'X': 0.002, 'Q': 0.001,
            'Z': 0.001
        }
        
        char_counts = {}
        for c in text:
            if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                char_counts[c] = char_counts.get(c, 0) + 1
        
        total = sum(char_counts.values())
        if total == 0:
            return 0.0
        
        score = 0.0
        for char, expected_freq in english_freq.items():
            actual_freq = char_counts.get(char, 0) / total
            score += abs(actual_freq - expected_freq)
        
        # Convert to similarity score [0, 1]
        return max(0, 1 - score / 2)
    
    def _compute_repetition(self, text: str) -> float:
        """Compute repetition penalty."""
        if len(text) < 4:
            return 0.0
        
        # Check for repeated patterns
        repetitions = 0
        for length in [2, 3, 4]:
            for i in range(len(text) - length * 2):
                pattern = text[i:i+length]
                if text[i+length:i+length*2] == pattern:
                    repetitions += 1
        
        # Normalize
        max_repetitions = len(text) // 2
        return min(1.0, repetitions / max(1, max_repetitions))
    
    def score_v3(self, text: str, policy: Dict = None) -> Dict:
        """
        Enhanced v3 scoring with generation quality metrics.
        
        Returns:
            Full scoring dictionary with v3 enhancements
        """
        if policy is None:
            policy = {"name": "fixed", "window_radius": 0, "typo_budget": 0}
        
        # Get generation quality BEFORE blinding
        gen_quality = self.score_generation_quality(text)
        
        # Run standard v2 scoring (anchors before blinding)
        v2_result = self.compute_score_v2(text, policy)
        
        # Add v3 metrics
        v2_result['generation_quality'] = gen_quality
        v2_result['v3_composite'] = (
            v2_result['score_norm'] * 0.5 +  # Original score
            gen_quality['quality_score'] * 0.5  # Generation quality
        )
        
        return v2_result
    
    def run_v3_evaluation(self, heads: List[Dict], campaign_id: str) -> Dict:
        """
        Run full v3 evaluation on generated heads.
        
        Args:
            heads: List of head dictionaries with 'text' and 'label'
            campaign_id: Campaign identifier
            
        Returns:
            Evaluation results with promotions
        """
        results = {
            'campaign': campaign_id,
            'total_heads': len(heads),
            'evaluations': [],
            'promotions': [],
            'statistics': {}
        }
        
        policies = [
            {"name": "fixed", "window_radius": 0, "typo_budget": 0},
            {"name": "windowed_r2", "window_radius": 2, "typo_budget": 0},
            {"name": "shuffled", "window_radius": 100, "typo_budget": 2}
        ]
        
        for head in heads:
            # Run through all policies
            eval_result = self.run_anchor_modes(head['text'], policies)
            
            # Add v3 scoring
            v3_score = self.score_v3(head['text'])
            eval_result['v3_metrics'] = {
                'generation_quality': v3_score['generation_quality'],
                'v3_composite': v3_score['v3_composite']
            }
            
            eval_result['label'] = head['label']
            results['evaluations'].append(eval_result)
            
            # Check for promotion
            if eval_result['pass_deltas']:
                results['promotions'].append({
                    'label': head['label'],
                    'text': head['text'],
                    'deltas': {
                        'windowed': float(eval_result['delta_vs_windowed']),
                        'shuffled': float(eval_result['delta_vs_shuffled'])
                    },
                    'v3_metrics': eval_result['v3_metrics']
                })
        
        # Compute statistics
        if results['evaluations']:
            results['statistics'] = {
                'promotion_rate': float(len(results['promotions']) / len(heads)),
                'avg_delta_windowed': float(sum(e['delta_vs_windowed'] for e in results['evaluations']) / len(heads)),
                'avg_delta_shuffled': float(sum(e['delta_vs_shuffled'] for e in results['evaluations']) / len(heads)),
                'avg_generation_quality': float(sum(
                    e['v3_metrics']['generation_quality']['quality_score'] 
                    for e in results['evaluations']
                ) / len(heads))
            }
        
        return results


def test_scoring():
    """Test the v3 scoring pipeline."""
    pipeline = V3ScoringPipeline(seed=1337)
    
    # Test texts
    test_heads = [
        {"label": "good", "text": "THEQUICKBROWNFOXJUMPSEASTNORTHEASTOVERTHELAZYBERLINCLOCKDOG"},
        {"label": "random", "text": "XYZQWRTYPLKJHGFDSAEASTSNORTHEASTBERLINCLOCKADFG"},
        {"label": "repeat", "text": "ABCABCABCABCABCEASTEASTNORTHEASTBERLINCLOCKXYZXYZ"}
    ]
    
    print("Testing V3 Scoring Pipeline")
    print("=" * 60)
    
    for head in test_heads:
        result = pipeline.score_v3(head['text'])
        print(f"\n{head['label']}:")
        print(f"  Generation quality: {result['generation_quality']['quality_score']:.4f}")
        print(f"  V3 composite: {result['v3_composite']:.4f}")
        print(f"  Original score: {result['score_norm']:.4f}")


if __name__ == "__main__":
    test_scoring()