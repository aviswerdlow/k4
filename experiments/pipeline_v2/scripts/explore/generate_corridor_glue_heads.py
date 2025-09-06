#!/usr/bin/env python3
"""
Generate corridor heads with non-narrative glue token injection.
Combines Campaign E (lexicon injection) with Campaign G (corridor alignment).
"""

import json
import random
import hashlib
from pathlib import Path
from typing import List, Dict
import sys

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

# Non-narrative glue tokens (avoid blinding)
GLUE_LEXICON = [
    "THE", "AND", "OF", "TO", "A", "IN", "IS", "IT", "FOR", "WITH",
    "AS", "ON", "AT", "BY", "FROM", "UP", "OUT", "IF", "BUT", "OR",
    "AN", "BE", "HAS", "HER", "HIS", "NOT", "WE", "ARE", "ALL", "SO"
]

def inject_glue_tokens(text: str, num_tokens: int, positions: List[int], seed: int = None) -> str:
    """
    Inject glue tokens at specified positions outside corridor.
    
    Args:
        text: Base text
        num_tokens: Number of glue tokens to inject (0-2)
        positions: Valid positions for injection (outside [21..33])
        seed: Random seed
        
    Returns:
        Text with injected glue tokens
    """
    if seed is not None:
        random.seed(seed)
    
    if num_tokens == 0:
        return text
    
    # Select random glue tokens
    tokens = random.sample(GLUE_LEXICON, min(num_tokens, len(GLUE_LEXICON)))
    
    # Select positions outside corridor [21..33] and [63..73]
    valid_positions = [p for p in positions if not (21 <= p <= 33 or 63 <= p <= 73)]
    
    if not valid_positions:
        return text  # No valid positions
    
    # Select injection positions
    injection_positions = random.sample(valid_positions, min(num_tokens, len(valid_positions)))
    
    # Convert to list for manipulation
    text_list = list(text)
    
    # Inject tokens
    for token, pos in zip(tokens, injection_positions):
        # Inject token, overwriting existing characters
        for i, char in enumerate(token):
            if pos + i < len(text_list):
                text_list[pos + i] = char
    
    return "".join(text_list)


def generate_corridor_glue_heads(input_file: Path, output_file: Path) -> None:
    """
    Generate corridor heads with glue token injection.
    """
    
    # Load corridor heads
    with open(input_file) as f:
        data = json.load(f)
    
    original_heads = data["heads"]
    
    # Generate variations with glue injection
    glue_heads = []
    head_id = 0
    
    # For each original corridor head
    for orig_head in original_heads:
        # Skip K4_PURE heads (no anchors)
        if "K4_PURE" in orig_head["label"]:
            continue
            
        # Generate versions with 0, 1, 2 glue tokens
        for num_glue in [0, 1, 2]:
            # Determine valid injection positions
            text_len = len(orig_head["text"])
            valid_positions = list(range(0, 21)) + list(range(34, 63)) + list(range(74, min(75, text_len)))
            
            # Create glue-injected variant
            glue_text = inject_glue_tokens(
                orig_head["text"],
                num_glue,
                valid_positions,
                seed=1337 + head_id
            )
            
            glue_head = {
                "label": f"{orig_head['label']}_GLUE{num_glue}",
                "text": glue_text,
                "metadata": {
                    "original_label": orig_head["label"],
                    "glue_tokens": num_glue,
                    "position_offsets": orig_head["metadata"].get("position_offsets", {}),
                    "typo_counts": orig_head["metadata"].get("typo_counts", {})
                }
            }
            glue_heads.append(glue_head)
            head_id += 1
    
    # Create output structure
    output = {
        "campaign": "EXPLORE_CORRIDOR_GLUE",
        "date": "2025-01-06",
        "description": "Corridor-aligned heads with non-narrative glue token injection",
        "anchor_positions": data.get("anchor_positions", {}),
        "glue_lexicon": GLUE_LEXICON,
        "total_heads": len(glue_heads),
        "heads": glue_heads
    }
    
    # Write output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Generated {len(glue_heads)} corridor+glue heads")
    print(f"Output: {output_file}")
    
    # Print distribution
    print("\nGlue distribution:")
    glue_counts = {}
    for head in glue_heads:
        num_glue = head["metadata"]["glue_tokens"]
        glue_counts[num_glue] = glue_counts.get(num_glue, 0) + 1
    
    for num_glue in sorted(glue_counts.keys()):
        print(f"  {num_glue} glue tokens: {glue_counts[num_glue]} heads")


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Generate corridor+glue heads")
    parser.add_argument("--input",
                       default="experiments/pipeline_v2/data/corridor_heads.json",
                       help="Input corridor heads file")
    parser.add_argument("--output",
                       default="experiments/pipeline_v2/data/corridor_glue_heads.json",
                       help="Output path for corridor+glue heads")
    
    args = parser.parse_args()
    
    generate_corridor_glue_heads(Path(args.input), Path(args.output))


if __name__ == "__main__":
    main()