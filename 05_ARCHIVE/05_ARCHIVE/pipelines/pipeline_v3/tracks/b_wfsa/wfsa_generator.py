#!/usr/bin/env python3
"""
Track B: WFSA/PCFG Synthesizer
Weighted finite-state automaton with corridor constraints.
"""

import json
import random
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import numpy as np

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from common_scoring import V3ScoringPipeline


class WFSAGenerator:
    """
    Weighted Finite-State Automaton generator.
    Builds structured text with language coherence.
    """
    
    def __init__(self, seed: int = 1337):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        # Load trigram model
        model_path = Path(__file__).parent.parent.parent / "trigram_model.json"
        with open(model_path, 'r') as f:
            self.trigram_model = json.load(f)
        
        # Initialize scoring pipeline
        self.scorer = V3ScoringPipeline(seed)
        
        # Anchor positions and texts
        self.anchors = {
            "EAST": (21, 25),
            "NORTHEAST": (25, 34), 
            "BERLINCLOCK": (63, 74)
        }
        
        # Build transition weights
        self._build_transition_weights()
    
    def _build_transition_weights(self):
        """
        Build weighted transition table from trigram model.
        """
        self.transitions = {}
        
        # Trigram transitions
        for prefix, suffixes in self.trigram_model['trigram_probs'].items():
            self.transitions[prefix] = suffixes
        
        # Bigram fallback
        self.bigram_transitions = {}
        for prefix, suffixes in self.trigram_model['bigram_probs'].items():
            self.bigram_transitions[prefix] = suffixes
        
        # Unigram fallback
        self.unigram_weights = self.trigram_model['unigram_probs']
    
    def generate_segment(self, length: int, start_context: str = "") -> str:
        """
        Generate a text segment using WFSA transitions.
        
        Args:
            length: Length of segment to generate
            start_context: Initial context (last 2 chars)
            
        Returns:
            Generated segment
        """
        result = []
        context = start_context[-2:] if len(start_context) >= 2 else start_context
        
        for _ in range(length):
            # Get next character based on context
            next_char = self._sample_next_char(context)
            result.append(next_char)
            
            # Update context
            context = (context + next_char)[-2:]
        
        return ''.join(result)
    
    def _sample_next_char(self, context: str) -> str:
        """
        Sample next character based on context.
        """
        # Try trigram
        if len(context) == 2 and context in self.transitions:
            weights = self.transitions[context]
            if weights:
                chars = list(weights.keys())
                probs = list(weights.values())
                # Filter to letters
                valid = [(c, p) for c, p in zip(chars, probs) if c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
                if valid:
                    chars, probs = zip(*valid)
                    return random.choices(chars, weights=probs)[0]
        
        # Try bigram
        if len(context) >= 1 and context[-1] in self.bigram_transitions:
            weights = self.bigram_transitions[context[-1]]
            if weights:
                chars = list(weights.keys())
                probs = list(weights.values())
                valid = [(c, p) for c, p in zip(chars, probs) if c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
                if valid:
                    chars, probs = zip(*valid)
                    return random.choices(chars, weights=probs)[0]
        
        # Fallback to unigram
        if self.unigram_weights:
            chars = list(self.unigram_weights.keys())
            probs = list(self.unigram_weights.values())
            valid = [(c, p) for c, p in zip(chars, probs) if c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
            if valid:
                chars, probs = zip(*valid)
                return random.choices(chars, weights=probs)[0]
        
        # Ultimate fallback
        return random.choice("ETAOINSHRDLCUMWFGYPBVKJXQZ")
    
    def generate_with_constraints(self) -> str:
        """
        Generate text with corridor constraints using WFSA.
        
        Returns:
            Generated 75-character text with anchors
        """
        # Generate segments around anchors
        segments = []
        
        # Segment 1: positions 0-20 (before EAST)
        seg1 = self.generate_segment(21)
        segments.append(seg1)
        
        # Anchor 1: EAST
        segments.append("EAST")
        
        # Anchor 2: NORTHEAST (immediately after EAST)
        segments.append("NORTHEAST")
        
        # Segment 2: positions 34-62 (between NORTHEAST and BERLINCLOCK)
        context = "NE"  # Last two chars of NORTHEAST
        seg2 = self.generate_segment(29, context)
        segments.append(seg2)
        
        # Anchor 3: BERLINCLOCK
        segments.append("BERLINCLOCK")
        
        # Segment 3: positions 74-74 (after BERLINCLOCK, just 1 char)
        context = "CK"  # Last two chars of BERLINCLOCK
        seg3 = self.generate_segment(1, context)
        segments.append(seg3)
        
        result = ''.join(segments)
        
        # Verify length
        if len(result) != 75:
            # Adjust if needed
            if len(result) < 75:
                result += self.generate_segment(75 - len(result), result[-2:])
            else:
                result = result[:75]
        
        return result
    
    def apply_smoothing(self, text: str, smoothing_passes: int = 3) -> str:
        """
        Apply local smoothing to improve coherence.
        
        Args:
            text: Input text
            smoothing_passes: Number of smoothing iterations
            
        Returns:
            Smoothed text
        """
        text_list = list(text)
        
        # Protected positions (anchors)
        protected = set()
        for start, end in self.anchors.values():
            protected.update(range(start, end))
        
        for _ in range(smoothing_passes):
            for i in range(2, len(text_list) - 1):
                if i in protected:
                    continue
                
                # Check trigram coherence
                trigram = ''.join(text_list[i-2:i+1])
                prefix = trigram[:2]
                current_char = trigram[2]
                
                # Get probability of current character
                if prefix in self.transitions:
                    current_prob = self.transitions[prefix].get(current_char, 1e-6)
                else:
                    current_prob = 1e-6
                
                # If probability is very low, try to improve
                if current_prob < 0.01:
                    # Sample a better character
                    better_char = self._sample_next_char(prefix)
                    
                    # Check if improvement
                    if prefix in self.transitions:
                        better_prob = self.transitions[prefix].get(better_char, 1e-6)
                        if better_prob > current_prob * 2:  # Significant improvement
                            text_list[i] = better_char
        
        return ''.join(text_list)
    
    def generate_heads(self, num_heads: int = 50) -> List[Dict]:
        """
        Generate heads using WFSA with various strategies.
        
        Returns:
            List of generated head dictionaries
        """
        print(f"Generating {num_heads} WFSA heads...")
        heads = []
        
        for i in range(num_heads):
            if i % 10 == 0 and i > 0:
                print(f"  Generated {i}/{num_heads} heads...")
            
            # Generate base text
            text = self.generate_with_constraints()
            
            # Apply smoothing with varying intensity
            smoothing = random.randint(1, 5)
            text = self.apply_smoothing(text, smoothing)
            
            # Score quality
            gen_quality = self.scorer.score_generation_quality(text)
            
            heads.append({
                'label': f'WFSA_{i:03d}',
                'text': text,
                'metadata': {
                    'smoothing_passes': smoothing,
                    'generation_score': gen_quality['quality_score'],
                    'trigram_score': gen_quality['trigram_score'],
                    'entropy': gen_quality['bigram_entropy']
                }
            })
        
        # Sort by quality
        heads.sort(key=lambda x: x['metadata']['generation_score'], reverse=True)
        
        print(f"\nGenerated {len(heads)} WFSA heads")
        print(f"Best generation score: {heads[0]['metadata']['generation_score']:.4f}")
        print(f"Worst generation score: {heads[-1]['metadata']['generation_score']:.4f}")
        
        return heads


def main():
    """Run Track B generation and evaluation."""
    print("=" * 60)
    print("TRACK B: WFSA/PCFG SYNTHESIZER")
    print("=" * 60)
    
    generator = WFSAGenerator(seed=1337)
    
    # Generate heads
    heads = generator.generate_heads(num_heads=50)
    
    # Save heads
    output_file = Path(__file__).parent / "heads_wfsa.json"
    with open(output_file, 'w') as f:
        json.dump({
            'track': 'B_WFSA',
            'total_heads': len(heads),
            'heads': heads
        }, f, indent=2)
    
    print(f"\nSaved {len(heads)} heads to {output_file}")
    
    # Run evaluation
    print("\nEvaluating through v3 pipeline...")
    results = generator.scorer.run_v3_evaluation(heads, "Track_B_WFSA")
    
    # Save results
    results_file = Path(__file__).parent / "results_wfsa.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TRACK B RESULTS")
    print("=" * 60)
    print(f"Total heads: {results['total_heads']}")
    print(f"Promotions: {len(results['promotions'])}")
    
    if results['statistics']:
        print(f"Avg delta windowed: {results['statistics']['avg_delta_windowed']:.4f}")
        print(f"Avg delta shuffled: {results['statistics']['avg_delta_shuffled']:.4f}")
        print(f"Avg generation quality: {results['statistics']['avg_generation_quality']:.4f}")
    
    if results['promotions']:
        print("\nPromoted heads:")
        for promo in results['promotions'][:5]:
            print(f"  {promo['label']}: δ_w={promo['deltas']['windowed']:.3f}, δ_s={promo['deltas']['shuffled']:.3f}")
    
    return results


if __name__ == "__main__":
    results = main()