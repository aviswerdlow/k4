#!/usr/bin/env python3
"""
Track C: Cipher-Space Hill-Climb
Search in cipher space optimizing blinded language score directly.
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

# K4 ciphertext
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"


class CipherSearchGenerator:
    """
    Search cipher space directly, optimizing for blinded language score.
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
        
        # Cipher text
        self.ciphertext = K4_CIPHERTEXT[:75]
        
        # Anchor positions and expected plaintext
        self.anchors = {
            "EAST": (21, 25),
            "NORTHEAST": (25, 34),
            "BERLINCLOCK": (63, 74)
        }
    
    def initialize_key(self, key_type: str = "vigenere", period: int = 19) -> Dict:
        """
        Initialize a cipher key.
        
        Args:
            key_type: Type of cipher (vigenere, beaufort, variant_beaufort)
            period: Key period
            
        Returns:
            Key dictionary
        """
        return {
            'type': key_type,
            'period': period,
            'values': [random.randint(0, 25) for _ in range(period)]
        }
    
    def decrypt(self, key: Dict) -> str:
        """
        Decrypt ciphertext with given key.
        
        Args:
            key: Key dictionary
            
        Returns:
            Decrypted plaintext
        """
        plaintext = []
        key_type = key['type']
        key_values = key['values']
        period = key['period']
        
        for i, c in enumerate(self.ciphertext):
            c_val = ord(c) - ord('A')
            k_val = key_values[i % period]
            
            if key_type == 'vigenere':
                p_val = (c_val - k_val) % 26
            elif key_type == 'beaufort':
                p_val = (k_val - c_val) % 26
            elif key_type == 'variant_beaufort':
                p_val = (c_val + k_val) % 26
            else:
                p_val = c_val  # No encryption
            
            plaintext.append(chr(p_val + ord('A')))
        
        return ''.join(plaintext)
    
    def score_plaintext(self, plaintext: str) -> float:
        """
        Score plaintext after blinding.
        This is what we optimize in cipher space.
        
        Args:
            plaintext: Candidate plaintext
            
        Returns:
            Score (higher is better)
        """
        # Blind the text (mask anchor terms)
        blinded = self._blind_text(plaintext)
        
        # Score blinded text with trigram model
        score = 0.0
        for i in range(2, len(blinded)):
            trigram = blinded[i-2:i+1]
            prefix = trigram[:2]
            char = trigram[2]
            
            if prefix in self.trigram_model['trigram_probs']:
                if char in self.trigram_model['trigram_probs'][prefix]:
                    prob = self.trigram_model['trigram_probs'][prefix][char]
                    score += max(-10, min(0, prob))
                else:
                    score -= 5  # Penalty for unseen trigram
            else:
                score -= 3  # Smaller penalty for unseen prefix
        
        # Normalize
        return score / max(1, len(blinded) - 2)
    
    def _blind_text(self, text: str) -> str:
        """
        Blind text by masking anchor terms.
        """
        blinded = list(text)
        
        # Mask each anchor region
        for anchor_text, (start, end) in self.anchors.items():
            # Check if anchor appears near expected position
            for offset in range(-5, 6):  # Search window
                pos = start + offset
                if pos >= 0 and pos + len(anchor_text) <= len(text):
                    if text[pos:pos+len(anchor_text)] == anchor_text:
                        # Mask it
                        for i in range(pos, pos + len(anchor_text)):
                            if i < len(blinded):
                                blinded[i] = 'X'
        
        return ''.join(blinded)
    
    def constrain_key_for_anchors(self, key: Dict) -> Dict:
        """
        Constrain key to produce anchors at correct positions.
        
        Args:
            key: Initial key
            
        Returns:
            Constrained key
        """
        key_type = key['type']
        key_values = key['values'].copy()
        period = key['period']
        
        # Expected plaintext at anchor positions
        expected = ['X'] * 75
        expected[21:25] = list("EAST")
        expected[25:34] = list("NORTHEAST")
        expected[63:74] = list("BERLINCLOCK")
        
        # Solve for required key values at anchor positions
        anchor_positions = (
            list(range(21, 25)) +
            list(range(25, 34)) +
            list(range(63, 74))
        )
        
        for pos in anchor_positions:
            c_val = ord(self.ciphertext[pos]) - ord('A')
            p_val = ord(expected[pos]) - ord('A')
            key_idx = pos % period
            
            if key_type == 'vigenere':
                required = (c_val - p_val) % 26
            elif key_type == 'beaufort':
                required = (p_val + c_val) % 26
            elif key_type == 'variant_beaufort':
                required = (p_val - c_val) % 26
            else:
                required = 0
            
            key_values[key_idx] = required
        
        key['values'] = key_values
        return key
    
    def hill_climb(
        self,
        key: Dict,
        iterations: int = 10000,
        temperature: float = 1.0,
        cooling_rate: float = 0.999
    ) -> Tuple[Dict, str, float]:
        """
        Hill climb in cipher space.
        
        Args:
            key: Starting key
            iterations: Number of iterations
            temperature: Initial temperature for simulated annealing
            cooling_rate: Temperature decay rate
            
        Returns:
            Best key, plaintext, and score
        """
        current_key = key.copy()
        current_key['values'] = key['values'].copy()
        
        # Constrain for anchors
        current_key = self.constrain_key_for_anchors(current_key)
        
        current_plain = self.decrypt(current_key)
        current_score = self.score_plaintext(current_plain)
        
        best_key = current_key.copy()
        best_key['values'] = current_key['values'].copy()
        best_plain = current_plain
        best_score = current_score
        
        # Track which key positions are constrained
        period = current_key['period']
        constrained_positions = set()
        
        # Identify constrained key positions
        anchor_positions = (
            list(range(21, 25)) +
            list(range(25, 34)) +
            list(range(63, 74))
        )
        for pos in anchor_positions:
            constrained_positions.add(pos % period)
        
        # Free positions for modification
        free_positions = [i for i in range(period) if i not in constrained_positions]
        
        for iteration in range(iterations):
            # Modify a free key position
            if free_positions:
                pos = random.choice(free_positions)
                old_val = current_key['values'][pos]
                new_val = random.randint(0, 25)
                current_key['values'][pos] = new_val
                
                # Decrypt and score
                new_plain = self.decrypt(current_key)
                new_score = self.score_plaintext(new_plain)
                
                # Accept or reject
                delta = new_score - current_score
                if delta > 0 or random.random() < min(1.0, (delta / temperature)):
                    current_plain = new_plain
                    current_score = new_score
                    
                    if current_score > best_score:
                        best_key = current_key.copy()
                        best_key['values'] = current_key['values'].copy()
                        best_plain = current_plain
                        best_score = current_score
                else:
                    # Revert
                    current_key['values'][pos] = old_val
            
            # Cool temperature
            temperature *= cooling_rate
            temperature = max(0.01, temperature)
            
            if iteration % 1000 == 0 and iteration > 0:
                print(f"  Iteration {iteration}: Score={current_score:.4f}, Best={best_score:.4f}, T={temperature:.3f}")
        
        return best_key, best_plain, best_score
    
    def generate_heads(self, num_searches: int = 20) -> List[Dict]:
        """
        Generate heads through cipher-space search.
        
        Returns:
            List of generated head dictionaries
        """
        print(f"Running {num_searches} cipher-space searches...")
        heads = []
        
        cipher_types = ['vigenere', 'beaufort', 'variant_beaufort']
        periods = [15, 17, 19, 21, 23]
        
        for search_id in range(num_searches):
            print(f"\nSearch {search_id + 1}/{num_searches}:")
            
            # Random cipher configuration
            cipher_type = random.choice(cipher_types)
            period = random.choice(periods)
            
            # Initialize key
            key = self.initialize_key(cipher_type, period)
            
            # Run hill climb
            best_key, best_plain, best_score = self.hill_climb(
                key,
                iterations=5000,
                temperature=random.uniform(0.5, 2.0),
                cooling_rate=random.uniform(0.995, 0.9995)
            )
            
            # Score with full pipeline
            gen_quality = self.scorer.score_generation_quality(best_plain)
            
            heads.append({
                'label': f'CIPHER_{search_id:03d}',
                'text': best_plain,
                'metadata': {
                    'cipher_type': cipher_type,
                    'period': period,
                    'key': best_key['values'],
                    'cipher_score': best_score,
                    'generation_score': gen_quality['quality_score']
                }
            })
        
        # Sort by cipher score
        heads.sort(key=lambda x: x['metadata']['cipher_score'], reverse=True)
        
        print(f"\nGenerated {len(heads)} heads through cipher search")
        print(f"Best cipher score: {heads[0]['metadata']['cipher_score']:.4f}")
        print(f"Worst cipher score: {heads[-1]['metadata']['cipher_score']:.4f}")
        
        return heads


def main():
    """Run Track C generation and evaluation."""
    print("=" * 60)
    print("TRACK C: CIPHER-SPACE HILL-CLIMB")
    print("=" * 60)
    
    generator = CipherSearchGenerator(seed=1337)
    
    # Generate heads
    heads = generator.generate_heads(num_searches=20)
    
    # Save heads
    output_file = Path(__file__).parent / "heads_cipher.json"
    with open(output_file, 'w') as f:
        json.dump({
            'track': 'C_CIPHER',
            'total_heads': len(heads),
            'heads': heads
        }, f, indent=2)
    
    print(f"\nSaved {len(heads)} heads to {output_file}")
    
    # Run evaluation
    print("\nEvaluating through v3 pipeline...")
    results = generator.scorer.run_v3_evaluation(heads, "Track_C_CIPHER")
    
    # Save results
    results_file = Path(__file__).parent / "results_cipher.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TRACK C RESULTS")
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