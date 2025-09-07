#!/usr/bin/env python3
"""
Gap-Aware Generator for v5.2.2
Generates content specifically sized for G1 (21 chars) and G2 (29 chars).
Avoids placing any content in anchor spans.
"""

import json
import random
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Function words set
FUNCTION_WORDS = {
    'THE', 'OF', 'AND', 'TO', 'IN', 'IS', 'ARE', 'WAS',
    'THEN', 'THERE', 'HERE', 'WITH', 'AT', 'BY', 'WE'
}

# Gap specifications
GAP_SPECS = {
    "G1": {"start": 0, "end": 20, "length": 21},
    "G2": {"start": 34, "end": 62, "length": 29}
}

class GapAwareGenerator:
    """Generates heads with content sized for gaps between anchors."""
    
    def __init__(self):
        # G1 templates (≤21 chars including spaces)
        self.g1_templates = [
            # Pattern: VERB THE NOUN [PREP]
            {"text": "SET THE LINE TRUE", "f_words": 1, "length": 17, "has_verb": True},
            {"text": "SET THE LINE TO TRUE", "f_words": 2, "length": 20, "has_verb": True},
            {"text": "READ THE DIAL", "f_words": 1, "length": 13, "has_verb": True},
            {"text": "SIGHT THE MARK", "f_words": 1, "length": 14, "has_verb": True},
            {"text": "NOTE THE ANGLE", "f_words": 1, "length": 14, "has_verb": True},
            {"text": "TRACE THE ARC", "f_words": 1, "length": 13, "has_verb": True},
            {"text": "FIND THE COURSE", "f_words": 1, "length": 15, "has_verb": True},
            {"text": "MARK THE POINT", "f_words": 1, "length": 14, "has_verb": True},
            {"text": "FOLLOW THE GRID", "f_words": 1, "length": 15, "has_verb": True},
            {"text": "APPLY THE CORRECTION", "f_words": 1, "length": 20, "has_verb": True},
            {"text": "REDUCE TO THE TRUE", "f_words": 2, "length": 18, "has_verb": True},
            {"text": "BRING TO THE MERIDIAN", "f_words": 2, "length": 21, "has_verb": True}
        ]
        
        # G2 templates (≤29 chars including spaces)
        self.g2_templates = [
            # Pattern: [PREP] VERB THE NOUN AND/THEN ...
            {"text": "AND THEN READ THE COURSE", "f_words": 3, "length": 24, "has_verb": True},
            {"text": "AND THEN SET THE DIAL", "f_words": 3, "length": 21, "has_verb": True},
            {"text": "TO THE MERIDIAN AND READ", "f_words": 3, "length": 24, "has_verb": True},
            {"text": "BY THE DIAL AND THEN NOTE", "f_words": 4, "length": 25, "has_verb": True},
            {"text": "AT THE STATION THEN READ", "f_words": 3, "length": 24, "has_verb": True},
            {"text": "OF THE LINE AND THEN MARK", "f_words": 4, "length": 25, "has_verb": True},
            {"text": "IN THE FIELD AND WE OBSERVE", "f_words": 4, "length": 27, "has_verb": True},
            {"text": "WITH THE ANGLE THEN SIGHT", "f_words": 3, "length": 25, "has_verb": True},
            {"text": "DECLINATION AND THEN READ", "f_words": 2, "length": 25, "has_verb": True},
            {"text": "THE TRUE BEARING AND NOTE", "f_words": 2, "length": 25, "has_verb": True},
            {"text": "HERE THE COURSE AND WE SET", "f_words": 4, "length": 26, "has_verb": True},
            {"text": "THERE THE MARK TO THE DIAL", "f_words": 4, "length": 26, "has_verb": True}
        ]
        
        # Vocabulary for substitutions
        self.nouns = ["LINE", "DIAL", "MARK", "GRID", "ARC", "ANGLE", "POINT", "COURSE", 
                      "BEARING", "MERIDIAN", "STATION", "FIELD", "PLATE"]
        self.verbs = ["SET", "READ", "SIGHT", "NOTE", "TRACE", "FIND", "MARK", "FOLLOW",
                      "APPLY", "REDUCE", "BRING", "OBSERVE", "CORRECT"]
    
    def count_function_words(self, text: str) -> int:
        """Count function words in text."""
        words = text.upper().split()
        return sum(1 for w in words if w in FUNCTION_WORDS)
    
    def select_g1_content(self, seed: int) -> Dict:
        """Select content for G1 gap (21 chars)."""
        random.seed(seed)
        
        # Select template
        template = random.choice(self.g1_templates)
        
        # Optional: substitute vocabulary
        text = template["text"]
        if random.random() > 0.7:
            # Replace a noun
            for noun in self.nouns:
                if noun in text:
                    candidates = [n for n in self.nouns if n != noun and len(n) <= len(noun)]
                    if candidates:
                        replacement = random.choice(candidates)
                        text = text.replace(noun, replacement, 1)
                        break
        
        # Ensure fits in G1
        if len(text) > 21:
            text = text[:21].rstrip()
        
        return {
            "text": text,
            "f_words": self.count_function_words(text),
            "length": len(text),
            "gap": "G1"
        }
    
    def select_g2_content(self, seed: int) -> Dict:
        """Select content for G2 gap (29 chars)."""
        random.seed(seed + 1000)  # Different seed space
        
        # Select template
        template = random.choice(self.g2_templates)
        
        # Optional: substitute vocabulary
        text = template["text"]
        if random.random() > 0.7:
            for noun in self.nouns:
                if noun in text:
                    candidates = [n for n in self.nouns if n != noun and len(n) <= len(noun)]
                    if candidates:
                        replacement = random.choice(candidates)
                        text = text.replace(noun, replacement, 1)
                        break
        
        # Ensure fits in G2
        if len(text) > 29:
            text = text[:29].rstrip()
        
        return {
            "text": text,
            "f_words": self.count_function_words(text),
            "length": len(text),
            "gap": "G2"
        }
    
    def generate_head(self, label: str, seed: int) -> Dict:
        """Generate a complete head with gap-aware content."""
        
        # Generate content for each gap
        g1 = self.select_g1_content(seed)
        g2 = self.select_g2_content(seed)
        
        # Create 75-char canvas
        canvas = [' '] * 75
        
        # Place G1 content (0-20)
        for i, char in enumerate(g1["text"]):
            if i < 21:
                canvas[i] = char
        
        # Anchors will go at 21-24 (EAST), 25-33 (NORTHEAST), 63-73 (BERLINCLOCK)
        # Leave these blank for now
        
        # Place G2 content (34-62)
        for i, char in enumerate(g2["text"]):
            if 34 + i <= 62:
                canvas[34 + i] = char
        
        # Construct head text (without anchors for now)
        head_text = ''.join(canvas[:74]).rstrip()
        
        # Calculate metrics
        total_f_words = g1["f_words"] + g2["f_words"]
        
        # Check for TRUE keyword
        has_true = "TRUE" in g1["text"] or "TRUE" in g2["text"]
        
        return {
            "label": label,
            "seed": seed,
            "head_text": head_text,
            "g1": g1,
            "g2": g2,
            "total_f_words": total_f_words,
            "has_true": has_true,
            "gap_lengths": {
                "g1": g1["length"],
                "g2": g2["length"]
            }
        }
    
    def generate_batch(self, n_heads: int, start_seed: int = 1337) -> List[Dict]:
        """Generate a batch of gap-aware heads."""
        
        heads = []
        for i in range(n_heads):
            label = f"HEAD_{i+1:03d}_v522"
            seed = start_seed + i * 1000
            head = self.generate_head(label, seed)
            heads.append(head)
        
        return heads

def test_generator():
    """Test the gap-aware generator."""
    
    generator = GapAwareGenerator()
    
    print("Gap-Aware Generator Test")
    print("=" * 80)
    print("Generating heads with content sized for:")
    print("  G1: [0-20] (21 chars)")
    print("  G2: [34-62] (29 chars)")
    print("  Anchors: EAST[21-24], NORTHEAST[25-33], BERLINCLOCK[63-73]")
    print("=" * 80)
    
    # Generate test heads
    heads = generator.generate_batch(n_heads=5, start_seed=1337)
    
    for head in heads:
        print(f"\n{head['label']}:")
        print(f"G1: '{head['g1']['text']}' (len={head['g1']['length']}, f={head['g1']['f_words']})")
        print(f"G2: '{head['g2']['text']}' (len={head['g2']['length']}, f={head['g2']['f_words']})")
        print(f"Total f-words: {head['total_f_words']}")
        print(f"Has TRUE: {head['has_true']}")
        
        # Show layout with gaps marked
        layout = head['head_text']
        print(f"\nLayout (74 chars):")
        print(layout)
        print("0" + " "*20 + "^" + " "*3 + "^" + " "*8 + "^" + " "*29 + "^" + " "*10 + "^")
        print(" "*21 + "EAST" + " " + "NORTHEAST" + " "*29 + "BERLINCLOCK")
    
    # Summary
    avg_f_words = sum(h['total_f_words'] for h in heads) / len(heads)
    with_true = sum(1 for h in heads if h['has_true'])
    
    print("\n" + "=" * 80)
    print("Summary:")
    print(f"  Average f-words (in gaps): {avg_f_words:.1f}")
    print(f"  With TRUE keyword: {with_true}/{len(heads)}")
    print(f"  All have G1 ≤21 chars: {all(h['gap_lengths']['g1'] <= 21 for h in heads)}")
    print(f"  All have G2 ≤29 chars: {all(h['gap_lengths']['g2'] <= 29 for h in heads)}")

if __name__ == "__main__":
    test_generator()