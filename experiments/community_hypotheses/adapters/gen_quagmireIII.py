#!/usr/bin/env python3
"""
Quagmire III cipher adapter for K4 decryption attempts.
Tests various scrambled alphabets and offset patterns.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import random

# K4 ciphertext (97 characters)
K4_CIPHERTEXT = (
    "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
)

class QuagmireIII:
    """Quagmire III cipher implementation."""
    
    def __init__(self, alphabet: str, key: str = None):
        """
        Initialize with a specific alphabet permutation.
        
        Args:
            alphabet: 26-character scrambled alphabet
            key: Optional key sequence for offsets
        """
        if len(alphabet) != 26 or len(set(alphabet)) != 26:
            raise ValueError("Alphabet must be 26 unique characters")
        
        self.alphabet = alphabet.upper()
        self.standard = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.key = key or ""
        
        # Build cipher table
        self.table = self._build_table()
    
    def _build_table(self) -> List[str]:
        """Build the Quagmire III cipher table."""
        table = []
        for i in range(26):
            # Rotate alphabet for each row
            row = self.alphabet[i:] + self.alphabet[:i]
            table.append(row)
        return table
    
    def decrypt(self, ciphertext: str, offsets: List[int] = None) -> str:
        """
        Decrypt using Quagmire III with given offsets.
        
        Args:
            ciphertext: Text to decrypt
            offsets: List of offsets for each position (mod 26)
        
        Returns:
            Decrypted plaintext
        """
        ciphertext = ciphertext.upper()
        
        if not offsets:
            # Default to zero offsets
            offsets = [0] * len(ciphertext)
        
        plaintext = []
        for i, char in enumerate(ciphertext):
            if char not in self.standard:
                plaintext.append(char)
                continue
            
            # Get offset for this position
            offset = offsets[i % len(offsets)] % 26
            
            # Find position in offset row
            row = self.table[offset]
            pos = row.index(char) if char in row else 0
            
            # Map back to standard alphabet
            plaintext.append(self.standard[pos])
        
        return ''.join(plaintext)


def generate_offset_pattern(pattern_type: str, length: int, seed: int = None) -> List[int]:
    """
    Generate offset patterns for Quagmire III.
    
    Args:
        pattern_type: Type of pattern (fixed, progressive, fibonacci, prime)
        length: Length of pattern needed
        seed: Random seed for reproducibility
    
    Returns:
        List of offsets
    """
    if seed is not None:
        random.seed(seed)
    
    if pattern_type == "fixed":
        # Single offset repeated
        offset = random.randint(0, 25)
        return [offset] * length
    
    elif pattern_type == "progressive":
        # 0, 1, 2, 3, ... mod 26
        return [i % 26 for i in range(length)]
    
    elif pattern_type == "fibonacci":
        # Fibonacci sequence mod 26
        fib = [0, 1]
        for i in range(2, length):
            fib.append((fib[-1] + fib[-2]) % 26)
        return fib[:length]
    
    elif pattern_type == "prime":
        # Prime numbers mod 26
        primes = []
        num = 2
        while len(primes) < length:
            is_prime = all(num % i != 0 for i in range(2, int(num**0.5) + 1))
            if is_prime:
                primes.append(num % 26)
            num += 1
        return primes
    
    else:
        # Random offsets
        return [random.randint(0, 25) for _ in range(length)]


def check_anchors(plaintext: str) -> Dict[str, bool]:
    """
    Check if expected anchors appear in decrypted text.
    
    Args:
        plaintext: Decrypted text to check
    
    Returns:
        Dict of anchor presence
    """
    anchors = {
        "EAST": False,
        "NORTHEAST": False,
        "BERLINCLOCK": False
    }
    
    # Check for anchors at expected positions (allowing some tolerance)
    if len(plaintext) >= 25:
        # EAST around position 21
        if "EAST" in plaintext[18:26]:
            anchors["EAST"] = True
    
    if len(plaintext) >= 34:
        # NORTHEAST around position 25
        if "NORTHEAST" in plaintext[22:35]:
            anchors["NORTHEAST"] = True
    
    if len(plaintext) >= 74:
        # BERLINCLOCK around position 63
        if "BERLINCLOCK" in plaintext[58:75]:
            anchors["BERLINCLOCK"] = True
    
    return anchors


def generate_quagmire_heads(
    num_heads: int,
    alphabets: List[str],
    offset_patterns: List[str],
    seed: int = 1337
) -> List[Dict]:
    """
    Generate decryption attempts using Quagmire III.
    
    Args:
        num_heads: Number of heads to generate
        alphabets: List of alphabet permutations to try
        offset_patterns: List of offset pattern types
        seed: Random seed
    
    Returns:
        List of decryption attempt results
    """
    random.seed(seed)
    heads = []
    
    for i in range(num_heads):
        # Select alphabet and pattern
        alphabet = random.choice(alphabets)
        pattern_type = random.choice(offset_patterns)
        
        # Generate offsets
        offsets = generate_offset_pattern(pattern_type, 97, seed + i)
        
        # Initialize cipher
        cipher = QuagmireIII(alphabet)
        
        # Decrypt K4
        plaintext = cipher.decrypt(K4_CIPHERTEXT, offsets)
        
        # Check anchors
        anchor_check = check_anchors(plaintext)
        
        # Create head entry
        head = {
            "label": f"QUAGMIRE_{i:03d}",
            "text": plaintext[:75],  # First 75 chars for pipeline
            "metadata": {
                "method": "quagmire_iii",
                "alphabet": alphabet,
                "pattern_type": pattern_type,
                "offset_sample": offsets[:10],  # First 10 offsets
                "anchors_found": anchor_check,
                "anchor_count": sum(anchor_check.values()),
                "seed": seed + i,
                "full_plaintext": plaintext  # Store full result
            }
        }
        heads.append(head)
    
    return heads


def run_campaign_c1(output_dir: Path, seed: int = 1337):
    """
    Run Campaign C1: Quagmire III testing.
    
    Args:
        output_dir: Directory for output files
        seed: Random seed
    """
    # Load campaign config
    catalog_path = Path(__file__).parent.parent / "catalog" / "campaign_C1_quagmire.json"
    with open(catalog_path) as f:
        config = json.load(f)
    
    # Extract parameters
    alphabets = config["parameters"]["alphabet_variations"]
    patterns = config["parameters"]["offset_patterns"]
    num_heads = config["parameters"]["num_heads"]
    
    print(f"Campaign C1: Quagmire III with Scrambled Alphabet")
    print(f"  Alphabets: {len(alphabets)} variations")
    print(f"  Patterns: {patterns}")
    print(f"  Heads: {num_heads}")
    
    # Generate heads
    heads = generate_quagmire_heads(num_heads, alphabets, patterns, seed)
    
    # Count anchor matches
    anchor_counts = {"0": 0, "1": 0, "2": 0, "3": 0}
    for head in heads:
        count = head["metadata"]["anchor_count"]
        anchor_counts[str(count)] += 1
    
    print(f"\nAnchor distribution:")
    for count, num in anchor_counts.items():
        print(f"  {count} anchors: {num} heads")
    
    # Create output structure
    output = {
        "campaign": "C1_QUAGMIRE_III",
        "date": "2025-01-06",
        "description": "Quagmire III cipher with scrambled alphabets",
        "method": "quagmire_iii",
        "parameters": config["parameters"],
        "seed": seed,
        "total_heads": len(heads),
        "anchor_distribution": anchor_counts,
        "heads": heads
    }
    
    # Save output
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "heads_c1_quagmire.json"
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nOutput saved to: {output_file}")
    
    # Create manifest
    manifest = {
        "campaign": "C1",
        "file": str(output_file),
        "hash": hashlib.sha256(json.dumps(output, sort_keys=True).encode()).hexdigest()[:16],
        "heads": len(heads),
        "anchor_matches": sum(1 for h in heads if h["metadata"]["anchor_count"] > 0)
    }
    
    manifest_file = output_dir / "manifest_c1.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return heads


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Generate Quagmire III decryption attempts")
    parser.add_argument("--output", 
                       default="experiments/community_hypotheses/runs/2025-01-06-campaign-c1",
                       help="Output directory")
    parser.add_argument("--seed", type=int, default=1337,
                       help="Random seed")
    
    args = parser.parse_args()
    
    run_campaign_c1(Path(args.output), args.seed)


if __name__ == "__main__":
    main()