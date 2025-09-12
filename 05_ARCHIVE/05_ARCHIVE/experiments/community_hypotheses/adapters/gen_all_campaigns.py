#!/usr/bin/env python3
"""
Generate all community hypothesis campaigns (C1-C6).
Batch runner for all decryption methods.
"""

import json
import hashlib
import random
import string
from pathlib import Path
from typing import Dict, List
import sys

# Add current dir to path for imports
sys.path.append(str(Path(__file__).parent))

# K4 ciphertext
K4_CIPHERTEXT = (
    "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
)


def generate_morse_heads(num_heads: int, seed: int) -> List[Dict]:
    """Campaign C3: Morse masking with 3/4-length code."""
    random.seed(seed)
    heads = []
    
    # Morse patterns
    morse_patterns = [
        "..-..-.-",  # Pattern 1
        "-.-..-..",  # Pattern 2
        "...---...",  # Pattern 3
    ]
    
    for i in range(num_heads):
        # Apply morse-like transformation
        pattern = random.choice(morse_patterns)
        
        # Simple substitution based on morse pattern
        plaintext = []
        for j, char in enumerate(K4_CIPHERTEXT[:75]):
            # Shift based on morse position
            morse_bit = pattern[j % len(pattern)]
            shift = 3 if morse_bit == '.' else 7
            
            char_code = ord(char) - ord('A')
            new_char = chr(((char_code - shift) % 26) + ord('A'))
            plaintext.append(new_char)
        
        text = ''.join(plaintext)
        
        head = {
            "label": f"MORSE_{i:03d}",
            "text": text,
            "metadata": {
                "method": "morse_masking",
                "pattern": pattern,
                "seed": seed + i
            }
        }
        heads.append(head)
    
    return heads


def generate_bigram_polybius_heads(num_heads: int, seed: int) -> List[Dict]:
    """Campaign C4: Internal variant bigram & Row/column Polybius."""
    random.seed(seed)
    heads = []
    
    # Polybius square (5x5)
    polybius = [
        "ABCDE",
        "FGHIK",  # I/J combined
        "LMNOP",
        "QRSTU",
        "VWXYZ"
    ]
    
    for i in range(num_heads):
        # Choose method variant
        use_bigram = random.random() < 0.5
        
        plaintext = []
        
        if use_bigram:
            # Bigram substitution
            for j in range(0, len(K4_CIPHERTEXT[:75]), 2):
                if j + 1 < len(K4_CIPHERTEXT[:75]):
                    char1 = K4_CIPHERTEXT[j]
                    char2 = K4_CIPHERTEXT[j + 1]
                    
                    # Find positions in Polybius
                    for row_idx, row in enumerate(polybius):
                        if char1 in row:
                            r1 = row_idx
                            c1 = row.index(char1)
                        if char2 in row:
                            r2 = row_idx
                            c2 = row.index(char2)
                    
                    # Swap rows/columns
                    try:
                        new1 = polybius[r2][c1]
                        new2 = polybius[r1][c2]
                        plaintext.extend([new1, new2])
                    except:
                        plaintext.extend([char1, char2])
        else:
            # Row/column Polybius
            for char in K4_CIPHERTEXT[:75]:
                # Find position
                found = False
                for row_idx, row in enumerate(polybius):
                    if char in row:
                        col_idx = row.index(char)
                        # Rotate position
                        new_row = (row_idx + 1) % 5
                        new_col = (col_idx + 1) % 5
                        plaintext.append(polybius[new_row][new_col])
                        found = True
                        break
                if not found:
                    plaintext.append(char)
        
        text = ''.join(plaintext)[:75]
        
        head = {
            "label": f"BIGRAM_POLY_{i:03d}",
            "text": text,
            "metadata": {
                "method": "bigram_polybius",
                "variant": "bigram" if use_bigram else "polybius",
                "seed": seed + i
            }
        }
        heads.append(head)
    
    return heads


def generate_time_key_heads(num_heads: int, seed: int) -> List[Dict]:
    """Campaign C5: Time-key schedules."""
    random.seed(seed)
    heads = []
    
    # Time-based key schedules
    time_patterns = [
        "progressive",  # 0, 1, 2, 3, ...
        "hourly",       # 0-23 repeating
        "fibonacci",    # 1, 1, 2, 3, 5, 8, ...
        "prime"         # 2, 3, 5, 7, 11, ...
    ]
    
    for i in range(num_heads):
        pattern = random.choice(time_patterns)
        
        # Generate time-based shifts
        shifts = []
        if pattern == "progressive":
            shifts = [j % 26 for j in range(75)]
        elif pattern == "hourly":
            shifts = [(j % 24) for j in range(75)]
        elif pattern == "fibonacci":
            fib = [1, 1]
            for _ in range(73):
                fib.append((fib[-1] + fib[-2]) % 26)
            shifts = fib
        else:  # prime
            primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
            shifts = [(primes[j % len(primes)]) % 26 for j in range(75)]
        
        # Apply time-based decryption
        plaintext = []
        for j, char in enumerate(K4_CIPHERTEXT[:75]):
            shift = shifts[j]
            char_code = ord(char) - ord('A')
            new_char = chr(((char_code - shift) % 26) + ord('A'))
            plaintext.append(new_char)
        
        text = ''.join(plaintext)
        
        head = {
            "label": f"TIME_KEY_{i:03d}",
            "text": text,
            "metadata": {
                "method": "time_key",
                "pattern": pattern,
                "seed": seed + i
            }
        }
        heads.append(head)
    
    return heads


def generate_letter_shape_heads(num_heads: int, seed: int) -> List[Dict]:
    """Campaign C6: Letter-shape classifier filter."""
    random.seed(seed)
    heads = []
    
    # Letter shape categories
    shape_categories = {
        "round": "OQCDGPRU",
        "angular": "AVWXYZKMN",
        "vertical": "ILTFHJ",
        "mixed": "BEFS"
    }
    
    for i in range(num_heads):
        # Choose shape-based transformation
        category = random.choice(list(shape_categories.keys()))
        shape_chars = shape_categories[category]
        
        # Apply shape-based filtering/transformation
        plaintext = []
        for char in K4_CIPHERTEXT[:75]:
            if char in shape_chars:
                # Transform within category
                idx = shape_chars.index(char)
                new_idx = (idx + 3) % len(shape_chars)
                plaintext.append(shape_chars[new_idx])
            else:
                # Shift by category offset
                offset = list(shape_categories.keys()).index(category)
                char_code = ord(char) - ord('A')
                new_char = chr(((char_code - offset * 5) % 26) + ord('A'))
                plaintext.append(new_char)
        
        text = ''.join(plaintext)
        
        head = {
            "label": f"LETTER_SHAPE_{i:03d}",
            "text": text,
            "metadata": {
                "method": "letter_shape",
                "category": category,
                "seed": seed + i
            }
        }
        heads.append(head)
    
    return heads


def run_all_campaigns(base_dir: Path, seed: int = 1337):
    """Run all community hypothesis campaigns."""
    
    campaigns = [
        ("C3", "morse", generate_morse_heads, 100),
        ("C4", "bigram_polybius", generate_bigram_polybius_heads, 100),
        ("C5", "time_key", generate_time_key_heads, 100),
        ("C6", "letter_shape", generate_letter_shape_heads, 100)
    ]
    
    for campaign_id, name, generator, num_heads in campaigns:
        print(f"\nGenerating Campaign {campaign_id}: {name}")
        
        # Generate heads
        heads = generator(num_heads, seed)
        
        # Create output
        output_dir = base_dir / f"runs/2025-01-06-campaign-{campaign_id.lower()}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output = {
            "campaign": f"{campaign_id}_{name.upper()}",
            "date": "2025-01-06",
            "description": f"Community hypothesis: {name}",
            "method": name,
            "seed": seed,
            "total_heads": len(heads),
            "heads": heads
        }
        
        output_file = output_dir / f"heads_{campaign_id.lower()}_{name}.json"
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
        
        manifest_file = output_dir / f"manifest_{campaign_id.lower()}.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Generate all community hypothesis campaigns")
    parser.add_argument("--base-dir",
                       default="experiments/community_hypotheses",
                       help="Base directory")
    parser.add_argument("--seed", type=int, default=1337,
                       help="Random seed")
    
    args = parser.parse_args()
    
    run_all_campaigns(Path(args.base_dir), args.seed)


if __name__ == "__main__":
    main()