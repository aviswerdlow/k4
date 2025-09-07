#!/usr/bin/env python3
"""Analyze anchor positions in the original text."""

import json
from pathlib import Path


def main():
    # Load selected candidate
    selection_path = Path("experiments/pipeline_v4/runs/v4_1_1/k200/CONFIRM_SELECTION.json")
    with open(selection_path) as f:
        selection = json.load(f)
    
    candidate = selection['selected_candidate']
    bundle_dir = Path(candidate['bundle_dir'])
    
    # Load head.json
    head_json_path = bundle_dir / "head.json"
    with open(head_json_path) as f:
        head_data = json.load(f)
    
    # Get text_final WITH spaces
    text_final = head_data['text_final']
    print(f"Text with spaces: {text_final}")
    print(f"Length with spaces: {len(text_final)}")
    
    # Show character positions
    print("\nCharacter-by-character (with spaces):")
    for i in range(0, len(text_final), 10):
        chunk = text_final[i:i+10]
        print(f"[{i:3d}-{i+9:3d}]: '{chunk}'")
    
    # Now look at the structure
    print("\nTokens:")
    tokens = text_final.split()
    for i, token in enumerate(tokens):
        print(f"  {i}: {token}")
    
    # Find where anchors appear
    print("\nSearching for anchors in text:")
    if "EAST" in text_final:
        idx = text_final.index("EAST")
        print(f"  EAST found at position {idx}")
    
    if "NORTHEAST" in text_final:
        idx = text_final.index("NORTHEAST")
        print(f"  NORTHEAST found at position {idx}")
    
    if "BERLINCLOCK" in text_final:
        # Need to check without space
        if "BERLIN" in text_final:
            idx = text_final.index("BERLIN")
            print(f"  BERLIN found at position {idx}")
        text_no_space = text_final.replace(" ", "")
        if "BERLINCLOCK" in text_no_space:
            idx = text_no_space.index("BERLINCLOCK")
            print(f"  BERLINCLOCK found at position {idx} (in no-space version)")
    
    # The issue is that the anchors are in specific positions AFTER removing spaces
    # Let's map the positions correctly
    text_no_space = text_final.replace(" ", "").upper()
    print(f"\nText without spaces: {text_no_space}")
    print(f"Length without spaces: {len(text_no_space)}")
    
    # Now check the actual positions in the no-space version
    print("\nActual content at anchor positions (0-indexed, no spaces):")
    print(f"  [2:6]:   '{text_no_space[2:6]}' (expecting EAST)")
    print(f"  [21:25]: '{text_no_space[21:25]}'")
    print(f"  [25:34]: '{text_no_space[25:34]}'")
    print(f"  [41:52]: '{text_no_space[41:52]}' (checking for NORTHEAST)")  
    print(f"  [63:74]: '{text_no_space[63:74]}'")
    
    # Find the actual positions of the anchor words
    print("\nFinding actual anchor positions in no-space text:")
    if "EAST" in text_no_space:
        idx = text_no_space.index("EAST")
        print(f"  EAST at position {idx}")
    if "NORTHEAST" in text_no_space:
        idx = text_no_space.index("NORTHEAST")
        print(f"  NORTHEAST at position {idx}")
    if "BERLINCLOCK" in text_no_space:
        idx = text_no_space.index("BERLINCLOCK")
        print(f"  BERLINCLOCK at position {idx}")


if __name__ == "__main__":
    main()