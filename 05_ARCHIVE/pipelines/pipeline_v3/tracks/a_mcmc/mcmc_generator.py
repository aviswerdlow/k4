#!/usr/bin/env python3
"""
Track A: Letter-Space MCMC/Gibbs Generator
Markov chain sampling directly in letter space with trigram model.
"""

import json
import random
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from common_scoring import V3ScoringPipeline


class MCMCGenerator:
    """
    MCMC generator that samples from English letter distribution.
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
    
    def initialize_chain(self, length: int = 75) -> str:
        """
        Initialize Markov chain with reasonable starting point.
        """
        # Start with common English letters
        text = ['T', 'H', 'E'] + ['A'] * (length - 3)
        
        # Place anchors at correct positions
        text[21:25] = list("EAST")
        text[25:34] = list("NORTHEAST")
        text[63:74] = list("BERLINCLOCK")
        
        # Fill remaining with common letters
        common = "ETAOINSHRDLCUMWFGYPBVKJXQZ"
        for i in range(length):
            if i < 21 or (i >= 34 and i < 63) or i >= 74:
                text[i] = random.choice(common[:10])  # Use most common
        
        return ''.join(text)
    
    def compute_energy(self, text: str, temperature: float = 1.0) -> float:
        """
        Compute energy (negative log probability) of text.
        Lower energy = better text.
        """
        # Trigram score
        trigram_energy = 0.0
        for i in range(2, len(text)):
            trigram = text[i-2:i+1]
            prefix = trigram[:2]
            char = trigram[2]
            
            # Get probability
            if prefix in self.trigram_model['trigram_probs']:
                if char in self.trigram_model['trigram_probs'][prefix]:
                    prob = self.trigram_model['trigram_probs'][prefix][char]
                else:
                    prob = 1e-6
            else:
                prob = 1e-6
            
            trigram_energy -= max(-20, min(0, prob)) / temperature
        
        # Character frequency penalty
        char_counts = {}
        for c in text:
            char_counts[c] = char_counts.get(c, 0) + 1
        
        # Penalize rare letters
        freq_energy = 0.0
        english_freq = {
            'E': 0.127, 'T': 0.091, 'A': 0.082, 'O': 0.075, 'I': 0.070,
            'N': 0.067, 'S': 0.063, 'H': 0.061, 'R': 0.060
        }
        
        for char, count in char_counts.items():
            actual_freq = count / len(text)
            expected_freq = english_freq.get(char, 0.01)
            freq_energy += abs(actual_freq - expected_freq) * 10
        
        return trigram_energy + freq_energy
    
    def propose_move(self, text: str, protected_positions: set) -> Tuple[str, int]:
        """
        Propose a move in the Markov chain.
        
        Returns:
            New text and position changed
        """
        text_list = list(text)
        
        # Choose position not in protected set
        available = [i for i in range(len(text)) if i not in protected_positions]
        if not available:
            return text, -1
        
        pos = random.choice(available)
        
        # Sample new character based on context
        if pos >= 2:
            # Use trigram model
            prefix = text[pos-2:pos]
            if prefix in self.trigram_model['trigram_probs']:
                probs = self.trigram_model['trigram_probs'][prefix]
                if probs:
                    # Sample from distribution
                    chars = list(probs.keys())
                    weights = list(probs.values())
                    new_char = random.choices(chars, weights=weights)[0]
                else:
                    new_char = random.choice("ETAOINSHRDLCUMWFGYPBVKJXQZ")
            else:
                new_char = random.choice("ETAOINSHRDLCUMWFGYPBVKJXQZ")
        else:
            # Use unigram for start
            if self.trigram_model['unigram_probs']:
                chars = list(self.trigram_model['unigram_probs'].keys())
                weights = list(self.trigram_model['unigram_probs'].values())
                # Filter to letters only
                valid = [(c, w) for c, w in zip(chars, weights) if c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
                if valid:
                    chars, weights = zip(*valid)
                    new_char = random.choices(chars, weights=weights)[0]
                else:
                    new_char = random.choice("ETAOINSHRDLCUMWFGYPBVKJXQZ")
            else:
                new_char = random.choice("ETAOINSHRDLCUMWFGYPBVKJXQZ")
        
        text_list[pos] = new_char
        return ''.join(text_list), pos
    
    def run_mcmc(
        self,
        iterations: int = 10000,
        temperature: float = 1.0,
        cooling_rate: float = 0.999,
        protect_anchors: bool = True
    ) -> List[str]:
        """
        Run MCMC to generate text.
        
        Returns:
            List of generated texts (samples from chain)
        """
        # Protected positions (anchors)
        protected = set()
        if protect_anchors:
            for start, end in self.anchors.values():
                protected.update(range(start, end))
        
        # Initialize
        current = self.initialize_chain()
        current_energy = self.compute_energy(current, temperature)
        
        best = current
        best_energy = current_energy
        
        samples = []
        accepted = 0
        
        for i in range(iterations):
            # Propose move
            proposed, pos = self.propose_move(current, protected)
            if pos == -1:
                continue
            
            # Compute energy change
            proposed_energy = self.compute_energy(proposed, temperature)
            delta_e = proposed_energy - current_energy
            
            # Metropolis acceptance
            if delta_e < 0 or random.random() < min(1.0, (-delta_e / temperature)):
                current = proposed
                current_energy = proposed_energy
                accepted += 1
                
                # Track best
                if current_energy < best_energy:
                    best = current
                    best_energy = current_energy
            
            # Cool temperature
            temperature *= cooling_rate
            temperature = max(0.01, temperature)  # Minimum temperature
            
            # Sample periodically
            if i % 1000 == 0 and i > 0:
                samples.append(current)
                if i % 5000 == 0:
                    print(f"  Iteration {i}: T={temperature:.3f}, Energy={current_energy:.2f}, Accept={accepted/i:.2%}")
        
        # Always include best
        if best not in samples:
            samples.append(best)
        
        return samples
    
    def generate_heads(self, num_chains: int = 10, iterations: int = 10000) -> List[Dict]:
        """
        Generate heads using multiple MCMC chains.
        
        Returns:
            List of generated head dictionaries
        """
        print(f"Running {num_chains} MCMC chains...")
        all_heads = []
        
        for chain_id in range(num_chains):
            print(f"\nChain {chain_id + 1}/{num_chains}:")
            
            # Vary temperature schedule
            init_temp = random.uniform(0.5, 2.0)
            cooling = random.uniform(0.995, 0.9995)
            
            # Run chain
            samples = self.run_mcmc(
                iterations=iterations,
                temperature=init_temp,
                cooling_rate=cooling,
                protect_anchors=True
            )
            
            # Score and select best samples
            scored_samples = []
            for sample in samples:
                # Quick quality check
                gen_quality = self.scorer.score_generation_quality(sample)
                scored_samples.append((sample, gen_quality['quality_score']))
            
            # Sort by quality
            scored_samples.sort(key=lambda x: x[1], reverse=True)
            
            # Take top samples
            for i, (text, score) in enumerate(scored_samples[:5]):
                all_heads.append({
                    'label': f'MCMC_chain{chain_id:02d}_sample{i:02d}',
                    'text': text,
                    'metadata': {
                        'chain_id': chain_id,
                        'sample_rank': i,
                        'init_temp': init_temp,
                        'cooling_rate': cooling,
                        'generation_score': score
                    }
                })
        
        print(f"\nGenerated {len(all_heads)} heads from MCMC")
        return all_heads


def main():
    """Run Track A generation and evaluation."""
    print("=" * 60)
    print("TRACK A: LETTER-SPACE MCMC/GIBBS")
    print("=" * 60)
    
    generator = MCMCGenerator(seed=1337)
    
    # Generate heads
    heads = generator.generate_heads(num_chains=10, iterations=10000)
    
    # Save heads
    output_file = Path(__file__).parent / "heads_mcmc.json"
    with open(output_file, 'w') as f:
        json.dump({
            'track': 'A_MCMC',
            'total_heads': len(heads),
            'heads': heads
        }, f, indent=2)
    
    print(f"\nSaved {len(heads)} heads to {output_file}")
    
    # Run evaluation
    print("\nEvaluating through v3 pipeline...")
    results = generator.scorer.run_v3_evaluation(heads, "Track_A_MCMC")
    
    # Save results
    results_file = Path(__file__).parent / "results_mcmc.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TRACK A RESULTS")
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