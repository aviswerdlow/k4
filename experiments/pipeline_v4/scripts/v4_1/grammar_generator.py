#!/usr/bin/env python3
"""
Grammar-first head generator using PCFG templates.
Generates linguistically valid heads BEFORE anchor insertion.
"""

import random
import string
from typing import List, Dict, Tuple, Optional
import json
from pathlib import Path

class GrammarGenerator:
    """
    PCFG-based generator for linguistically valid K4 heads.
    Uses templates with placeholders for anchors.
    """
    
    def __init__(self, seed: int = 1338):
        """Initialize with grammar rules and lexicon."""
        random.seed(seed)
        
        # Function words (high frequency, structure-bearing)
        self.function_words = [
            'THE', 'A', 'AN', 'IS', 'ARE', 'WAS', 'BE', 'TO', 'OF', 'AND',
            'IN', 'FOR', 'ON', 'WITH', 'AS', 'BY', 'AT', 'FROM', 'BUT', 'OR',
            'IF', 'THEN', 'SO', 'ALL', 'WOULD', 'THERE', 'THEIR', 'WHAT',
            'WHEN', 'WHERE', 'WHO', 'WILL', 'MORE', 'CAN', 'HAS', 'HAD',
            'HAVE', 'BEEN', 'ONE', 'TWO', 'NO', 'NOT', 'THIS', 'THAT'
        ]
        
        # Verbs (action words for has_verb requirement)
        self.verbs = [
            'SET', 'READ', 'SEE', 'FIND', 'SEEK', 'LOOK', 'APPLY', 'USE',
            'TAKE', 'MAKE', 'TURN', 'CHECK', 'MARK', 'NOTE', 'KEEP', 'HOLD',
            'WATCH', 'WAIT', 'MOVE', 'STEP', 'GO', 'COME', 'BRING', 'SEND',
            'GIVE', 'GET', 'PUT', 'PLACE', 'POINT', 'SHOW', 'TELL', 'ASK',
            'KNOW', 'THINK', 'BELIEVE', 'UNDERSTAND', 'REMEMBER', 'FORGET'
        ]
        
        # Nouns (content words, avoid anchor terms)
        self.nouns = [
            'PATH', 'WAY', 'COURSE', 'LINE', 'POINT', 'MARK', 'SIGN', 'CODE',
            'KEY', 'LOCK', 'DOOR', 'GATE', 'WALL', 'ROOM', 'HALL', 'STEP',
            'WORD', 'TEXT', 'PAGE', 'BOOK', 'MAP', 'PLAN', 'RULE', 'LAW',
            'TIME', 'HOUR', 'DAY', 'YEAR', 'LIFE', 'DEATH', 'TRUTH', 'LIE',
            'LIGHT', 'DARK', 'SHADOW', 'SUN', 'MOON', 'STAR', 'SKY', 'GROUND'
        ]
        
        # Adjectives/Adverbs
        self.modifiers = [
            'TRUE', 'FALSE', 'RIGHT', 'WRONG', 'GOOD', 'BAD', 'NEW', 'OLD',
            'FIRST', 'LAST', 'NEXT', 'NEAR', 'FAR', 'HIGH', 'LOW', 'FAST',
            'SLOW', 'HARD', 'SOFT', 'CLEAR', 'DARK', 'BRIGHT', 'DIM'
        ]
        
        # Imperatives (command forms)
        self.imperatives = [
            'GO', 'STOP', 'WAIT', 'LOOK', 'SEE', 'FIND', 'SEEK', 'TAKE',
            'KEEP', 'HOLD', 'SET', 'TURN', 'MOVE', 'STEP', 'CHECK', 'MARK'
        ]
        
        # Templates with placeholders
        self.templates = [
            # Imperative + object + modifier
            "{IMP} THE {NOUN} {MOD}",
            "{IMP} {MOD} AND {IMP} {MOD}",
            
            # Set/apply patterns
            "SET THE {NOUN} TO {MOD}",
            "APPLY THE {NOUN} AND {VERB}",
            
            # Conditional patterns
            "IF {NOUN} THEN {VERB} THE {NOUN}",
            "WHEN {MOD} {VERB} THE {NOUN}",
            
            # Compound imperatives
            "{IMP} THEN {IMP} AND {IMP}",
            "{VERB} THE {NOUN} AND {VERB} THE {NOUN}",
            
            # Question patterns
            "WHERE IS THE {NOUN} AND THE {NOUN}",
            "WHAT {VERB} THE {NOUN} {MOD}",
            
            # Directional patterns (using placeholders)
            "{IMP} [DIR1] AND {IMP} [DIR2]",
            "THE {NOUN} IS [DIR1] OF THE {NOUN}",
            
            # Time/sequence patterns
            "FIRST {VERB} THEN {VERB} THE {NOUN}",
            "BEFORE THE {NOUN} {VERB} THE {NOUN}",
            
            # Complex compounds
            "{IMP} THE {NOUN} {MOD} AND {IMP} THE {NOUN} {MOD}",
            "IF THE {NOUN} IS {MOD} THEN {VERB} [DIR1]"
        ]
        
        # Placeholder markers for anchors
        self.placeholders = ['[DIR1]', '[DIR2]', '[NOUN1]', '[NOUN2]']
    
    def generate_from_template(self, template: str) -> str:
        """
        Generate text from a template by filling slots.
        
        Args:
            template: Template string with {TYPE} slots
            
        Returns:
            Generated text with filled slots
        """
        result = template
        
        # Fill each slot type
        replacements = {
            '{IMP}': lambda: random.choice(self.imperatives),
            '{VERB}': lambda: random.choice(self.verbs),
            '{NOUN}': lambda: random.choice(self.nouns),
            '{MOD}': lambda: random.choice(self.modifiers),
            '{FW}': lambda: random.choice(self.function_words)
        }
        
        for pattern, generator in replacements.items():
            while pattern in result:
                result = result.replace(pattern, generator(), 1)
        
        return result
    
    def count_function_words(self, text: str) -> int:
        """Count function words in text."""
        words = text.split()
        return sum(1 for w in words if w in self.function_words)
    
    def has_verb(self, text: str) -> bool:
        """Check if text contains a verb."""
        words = text.split()
        all_verbs = self.verbs + self.imperatives
        return any(w in all_verbs for w in words)
    
    def calculate_coverage(self, text: str, dictionary: set) -> float:
        """Calculate dictionary coverage."""
        words = text.replace('[', ' ').replace(']', ' ').split()
        words = [w for w in words if w and not w.startswith('[')]
        
        if not words:
            return 0.0
        
        matches = sum(1 for w in words if w in dictionary)
        return matches / len(words)
    
    def generate_head(self, min_length: int = 70, max_length: int = 75) -> Dict:
        """
        Generate a linguistically valid head.
        
        Args:
            min_length: Minimum character length
            max_length: Maximum character length
            
        Returns:
            Dict with head text and metrics
        """
        attempts = 0
        best_head = None
        best_score = 0
        
        # Build dictionary for coverage
        dictionary = set(self.function_words + self.verbs + self.nouns + 
                        self.modifiers + self.imperatives)
        
        while attempts < 100:
            # Choose random templates
            num_templates = random.randint(2, 4)
            chosen = random.sample(self.templates, min(num_templates, len(self.templates)))
            
            # Generate from templates
            parts = []
            for template in chosen:
                part = self.generate_from_template(template)
                parts.append(part)
            
            # Combine with punctuation
            if random.random() < 0.3:
                text = ' AND '.join(parts)
            elif random.random() < 0.5:
                text = ' '.join(parts)
            else:
                text = '. '.join(parts) + '.'
            
            # Truncate or pad to length
            if len(text) > max_length:
                # Truncate at word boundary
                text = text[:max_length]
                last_space = text.rfind(' ')
                if last_space > min_length:
                    text = text[:last_space]
            
            if len(text) < min_length:
                # Pad with function words
                while len(text) < min_length:
                    fw = random.choice(self.function_words)
                    if len(text) + len(fw) + 1 <= max_length:
                        text += ' ' + fw
                    else:
                        break
            
            # Calculate metrics
            fw_count = self.count_function_words(text)
            has_v = self.has_verb(text)
            coverage = self.calculate_coverage(text, dictionary)
            
            # Score this head
            score = fw_count * 0.3 + (10 if has_v else 0) + coverage * 20
            
            if score > best_score:
                best_score = score
                best_head = {
                    'text': text,
                    'length': len(text),
                    'f_words': fw_count,
                    'has_verb': has_v,
                    'coverage': coverage,
                    'score': score,
                    'placeholders': [p for p in self.placeholders if p in text]
                }
            
            # Check if good enough
            if fw_count >= 8 and has_v and coverage >= 0.85:
                return best_head
            
            attempts += 1
        
        return best_head
    
    def generate_batch(self, n: int = 10) -> List[Dict]:
        """
        Generate a batch of heads.
        
        Args:
            n: Number of heads to generate
            
        Returns:
            List of head dictionaries
        """
        heads = []
        for i in range(n):
            head = self.generate_head()
            head['id'] = f"GRAMMAR_{i:04d}"
            heads.append(head)
            
            # Progress
            if (i + 1) % 10 == 0:
                print(f"Generated {i + 1}/{n} heads...")
        
        return heads
    
    def filter_quality(self, heads: List[Dict]) -> List[Dict]:
        """
        Filter heads that meet quality thresholds.
        
        Args:
            heads: List of generated heads
            
        Returns:
            Filtered list meeting requirements
        """
        quality = []
        for head in heads:
            if (head['f_words'] >= 8 and 
                head['has_verb'] and 
                head['coverage'] >= 0.85):
                quality.append(head)
        
        return quality
    
    def save_batch(self, heads: List[Dict], output_path: str):
        """Save batch to JSON file."""
        with open(output_path, 'w') as f:
            json.dump(heads, f, indent=2)
        print(f"Saved {len(heads)} heads to {output_path}")


def main():
    """Generate initial batch of grammar-first heads."""
    
    # Initialize generator
    gen = GrammarGenerator(seed=1338)
    
    # Generate batch
    print("Generating grammar-first heads...")
    heads = gen.generate_batch(n=50)
    
    # Filter for quality
    quality = gen.filter_quality(heads)
    print(f"\nQuality heads: {len(quality)}/{len(heads)}")
    
    # Show examples
    print("\nExample heads:")
    for head in quality[:5]:
        print(f"\n{head['id']}:")
        print(f"  Text: {head['text']}")
        print(f"  F-words: {head['f_words']}, Has verb: {head['has_verb']}, Coverage: {head['coverage']:.3f}")
        print(f"  Placeholders: {head['placeholders']}")
    
    # Save
    output_dir = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/experiments/pipeline_v4/runs/track_a_l")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    gen.save_batch(heads, output_dir / "grammar_heads.json")
    gen.save_batch(quality, output_dir / "grammar_heads_quality.json")
    
    # Stats
    print(f"\nStatistics:")
    print(f"  Total generated: {len(heads)}")
    print(f"  Meeting quality: {len(quality)} ({100*len(quality)/len(heads):.1f}%)")
    print(f"  Avg F-words: {sum(h['f_words'] for h in heads)/len(heads):.1f}")
    print(f"  With verb: {sum(1 for h in heads if h['has_verb'])}/{len(heads)}")
    print(f"  Avg coverage: {sum(h['coverage'] for h in heads)/len(heads):.3f}")


if __name__ == "__main__":
    main()