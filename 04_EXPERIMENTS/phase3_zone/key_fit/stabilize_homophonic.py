#!/usr/bin/env python3
"""
Stabilize homophonic mapping through multiple runs and consensus building
"""

import sys
import os
import json
import random
import numpy as np
from typing import Dict, List, Tuple, Set
from collections import defaultdict, Counter

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../03_SOLVERS/zone_mask_v1/scripts'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../07_TOOLS/language'))

from cipher_homophonic import AnchorConstrainedHomophonic
from scoring import LanguageScorer

# K4 ciphertext
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Anchor constraints
ANCHORS = {
    "EAST": (21, 24),
    "NORTHEAST": (25, 33),
    "BERLIN": (63, 68),
    "CLOCK": (69, 73)
}

class EnhancedScorer:
    """Enhanced scoring with soft constraints"""
    
    def __init__(self):
        self.base_scorer = LanguageScorer()
        
        # English letter frequencies
        self.eng_freq = {
            'E': 0.127, 'T': 0.091, 'A': 0.082, 'O': 0.075, 'I': 0.070,
            'N': 0.067, 'S': 0.063, 'H': 0.061, 'R': 0.060, 'D': 0.043,
            'L': 0.040, 'C': 0.028, 'U': 0.028, 'M': 0.024, 'W': 0.024,
            'F': 0.022, 'G': 0.020, 'Y': 0.020, 'P': 0.019, 'B': 0.013,
            'V': 0.010, 'K': 0.008, 'J': 0.002, 'X': 0.002, 'Q': 0.001,
            'Z': 0.001
        }
    
    def score_with_constraints(self, text: str, 
                              frequency_weight: float = 0.1,
                              repetition_penalty: float = 0.5,
                              function_bonus: float = 2.0) -> float:
        """Score with soft constraints"""
        base_score = self.base_scorer.combined_score(text)
        
        # Frequency prior (KL divergence penalty)
        freq_penalty = self.frequency_penalty(text) * frequency_weight
        
        # Repetition penalty
        rep_penalty = self.repetition_penalty(text) * repetition_penalty
        
        # Function word bonus
        func_bonus = self.function_word_bonus(text) * function_bonus
        
        return base_score - freq_penalty - rep_penalty + func_bonus
    
    def frequency_penalty(self, text: str) -> float:
        """KL divergence from English frequencies"""
        text_upper = text.upper()
        text_letters = [c for c in text_upper if c.isalpha()]
        
        if not text_letters:
            return 0.0
        
        # Count frequencies
        counts = Counter(text_letters)
        total = len(text_letters)
        
        # Calculate KL divergence
        kl = 0.0
        for letter in self.eng_freq:
            expected = self.eng_freq[letter]
            observed = counts.get(letter, 0) / total if total > 0 else 0
            
            if observed > 0:
                kl += observed * np.log(observed / expected) if expected > 0 else 0
        
        return kl * 100  # Scale for impact
    
    def repetition_penalty(self, text: str) -> float:
        """Penalty for repeated characters/bigrams"""
        penalty = 0.0
        
        # Check for repeated characters
        for i in range(len(text) - 2):
            if text[i] == text[i+1] == text[i+2]:
                penalty += 1
        
        # Check for repeated bigrams
        bigrams = [text[i:i+2] for i in range(len(text) - 1)]
        bigram_counts = Counter(bigrams)
        for count in bigram_counts.values():
            if count > 3:
                penalty += (count - 3) * 0.5
        
        return penalty
    
    def function_word_bonus(self, text: str) -> float:
        """Bonus for function words"""
        function_words = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 
                         'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE']
        
        bonus = 0.0
        text_upper = text.upper()
        for word in function_words:
            if word in text_upper:
                bonus += len(word)
        
        return bonus

def run_multiple_seeds(num_runs: int = 10, 
                       iterations_per_run: int = 200000) -> List[Dict]:
    """Run multiple independent searches"""
    results = []
    scorer = EnhancedScorer()
    
    for run in range(num_runs):
        print(f"\nRun {run + 1}/{num_runs}")
        print("-" * 40)
        
        # Vary temperature schedule
        initial_temp = random.uniform(0.8, 1.2)
        cooling_rate = random.uniform(0.9999, 0.99995)
        
        # Initialize homophonic solver
        homophonic = AnchorConstrainedHomophonic(ANCHORS)
        
        # Run annealing
        best_pt, best_mapping = homophonic.simulated_annealing(
            K4_CIPHERTEXT,
            lambda x: scorer.score_with_constraints(x),
            max_iterations=iterations_per_run,
            initial_temp=initial_temp,
            cooling_rate=cooling_rate
        )
        
        # Calculate score
        non_anchor_text = extract_non_anchor_text(best_pt)
        score = scorer.score_with_constraints(non_anchor_text)
        
        result = {
            'plaintext': best_pt,
            'mapping': best_mapping,
            'score': score,
            'temp': initial_temp,
            'cooling': cooling_rate
        }
        
        results.append(result)
        print(f"Score: {score:.2f}")
        print(f"Preview: {best_pt[:40]}...")
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return results

def build_consensus_mapping(top_results: List[Dict], 
                           consensus_threshold: float = 0.8) -> Dict[str, str]:
    """Build consensus mapping from top results"""
    # Collect all mappings
    mapping_votes = defaultdict(lambda: defaultdict(int))
    
    for result in top_results:
        mapping = result['mapping']
        for ct_symbol, pt_letter in mapping.items():
            mapping_votes[ct_symbol][pt_letter] += 1
    
    # Build consensus
    consensus = {}
    frozen = set()
    
    for ct_symbol, votes in mapping_votes.items():
        total_votes = sum(votes.values())
        for pt_letter, count in votes.items():
            if count / total_votes >= consensus_threshold:
                consensus[ct_symbol] = pt_letter
                frozen.add(ct_symbol)
                break
    
    print(f"\nConsensus mapping: {len(consensus)} symbols frozen")
    print(f"Frozen symbols: {frozen}")
    
    return consensus, frozen

def extract_non_anchor_text(text: str) -> str:
    """Extract text outside anchor positions"""
    locked_positions = set()
    for anchor, (start, end) in ANCHORS.items():
        for i in range(start, end + 1):
            locked_positions.add(i)
    
    non_anchor = []
    for i, char in enumerate(text):
        if i not in locked_positions:
            non_anchor.append(char)
    
    return ''.join(non_anchor)

def rerun_with_consensus(consensus: Dict[str, str], 
                        frozen: Set[str],
                        iterations: int = 200000) -> Dict:
    """Rerun with consensus mapping partially frozen"""
    print("\nRerunning with consensus mapping...")
    
    scorer = EnhancedScorer()
    homophonic = AnchorConstrainedHomophonic(ANCHORS)
    
    # Initialize mapping with consensus
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    current_mapping = consensus.copy()
    
    # Fill in unfrozen mappings randomly
    used_pt = set(consensus.values())
    available_pt = [c for c in alphabet if c not in used_pt]
    unfrozen_ct = [c for c in alphabet if c not in frozen]
    
    random.shuffle(available_pt)
    for ct, pt in zip(unfrozen_ct, available_pt):
        if ct not in current_mapping:
            current_mapping[ct] = pt
    
    # Custom annealing that respects frozen mappings
    temperature = 1.0
    cooling_rate = 0.99995
    best_mapping = current_mapping.copy()
    best_score = -float('inf')
    
    for iteration in range(iterations):
        # Only swap unfrozen symbols
        if len(unfrozen_ct) >= 2:
            k1, k2 = random.sample(unfrozen_ct, 2)
            
            # Swap
            new_mapping = current_mapping.copy()
            new_mapping[k1], new_mapping[k2] = new_mapping[k2], new_mapping[k1]
            
            # Score
            pt = homophonic.decrypt_with_anchors(K4_CIPHERTEXT, new_mapping)
            non_anchor = extract_non_anchor_text(pt)
            score = scorer.score_with_constraints(non_anchor)
            
            # Accept/reject
            delta = score - best_score
            if delta > 0 or random.random() < np.exp(delta / temperature):
                current_mapping = new_mapping
                if score > best_score:
                    best_score = score
                    best_mapping = current_mapping.copy()
        
        temperature *= cooling_rate
        
        if iteration % 50000 == 0:
            print(f"  Iteration {iteration}: Best score = {best_score:.3f}")
    
    # Get final plaintext
    final_pt = homophonic.decrypt_with_anchors(K4_CIPHERTEXT, best_mapping)
    
    return {
        'plaintext': final_pt,
        'mapping': best_mapping,
        'score': best_score,
        'consensus_used': True
    }

def null_protection_tests(best_mapping: Dict[str, str]) -> Dict:
    """Run null protection tests"""
    print("\nRunning null protection tests...")
    
    homophonic = AnchorConstrainedHomophonic(ANCHORS)
    scorer = EnhancedScorer()
    
    results = {}
    
    # Test 1: Anchor-locked nulls
    print("  1. Anchor-locked null test...")
    shuffled_ct = list(K4_CIPHERTEXT)
    locked_positions = set()
    for anchor, (start, end) in ANCHORS.items():
        for i in range(start, end + 1):
            locked_positions.add(i)
    
    # Shuffle non-anchor positions
    non_anchor_positions = [i for i in range(len(shuffled_ct)) if i not in locked_positions]
    non_anchor_chars = [shuffled_ct[i] for i in non_anchor_positions]
    random.shuffle(non_anchor_chars)
    
    for i, pos in enumerate(non_anchor_positions):
        shuffled_ct[pos] = non_anchor_chars[i]
    
    shuffled_ct_str = ''.join(shuffled_ct)
    
    # Try to fit the shuffled version
    null_pt, null_mapping = homophonic.simulated_annealing(
        shuffled_ct_str,
        lambda x: scorer.score_with_constraints(x),
        max_iterations=50000
    )
    
    null_score = scorer.score_with_constraints(extract_non_anchor_text(null_pt))
    results['anchor_locked_null'] = null_score
    
    # Test 2: Random CT test
    print("  2. Random CT test...")
    random_ct = ''.join(random.choices(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), k=97))
    random_pt = homophonic.decrypt_with_anchors(random_ct, best_mapping)
    random_score = scorer.score_with_constraints(extract_non_anchor_text(random_pt))
    results['random_ct'] = random_score
    
    return results

def main():
    """Main stabilization workflow"""
    print("=" * 80)
    print("HOMOPHONIC STABILIZATION AND CONSENSUS BUILDING")
    print("=" * 80)
    
    # Step 1: Multiple runs
    print("\nStep 1: Running multiple seeds...")
    results = run_multiple_seeds(num_runs=5, iterations_per_run=100000)
    
    # Step 2: Build consensus from top 3
    print("\nStep 2: Building consensus mapping...")
    top_results = results[:3]
    consensus, frozen = build_consensus_mapping(top_results)
    
    # Step 3: Rerun with consensus
    print("\nStep 3: Optimizing with consensus...")
    refined = rerun_with_consensus(consensus, frozen, iterations=100000)
    
    # Step 4: Null protection
    print("\nStep 4: Null protection tests...")
    null_results = null_protection_tests(refined['mapping'])
    
    # Final report
    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    
    print(f"\nBest score: {refined['score']:.2f}")
    print(f"Null score (anchor-locked): {null_results['anchor_locked_null']:.2f}")
    print(f"Random CT score: {null_results['random_ct']:.2f}")
    
    print(f"\nPlaintext:")
    pt = refined['plaintext']
    print(f"  [0:21]: {pt[0:21]}")
    print(f"  [21:34]: {pt[21:34]} (anchors)")
    print(f"  [34:63]: {pt[34:63]}")
    print(f"  [63:74]: {pt[63:74]} (anchors)")
    print(f"  [74:97]: {pt[74:97]}")
    
    # Save results
    output = {
        'plaintext': refined['plaintext'],
        'mapping': refined['mapping'],
        'score': refined['score'],
        'null_tests': null_results,
        'consensus_symbols': len(consensus),
        'top_scores': [r['score'] for r in results[:5]]
    }
    
    with open('stabilized_homophonic.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\n✅ Results saved to stabilized_homophonic.json")

if __name__ == "__main__":
    main()