#!/usr/bin/env python3
"""
Fixed MCMC generator that prevents duplicates.
"""

import json
import random
import hashlib
import sys
import numpy as np
from pathlib import Path
from typing import List, Dict, Set, Tuple

# Add parent directories
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from experiments.pipeline_v2.scripts.explore.run_family import ExplorePipeline


class BlindedMCMCGeneratorFixed:
    """
    Fixed MCMC generator with duplicate prevention.
    """
    
    def __init__(self, seed: int = 1337):
        self.global_seed = seed
        
        # Load trigram model
        model_path = Path(__file__).parent.parent.parent / "trigram_model.json"
        with open(model_path, 'r') as f:
            self.trigram_model = json.load(f)
        
        # Initialize scorer for blinding
        self.scorer = ExplorePipeline(seed)
        
        # Frozen parameters
        self.alpha = 0.7
        self.beta = 0.3
        self.gamma = 0.15
        self.lambda_content = 0.5
        self.lambda_repeat = 0.8
    
    def get_chain_seed(self, chain_id: int, stage_id: int) -> int:
        """Generate independent seed for each chain and stage."""
        seed_str = f"{self.global_seed}|chain:{chain_id}|stage:{stage_id}"
        seed_hash = hashlib.sha256(seed_str.encode()).hexdigest()
        return int(seed_hash[:16], 16) % (2**32)
    
    def blind_text(self, text: str) -> str:
        """Apply blinding to text."""
        return self.scorer._blind_text(text)
    
    def compute_blinded_score(self, text: str) -> Tuple[float, Dict]:
        """Compute S_blind objective for unanchored text."""
        blinded = self.blind_text(text)
        
        # Compute z-scores on blinded text
        z_trigram = self._compute_z_trigram(blinded)
        z_bigram = self._compute_z_bigram(blinded)
        z_compress = self._compute_z_compress(blinded)
        
        # Content diversity
        content_chars = set(c for c in blinded if c != 'X' and c.isalpha())
        content_count = len(content_chars)
        content_penalty = max(0, 6 - content_count)
        
        # Repetition penalty
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
            if 'X' in trigram:
                continue
            
            prefix = trigram[:2]
            char = trigram[2]
            
            if prefix in self.trigram_model['trigram_probs']:
                if char in self.trigram_model['trigram_probs'][prefix]:
                    prob = self.trigram_model['trigram_probs'][prefix][char]
                    score += np.log(prob + 1e-10)
                else:
                    score -= 2
            else:
                score -= 1
            count += 1
        
        if count == 0:
            return -5.0
        
        mean_score = score / count
        z_score = (mean_score + 2.5) / 0.8
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
        """Compute compression z-score."""
        substrings = set()
        for length in [2, 3, 4]:
            for i in range(len(text) - length + 1):
                substr = text[i:i+length]
                if 'X' not in substr:
                    substrings.add(substr)
        
        expected = len(text) * 0.8
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
    
    def propose_move(self, text: str, move_type: str = None) -> str:
        """Propose a move in MCMC chain."""
        if move_type is None:
            move_type = random.choice(['flip', 'swap', 'shuffle'])
        
        text_list = list(text)
        
        if move_type == 'flip':
            # Single-site flip
            pos = random.randint(0, len(text) - 1)
            old_char = text_list[pos]
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
                block1 = text_list[pos1:pos1+3]
                block2 = text_list[pos2:pos2+3]
                text_list[pos1:pos1+3] = block2
                text_list[pos2:pos2+3] = block1
        
        return ''.join(text_list)
    
    def run_mcmc_4stage_fixed(self, chain_id: int = 0) -> List[Dict]:
        """
        Run 4-stage annealed MCMC with duplicate prevention.
        """
        # Temperature schedule for 4 stages
        temp_schedule = [
            (3.0, 0.9995, 15000),  # Stage 1: High temp exploration
            (2.0, 0.9997, 15000),  # Stage 2: Medium-high
            (1.0, 0.9998, 15000),  # Stage 3: Medium
            (0.5, 0.9999, 15000),  # Stage 4: Low temp refinement
        ]
        
        all_samples = []
        seen_hashes = set()  # Track unique states
        
        # Initialize with common English letters
        current = None
        for attempt in range(10):  # Try to get unique start
            seed = self.get_chain_seed(chain_id, 0)
            random.seed(seed)
            np.random.seed(seed)
            
            candidate = ''.join(random.choices("ETAOINSHRDLCUMWFGYPBVKJXQZ", k=75))
            h = hashlib.sha256(candidate.encode()).hexdigest()
            if h not in seen_hashes:
                current = candidate
                seen_hashes.add(h)
                break
        
        if current is None:
            raise ValueError(f"Failed to generate unique start for chain {chain_id}")
        
        current_score, current_components = self.compute_blinded_score(current)
        
        best_overall = current
        best_overall_score = current_score
        
        for stage, (init_temp, cooling_rate, iterations) in enumerate(temp_schedule):
            # Set stage-specific seed
            seed = self.get_chain_seed(chain_id, stage + 1)
            random.seed(seed)
            np.random.seed(seed)
            
            print(f"    Stage {stage+1}/4: T={init_temp}, iterations={iterations}")
            
            temperature = init_temp
            accepted = 0
            stagnation = 0
            max_stagnation = 1000
            
            best_stage = current
            best_stage_score = current_score
            
            for iteration in range(iterations):
                # Propose move (vary type if stagnating)
                if stagnation > max_stagnation // 2:
                    move_type = random.choice(['flip', 'swap', 'shuffle'])
                else:
                    move_type = None
                
                proposed = self.propose_move(current, move_type)
                
                # Check for duplicate
                h = hashlib.sha256(proposed.encode()).hexdigest()
                if h in seen_hashes:
                    stagnation += 1
                    continue
                
                proposed_score, proposed_components = self.compute_blinded_score(proposed)
                
                # Metropolis-Hastings acceptance
                delta = proposed_score - current_score
                if delta > 0 or random.random() < np.exp(delta / temperature):
                    current = proposed
                    current_score = proposed_score
                    current_components = proposed_components
                    accepted += 1
                    stagnation = 0
                    seen_hashes.add(h)
                    
                    if current_score > best_stage_score:
                        best_stage = current
                        best_stage_score = current_score
                    
                    if current_score > best_overall_score:
                        best_overall = current
                        best_overall_score = current_score
                else:
                    stagnation += 1
                
                # Force move if too stagnant
                if stagnation > max_stagnation:
                    print(f"      Force move at iteration {iteration}")
                    for _ in range(10):
                        forced = self.propose_move(current, 'shuffle')
                        h = hashlib.sha256(forced.encode()).hexdigest()
                        if h not in seen_hashes:
                            current = forced
                            current_score, current_components = self.compute_blinded_score(current)
                            seen_hashes.add(h)
                            stagnation = 0
                            break
                
                # Cool temperature
                temperature *= cooling_rate
                temperature = max(0.01, temperature)
                
                # Sample periodically
                if iteration % 3000 == 0 and iteration > 0:
                    # Only add if unique
                    if current not in [s['text'] for s in all_samples]:
                        all_samples.append({
                            'text': current,
                            'score': current_score,
                            'components': current_components,
                            'chain_id': chain_id,
                            'stage': stage + 1,
                            'iteration': iteration,
                            'temperature': temperature,
                            'accept_rate': accepted / (iteration + 1)
                        })
                    
                    if iteration % 9000 == 0:
                        print(f"      Iter {iteration}: Score={current_score:.3f}, "
                              f"Best={best_stage_score:.3f}, Accept={accepted/(iteration+1):.2%}")
            
            # Add best from stage (if unique)
            if best_stage not in [s['text'] for s in all_samples]:
                all_samples.append({
                    'text': best_stage,
                    'score': best_stage_score,
                    'components': current_components,
                    'chain_id': chain_id,
                    'stage': stage + 1,
                    'iteration': iterations,
                    'temperature': temperature,
                    'accept_rate': accepted / iterations,
                    'label': f'BLINDED_CH{chain_id:02d}_S{stage+1}_BEST'
                })
        
        # Always include global best (if unique)
        if best_overall not in [s['text'] for s in all_samples]:
            all_samples.append({
                'text': best_overall,
                'score': best_overall_score,
                'components': current_components,
                'chain_id': chain_id,
                'stage': 'best',
                'iteration': 60000,
                'temperature': 0.01,
                'accept_rate': 0,
                'label': f'BLINDED_CH{chain_id:02d}_OVERALL_BEST'
            })
        
        print(f"    Generated {len(all_samples)} unique samples")
        
        return all_samples
    
    def generate_heads_scaled(self, n_chains: int = 2) -> List[Dict]:
        """Generate heads with duplicate prevention."""
        print(f"Running {n_chains} 4-stage MCMC chains with duplicate prevention...")
        all_heads = []
        
        for chain_id in range(n_chains):
            print(f"\nChain {chain_id + 1}/{n_chains}:")
            samples = self.run_mcmc_4stage_fixed(chain_id)
            
            for i, sample in enumerate(samples):
                if 'label' not in sample:
                    sample['label'] = f'BLINDED_CH{chain_id:02d}_I{i:03d}'
                all_heads.append(sample)
        
        # Final deduplication check
        unique_heads = []
        seen_texts = set()
        
        for head in all_heads:
            if head['text'] not in seen_texts:
                unique_heads.append(head)
                seen_texts.add(head['text'])
        
        # Sort by score
        unique_heads.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\nGenerated {len(all_heads)} total heads")
        print(f"After deduplication: {len(unique_heads)} unique heads")
        print(f"Score range: {unique_heads[0]['score']:.3f} to {unique_heads[-1]['score']:.3f}")
        
        # Return top 25
        return unique_heads[:25]


def main():
    """Generate heads with fixed MCMC."""
    generator = BlindedMCMCGeneratorFixed(seed=1337)
    
    # Generate with fixed parameters
    heads = generator.generate_heads_scaled(n_chains=2)
    
    # Save
    output_dir = Path(__file__).parent.parent.parent / "runs" / "track_a_scaled"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "blinded_heads_fixed.json"
    with open(output_file, 'w') as f:
        json.dump({
            'track': 'A1_BLINDED_MCMC_FIXED',
            'total_generated': len(heads),
            'config': {
                'n_chains': 2,
                'stages': 4,
                'proposals_per_stage': 15000,
                'alpha': 0.7,
                'beta': 0.3,
                'gamma': 0.15,
                'duplicate_prevention': True
            },
            'heads': heads
        }, f, indent=2)
    
    print(f"\nSaved {len(heads)} unique heads to {output_file}")
    
    return heads


if __name__ == "__main__":
    heads = main()