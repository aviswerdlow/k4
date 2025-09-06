#!/usr/bin/env python3
"""
Verb-robust MCMC optimization with enhanced objective.
Enforces ≥2 verbs, V...THEN/AND...V pattern, and caps function word bloat.
"""

import json
import random
import hashlib
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import numpy as np

class VerbRobustMCMC:
    """
    Multi-objective MCMC with verb robustness constraints.
    """
    
    def __init__(self, seed: int = 1338):
        """Initialize with enhanced objective weights."""
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        # Enhanced objective weights - boost f-words to maintain ≥10
        self.config = {
            'lambda_ng': 1.0,      # Trigram score
            'lambda_fw': 0.8,      # Function words (increased)
            'lambda_cov': 0.2,     # Coverage
            'lambda_pattern': 0.8, # V...THEN/AND...V pattern
            'lambda_verb': 1.2,    # ≥2 verbs
            'lambda_fw_cap': 0.2,  # Cap function words (reduced)
            'lambda_fratio': 0.3   # Cap f-word ratio (reduced)
        }
        
        # Vocabulary
        self.verbs = [
            'SET', 'READ', 'SEE', 'NOTE', 'SIGHT', 'OBSERVE',
            'FIND', 'APPLY', 'CORRECT', 'REDUCE', 'ALIGN',
            'BRING', 'MARK', 'TRACE', 'FOLLOW', 'CHECK',
            'TURN', 'MOVE', 'WAIT', 'STOP', 'START', 'BEGIN'
        ]
        
        self.function_words = [
            'THE', 'A', 'AN', 'IS', 'ARE', 'WAS', 'BE', 'TO', 'OF', 'AND',
            'IN', 'FOR', 'ON', 'WITH', 'AS', 'BY', 'AT', 'FROM', 'BUT', 'OR',
            'IF', 'THEN', 'SO', 'ALL', 'WOULD', 'THERE', 'THEIR', 'WHAT',
            'HAS', 'HAVE', 'HAD', 'WILL', 'CAN', 'MORE', 'NO', 'NOT', 'THIS',
            'ITS', 'YOUR', 'OUR', 'WE', 'YOU', 'THEY', 'THEM', 'ONE', 'TWO'
        ]
        
        self.content_words = [
            'COURSE', 'LINE', 'TEXT', 'SIGN', 'MARK', 'DIAL', 'PLATE',
            'ERROR', 'DECLINATION', 'BEARING', 'PATH', 'WAY', 'CODE',
            'TIME', 'TRUTH', 'LIGHT', 'DARK', 'SHADOW', 'STEP'
        ]
        
        self.connectors = ['THEN', 'AND']
        
        # Temperature schedule
        self.temperatures = [3.0, 2.0, 1.0, 0.5]
        self.moves_per_temp = 500
    
    def count_verbs(self, text: str) -> int:
        """Count distinct verbs in text."""
        words = text.split()
        seen_verbs = set()
        
        for word in words:
            if word in self.verbs:
                seen_verbs.add(word)
        
        return len(seen_verbs)
    
    def has_verb_pattern(self, text: str) -> bool:
        """Check for V...THEN/AND...V pattern."""
        for connector in self.connectors:
            if connector in text:
                parts = text.split(connector)
                if len(parts) >= 2:
                    # Check for verbs on both sides
                    part1_has_verb = any(v in parts[0] for v in self.verbs)
                    part2_has_verb = any(v in parts[1] for v in self.verbs)
                    if part1_has_verb and part2_has_verb:
                        return True
        return False
    
    def verbs_in_distinct_clauses(self, text: str) -> bool:
        """Check if verbs appear in distinct clauses."""
        # Split by connectors
        parts = text
        for connector in self.connectors:
            parts = parts.replace(connector, '|')
        
        clauses = parts.split('|')
        clauses_with_verbs = 0
        
        for clause in clauses:
            if any(v in clause for v in self.verbs):
                clauses_with_verbs += 1
        
        return clauses_with_verbs >= 2
    
    def count_function_words(self, text: str) -> int:
        """Count function words."""
        words = text.split()
        return sum(1 for w in words if w in self.function_words)
    
    def calculate_coverage(self, text: str) -> float:
        """Calculate vocabulary coverage."""
        all_words = set(self.verbs + self.function_words + 
                       self.content_words + self.connectors)
        
        words = text.split()
        if not words:
            return 0.0
        
        matches = sum(1 for w in words if w in all_words)
        return matches / len(words)
    
    def calculate_trigram_score(self, text: str) -> float:
        """Calculate normalized trigram score."""
        words = text.split()
        if len(words) < 3:
            return 0.0
        
        # Simple trigram scoring (placeholder)
        score = 0.0
        for i in range(len(words) - 2):
            trigram = (words[i], words[i+1], words[i+2])
            # Reward common patterns
            if trigram[1] in ['THE', 'AND', 'THEN']:
                score += 0.1
            if trigram[0] in self.verbs and trigram[1] == 'THE':
                score += 0.2
        
        return min(1.0, score / (len(words) - 2))
    
    def calculate_objective(self, text: str) -> float:
        """
        Calculate enhanced objective with verb robustness.
        
        Score = λ_ng*S_blind + λ_fw*FW + λ_cov*COV + λ_pattern*PAT + λ_verb*V2 
                - λ_fw_cap*max(0, FW - 18) - λ_fratio*max(0, FW/TOK - 0.45)
        """
        words = text.split()
        num_words = len(words)
        
        if num_words == 0:
            return 0.0
        
        # Base metrics
        trigram = self.calculate_trigram_score(text)
        fw_count = self.count_function_words(text)
        coverage = self.calculate_coverage(text)
        
        # Verb metrics
        verb_count = self.count_verbs(text)
        has_pattern = self.has_verb_pattern(text)
        distinct_clauses = self.verbs_in_distinct_clauses(text)
        
        # V2: ≥2 verbs in distinct clauses
        v2 = 1.0 if (verb_count >= 2 and distinct_clauses) else 0.0
        
        # PAT: V...THEN/AND...V pattern
        pat = 1.0 if has_pattern else 0.0
        
        # Normalized f-words (0-1 scale)
        fw_norm = min(1.0, fw_count / 20.0)
        
        # Penalties
        fw_cap_penalty = max(0, fw_count - 18)
        fw_ratio = fw_count / num_words
        fw_ratio_penalty = max(0, fw_ratio - 0.45)
        
        # Combined score
        score = (
            self.config['lambda_ng'] * trigram +
            self.config['lambda_fw'] * fw_norm +
            self.config['lambda_cov'] * coverage +
            self.config['lambda_pattern'] * pat +
            self.config['lambda_verb'] * v2 -
            self.config['lambda_fw_cap'] * fw_cap_penalty / 10.0 -
            self.config['lambda_fratio'] * fw_ratio_penalty
        )
        
        return score
    
    def propose_move(self, text: str) -> str:
        """Propose a move (word swap/replacement)."""
        words = text.split()
        if len(words) < 2:
            return text
        
        move_type = random.choice(['swap', 'replace_verb', 'replace_fw', 'insert_verb'])
        
        if move_type == 'swap':
            # Swap two adjacent words
            if len(words) > 1:
                i = random.randint(0, len(words) - 2)
                words[i], words[i+1] = words[i+1], words[i]
        
        elif move_type == 'replace_verb':
            # Replace a word with a verb
            i = random.randint(0, len(words) - 1)
            # Prefer replacing non-verbs
            if words[i] not in self.verbs:
                words[i] = random.choice(self.verbs)
        
        elif move_type == 'replace_fw':
            # Replace a word with a function word
            i = random.randint(0, len(words) - 1)
            # Don't replace verbs
            if words[i] not in self.verbs:
                words[i] = random.choice(self.function_words)
        
        elif move_type == 'insert_verb':
            # Insert a verb if we have < 2
            if self.count_verbs(' '.join(words)) < 2:
                # Find a good position (after a connector)
                for i, word in enumerate(words):
                    if word in self.connectors and i < len(words) - 1:
                        words.insert(i + 1, random.choice(self.verbs))
                        break
        
        return ' '.join(words)
    
    def optimize_single(self, text: str, label: str = "HEAD") -> Dict:
        """Optimize a single head."""
        current_text = text
        current_score = self.calculate_objective(current_text)
        best_text = current_text
        best_score = current_score
        
        # Initial metrics
        initial_metrics = {
            'verb_count': self.count_verbs(text),
            'has_pattern': self.has_verb_pattern(text),
            'f_words': self.count_function_words(text),
            'coverage': self.calculate_coverage(text)
        }
        
        trajectory = []
        accepted = 0
        rejected = 0
        
        for temp_idx, temperature in enumerate(self.temperatures):
            for move in range(self.moves_per_temp):
                # Propose move
                proposed_text = self.propose_move(current_text)
                proposed_score = self.calculate_objective(proposed_text)
                
                # Metropolis criterion
                delta = proposed_score - current_score
                if delta > 0 or random.random() < np.exp(delta / temperature):
                    current_text = proposed_text
                    current_score = proposed_score
                    accepted += 1
                    
                    if current_score > best_score:
                        best_text = current_text
                        best_score = current_score
                else:
                    rejected += 1
                
                # Log trajectory
                if (move + 1) % 100 == 0:
                    trajectory.append({
                        'move': temp_idx * self.moves_per_temp + move + 1,
                        'score': current_score,
                        'temp': temperature,
                        'verb_count': self.count_verbs(current_text),
                        'fw': self.count_function_words(current_text),
                        'cov': self.calculate_coverage(current_text)
                    })
        
        # Final metrics
        final_metrics = {
            'verb_count': self.count_verbs(best_text),
            'has_pattern': self.has_verb_pattern(best_text),
            'f_words': self.count_function_words(best_text),
            'coverage': self.calculate_coverage(best_text)
        }
        
        # Check if meets criteria
        meets_criteria = (
            final_metrics['verb_count'] >= 2 and
            final_metrics['has_pattern'] and
            final_metrics['f_words'] >= 10 and
            final_metrics['coverage'] >= 0.85
        )
        
        return {
            'initial_text': text,
            'final_text': best_text,
            'initial_score': self.calculate_objective(text),
            'final_score': best_score,
            'initial_metrics': initial_metrics,
            'final_metrics': final_metrics,
            'accepted_moves': accepted,
            'rejected_moves': rejected,
            'trajectory': trajectory,
            'meets_criteria': meets_criteria,
            'id': label
        }
    
    def batch_optimize(self, heads: List[Dict], output_dir: Path = None) -> List[Dict]:
        """Optimize a batch of heads."""
        optimized = []
        
        for i, head in enumerate(heads):
            print(f"\nOptimizing head {i+1}/{len(heads)}: {head['id']}")
            
            # Get text
            text = head.get('text', head.get('final_text', ''))
            
            # Optimize
            result = self.optimize_single(text, head['id'])
            
            # Print progress
            print(f"  Initial: verbs={result['initial_metrics']['verb_count']}, "
                  f"fw={result['initial_metrics']['f_words']}, "
                  f"cov={result['initial_metrics']['coverage']:.3f}")
            print(f"  Final:   verbs={result['final_metrics']['verb_count']}, "
                  f"fw={result['final_metrics']['f_words']}, "
                  f"cov={result['final_metrics']['coverage']:.3f}")
            print(f"  Pattern: {result['final_metrics']['has_pattern']}, "
                  f"Meets criteria: {result['meets_criteria']}")
            
            optimized.append(result)
        
        # Save if output directory provided
        if output_dir:
            output_path = output_dir / "verb_robust_mcmc.json"
            with open(output_path, 'w') as f:
                json.dump(optimized, f, indent=2)
            print(f"\nSaved {len(optimized)} optimized heads to {output_path}")
        
        return optimized


def main():
    """Test verb-robust MCMC."""
    
    # Test heads
    test_heads = [
        {
            'id': 'TEST_0000',
            'text': 'SET THE COURSE THEN READ THE SIGN AND NOTE THE MARK'
        },
        {
            'id': 'TEST_0001', 
            'text': 'FIND THE PATH AND OBSERVE THEN TRACE THE LINE TRUE'
        }
    ]
    
    # Initialize optimizer
    mcmc = VerbRobustMCMC(seed=1338)
    
    # Optimize
    print("Testing verb-robust MCMC optimization...")
    optimized = mcmc.batch_optimize(test_heads)
    
    # Summary
    print("\nSummary:")
    meets = sum(1 for h in optimized if h['meets_criteria'])
    print(f"  Meeting criteria: {meets}/{len(optimized)}")
    
    avg_verbs = sum(h['final_metrics']['verb_count'] for h in optimized) / len(optimized)
    print(f"  Avg verb count: {avg_verbs:.1f}")
    
    with_pattern = sum(1 for h in optimized if h['final_metrics']['has_pattern'])
    print(f"  With pattern: {with_pattern}/{len(optimized)}")


if __name__ == "__main__":
    main()