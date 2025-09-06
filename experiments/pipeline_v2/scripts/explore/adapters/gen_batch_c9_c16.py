#!/usr/bin/env python3
"""
Batch implementation of Campaigns C9-C16.
High-impact Explore campaigns with various generation strategies.
"""

import random
import hashlib
import string
import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
import re

# Anchor positions
ANCHOR_POSITIONS = {
    "EAST": 21,
    "NORTHEAST": 25, 
    "BERLINCLOCK": 63
}

# Masked narrative terms (to exclude from generation)
MASKED_TERMS = [
    "DIAL", "SET", "COURSE", "TRUE", "READ", "SEE", "NOTE",
    "SIGHT", "OBSERVE", "MERIDIAN", "DECLINATION", "BEARING", "LINE"
]

# Function words for scoring
FUNCTION_WORDS = [
    "THE", "AND", "OF", "TO", "IN", "IS", "IT", "BE", "AS", "AT",
    "BY", "FOR", "ON", "OR", "IF", "AN", "BUT", "CAN", "HAD", "HER"
]


class C9_PCFG_Generator:
    """Campaign C9: PCFG Imperative Grammar Generator (PIGG)"""
    
    def __init__(self, seed: int = 1337):
        random.seed(seed)
        
        # Simple PCFG rules
        self.rules = {
            "S": [["VP"], ["VP", "CC", "VP"]],
            "VP": [["VERB", "DET", "NOUN"], ["VERB", "NOUN"], ["VERB", "PP"]],
            "PP": [["PREP", "DET", "NOUN"], ["PREP", "NOUN"]],
            "CC": [["AND"], ["OR"], ["BUT"]],
            "DET": [["THE"], ["A"], ["YOUR"]],
            "VERB": [["FIND"], ["MOVE"], ["TURN"], ["WALK"], ["LOOK"]],
            "NOUN": [["PATH"], ["WALL"], ["DOOR"], ["STEP"], ["MARK"]],
            "PREP": [["TO"], ["AT"], ["BY"], ["ON"], ["IN"]]
        }
        
    def generate(self, symbol: str = "S", max_depth: int = 3) -> List[str]:
        """Generate from PCFG starting at symbol."""
        if max_depth == 0 or symbol not in self.rules:
            return [symbol]
        
        # Choose random expansion
        expansion = random.choice(self.rules[symbol])
        result = []
        
        for sym in expansion:
            result.extend(self.generate(sym, max_depth - 1))
        
        return result
    
    def generate_head(self, seed: int) -> str:
        """Generate a head with PCFG and corridor constraints."""
        random.seed(seed)
        
        # Generate base text
        words = self.generate("S", max_depth=4)
        text = ''.join(words)
        
        # Ensure corridor anchors
        text = list(text[:75].ljust(75, 'X'))
        
        # Place anchors
        text[21:25] = list("EAST")
        text[25:34] = list("NORTHEAST")
        if len(text) >= 74:
            text[63:74] = list("BERLINCLOCK")
        
        return ''.join(text[:75])


class C10_CorpusNgram_Generator:
    """Campaign C10: Corpus-Adapted n-gram Generator (CANG)"""
    
    def __init__(self, seed: int = 1337):
        random.seed(seed)
        
        # Simplified n-gram model (would be trained on surveying corpus)
        # Using K1-K3 plaintexts as proxy
        self.corpus = (
            "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
            "ITWASTOTALLYINVISIBLESHOWSTHISISWASPOSSIBLETHEYDUSEDTHEEARTHSMAGNETICFIELD"
        )
        
        # Build trigram model
        self.trigrams = defaultdict(list)
        for i in range(len(self.corpus) - 2):
            prefix = self.corpus[i:i+2]
            next_char = self.corpus[i+2]
            self.trigrams[prefix].append(next_char)
    
    def generate_head(self, seed: int) -> str:
        """Generate head using n-gram model."""
        random.seed(seed)
        
        # Start with random bigram
        text = random.choice(list(self.trigrams.keys()))
        
        # Generate using trigrams
        while len(text) < 75:
            prefix = text[-2:]
            if prefix in self.trigrams:
                next_char = random.choice(self.trigrams[prefix])
                text += next_char
            else:
                text += random.choice(string.ascii_uppercase)
        
        # Insert corridor anchors
        text = list(text[:75])
        text[21:25] = list("EAST")
        text[25:34] = list("NORTHEAST")
        text[63:74] = list("BERLINCLOCK")
        
        return ''.join(text)


class C11_AnchorEcho_Generator:
    """Campaign C11: Anchor-Echo / Palindrome Templates (AEPT)"""
    
    def generate_head(self, seed: int) -> str:
        """Generate head with palindromic echoes around anchors."""
        random.seed(seed)
        
        text = list('X' * 75)
        
        # Place anchors
        text[21:25] = list("EAST")
        text[25:34] = list("NORTHEAST")
        text[63:74] = list("BERLINCLOCK")
        
        # Create echoes (simplified palindromes)
        # Before EAST
        if random.random() > 0.5:
            text[17:21] = list("TSAE")  # Reverse of EAST
        
        # After NORTHEAST
        if random.random() > 0.5:
            text[34:38] = list("TRON")  # Partial reverse
        
        # Around BERLINCLOCK
        if random.random() > 0.5:
            text[59:63] = list("KCOL")  # Partial reverse
        
        # Fill remaining with pattern
        for i in range(75):
            if text[i] == 'X':
                # Use consonant/vowel pattern
                if i % 3 == 0:
                    text[i] = random.choice("AEIOU")
                else:
                    text[i] = random.choice("BCDFGHJKLMNPQRSTVWXYZ")
        
        return ''.join(text)


class C12_DeBruijn_Generator:
    """Campaign C12: de Bruijn Grid Walk Constraints (DBGW)"""
    
    def __init__(self):
        # Pre-computed de Bruijn sequence for alphabet subset
        self.debruijn = "ABACADAEAFAGAHAIAJAKALAMANAOAPAQARASATAUAVAWAXAYAZ"
    
    def generate_head(self, seed: int) -> str:
        """Generate head using de Bruijn walk."""
        random.seed(seed)
        
        # Start at random position in de Bruijn sequence
        start = random.randint(0, len(self.debruijn) - 1)
        
        text = []
        for i in range(75):
            idx = (start + i) % len(self.debruijn)
            text.append(self.debruijn[idx])
        
        # Override with anchors
        text[21:25] = list("EAST")
        text[25:34] = list("NORTHEAST")
        text[63:74] = list("BERLINCLOCK")
        
        return ''.join(text)


class C13_FunctionWord_Generator:
    """Campaign C13: Function-Word Maximizer (FWM)"""
    
    def generate_head(self, seed: int) -> str:
        """Generate head maximizing function word density."""
        random.seed(seed)
        
        # Start with function words
        words = []
        text_len = 0
        
        while text_len < 60:  # Leave room for anchors
            word = random.choice(FUNCTION_WORDS)
            if text_len + len(word) < 60:
                words.append(word)
                text_len += len(word)
        
        # Join and pad
        text = ''.join(words)
        text = list(text[:75].ljust(75, 'X'))
        
        # Place anchors
        text[21:25] = list("EAST")
        text[25:34] = list("NORTHEAST")
        text[63:74] = list("BERLINCLOCK")
        
        return ''.join(text)


class C14_MI_Anchor_Generator:
    """Campaign C14: MI-Guided Anchor Context (MIGAC)"""
    
    def __init__(self):
        # Simplified MI scores (would be computed from corpus)
        self.mi_scores = {
            ('E', 'A'): 0.8,
            ('A', 'S'): 0.7,
            ('S', 'T'): 0.9,
            ('N', 'O'): 0.6,
            ('O', 'R'): 0.7,
            ('T', 'H'): 0.9
        }
    
    def generate_head(self, seed: int) -> str:
        """Generate head maximizing MI around anchors."""
        random.seed(seed)
        
        text = list('X' * 75)
        
        # Place anchors
        text[21:25] = list("EAST")
        text[25:34] = list("NORTHEAST")  
        text[63:74] = list("BERLINCLOCK")
        
        # Fill context with high-MI bigrams
        for i in range(75):
            if text[i] == 'X':
                if i > 0:
                    # Look for high MI with previous char
                    prev = text[i-1]
                    best_char = 'A'
                    best_mi = 0
                    
                    for next_char in string.ascii_uppercase:
                        bigram = (prev, next_char)
                        if bigram in self.mi_scores:
                            if self.mi_scores[bigram] > best_mi:
                                best_mi = self.mi_scores[bigram]
                                best_char = next_char
                    
                    text[i] = best_char
                else:
                    text[i] = random.choice(string.ascii_uppercase)
        
        return ''.join(text)


class C15_POS_HMM_Generator:
    """Campaign C15: POS HMM Tag-Conditioned Generator (HTG)"""
    
    def __init__(self):
        # Simplified POS patterns from imperative register
        self.pos_patterns = [
            ["VB", "DT", "NN"],
            ["VB", "IN", "DT", "NN"],
            ["VB", "CC", "VB"],
            ["DT", "NN", "VBZ", "JJ"]
        ]
        
        # Word lists by POS
        self.words_by_pos = {
            "VB": ["FIND", "TURN", "WALK", "MOVE"],
            "DT": ["THE", "A", "YOUR"],
            "NN": ["PATH", "DOOR", "WALL", "MARK"],
            "IN": ["TO", "AT", "IN", "BY"],
            "CC": ["AND", "OR", "BUT"],
            "VBZ": ["IS", "HAS", "GOES"],
            "JJ": ["DARK", "LONG", "HIGH"]
        }
    
    def generate_head(self, seed: int) -> str:
        """Generate head following POS pattern."""
        random.seed(seed)
        
        # Choose pattern
        pattern = random.choice(self.pos_patterns)
        
        # Generate words
        words = []
        for pos in pattern * 10:  # Repeat pattern
            if pos in self.words_by_pos:
                words.append(random.choice(self.words_by_pos[pos]))
        
        text = ''.join(words)
        text = list(text[:75].ljust(75, 'X'))
        
        # Place anchors
        text[21:25] = list("EAST")
        text[25:34] = list("NORTHEAST")
        text[63:74] = list("BERLINCLOCK")
        
        return ''.join(text)


class C16_TailCohesion_Generator:
    """Campaign C16: Tail-Head Cohesion Probe (THCP)"""
    
    def __init__(self):
        # Tail starts with "THEJOY..."
        self.tail_start = "THEJOY"
        
        # Bigram scores for cohesion
        self.bigram_scores = {
            "TH": 0.9, "HE": 0.8, "EJ": 0.2, "JO": 0.3, "OY": 0.4
        }
    
    def generate_head(self, seed: int) -> str:
        """Generate head optimizing tail boundary cohesion."""
        random.seed(seed)
        
        text = list('X' * 75)
        
        # Place anchors
        text[21:25] = list("EAST")
        text[25:34] = list("NORTHEAST")
        text[63:74] = list("BERLINCLOCK")
        
        # Optimize boundary (indices 73-74)
        # Want high cohesion with "TH" of "THEJOY"
        text[73] = 'O'  # Forms "OT" with tail
        text[74] = 'F'  # Forms "FT" with tail
        
        # Fill remaining to support cohesion
        for i in range(75):
            if text[i] == 'X':
                if i < 73:
                    # Build toward boundary
                    text[i] = random.choice("OFTHEIN")
                else:
                    text[i] = random.choice(string.ascii_uppercase)
        
        return ''.join(text)


def run_batch_campaigns(base_dir: Path, campaigns: List[str], seed: int = 1337):
    """Run batch of campaigns C9-C16."""
    
    generators = {
        "C9": C9_PCFG_Generator(),
        "C10": C10_CorpusNgram_Generator(),
        "C11": C11_AnchorEcho_Generator(),
        "C12": C12_DeBruijn_Generator(),
        "C13": C13_FunctionWord_Generator(),
        "C14": C14_MI_Anchor_Generator(),
        "C15": C15_POS_HMM_Generator(),
        "C16": C16_TailCohesion_Generator()
    }
    
    campaign_names = {
        "C9": "PIGG_PCFG",
        "C10": "CANG_CorpusNgram",
        "C11": "AEPT_AnchorEcho",
        "C12": "DBGW_DeBruijn",
        "C13": "FWM_FunctionWord",
        "C14": "MIGAC_MI_Anchor",
        "C15": "HTG_POS_HMM",
        "C16": "THCP_TailCohesion"
    }
    
    for campaign_id in campaigns:
        if campaign_id not in generators:
            print(f"Skipping unknown campaign: {campaign_id}")
            continue
        
        print(f"\nGenerating Campaign {campaign_id}: {campaign_names[campaign_id]}")
        
        generator = generators[campaign_id]
        heads = []
        
        # Generate 100 heads
        for i in range(100):
            head_seed = seed + i
            
            if hasattr(generator, 'generate_head'):
                text = generator.generate_head(head_seed)
            else:
                text = "X" * 75  # Fallback
            
            head = {
                "label": f"{campaign_id}_{i:03d}",
                "text": text,
                "metadata": {
                    "campaign": campaign_id,
                    "method": campaign_names[campaign_id],
                    "seed": head_seed
                }
            }
            heads.append(head)
        
        # Save output
        output_dir = base_dir / f"runs/2025-01-06-explore-ideas-{campaign_id}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output = {
            "campaign": f"{campaign_id}_{campaign_names[campaign_id]}",
            "date": "2025-01-06",
            "description": f"Campaign {campaign_id}: {campaign_names[campaign_id]}",
            "seed": seed,
            "total_heads": len(heads),
            "heads": heads
        }
        
        output_file = output_dir / f"heads_{campaign_id.lower()}.json"
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"  Generated {len(heads)} heads")
        print(f"  Saved to: {output_file}")
        
        # Create manifest
        manifest = {
            "campaign": campaign_id,
            "file": str(output_file),
            "hash": hashlib.sha256(json.dumps(output, sort_keys=True).encode()).hexdigest()[:16],
            "heads": len(heads)
        }
        
        manifest_file = output_dir / "MANIFEST.sha256"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Generate campaigns C9-C16")
    parser.add_argument("--campaigns", nargs='+',
                       default=["C9", "C10", "C11", "C12", "C13", "C14", "C15", "C16"],
                       help="Campaigns to run")
    parser.add_argument("--base-dir",
                       default="experiments/pipeline_v2",
                       help="Base directory")
    parser.add_argument("--seed", type=int, default=1337,
                       help="Random seed")
    
    args = parser.parse_args()
    
    run_batch_campaigns(Path(args.base_dir), args.campaigns, args.seed)


if __name__ == "__main__":
    main()