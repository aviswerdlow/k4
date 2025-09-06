#!/usr/bin/env python3
"""
Sample heads biased toward K1-K3 letter n-grams and word-length profiles.
Report-only analysis of K-style cadence impact.
"""

import json
import random
import hashlib
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict
import sys

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from experiments.pipeline_v2.scripts.explore.blind_text import blind_text
from experiments.pipeline_v2.scripts.explore.run_anchor_modes import compute_ngram_score

# K1-K3 plaintexts from Kryptos
K1_PLAINTEXT = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
K2_PLAINTEXT = "ITWASTOTALLYINVISIBLESHOWSTHISISWASPOSSIBLETHEYDUSEDTHEEARTHSMAGNETICFIELD"
K3_PLAINTEXT = "ONLYWTHATTHEVIRTUALLYDOESYOUCANSEEEXPERENCETHATYOUWILLNOTFINDANYWHERELSE"

# Combine for analysis
K_COMBINED = K1_PLAINTEXT + K2_PLAINTEXT + K3_PLAINTEXT

# Corridor positions (enforced)
CORRIDOR_POSITIONS = {
    "EAST": 21,
    "NORTHEAST": 25,
    "BERLINCLOCK": 63
}

# Masked tokens to avoid
MASKED_TOKENS = [
    "DIAL", "SET", "COURSE", "TRUE", "READ", "SEE", "NOTE", 
    "SIGHT", "OBSERVE", "MERIDIAN", "DECLINATION", "BEARING", "LINE"
]


class KStyleModel:
    """Character model based on K1-K3 statistics."""
    
    def __init__(self):
        # Build frequency models from K texts
        self.char_freq = Counter(K_COMBINED)
        self.bigram_freq = Counter()
        self.trigram_freq = Counter()
        
        for i in range(len(K_COMBINED) - 1):
            self.bigram_freq[K_COMBINED[i:i+2]] += 1
        
        for i in range(len(K_COMBINED) - 2):
            self.trigram_freq[K_COMBINED[i:i+3]] += 1
        
        # Word length distribution (approximate by common patterns)
        self.word_lengths = self._extract_word_lengths()
    
    def _extract_word_lengths(self) -> List[int]:
        """Extract approximate word lengths from K texts."""
        # Common word boundaries in K texts
        patterns = ["THE", "AND", "OF", "TO", "IN", "IS", "WAS", "THAT", "YOU", "CAN"]
        
        lengths = []
        current_len = 0
        
        for i, char in enumerate(K_COMBINED):
            current_len += 1
            
            # Check if we hit a common word boundary
            for pattern in patterns:
                if K_COMBINED[i:i+len(pattern)] == pattern:
                    if current_len > len(pattern):
                        lengths.append(current_len - len(pattern))
                    lengths.append(len(pattern))
                    current_len = 0
                    break
        
        if current_len > 0:
            lengths.append(current_len)
        
        return lengths if lengths else [4, 5, 6, 7, 8]  # Default
    
    def sample_char_biased(self) -> str:
        """Sample a character biased toward K frequencies."""
        chars = list(self.char_freq.keys())
        weights = list(self.char_freq.values())
        
        # Add smoothing for unseen chars
        for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if c not in chars:
                chars.append(c)
                weights.append(1)
        
        return random.choices(chars, weights=weights)[0]
    
    def sample_next_given_context(self, context: str) -> str:
        """Sample next character given context (bigram/trigram)."""
        # Try trigram first
        if len(context) >= 2:
            trigram_context = context[-2:]
            candidates = []
            weights = []
            
            for trigram, count in self.trigram_freq.items():
                if trigram[:2] == trigram_context:
                    candidates.append(trigram[2])
                    weights.append(count)
            
            if candidates:
                return random.choices(candidates, weights=weights)[0]
        
        # Fall back to bigram
        if len(context) >= 1:
            bigram_context = context[-1]
            candidates = []
            weights = []
            
            for bigram, count in self.bigram_freq.items():
                if bigram[0] == bigram_context:
                    candidates.append(bigram[1])
                    weights.append(count)
            
            if candidates:
                return random.choices(candidates, weights=weights)[0]
        
        # Fall back to character frequency
        return self.sample_char_biased()


def generate_k_style_head(model: KStyleModel, seed: int) -> str:
    """Generate a head with K-style cadence and corridor."""
    random.seed(seed)
    
    # Start with K-style prefix
    k_prefixes = [
        "BETWEEN", "ITWAS", "ONLY", "SUBTLE", "TOTALLY", "VIRTUALLY",
        "ABSENCE", "LIGHT", "NUANCE", "INVISIBLE", "POSSIBLE", "MAGNETIC"
    ]
    
    prefix = random.choice(k_prefixes)
    text = prefix
    
    # Build to position 21
    while len(text) < 21:
        next_char = model.sample_next_given_context(text)
        text += next_char
    
    # Ensure exactly 21 chars before EAST
    text = text[:21]
    
    # Add EAST at 21
    text += "EAST"
    
    # Add NORTHEAST at 25
    text += "NORTHEAST"
    
    # Fill to position 63 with K-style generation
    while len(text) < 63:
        next_char = model.sample_next_given_context(text)
        
        # Avoid creating masked tokens
        potential = text + next_char
        skip = False
        for token in MASKED_TOKENS:
            if token in potential[-len(token):]:
                skip = True
                break
        
        if not skip:
            text += next_char
        else:
            text += "X"
    
    # Ensure exactly 63 chars before BERLINCLOCK
    text = text[:63]
    
    # Add BERLINCLOCK at 63
    text += "BERLINCLOCK"
    
    # Fill to 75 if needed
    if len(text) < 75:
        text += "X"
    
    return text[:75]


def sample_k_style_campaign(
    num_heads: int,
    output_file: Path,
    seed: int = 1337
) -> None:
    """
    Generate K-style biased heads for report-only analysis.
    """
    random.seed(seed)
    
    # Build K-style model
    print("Building K-style model from K1-K3 texts...")
    model = KStyleModel()
    
    # Print statistics
    print(f"\nK-text statistics:")
    print(f"  Total chars: {len(K_COMBINED)}")
    print(f"  Unique chars: {len(model.char_freq)}")
    print(f"  Unique bigrams: {len(model.bigram_freq)}")
    print(f"  Unique trigrams: {len(model.trigram_freq)}")
    
    # Top characters
    top_chars = model.char_freq.most_common(10)
    print(f"  Top 10 chars: {', '.join(f'{c}:{n}' for c, n in top_chars)}")
    
    # Generate heads
    heads = []
    
    for i in range(num_heads):
        if i % 20 == 0:
            print(f"Generating head {i+1}/{num_heads}...")
        
        text = generate_k_style_head(model, seed + i)
        
        # Score for metadata
        blinded, _ = blind_text(text, blind_anchors=True, blind_narrative=True)
        ngram_score = compute_ngram_score(blinded)
        
        head = {
            "label": f"K_STYLE_{i:03d}",
            "text": text,
            "metadata": {
                "style": "k_mimic",
                "ngram_score_blinded": ngram_score,
                "corridor_ok": True,
                "anchor_found_east_idx": 21,
                "anchor_found_ne_idx": 25,
                "anchor_found_berlin_idx": 63,
                "seed": seed + i
            }
        }
        heads.append(head)
    
    # Compute corpus hash
    k_hash = hashlib.sha256(K_COMBINED.encode()).hexdigest()[:16]
    
    # Output structure
    output = {
        "campaign": "EXPLORE_K_STYLE_MIMIC",
        "date": "2025-01-06",
        "description": "K1-K3 register mimic with biased sampling (report-only)",
        "seed": seed,
        "k_corpus_hash": k_hash,
        "k_text_lengths": {
            "k1": len(K1_PLAINTEXT),
            "k2": len(K2_PLAINTEXT),
            "k3": len(K3_PLAINTEXT)
        },
        "anchor_positions": CORRIDOR_POSITIONS,
        "masked_tokens": MASKED_TOKENS,
        "total_heads": len(heads),
        "heads": heads
    }
    
    # Write output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nGenerated {len(heads)} K-style heads")
    print(f"Output: {output_file}")
    
    # Print score distribution
    scores = [h["metadata"]["ngram_score_blinded"] for h in heads]
    if scores:
        print(f"\nBlinded n-gram scores:")
        print(f"  Min: {min(scores):.4f}")
        print(f"  Max: {max(scores):.4f}")
        print(f"  Mean: {sum(scores)/len(scores):.4f}")


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Sample K-style heads")
    parser.add_argument("--num", type=int, default=100,
                       help="Number of heads to generate")
    parser.add_argument("--out",
                       default="experiments/pipeline_v2/data/heads_k_style.json",
                       help="Output path")
    parser.add_argument("--seed", type=int, default=1337,
                       help="Random seed")
    
    args = parser.parse_args()
    
    sample_k_style_campaign(
        args.num,
        Path(args.out),
        args.seed
    )


if __name__ == "__main__":
    main()