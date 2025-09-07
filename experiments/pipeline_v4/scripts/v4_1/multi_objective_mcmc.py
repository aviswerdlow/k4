#!/usr/bin/env python3
"""
Multi-objective MCMC for language-first head optimization.
Operates in blinded space with language-focused objectives.
"""

import random
import math
import json
import hashlib
from typing import List, Dict, Tuple, Optional, Set
from pathlib import Path
import numpy as np

class MultiObjectiveMCMC:
    """
    Annealed MCMC with multi-objective scoring for linguistic quality.
    """
    
    def __init__(self, config: Optional[Dict] = None, seed: int = 1338):
        """
        Initialize MCMC with configuration.
        
        Args:
            config: Configuration dictionary
            seed: Random seed
        """
        random.seed(seed)
        np.random.seed(seed)
        
        # Default configuration
        self.config = {
            'temperatures': [3.0, 2.0, 1.0, 0.5],
            'moves_per_temp': 500,
            'lambda_ng': 1.0,      # Trigram score weight
            'lambda_fw': 0.5,      # Function word weight
            'lambda_cov': 0.3,     # Coverage weight
            'lambda_verb': 0.4,    # Verb presence weight
            'max_moves': 2000,     # Total accepted moves cap
            'min_fw': 8,          # Minimum function words
            'min_cov': 0.85       # Minimum coverage
        }
        
        if config:
            self.config.update(config)
        
        # Load language resources
        self.function_words = self._load_function_words()
        self.verbs = self._load_verbs()
        self.lexicon = self._load_lexicon()
        self.narrative_tokens = self._load_narrative_tokens()
        self.trigram_model = self._load_trigram_model()
        
        # Track statistics
        self.stats = {
            'proposed': 0,
            'accepted': 0,
            'rejected': 0,
            'best_score': -float('inf'),
            'trajectory': []
        }
    
    def _load_function_words(self) -> Set[str]:
        """Load function word list."""
        return {
            'THE', 'A', 'AN', 'IS', 'ARE', 'WAS', 'BE', 'TO', 'OF', 'AND',
            'IN', 'FOR', 'ON', 'WITH', 'AS', 'BY', 'AT', 'FROM', 'BUT', 'OR',
            'IF', 'THEN', 'SO', 'ALL', 'WOULD', 'THERE', 'THEIR', 'WHAT',
            'WHEN', 'WHERE', 'WHO', 'WILL', 'MORE', 'CAN', 'HAS', 'HAD',
            'HAVE', 'BEEN', 'ONE', 'TWO', 'NO', 'NOT', 'THIS', 'THAT',
            'IT', 'ITS', 'WE', 'OUR', 'YOU', 'YOUR', 'THEY', 'THEM'
        }
    
    def _load_verbs(self) -> Set[str]:
        """Load verb list."""
        return {
            'SET', 'READ', 'SEE', 'FIND', 'SEEK', 'LOOK', 'APPLY', 'USE',
            'TAKE', 'MAKE', 'TURN', 'CHECK', 'MARK', 'NOTE', 'KEEP', 'HOLD',
            'WATCH', 'WAIT', 'MOVE', 'STEP', 'GO', 'COME', 'BRING', 'SEND',
            'GIVE', 'GET', 'PUT', 'PLACE', 'POINT', 'SHOW', 'TELL', 'ASK',
            'KNOW', 'THINK', 'BELIEVE', 'UNDERSTAND', 'REMEMBER', 'FORGET',
            'START', 'STOP', 'BEGIN', 'END', 'CONTINUE', 'FOLLOW', 'LEAD'
        }
    
    def _load_lexicon(self) -> Set[str]:
        """Load full lexicon for coverage calculation."""
        # Combine all word lists
        lexicon = self.function_words | self.verbs
        
        # Add content words
        content = {
            'PATH', 'WAY', 'COURSE', 'LINE', 'POINT', 'MARK', 'SIGN', 'CODE',
            'KEY', 'LOCK', 'DOOR', 'GATE', 'WALL', 'ROOM', 'HALL', 'STEP',
            'WORD', 'TEXT', 'PAGE', 'BOOK', 'MAP', 'PLAN', 'RULE', 'LAW',
            'TIME', 'HOUR', 'DAY', 'YEAR', 'LIFE', 'DEATH', 'TRUTH', 'LIE',
            'LIGHT', 'DARK', 'SHADOW', 'SUN', 'MOON', 'STAR', 'SKY', 'GROUND',
            'TRUE', 'FALSE', 'RIGHT', 'WRONG', 'GOOD', 'BAD', 'NEW', 'OLD',
            'FIRST', 'LAST', 'NEXT', 'NEAR', 'FAR', 'HIGH', 'LOW', 'FAST'
        }
        
        return lexicon | content
    
    def _load_narrative_tokens(self) -> Set[str]:
        """Load forbidden narrative tokens."""
        return {
            'EAST', 'NORTHEAST', 'NORTHWEST', 'SOUTHEAST', 'SOUTHWEST',
            'NORTH', 'SOUTH', 'WEST', 'BERLIN', 'CLOCK', 'ANGLE', 'JOY'
        }
    
    def _load_trigram_model(self) -> Dict:
        """Load or create simple trigram model."""
        # Simplified trigram model - in real implementation would load from corpus
        return {
            'mean': 0.0,
            'std': 1.0,
            'smoothing': 0.001
        }
    
    def compute_trigram_score(self, text: str, blinded: bool = True) -> float:
        """
        Compute trigram score for text.
        
        Args:
            text: Input text
            blinded: Whether to mask narrative tokens
            
        Returns:
            Z-score of trigram log probability
        """
        if blinded:
            # Mask narrative tokens
            for token in self.narrative_tokens:
                text = text.replace(token, 'XXX')
        
        # Simple approximation - in real implementation would use actual trigram probs
        words = text.split()
        
        # Count common trigrams
        score = 0.0
        for i in range(len(words) - 2):
            trigram = (words[i], words[i+1], words[i+2])
            
            # Reward common patterns
            if trigram[0] in self.function_words and trigram[2] in self.function_words:
                score += 1.0
            if trigram[1] in self.verbs:
                score += 0.5
        
        # Normalize by length
        if len(words) > 2:
            score = score / (len(words) - 2)
        
        # Convert to z-score
        z_score = (score - self.trigram_model['mean']) / self.trigram_model['std']
        
        return z_score
    
    def count_function_words(self, text: str) -> int:
        """Count function words in text."""
        words = text.split()
        return sum(1 for w in words if w in self.function_words)
    
    def has_verb(self, text: str) -> bool:
        """Check if text contains a verb."""
        words = text.split()
        return any(w in self.verbs for w in words)
    
    def calculate_coverage(self, text: str) -> float:
        """Calculate lexicon coverage."""
        words = text.split()
        words = [w for w in words if w and not w.startswith('[')]
        
        if not words:
            return 0.0
        
        matches = sum(1 for w in words if w in self.lexicon)
        return matches / len(words)
    
    def compute_objective(self, text: str) -> float:
        """
        Compute multi-objective score.
        
        Args:
            text: Head text
            
        Returns:
            Combined objective score
        """
        # Compute components
        z_trigram = self.compute_trigram_score(text, blinded=True)
        f_words = self.count_function_words(text)
        coverage = self.calculate_coverage(text)
        has_v = self.has_verb(text)
        
        # Soft ramp for function words
        fw_score = min(1.0, f_words / self.config['min_fw'])
        
        # Combine objectives
        score = (
            self.config['lambda_ng'] * z_trigram +
            self.config['lambda_fw'] * fw_score +
            self.config['lambda_cov'] * coverage +
            self.config['lambda_verb'] * (1.0 if has_v else 0.0)
        )
        
        return score
    
    def propose_move(self, text: str) -> str:
        """
        Propose a random move.
        
        Args:
            text: Current text
            
        Returns:
            Modified text
        """
        words = text.split()
        
        if not words:
            return text
        
        # Choose move type
        move_type = random.choice(['swap', 'insert_fw', 'delete', 'reorder'])
        
        if move_type == 'swap':
            # Synonym swap (simplified - would use real synonyms)
            if len(words) > 0:
                idx = random.randint(0, len(words) - 1)
                if words[idx] not in self.narrative_tokens:
                    # Simple swap with similar word
                    if words[idx] in {'THE', 'A', 'AN'}:
                        words[idx] = random.choice(['THE', 'A', 'AN'])
                    elif words[idx] in self.verbs:
                        words[idx] = random.choice(list(self.verbs))
        
        elif move_type == 'insert_fw' and len(' '.join(words)) < 74:
            # Insert function word
            fw = random.choice(list(self.function_words))
            pos = random.randint(0, len(words))
            words.insert(pos, fw)
        
        elif move_type == 'delete' and len(words) > 10:
            # Delete random word (not verb)
            idx = random.randint(0, len(words) - 1)
            if words[idx] not in self.verbs:
                del words[idx]
        
        elif move_type == 'reorder' and len(words) > 2:
            # Local reorder (±2 positions)
            idx = random.randint(0, len(words) - 1)
            offset = random.choice([-2, -1, 1, 2])
            new_idx = max(0, min(len(words) - 1, idx + offset))
            if idx != new_idx:
                words[idx], words[new_idx] = words[new_idx], words[idx]
        
        new_text = ' '.join(words)
        
        # Truncate if too long
        if len(new_text) > 75:
            new_text = new_text[:75]
            last_space = new_text.rfind(' ')
            if last_space > 60:
                new_text = new_text[:last_space]
        
        return new_text
    
    def accept_move(self, old_score: float, new_score: float, temperature: float) -> bool:
        """
        Metropolis acceptance criterion.
        
        Args:
            old_score: Current score
            new_score: Proposed score
            temperature: Current temperature
            
        Returns:
            Whether to accept the move
        """
        if new_score > old_score:
            return True
        
        # Probabilistic acceptance
        delta = new_score - old_score
        prob = math.exp(delta / temperature)
        return random.random() < prob
    
    def optimize(self, initial_text: str) -> Dict:
        """
        Run MCMC optimization.
        
        Args:
            initial_text: Starting text
            
        Returns:
            Optimization results
        """
        current_text = initial_text
        current_score = self.compute_objective(current_text)
        
        best_text = current_text
        best_score = current_score
        
        accepted_moves = 0
        
        # Annealed MCMC
        for temp in self.config['temperatures']:
            temp_accepted = 0
            
            for _ in range(self.config['moves_per_temp']):
                if accepted_moves >= self.config['max_moves']:
                    break
                
                # Propose move
                proposed_text = self.propose_move(current_text)
                
                # Check narrative tokens
                if any(token in proposed_text for token in self.narrative_tokens):
                    self.stats['rejected'] += 1
                    continue
                
                # Score
                proposed_score = self.compute_objective(proposed_text)
                
                self.stats['proposed'] += 1
                
                # Accept/reject
                if self.accept_move(current_score, proposed_score, temp):
                    current_text = proposed_text
                    current_score = proposed_score
                    accepted_moves += 1
                    temp_accepted += 1
                    self.stats['accepted'] += 1
                    
                    # Update best
                    if current_score > best_score:
                        best_text = current_text
                        best_score = current_score
                        self.stats['best_score'] = best_score
                else:
                    self.stats['rejected'] += 1
                
                # Track trajectory
                if accepted_moves % 100 == 0:
                    self.stats['trajectory'].append({
                        'move': accepted_moves,
                        'score': current_score,
                        'temp': temp,
                        'fw': self.count_function_words(current_text),
                        'cov': self.calculate_coverage(current_text)
                    })
            
            print(f"  Temperature {temp}: {temp_accepted} moves accepted")
            
            if accepted_moves >= self.config['max_moves']:
                break
        
        # Final metrics
        result = {
            'initial_text': initial_text,
            'final_text': best_text,
            'initial_score': self.compute_objective(initial_text),
            'final_score': best_score,
            'coverage_pre': self.calculate_coverage(initial_text),
            'coverage_post': self.calculate_coverage(best_text),
            'f_words_pre': self.count_function_words(initial_text),
            'f_words_post': self.count_function_words(best_text),
            'has_verb_pre': self.has_verb(initial_text),
            'has_verb_post': self.has_verb(best_text),
            'z_trigram_pre': self.compute_trigram_score(initial_text),
            'z_trigram_post': self.compute_trigram_score(best_text),
            'accepted_moves': accepted_moves,
            'stats': self.stats
        }
        
        return result
    
    def batch_optimize(self, heads: List[Dict], output_dir: Path) -> List[Dict]:
        """
        Optimize a batch of heads.
        
        Args:
            heads: List of head dictionaries
            output_dir: Output directory
            
        Returns:
            List of optimized heads
        """
        optimized = []
        
        for i, head in enumerate(heads):
            print(f"\nOptimizing head {i+1}/{len(heads)}: {head['id']}")
            
            # Reset stats
            self.stats = {
                'proposed': 0,
                'accepted': 0,
                'rejected': 0,
                'best_score': -float('inf'),
                'trajectory': []
            }
            
            # Optimize
            result = self.optimize(head['text'])
            
            # Add metadata
            result['id'] = head['id']
            result['seed'] = hashlib.sha256(f"{head['id']}_{i}".encode()).hexdigest()[:8]
            
            # Check acceptance criteria
            result['meets_criteria'] = (
                result['coverage_post'] >= self.config['min_cov'] and
                result['f_words_post'] >= self.config['min_fw'] and
                result['has_verb_post']
            )
            
            optimized.append(result)
            
            # Progress
            print(f"  Initial: fw={result['f_words_pre']}, cov={result['coverage_pre']:.3f}")
            print(f"  Final:   fw={result['f_words_post']}, cov={result['coverage_post']:.3f}")
            print(f"  Meets criteria: {result['meets_criteria']}")
        
        # Save results
        output_file = output_dir / "mcmc_optimized.json"
        with open(output_file, 'w') as f:
            json.dump(optimized, f, indent=2)
        
        print(f"\nSaved {len(optimized)} optimized heads to {output_file}")
        
        return optimized


def main():
    """Test MCMC optimization."""
    
    # Load grammar heads
    input_file = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/experiments/pipeline_v4/runs/track_a_l/grammar_heads_quality.json")
    
    with open(input_file, 'r') as f:
        heads = json.load(f)
    
    print(f"Loaded {len(heads)} quality heads")
    
    # Initialize MCMC
    mcmc = MultiObjectiveMCMC(seed=1338)
    
    # Optimize subset
    subset = heads[:5]  # Test with first 5
    
    output_dir = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/experiments/pipeline_v4/runs/track_a_l")
    optimized = mcmc.batch_optimize(subset, output_dir)
    
    # Summary
    meeting = sum(1 for h in optimized if h['meets_criteria'])
    print(f"\nSummary:")
    print(f"  Optimized: {len(optimized)}")
    print(f"  Meeting criteria: {meeting}/{len(optimized)}")
    
    # Show best
    best = max(optimized, key=lambda h: h['final_score'])
    print(f"\nBest head: {best['id']}")
    print(f"  Text: {best['final_text']}")
    print(f"  Score: {best['final_score']:.3f}")
    print(f"  F-words: {best['f_words_post']}, Coverage: {best['coverage_post']:.3f}")


if __name__ == "__main__":
    main()