#!/usr/bin/env python3
"""
Extended optimization of homophonic cipher
500K-1M iterations with enhanced scoring
"""

import sys
import os
import json
import random
import numpy as np
from typing import Dict, List, Tuple
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

class ExtendedScorer:
    """Enhanced scoring with phrase detection and token awareness"""
    
    def __init__(self):
        self.base_scorer = LanguageScorer()
        
        # Common English phrases
        self.phrases = [
            'YOU CAN', 'YOU ARE', 'I AM', 'IT IS', 'THEY ARE',
            'WE ARE', 'CAN YOU', 'DO YOU', 'DID YOU', 'WILL YOU',
            'THE KEY', 'THE CODE', 'THE ANSWER', 'LOOK AT', 'FIND THE',
            'GO TO', 'TURN TO', 'SET TO', 'WALK TO', 'MOVE TO',
            'DEGREES', 'TRUE NORTH', 'MAGNETIC', 'BEARING', 'AZIMUTH'
        ]
        
        # Survey-specific phrases
        self.survey_phrases = [
            'GO NORTH', 'GO SOUTH', 'GO EAST', 'GO WEST',
            'TURN LEFT', 'TURN RIGHT', 'SET BEARING', 'TRUE BEARING',
            'MAGNETIC NORTH', 'DEGREES EAST', 'DEGREES WEST',
            'BENCHMARK', 'REFERENCE POINT', 'SURVEY MARKER'
        ]
        
    def enhanced_score(self, text: str) -> float:
        """Score with phrase detection and token awareness"""
        base_score = self.base_scorer.combined_score(text)
        
        # Phrase bonus
        phrase_score = 0
        text_upper = text.upper()
        for phrase in self.phrases:
            if phrase in text_upper:
                phrase_score += len(phrase) * 3
        
        for phrase in self.survey_phrases:
            if phrase in text_upper:
                phrase_score += len(phrase) * 4  # Higher weight for survey phrases
        
        # Penalize excessive repetition
        repetition_penalty = 0
        for i in range(len(text) - 3):
            if text[i:i+2] == text[i+2:i+4]:  # Repeated bigram
                repetition_penalty += 1
        
        # Bonus for sentence-like structure
        structure_bonus = 0
        words = self.base_scorer.find_words(text)
        if len(words) > 5:
            # Check for function words that suggest sentences
            function_words = ['THE', 'AND', 'YOU', 'ARE', 'CAN', 'TO', 'FROM', 'AT']
            found_functions = sum(1 for w in words if w in function_words)
            structure_bonus = found_functions * 5
        
        return base_score + phrase_score - repetition_penalty + structure_bonus

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

def run_extended_optimization(iterations: int = 500000):
    """Run extended optimization with multiple strategies"""
    print("=" * 80)
    print("EXTENDED HOMOPHONIC OPTIMIZATION")
    print("=" * 80)
    
    scorer = ExtendedScorer()
    homophonic = AnchorConstrainedHomophonic(ANCHORS)
    
    best_solutions = []
    
    # Strategy 1: Very long run with slow cooling
    print(f"\nStrategy 1: Long run ({iterations} iterations, slow cooling)")
    print("-" * 40)
    
    best_pt, best_mapping = homophonic.simulated_annealing(
        K4_CIPHERTEXT,
        lambda x: scorer.enhanced_score(x),
        max_iterations=iterations,
        initial_temp=1.5,
        cooling_rate=0.999995  # Very slow cooling
    )
    
    non_anchor = extract_non_anchor_text(best_pt)
    score = scorer.enhanced_score(non_anchor)
    words = scorer.base_scorer.find_words(non_anchor)
    
    best_solutions.append({
        'strategy': 'long_slow_cooling',
        'plaintext': best_pt,
        'mapping': best_mapping,
        'score': score,
        'words': words,
        'iterations': iterations
    })
    
    print(f"Score: {score:.2f}")
    print(f"Words: {len(words)}")
    print(f"Preview: {best_pt[:40]}...")
    
    # Strategy 2: Multiple restarts with consensus
    print(f"\nStrategy 2: Multiple restarts (10 x {iterations//10} iterations)")
    print("-" * 40)
    
    restart_results = []
    for restart in range(10):
        if restart % 2 == 0:
            print(f"  Restart {restart + 1}/10...", end=" ")
        
        # Vary temperature for diversity
        temp = random.uniform(0.8, 2.0)
        cooling = random.uniform(0.9999, 0.99998)
        
        pt, mapping = homophonic.simulated_annealing(
            K4_CIPHERTEXT,
            lambda x: scorer.enhanced_score(x),
            max_iterations=iterations // 10,
            initial_temp=temp,
            cooling_rate=cooling
        )
        
        non_anchor = extract_non_anchor_text(pt)
        score = scorer.enhanced_score(non_anchor)
        restart_results.append({
            'plaintext': pt,
            'mapping': mapping,
            'score': score
        })
        
        if restart % 2 == 0:
            print(f"Score: {score:.2f}")
    
    # Take best from restarts
    restart_results.sort(key=lambda x: x['score'], reverse=True)
    best_restart = restart_results[0]
    
    words = scorer.base_scorer.find_words(extract_non_anchor_text(best_restart['plaintext']))
    
    best_solutions.append({
        'strategy': 'multiple_restarts',
        'plaintext': best_restart['plaintext'],
        'mapping': best_restart['mapping'],
        'score': best_restart['score'],
        'words': words,
        'iterations': iterations
    })
    
    print(f"\nBest restart score: {best_restart['score']:.2f}")
    print(f"Words: {len(words)}")
    
    # Strategy 3: Adaptive temperature (reheat when stuck)
    print(f"\nStrategy 3: Adaptive temperature ({iterations} iterations)")
    print("-" * 40)
    
    # Start from best so far
    best_overall = max(best_solutions, key=lambda x: x['score'])
    current_mapping = best_overall['mapping'].copy()
    
    temperature = 0.5  # Start warm but not hot
    best_score = best_overall['score']
    no_improvement = 0
    
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    for iteration in range(iterations):
        # Swap two random mappings
        k1, k2 = random.sample(list(alphabet), 2)
        new_mapping = current_mapping.copy()
        new_mapping[k1], new_mapping[k2] = new_mapping[k2], new_mapping[k1]
        
        # Decrypt and score
        pt = homophonic.decrypt_with_anchors(K4_CIPHERTEXT, new_mapping)
        non_anchor = extract_non_anchor_text(pt)
        score = scorer.enhanced_score(non_anchor)
        
        # Accept/reject
        delta = score - best_score
        if delta > 0 or random.random() < np.exp(delta / temperature):
            current_mapping = new_mapping
            if score > best_score:
                best_score = score
                best_mapping = current_mapping.copy()
                best_pt = pt
                no_improvement = 0
            else:
                no_improvement += 1
        else:
            no_improvement += 1
        
        # Adaptive temperature
        if no_improvement > 10000:
            # Reheat when stuck
            temperature = min(1.0, temperature * 2)
            no_improvement = 0
        else:
            # Cool down normally
            temperature *= 0.99999
        
        if iteration % 100000 == 0 and iteration > 0:
            print(f"  Iteration {iteration}: Best score = {best_score:.3f}, Temp = {temperature:.6f}")
    
    words = scorer.base_scorer.find_words(extract_non_anchor_text(best_pt))
    
    best_solutions.append({
        'strategy': 'adaptive_temperature',
        'plaintext': best_pt,
        'mapping': best_mapping,
        'score': best_score,
        'words': words,
        'iterations': iterations
    })
    
    print(f"Final score: {best_score:.2f}")
    print(f"Words: {len(words)}")
    
    # Find overall best
    best_solutions.sort(key=lambda x: x['score'], reverse=True)
    champion = best_solutions[0]
    
    print("\n" + "=" * 80)
    print("CHAMPION SOLUTION")
    print("=" * 80)
    
    print(f"\nStrategy: {champion['strategy']}")
    print(f"Score: {champion['score']:.2f}")
    print(f"Words found: {len(champion['words'])}")
    
    print(f"\nPlaintext:")
    pt = champion['plaintext']
    print(f"  [0:21]: {pt[0:21]}")
    print(f"  [21:34]: {pt[21:34]} (anchors)")
    print(f"  [34:63]: {pt[34:63]}")
    print(f"  [63:74]: {pt[63:74]} (anchors)")
    print(f"  [74:97]: {pt[74:97]}")
    
    print(f"\nWords: {', '.join(champion['words'][:20])}")
    
    # Check for phrases
    text_upper = champion['plaintext'].upper()
    found_phrases = []
    for phrase in scorer.phrases + scorer.survey_phrases:
        if phrase in text_upper:
            found_phrases.append(phrase)
    
    if found_phrases:
        print(f"\nPhrases detected: {', '.join(found_phrases)}")
    
    # Save results
    output = {
        'plaintext': champion['plaintext'],
        'mapping': champion['mapping'],
        'score': champion['score'],
        'strategy': champion['strategy'],
        'words': champion['words'],
        'phrases': found_phrases,
        'iterations': champion['iterations'],
        'all_strategies': [
            {
                'strategy': s['strategy'],
                'score': s['score'],
                'words_count': len(s['words'])
            } for s in best_solutions
        ]
    }
    
    with open('optimized_homophonic.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\n✅ Results saved to optimized_homophonic.json")
    
    return champion

def main():
    """Run extended optimization"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extended homophonic optimization')
    parser.add_argument('--iterations', type=int, default=500000,
                       help='Number of iterations (default: 500000)')
    
    args = parser.parse_args()
    
    champion = run_extended_optimization(args.iterations)
    
    # Run token segmentation on best result
    print("\n" + "=" * 80)
    print("TOKEN SEGMENTATION OF CHAMPION")
    print("=" * 80)
    
    from segment_tokens import segment_with_anchors
    
    result = segment_with_anchors(champion['plaintext'], ANCHORS)
    
    print(f"\nToken coverage: {result['token_coverage']:.2%}")
    if result['categories']:
        print("Token categories found:")
        for cat, tokens in result['categories'].items():
            print(f"  {cat}: {', '.join(set(tokens))}")

if __name__ == "__main__":
    main()