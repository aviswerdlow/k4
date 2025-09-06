#!/usr/bin/env python3
"""
Track A1: Blinded-first MCMC head generator.
Generates heads that maximize blinded n-gram quality without anchor constraints.
"""

import json
import random
import sys
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np

# Add parent directories
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from experiments.pipeline_v2.scripts.explore.run_family import ExplorePipeline


class BlindedMCMCGenerator:
    """
    Generate heads optimized for blinded n-gram quality.
    """
    
    def __init__(self, seed: int = 1337):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        # Load trigram model
        model_path = Path(__file__).parent.parent.parent / "trigram_model.json"
        with open(model_path, 'r') as f:
            self.trigram_model = json.load(f)
        
        # Initialize scorer for blinding
        self.scorer = ExplorePipeline(seed)
        
        # Parameters (from v2.3 calibration)
        self.alpha = 0.7  # trigram weight
        self.beta = 0.3   # bigram weight
        self.gamma = 0.1  # compression proxy weight
        self.lambda_content = 0.5  # content diversity penalty
        self.lambda_repeat = 0.8   # repetition penalty
    
    def blind_text(self, text: str) -> str:
        """
        Apply blinding to text (mask narrative/anchor terms).
        """
        # Use the same blinding as the scorer
        blinded = self.scorer._blind_text(text)
        return blinded
    
    def compute_blinded_score(self, text: str) -> Tuple[float, Dict]:
        """
        Compute S_blind objective for unanchored text.
        
        Returns:
            (score, components_dict)
        """
        # Blind the text first
        blinded = self.blind_text(text)
        
        # Compute z-scores on blinded text
        z_trigram = self._compute_z_trigram(blinded)
        z_bigram = self._compute_z_bigram(blinded)
        z_compress = self._compute_z_compress(blinded)
        
        # Content diversity (unique non-X chars after blinding)
        content_chars = set(c for c in blinded if c != 'X' and c.isalpha())
        content_count = len(content_chars)
        content_penalty = max(0, 6 - content_count)
        
        # Repetition penalty (longest repeat in blinded text)
        max_repeat = self._find_max_repeat(blinded)
        repeat_penalty = max(0, max_repeat - 2)
        
        # Combined objective
        score = (self.alpha * z_trigram + 
                self.beta * z_bigram + 
                self.gamma * z_compress -
                self.lambda_content * content_penalty -
                self.lambda_repeat * repeat_penalty)
        
        components = {
            'z_trigram': z_trigram,
            'z_bigram': z_bigram,
            'z_compress': z_compress,
            'content_count': content_count,
            'max_repeat': max_repeat,
            'score': score
        }
        
        return score, components
    
    def _compute_z_trigram(self, text: str) -> float:
        """Compute trigram z-score against model."""
        if len(text) < 3:
            return -5.0
        
        score = 0.0
        count = 0
        
        for i in range(len(text) - 2):
            trigram = text[i:i+3]
            # Skip if contains masked char
            if 'X' in trigram:
                continue
            
            prefix = trigram[:2]
            char = trigram[2]
            
            if prefix in self.trigram_model['trigram_probs']:
                if char in self.trigram_model['trigram_probs'][prefix]:
                    prob = self.trigram_model['trigram_probs'][prefix][char]
                    score += np.log(prob + 1e-10)
                else:
                    score -= 2  # Unseen trigram penalty
            else:
                score -= 1  # Unseen prefix penalty
            count += 1
        
        if count == 0:
            return -5.0
        
        # Normalize to z-score (approximate)
        mean_score = score / count
        z_score = (mean_score + 2.5) / 0.8  # Empirical normalization
        return max(-5, min(5, z_score))
    
    def _compute_z_bigram(self, text: str) -> float:
        """Compute bigram z-score."""
        if len(text) < 2:
            return -5.0
        
        score = 0.0
        count = 0
        
        for i in range(len(text) - 1):
            bigram = text[i:i+2]
            if 'X' in bigram:
                continue
            
            prefix = bigram[0]
            char = bigram[1]
            
            if prefix in self.trigram_model['bigram_probs']:
                if char in self.trigram_model['bigram_probs'][prefix]:
                    prob = self.trigram_model['bigram_probs'][prefix][char]
                    score += np.log(prob + 1e-10)
                else:
                    score -= 1
            else:
                score -= 0.5
            count += 1
        
        if count == 0:
            return -5.0
        
        mean_score = score / count
        z_score = (mean_score + 1.8) / 0.6
        return max(-5, min(5, z_score))
    
    def _compute_z_compress(self, text: str) -> float:
        """Compute compression z-score (simplified LZ78 proxy)."""
        # Count unique substrings as compression proxy
        substrings = set()
        for length in [2, 3, 4]:
            for i in range(len(text) - length + 1):
                substr = text[i:i+length]
                if 'X' not in substr:
                    substrings.add(substr)
        
        # More unique substrings = better compressibility
        expected = len(text) * 0.8  # Empirical
        z_score = (len(substrings) - expected) / (expected * 0.2)
        return max(-5, min(5, z_score))
    
    def _find_max_repeat(self, text: str) -> int:
        """Find longest repeated substring."""
        max_repeat = 1
        for length in range(2, min(10, len(text) // 2)):
            for i in range(len(text) - length * 2 + 1):
                pattern = text[i:i+length]
                if 'X' in pattern:
                    continue
                if text[i+length:i+2*length] == pattern:
                    max_repeat = max(max_repeat, length)
        return max_repeat
    
    def propose_move(self, text: str) -> str:
        """
        Propose a move in MCMC chain.
        Move types: single-site flip, adjacent swap, 3-gram block shuffle.
        """
        move_type = random.choice(['flip', 'swap', 'shuffle'])
        text_list = list(text)
        
        if move_type == 'flip':
            # Single-site flip
            pos = random.randint(0, len(text) - 1)
            old_char = text_list[pos]
            # Sample from common letters
            new_char = random.choice("ETAOINSHRDLCUMWFGYPBVKJXQZ")
            while new_char == old_char:
                new_char = random.choice("ETAOINSHRDLCUMWFGYPBVKJXQZ")
            text_list[pos] = new_char
            
        elif move_type == 'swap':
            # Adjacent swap
            if len(text) > 1:
                pos = random.randint(0, len(text) - 2)
                text_list[pos], text_list[pos+1] = text_list[pos+1], text_list[pos]
        
        else:  # shuffle
            # 3-gram block shuffle
            if len(text) >= 6:
                pos1 = random.randint(0, len(text) - 3)
                pos2 = random.randint(0, len(text) - 3)
                while abs(pos1 - pos2) < 3:
                    pos2 = random.randint(0, len(text) - 3)
                # Swap 3-gram blocks
                block1 = text_list[pos1:pos1+3]
                block2 = text_list[pos2:pos2+3]
                text_list[pos1:pos1+3] = block2
                text_list[pos2:pos2+3] = block1
        
        return ''.join(text_list)
    
    def run_mcmc(
        self, 
        iterations: int = 10000,
        init_temp: float = 2.0,
        cooling_rate: float = 0.999,
        sample_interval: int = 100
    ) -> List[Dict]:
        """
        Run MCMC to generate heads optimized for blinded scoring.
        
        Returns:
            List of head dictionaries with scores
        """
        # Initialize with common English letters
        current = ''.join(random.choices("ETAOINSHRDLCUMWFGYPBVKJXQZ", k=75))
        current_score, current_components = self.compute_blinded_score(current)
        
        best = current
        best_score = current_score
        best_components = current_components
        
        samples = []
        temperature = init_temp
        accepted = 0
        
        for iteration in range(iterations):
            # Propose move
            proposed = self.propose_move(current)
            proposed_score, proposed_components = self.compute_blinded_score(proposed)
            
            # Metropolis acceptance
            delta = proposed_score - current_score
            if delta > 0 or random.random() < np.exp(delta / temperature):
                current = proposed
                current_score = proposed_score
                current_components = proposed_components
                accepted += 1
                
                if current_score > best_score:
                    best = current
                    best_score = current_score
                    best_components = current_components
            
            # Cool temperature
            temperature *= cooling_rate
            temperature = max(0.01, temperature)
            
            # Sample periodically
            if iteration % sample_interval == 0 and iteration > 0:
                samples.append({
                    'text': current,
                    'score': current_score,
                    'components': current_components,
                    'iteration': iteration,
                    'temperature': temperature,
                    'accept_rate': accepted / iteration
                })
                
                if iteration % 1000 == 0:
                    print(f"  Iteration {iteration}: Score={current_score:.3f}, "
                          f"Best={best_score:.3f}, T={temperature:.3f}, "
                          f"Accept={accepted/iteration:.2%}")
        
        # Always include best
        samples.append({
            'text': best,
            'score': best_score,
            'components': best_components,
            'iteration': iterations,
            'temperature': temperature,
            'accept_rate': accepted / iterations
        })
        
        return samples
    
    def generate_heads(self, n_chains: int = 10, iterations: int = 10000) -> List[Dict]:
        """
        Generate N heads using multiple MCMC chains.
        
        Returns:
            List of head dictionaries sorted by score
        """
        print(f"Running {n_chains} blinded MCMC chains...")
        all_heads = []
        
        for chain_id in range(n_chains):
            print(f"\nChain {chain_id + 1}/{n_chains}:")
            
            # Vary temperature schedule
            init_temp = random.uniform(1.0, 3.0)
            cooling = random.uniform(0.997, 0.9995)
            
            # Run chain
            samples = self.run_mcmc(
                iterations=iterations,
                init_temp=init_temp,
                cooling_rate=cooling,
                sample_interval=500
            )
            
            # Add chain metadata
            for sample in samples:
                sample['chain_id'] = chain_id
                sample['label'] = f'BLINDED_{chain_id:03d}_{sample["iteration"]:05d}'
                all_heads.append(sample)
        
        # Sort by score
        all_heads.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\nGenerated {len(all_heads)} heads")
        print(f"Best blinded score: {all_heads[0]['score']:.3f}")
        print(f"Worst blinded score: {all_heads[-1]['score']:.3f}")
        
        return all_heads


def main():
    """Generate blinded-first heads and save."""
    generator = BlindedMCMCGenerator(seed=1337)
    
    # Generate heads
    heads = generator.generate_heads(n_chains=5, iterations=5000)
    
    # Keep top K=200
    top_heads = heads[:200]
    
    # Save
    output_dir = Path(__file__).parent.parent.parent / "runs" / "track_a"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "blinded_heads.json"
    with open(output_file, 'w') as f:
        json.dump({
            'track': 'A1_BLINDED_MCMC',
            'total_generated': len(heads),
            'kept': len(top_heads),
            'heads': top_heads
        }, f, indent=2)
    
    print(f"\nSaved {len(top_heads)} heads to {output_file}")
    
    # Create manifest
    manifest = {
        'files': ['blinded_heads.json'],
        'hashes': {}
    }
    
    for fname in manifest['files']:
        fpath = output_dir / fname
        if fpath.exists():
            with open(fpath, 'rb') as f:
                manifest['hashes'][fname] = hashlib.sha256(f.read()).hexdigest()
    
    with open(output_dir / "MANIFEST.sha256", 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return top_heads


if __name__ == "__main__":
    heads = main()