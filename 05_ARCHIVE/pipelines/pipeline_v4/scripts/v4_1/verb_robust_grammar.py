#!/usr/bin/env python3
"""
Verb-robust grammar generator enforcing ≥2 verbs per head.
Generates heads with V...THEN/AND...V pattern for anchor resilience.
"""

import random
from typing import List, Dict, Tuple, Optional
import json
from pathlib import Path

class VerbRobustGrammar:
    """
    Grammar generator enforcing verb robustness for anchor survival.
    """
    
    def __init__(self, seed: int = 1338):
        """Initialize with verb-focused templates and vocabulary."""
        random.seed(seed)
        
        # Core verbs (expanded set for robustness)
        self.verbs = [
            'SET', 'READ', 'SEE', 'NOTE', 'SIGHT', 'OBSERVE',
            'FIND', 'APPLY', 'CORRECT', 'REDUCE', 'ALIGN',
            'BRING', 'MARK', 'TRACE', 'FOLLOW'
        ]
        
        # Content nouns (no anchor words)
        self.nouns = [
            'COURSE', 'LINE', 'TEXT', 'SIGN', 'MARK',
            'DIAL', 'PLATE', 'ERROR', 'DECLINATION', 'BEARING',
            'PATH', 'WAY', 'CODE', 'TIME', 'TRUTH'
        ]
        
        # Modifiers for variety
        self.modifiers = ['TRUE', 'CLEAR', 'FULL', 'FAST', 'SURE']
        
        # Connectors
        self.connectors = ['THEN', 'AND']
        
        # Function words for padding
        self.function_words = [
            'THE', 'A', 'TO', 'OF', 'IN', 'FOR', 'WITH', 'BY', 'AT',
            'IS', 'ARE', 'WAS', 'BE', 'HAS', 'HAVE', 'ALL', 'YOUR', 'ITS'
        ]
        
        # Verb-robust templates enforcing V...THEN/AND...V pattern
        self.templates = [
            "{V1} THE {N1} THEN {V2} THE {N2}",
            "{V1} THE {N1} AND {V2} THE {N2}",
            "SET THE {N1} TRUE THEN READ THE {N2}",
            "{V1} THEN {V2} AND NOTE THE {N}",
            "APPLY THE {N1} THEN CORRECT THE {N2}",
            "READ THE {N1} AND SEE THE {N2}",
            "{V1} THE {N} THEN {V2} AND {V3}",
            "FIND THE {N1} THEN MARK THE {N2}",
            "OBSERVE THE {N1} AND TRACE THE {N2}",
            "REDUCE {N1} THEN ALIGN THE {N2}",
            "{V1} AND {V2} THEN {V3} THE {N}",
            "FIRST {V1} THE {N1} THEN {V2} THE {N2}",
            "IF {V1} THEN {V2} THE {N} AND {V3}",
            "{V1} {M} THEN {V2} THE {N} {M}",
            "BEFORE {V1} THE {N1} THEN {V2} THE {N2}"
        ]
        
        # Recovery verbs for repair phase
        self.recovery_verbs = ['READ', 'SEE', 'NOTE']
    
    def fill_template(self, template: str) -> Tuple[str, int, bool]:
        """
        Fill a template with random vocabulary.
        
        Returns:
            (text, verb_count, has_pattern)
        """
        result = template
        verb_count = 0
        
        # Track verbs used
        used_verbs = []
        
        # Fill verb slots
        for i in range(1, 4):
            v_slot = f"{{V{i}}}"
            if v_slot in result:
                verb = random.choice(self.verbs)
                result = result.replace(v_slot, verb)
                used_verbs.append(verb)
                verb_count += 1
        
        # Fill general verb slot
        while "{V}" in result:
            verb = random.choice(self.verbs)
            result = result.replace("{V}", verb, 1)
            used_verbs.append(verb)
            verb_count += 1
        
        # Fill noun slots
        for i in range(1, 3):
            n_slot = f"{{N{i}}}"
            if n_slot in result:
                noun = random.choice(self.nouns)
                result = result.replace(n_slot, noun)
        
        # Fill general noun slot
        while "{N}" in result:
            noun = random.choice(self.nouns)
            result = result.replace("{N}", noun, 1)
        
        # Fill modifier slots
        while "{M}" in result:
            mod = random.choice(self.modifiers)
            result = result.replace("{M}", mod, 1)
        
        # Check for V...THEN/AND...V pattern
        has_pattern = False
        for connector in self.connectors:
            if connector in result:
                parts = result.split(connector)
                if len(parts) >= 2:
                    # Check if verbs on both sides
                    part1_has_verb = any(v in parts[0] for v in self.verbs)
                    part2_has_verb = any(v in parts[1] for v in self.verbs)
                    if part1_has_verb and part2_has_verb:
                        has_pattern = True
                        break
        
        return result, verb_count, has_pattern
    
    def count_verbs(self, text: str) -> int:
        """Count distinct verbs in text."""
        words = text.split()
        verb_count = 0
        seen_verbs = set()
        
        for word in words:
            if word in self.verbs and word not in seen_verbs:
                verb_count += 1
                seen_verbs.add(word)
        
        return verb_count
    
    def has_verb_pattern(self, text: str) -> bool:
        """Check if text has V...THEN/AND...V pattern."""
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
    
    def count_function_words(self, text: str) -> int:
        """Count function words in text."""
        words = text.split()
        return sum(1 for w in words if w in self.function_words)
    
    def calculate_coverage(self, text: str) -> float:
        """Calculate vocabulary coverage."""
        all_words = set(self.verbs + self.nouns + self.modifiers + 
                       self.connectors + self.function_words)
        
        words = text.split()
        if not words:
            return 0.0
        
        matches = sum(1 for w in words if w in all_words)
        return matches / len(words)
    
    def generate_head(self, min_length: int = 68, max_length: int = 75) -> Dict:
        """
        Generate a verb-robust head with ≥2 verbs and pattern.
        """
        attempts = 0
        best_head = None
        best_score = 0
        
        while attempts < 100:
            # Choose template
            template = random.choice(self.templates)
            
            # Fill template
            text, verb_count, has_pattern = self.fill_template(template)
            
            # Add function words to reach length
            while len(text) < min_length and len(text) < max_length:
                fw = random.choice(self.function_words)
                if random.random() < 0.5:
                    text = fw + ' ' + text
                else:
                    text = text + ' ' + fw
            
            # Truncate if too long
            if len(text) > max_length:
                text = text[:max_length]
                # Truncate at word boundary
                last_space = text.rfind(' ')
                if last_space > min_length:
                    text = text[:last_space]
            
            # Count metrics
            verb_count = self.count_verbs(text)
            has_pattern = self.has_verb_pattern(text)
            f_words = self.count_function_words(text)
            coverage = self.calculate_coverage(text)
            
            # Check hard constraints
            if verb_count < 2:
                attempts += 1
                continue
            
            if not has_pattern:
                attempts += 1
                continue
            
            # Score head
            score = (verb_count * 10 + 
                    (20 if has_pattern else 0) +
                    min(f_words, 15) +
                    coverage * 10)
            
            if score > best_score:
                best_score = score
                best_head = {
                    'text': text,
                    'length': len(text),
                    'verb_count': verb_count,
                    'has_pattern': has_pattern,
                    'f_words': f_words,
                    'coverage': coverage,
                    'score': score
                }
            
            # Check if meets all requirements
            if (verb_count >= 2 and has_pattern and 
                f_words >= 10 and coverage >= 0.85):
                return best_head
            
            attempts += 1
        
        return best_head if best_head else {
            'text': "READ THE COURSE THEN SEE THE SIGN AND NOTE THE MARK",
            'verb_count': 3,
            'has_pattern': True,
            'f_words': 6,
            'coverage': 1.0
        }
    
    def generate_batch(self, n: int = 10) -> List[Dict]:
        """Generate batch of verb-robust heads."""
        heads = []
        
        for i in range(n):
            head = self.generate_head()
            head['id'] = f"VROBUST_{i:04d}"
            heads.append(head)
            
            if (i + 1) % 10 == 0:
                print(f"Generated {i + 1}/{n} verb-robust heads...")
        
        return heads
    
    def filter_quality(self, heads: List[Dict]) -> List[Dict]:
        """Filter heads meeting all requirements."""
        quality = []
        
        for head in heads:
            if (head['verb_count'] >= 2 and
                head['has_pattern'] and
                head['f_words'] >= 10 and
                head['coverage'] >= 0.85):
                quality.append(head)
        
        return quality


def main():
    """Test verb-robust generation."""
    
    gen = VerbRobustGrammar(seed=1338)
    
    print("Generating verb-robust heads...")
    heads = gen.generate_batch(n=20)
    
    # Filter quality
    quality = gen.filter_quality(heads)
    print(f"\nQuality heads: {len(quality)}/{len(heads)}")
    
    # Show examples
    print("\nExample verb-robust heads:")
    for head in heads[:5]:
        print(f"\n{head['id']}:")
        print(f"  Text: {head['text']}")
        print(f"  Verbs: {head['verb_count']}, Pattern: {head['has_pattern']}")
        print(f"  F-words: {head['f_words']}, Coverage: {head['coverage']:.3f}")
    
    # Stats
    print(f"\nStatistics:")
    print(f"  Total generated: {len(heads)}")
    print(f"  Meeting requirements: {len(quality)} ({100*len(quality)/len(heads):.1f}%)")
    print(f"  Avg verb count: {sum(h['verb_count'] for h in heads)/len(heads):.1f}")
    print(f"  With pattern: {sum(1 for h in heads if h['has_pattern'])}/{len(heads)}")
    print(f"  Avg F-words: {sum(h['f_words'] for h in heads)/len(heads):.1f}")
    
    # Save
    output_dir = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/experiments/pipeline_v4/runs/track_a_l")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "verb_robust_heads.json", 'w') as f:
        json.dump(heads, f, indent=2)
    
    print(f"\nSaved to {output_dir / 'verb_robust_heads.json'}")


if __name__ == "__main__":
    main()