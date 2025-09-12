#!/usr/bin/env python3
"""
Generate anchor-aligned heads with controlled variations for window elasticity testing.
Places anchors at expected corridor positions to enable proper window testing.
"""

import json
import random
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple
import sys

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

# K4 plaintext from Kryptos sculptor (last section)
K4_PLAINTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Expected anchor positions in corridor
ANCHOR_POSITIONS = {
    "EAST": 21,
    "NORTHEAST": 25, 
    "BERLINCLOCK": 63
}


def edit_distance_1(word: str) -> List[str]:
    """Generate all strings with edit distance 1 from word."""
    variants = []
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    # Substitutions
    for i in range(len(word)):
        for c in alphabet:
            if c != word[i]:
                variant = word[:i] + c + word[i+1:]
                variants.append(variant)
    
    # Deletions (if word is long enough)
    if len(word) > 3:  # Keep minimum length
        for i in range(len(word)):
            variant = word[:i] + word[i+1:]
            variants.append(variant)
    
    # Insertions (if not too long)
    if len(word) < 12:  # Max anchor length
        for i in range(len(word) + 1):
            for c in alphabet:
                variant = word[:i] + c + word[i:]
                variants.append(variant)
    
    return variants


def generate_typo_variant(anchor: str, typo_count: int) -> str:
    """Generate a variant of anchor with specified typo count."""
    if typo_count == 0:
        return anchor
    elif typo_count == 1:
        variants = edit_distance_1(anchor)
        return random.choice(variants) if variants else anchor
    elif typo_count == 2:
        # Apply two edits
        variants1 = edit_distance_1(anchor)
        if not variants1:
            return anchor
        intermediate = random.choice(variants1)
        variants2 = edit_distance_1(intermediate)
        return random.choice(variants2) if variants2 else intermediate
    else:
        return anchor  # Don't support >2 typos


def generate_corridor_head(
    base_text: str,
    position_offsets: Dict[str, int],
    typo_counts: Dict[str, int],
    label: str,
    seed: int = None
) -> Dict:
    """
    Generate a head with anchors at specified positions with typos.
    
    Args:
        base_text: Base text to use (typically K4 plaintext)
        position_offsets: Offset from canonical position for each anchor
        typo_counts: Number of typos to introduce for each anchor
        label: Label for this head
        seed: Random seed for reproducibility
        
    Returns:
        Dict with label and generated text
    """
    if seed is not None:
        random.seed(seed)
    
    # Start with base text padded to 75 chars
    if len(base_text) < 75:
        text = base_text + "X" * (75 - len(base_text))
    else:
        text = base_text[:75]
    
    # Convert to list for easier manipulation
    text_list = list(text)
    
    # Place each anchor with offsets and typos
    for anchor, canonical_pos in ANCHOR_POSITIONS.items():
        # Apply position offset
        actual_pos = canonical_pos + position_offsets.get(anchor, 0)
        
        # Ensure position is valid
        if actual_pos < 0:
            actual_pos = 0
        if actual_pos + len(anchor) > 75:
            actual_pos = 75 - len(anchor)
        
        # Generate typo variant
        typo_count = typo_counts.get(anchor, 0)
        anchor_text = generate_typo_variant(anchor, typo_count)
        
        # Place anchor in text
        for i, char in enumerate(anchor_text):
            if actual_pos + i < 75:
                text_list[actual_pos + i] = char
    
    return {
        "label": label,
        "text": "".join(text_list),
        "metadata": {
            "position_offsets": position_offsets,
            "typo_counts": typo_counts
        }
    }


def generate_systematic_variations() -> List[Dict]:
    """Generate systematic variations for window elasticity testing."""
    heads = []
    head_id = 0
    
    # Perfect anchors (control)
    for i in range(10):
        head = generate_corridor_head(
            K4_PLAINTEXT,
            position_offsets={},
            typo_counts={},
            label=f"CORRIDOR_PERFECT_{head_id:03d}",
            seed=1337 + head_id
        )
        heads.append(head)
        head_id += 1
    
    # Position offsets only (no typos)
    for offset in [-3, -2, -1, 1, 2, 3]:
        for i in range(5):
            # All anchors shift together
            head = generate_corridor_head(
                K4_PLAINTEXT,
                position_offsets={"EAST": offset, "NORTHEAST": offset, "BERLINCLOCK": offset},
                typo_counts={},
                label=f"CORRIDOR_SHIFT{offset:+d}_{head_id:03d}",
                seed=1337 + head_id
            )
            heads.append(head)
            head_id += 1
    
    # Individual anchor shifts
    for anchor in ["EAST", "NORTHEAST", "BERLINCLOCK"]:
        for offset in [-2, -1, 1, 2]:
            for i in range(3):
                head = generate_corridor_head(
                    K4_PLAINTEXT,
                    position_offsets={anchor: offset},
                    typo_counts={},
                    label=f"CORRIDOR_{anchor}_SHIFT{offset:+d}_{head_id:03d}",
                    seed=1337 + head_id
                )
                heads.append(head)
                head_id += 1
    
    # Typos only (no position shift)
    for typo_count in [1, 2]:
        for i in range(5):
            # All anchors get typos
            head = generate_corridor_head(
                K4_PLAINTEXT,
                position_offsets={},
                typo_counts={"EAST": typo_count, "NORTHEAST": typo_count, "BERLINCLOCK": typo_count},
                label=f"CORRIDOR_TYPO{typo_count}_{head_id:03d}",
                seed=1337 + head_id
            )
            heads.append(head)
            head_id += 1
    
    # Combined: small shift + 1 typo
    for offset in [-1, 1]:
        for i in range(5):
            head = generate_corridor_head(
                K4_PLAINTEXT,
                position_offsets={"EAST": offset, "NORTHEAST": offset},
                typo_counts={"EAST": 1},
                label=f"CORRIDOR_COMBO_SHIFT{offset:+d}_TYPO_{head_id:03d}",
                seed=1337 + head_id
            )
            heads.append(head)
            head_id += 1
    
    return heads


def generate_corridor_candidates(output_path: Path) -> None:
    """Generate corridor-aligned candidates file."""
    
    # Generate systematic variations
    heads = generate_systematic_variations()
    
    # Add some pure K4 controls (no anchors)
    for i in range(5):
        heads.append({
            "label": f"CORRIDOR_K4_PURE_{i:03d}",
            "text": K4_PLAINTEXT[:75] if len(K4_PLAINTEXT) >= 75 else K4_PLAINTEXT + "X" * (75 - len(K4_PLAINTEXT)),
            "metadata": {"position_offsets": {}, "typo_counts": {}}
        })
    
    # Create output structure
    output = {
        "campaign": "EXPLORE_CORRIDOR_WINDOW_ELASTICITY",
        "date": "2025-01-06",
        "description": "Anchor-aligned heads for window elasticity testing",
        "anchor_positions": ANCHOR_POSITIONS,
        "total_heads": len(heads),
        "heads": heads
    }
    
    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Generated {len(heads)} corridor-aligned heads")
    print(f"Output: {output_path}")
    
    # Print distribution
    print("\nHead distribution:")
    categories = {}
    for head in heads:
        category = head["label"].split("_")[1]
        categories[category] = categories.get(category, 0) + 1
    
    for category, count in sorted(categories.items()):
        print(f"  {category}: {count}")


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Generate corridor-aligned heads")
    parser.add_argument("--output", 
                       default="experiments/pipeline_v2/data/corridor_heads.json",
                       help="Output path for candidates file")
    
    args = parser.parse_args()
    
    generate_corridor_candidates(Path(args.output))


if __name__ == "__main__":
    main()