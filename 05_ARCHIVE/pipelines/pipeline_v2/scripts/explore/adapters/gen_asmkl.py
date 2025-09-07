#!/usr/bin/env python3
"""
Campaign C7: Anchor-Solved Multi-Class Key Lift (ASMKL)
Solve per-class residues at anchors for lawful cipher schedules.
"""

import random
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import json

# K4 ciphertext (97 characters)
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Anchor positions and expected plaintext
ANCHORS = {
    "EAST": (21, 25),
    "NORTHEAST": (25, 34),
    "BERLINCLOCK": (63, 74)
}

# Anchor indices for forced residues
ANCHOR_INDICES = list(range(21, 25)) + list(range(25, 34)) + list(range(63, 74))


class MultiClassCipher:
    """Multi-class Vigenère/Beaufort/Variant-Beaufort implementation."""
    
    def __init__(self, family: str, classing: str, period: int, phase: int):
        """
        Initialize cipher with family, classing, period, and phase.
        
        Args:
            family: VIG, BF, or VB
            classing: c6a or c6b
            period: Key period (10-22)
            phase: Phase offset (0 to period-1)
        """
        self.family = family
        self.classing = classing
        self.period = period
        self.phase = phase
        self.key = [None] * period  # To be filled with residues
        
    def get_class(self, index: int) -> int:
        """Get class for position based on classing scheme."""
        if self.classing == "c6a":
            # 6-class alternating
            return index % 6
        else:  # c6b
            # 6-class with different pattern
            return (index // 2) % 6
    
    def solve_anchor_residues(self) -> bool:
        """
        Solve for key residues that produce correct anchors.
        
        Returns:
            True if solution found, False if conflicts
        """
        # Expected plaintext at anchor positions
        expected = "EASTNORTHEASTXXXXXXXXXXXXXXXXXXXXXXXXXXXBERLINCLOCK"
        
        for idx in ANCHOR_INDICES:
            if idx >= len(K4_CIPHERTEXT):
                continue
                
            ct_char = K4_CIPHERTEXT[idx]
            pt_char = expected[idx] if idx < len(expected) else 'X'
            
            if pt_char == 'X':
                continue
            
            # Calculate required key residue
            ct_val = ord(ct_char) - ord('A')
            pt_val = ord(pt_char) - ord('A')
            
            key_pos = (idx + self.phase) % self.period
            
            if self.family == "VIG":
                # Vigenère: PT = (CT - K) mod 26
                required = (ct_val - pt_val) % 26
                if required == 0:  # Forbid K=0 for VIG
                    return False
            elif self.family == "BF":
                # Beaufort: PT = (K - CT) mod 26
                required = (pt_val + ct_val) % 26
            else:  # VB
                # Variant Beaufort: PT = (CT + K) mod 26
                required = (pt_val - ct_val) % 26
                if required == 0:  # Forbid K=0 for VB
                    return False
            
            # Check for conflicts
            if self.key[key_pos] is not None and self.key[key_pos] != required:
                return False  # Collision detected
            
            self.key[key_pos] = required
        
        return True
    
    def fill_free_residues(self, seed: int):
        """Fill remaining key positions with random residues."""
        random.seed(seed)
        
        for i in range(self.period):
            if self.key[i] is None:
                # Sample uniformly, avoiding 0 for VIG/VB if needed
                if self.family in ["VIG", "VB"]:
                    self.key[i] = random.randint(1, 25)
                else:
                    self.key[i] = random.randint(0, 25)
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext using the solved key."""
        plaintext = []
        
        for i, char in enumerate(ciphertext):
            if char not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                plaintext.append(char)
                continue
            
            ct_val = ord(char) - ord('A')
            key_val = self.key[(i + self.phase) % self.period]
            
            if self.family == "VIG":
                pt_val = (ct_val - key_val) % 26
            elif self.family == "BF":
                pt_val = (key_val - ct_val) % 26
            else:  # VB
                pt_val = (ct_val + key_val) % 26
            
            plaintext.append(chr(pt_val + ord('A')))
        
        return ''.join(plaintext)


def generate_asmkl_heads(
    num_heads: int = 100,
    families: List[str] = ["VIG", "BF", "VB"],
    classings: List[str] = ["c6a", "c6b"],
    periods: List[int] = None,
    seed: int = 1337
) -> List[Dict]:
    """
    Generate ASMKL heads with anchor-solved keys.
    
    Args:
        num_heads: Number of heads to generate
        families: Cipher families to test
        classings: Classing schemes to test
        periods: Key periods to test (default 10-22)
        seed: Random seed
    
    Returns:
        List of candidate heads
    """
    if periods is None:
        periods = list(range(10, 23))
    
    random.seed(seed)
    heads = []
    attempt = 0
    
    while len(heads) < num_heads and attempt < num_heads * 10:
        attempt += 1
        
        # Sample parameters
        family = random.choice(families)
        classing = random.choice(classings)
        period = random.choice(periods)
        phase = random.randint(0, period - 1)
        
        # Create cipher and solve anchors
        cipher = MultiClassCipher(family, classing, period, phase)
        
        if not cipher.solve_anchor_residues():
            continue  # Skip if conflicts
        
        # Fill free residues
        cipher.fill_free_residues(seed + attempt)
        
        # Decrypt
        plaintext = cipher.decrypt(K4_CIPHERTEXT)
        
        # Verify anchors present
        head_text = plaintext[:75]
        
        # Check for anchors
        has_east = "EAST" in head_text[18:28]
        has_northeast = "NORTHEAST" in head_text[22:36]
        has_berlin = "BERLIN" in head_text[60:75]
        
        # Create head entry
        head = {
            "label": f"ASMKL_{len(heads):03d}",
            "text": head_text,
            "metadata": {
                "family": family,
                "classing": classing,
                "period": period,
                "phase": phase,
                "key": cipher.key,
                "anchors_ok": has_east and has_northeast and has_berlin,
                "seed": seed + attempt
            }
        }
        heads.append(head)
    
    return heads


def run_campaign_c7(output_dir: Path, seed: int = 1337):
    """
    Run Campaign C7: ASMKL testing.
    
    Args:
        output_dir: Directory for output files
        seed: Random seed
    """
    print("Campaign C7: Anchor-Solved Multi-Class Key Lift (ASMKL)")
    print(f"  Families: VIG, BF, VB")
    print(f"  Classings: c6a, c6b")
    print(f"  Periods: 10-22")
    
    # Generate heads
    heads = generate_asmkl_heads(num_heads=100, seed=seed)
    
    # Count statistics
    family_counts = {"VIG": 0, "BF": 0, "VB": 0}
    anchors_ok_count = 0
    
    for head in heads:
        family_counts[head["metadata"]["family"]] += 1
        if head["metadata"]["anchors_ok"]:
            anchors_ok_count += 1
    
    print(f"\nGenerated {len(heads)} heads:")
    for family, count in family_counts.items():
        print(f"  {family}: {count}")
    print(f"  Anchors OK: {anchors_ok_count}/{len(heads)}")
    
    # Create output structure
    output = {
        "campaign": "C7_ASMKL",
        "date": "2025-01-06",
        "description": "Anchor-Solved Multi-Class Key Lift",
        "hypothesis": "Solve per-class residues at anchors for lawful cipher schedules",
        "parameters": {
            "families": ["VIG", "BF", "VB"],
            "classings": ["c6a", "c6b"],
            "periods": list(range(10, 23))
        },
        "seed": seed,
        "total_heads": len(heads),
        "family_distribution": family_counts,
        "anchors_ok": anchors_ok_count,
        "heads": heads
    }
    
    # Save output
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "heads_c7_asmkl.json"
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nOutput saved to: {output_file}")
    
    # Create manifest
    manifest = {
        "campaign": "C7",
        "file": str(output_file),
        "hash": hashlib.sha256(json.dumps(output, sort_keys=True).encode()).hexdigest()[:16],
        "heads": len(heads),
        "anchors_ok": anchors_ok_count
    }
    
    manifest_file = output_dir / "MANIFEST.sha256"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return heads


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Generate ASMKL heads")
    parser.add_argument("--output",
                       default="experiments/pipeline_v2/runs/2025-01-06-explore-ideas-C7",
                       help="Output directory")
    parser.add_argument("--seed", type=int, default=1337,
                       help="Random seed")
    
    args = parser.parse_args()
    
    run_campaign_c7(Path(args.output), args.seed)


if __name__ == "__main__":
    main()