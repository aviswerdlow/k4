#!/usr/bin/env python3
"""
Trifid cipher and Eight-cube transposition adapter for K4 decryption attempts.
Tests 3D cipher variants with various orientations and reading orders.
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


class TrifidCipher:
    """Trifid cipher implementation."""
    
    def __init__(self, key: str = None):
        """
        Initialize with a 27-character key.
        
        Args:
            key: 27-character key (26 letters + 1 special)
        """
        if key is None:
            key = "ABCDEFGHIJKLMNOPQRSTUVWXYZ."
        
        if len(key) != 27:
            raise ValueError("Key must be 27 characters")
        
        self.key = key.upper()
        
        # Build 3x3x3 cube
        self.cube = self._build_cube()
        self.char_to_coords = {}
        
        for layer in range(3):
            for row in range(3):
                for col in range(3):
                    char = self.cube[layer][row][col]
                    self.char_to_coords[char] = (layer, row, col)
    
    def _build_cube(self) -> List[List[List[str]]]:
        """Build the 3x3x3 Trifid cube."""
        cube = []
        idx = 0
        
        for layer in range(3):
            layer_grid = []
            for row in range(3):
                row_chars = []
                for col in range(3):
                    row_chars.append(self.key[idx])
                    idx += 1
                layer_grid.append(row_chars)
            cube.append(layer_grid)
        
        return cube
    
    def decrypt(self, ciphertext: str, reading_order: str = "rows") -> str:
        """
        Decrypt using Trifid cipher.
        
        Args:
            ciphertext: Text to decrypt
            reading_order: How to read coordinates (rows, columns, spiral)
        
        Returns:
            Decrypted plaintext
        """
        ciphertext = ciphertext.upper()
        
        # Convert to coordinates
        coords = []
        for char in ciphertext:
            if char in self.char_to_coords:
                coords.append(self.char_to_coords[char])
            else:
                # Map unknown chars to period
                coords.append(self.char_to_coords.get('.', (2, 2, 2)))
        
        # Extract coordinate lists based on reading order
        if reading_order == "rows":
            # Read by rows: all layers, then all rows, then all cols
            layers = [c[0] for c in coords]
            rows = [c[1] for c in coords]
            cols = [c[2] for c in coords]
        elif reading_order == "columns":
            # Read by columns: all cols, then all rows, then all layers
            cols = [c[2] for c in coords]
            rows = [c[1] for c in coords]
            layers = [c[0] for c in coords]
        else:  # spiral or other
            # Interleaved reading
            layers = []
            rows = []
            cols = []
            for i, c in enumerate(coords):
                if i % 3 == 0:
                    layers.append(c[0])
                    rows.append(c[1])
                    cols.append(c[2])
                elif i % 3 == 1:
                    rows.append(c[0])
                    cols.append(c[1])
                    layers.append(c[2])
                else:
                    cols.append(c[0])
                    layers.append(c[1])
                    rows.append(c[2])
        
        # Reconstruct plaintext
        plaintext = []
        for i in range(len(coords)):
            if i < len(layers) and i < len(rows) and i < len(cols):
                layer = layers[i] % 3
                row = rows[i] % 3
                col = cols[i] % 3
                char = self.cube[layer][row][col]
                if char == '.':
                    char = ' '  # Replace period with space for readability
                plaintext.append(char)
        
        return ''.join(plaintext)


class EightCube:
    """Eight-cube transposition cipher."""
    
    def __init__(self, orientation: str = "standard"):
        """
        Initialize with a specific orientation.
        
        Args:
            orientation: Cube orientation (standard, rotated_90, etc.)
        """
        self.orientation = orientation
        
        # Define vertex mappings for different orientations
        if orientation == "standard":
            self.vertex_map = [0, 1, 2, 3, 4, 5, 6, 7]
        elif orientation == "rotated_90":
            self.vertex_map = [1, 3, 0, 2, 5, 7, 4, 6]
        elif orientation == "rotated_180":
            self.vertex_map = [3, 2, 1, 0, 7, 6, 5, 4]
        else:  # diagonal
            self.vertex_map = [6, 4, 7, 5, 2, 0, 3, 1]
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt using Eight-cube transposition.
        
        Args:
            ciphertext: Text to decrypt
        
        Returns:
            Decrypted plaintext
        """
        # Pad to multiple of 8
        while len(ciphertext) % 8 != 0:
            ciphertext += 'X'
        
        plaintext = []
        
        # Process in blocks of 8
        for i in range(0, len(ciphertext), 8):
            block = ciphertext[i:i+8]
            
            # Rearrange according to vertex mapping
            decrypted_block = [''] * 8
            for j, vertex in enumerate(self.vertex_map):
                if vertex < len(block):
                    decrypted_block[j] = block[vertex]
            
            plaintext.extend(decrypted_block)
        
        return ''.join(plaintext)[:97]  # Return original length


def check_anchors(plaintext: str) -> Dict[str, bool]:
    """Check if expected anchors appear in decrypted text."""
    anchors = {
        "EAST": False,
        "NORTHEAST": False,
        "BERLINCLOCK": False
    }
    
    # Check for anchors with some tolerance
    if "EAST" in plaintext:
        anchors["EAST"] = True
    if "NORTHEAST" in plaintext or "NORTH" in plaintext:
        anchors["NORTHEAST"] = True
    if "BERLIN" in plaintext or "CLOCK" in plaintext:
        anchors["BERLINCLOCK"] = True
    
    return anchors


def generate_trifid_cube_heads(
    num_heads: int,
    trifid_keys: List[str],
    cube_orientations: List[str],
    reading_orders: List[str],
    seed: int = 1337
) -> List[Dict]:
    """
    Generate decryption attempts using Trifid and Eight-cube.
    
    Args:
        num_heads: Number of heads to generate
        trifid_keys: List of Trifid keys to try
        cube_orientations: List of cube orientations
        reading_orders: List of reading orders
        seed: Random seed
    
    Returns:
        List of decryption attempt results
    """
    random.seed(seed)
    heads = []
    
    for i in range(num_heads):
        # Randomly choose method
        use_trifid = random.random() < 0.5
        
        if use_trifid:
            # Trifid cipher
            key = random.choice(trifid_keys)
            order = random.choice(reading_orders)
            
            cipher = TrifidCipher(key)
            plaintext = cipher.decrypt(K4_CIPHERTEXT, order)
            
            method = "trifid"
            params = {"key": key[:10] + "...", "order": order}
        else:
            # Eight-cube transposition
            orientation = random.choice(cube_orientations)
            
            cipher = EightCube(orientation)
            plaintext = cipher.decrypt(K4_CIPHERTEXT)
            
            method = "eight_cube"
            params = {"orientation": orientation}
        
        # Check anchors
        anchor_check = check_anchors(plaintext)
        
        # Create head entry
        head = {
            "label": f"TRIFID_CUBE_{i:03d}",
            "text": plaintext[:75],
            "metadata": {
                "method": method,
                "parameters": params,
                "anchors_found": anchor_check,
                "anchor_count": sum(anchor_check.values()),
                "seed": seed + i,
                "full_plaintext": plaintext
            }
        }
        heads.append(head)
    
    return heads


def run_campaign_c2(output_dir: Path, seed: int = 1337):
    """
    Run Campaign C2: Trifid and Eight-cube testing.
    
    Args:
        output_dir: Directory for output files
        seed: Random seed
    """
    # Load campaign config
    catalog_path = Path(__file__).parent.parent / "catalog" / "campaign_C2_trifid_cube.json"
    with open(catalog_path) as f:
        config = json.load(f)
    
    # Extract parameters
    trifid_keys = config["parameters"]["trifid_keys"]
    orientations = config["parameters"]["cube_orientations"]
    orders = config["parameters"]["reading_orders"]
    num_heads = config["parameters"]["num_heads"]
    
    print(f"Campaign C2: Trifid & Eight-cube")
    print(f"  Trifid keys: {len(trifid_keys)}")
    print(f"  Orientations: {orientations}")
    print(f"  Reading orders: {orders}")
    print(f"  Heads: {num_heads}")
    
    # Generate heads
    heads = generate_trifid_cube_heads(
        num_heads, trifid_keys, orientations, orders, seed
    )
    
    # Count methods and anchors
    method_counts = {"trifid": 0, "eight_cube": 0}
    anchor_counts = {"0": 0, "1": 0, "2": 0, "3": 0}
    
    for head in heads:
        method_counts[head["metadata"]["method"]] += 1
        count = head["metadata"]["anchor_count"]
        anchor_counts[str(count)] += 1
    
    print(f"\nMethod distribution:")
    for method, num in method_counts.items():
        print(f"  {method}: {num} heads")
    
    print(f"\nAnchor distribution:")
    for count, num in anchor_counts.items():
        print(f"  {count} anchors: {num} heads")
    
    # Create output structure
    output = {
        "campaign": "C2_TRIFID_CUBE",
        "date": "2025-01-06",
        "description": "Trifid cipher and Eight-cube transposition",
        "methods": ["trifid", "eight_cube"],
        "parameters": config["parameters"],
        "seed": seed,
        "total_heads": len(heads),
        "method_distribution": method_counts,
        "anchor_distribution": anchor_counts,
        "heads": heads
    }
    
    # Save output
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "heads_c2_trifid_cube.json"
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nOutput saved to: {output_file}")
    
    # Create manifest
    manifest = {
        "campaign": "C2",
        "file": str(output_file),
        "hash": hashlib.sha256(json.dumps(output, sort_keys=True).encode()).hexdigest()[:16],
        "heads": len(heads),
        "anchor_matches": sum(1 for h in heads if h["metadata"]["anchor_count"] > 0)
    }
    
    manifest_file = output_dir / "manifest_c2.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return heads


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Generate Trifid/Eight-cube decryption attempts")
    parser.add_argument("--output",
                       default="experiments/community_hypotheses/runs/2025-01-06-campaign-c2",
                       help="Output directory")
    parser.add_argument("--seed", type=int, default=1337,
                       help="Random seed")
    
    args = parser.parse_args()
    
    run_campaign_c2(Path(args.output), args.seed)


if __name__ == "__main__":
    main()