#!/usr/bin/env python3
"""Prepare plaintext_97.txt for Confirm candidate - v2 with proper length."""

import json
import re
from pathlib import Path


def main():
    # Load selected candidate
    selection_path = Path("experiments/pipeline_v4/runs/v4_1_1/k200/CONFIRM_SELECTION.json")
    with open(selection_path) as f:
        selection = json.load(f)
    
    candidate = selection['selected_candidate']
    label = candidate['label']
    bundle_dir = Path(candidate['bundle_dir'])
    
    print(f"Processing: {label}")
    print(f"Bundle: {bundle_dir}")
    
    # Load head.json
    head_json_path = bundle_dir / "head.json"
    with open(head_json_path) as f:
        head_data = json.load(f)
    
    # Get text_final
    text_final = head_data['text_final']
    print(f"Original text_final: {text_final}")
    
    # Normalize to uppercase A-Z letters
    text_clean = re.sub(r'[^A-Z]', '', text_final.upper())
    print(f"Cleaned (len={len(text_clean)}): {text_clean}")
    
    # We need exactly 97 chars. Current is 101, so we need to trim 4 chars from the tail
    # The head window [0:74] is locked, so trim from position 74 onwards
    if len(text_clean) > 97:
        text_97 = text_clean[:97]
        print(f"Trimmed to 97: {text_97}")
    elif len(text_clean) < 97:
        # Pad with X if needed (shouldn't happen)
        text_97 = text_clean + 'X' * (97 - len(text_clean))
        print(f"Padded to 97: {text_97}")
    else:
        text_97 = text_clean
    
    # Verify length
    assert len(text_97) == 97, f"Expected 97 chars, got {len(text_97)}"
    
    # Verify anchors (0-indexed)
    errors = []
    
    # PT[21:25] == EAST
    if text_97[21:25] != "EAST":
        errors.append(f"Anchor 1 failed: PT[21:25] = '{text_97[21:25]}' != 'EAST'")
    
    # PT[25:34] == NORTHEAST
    if text_97[25:34] != "NORTHEAST":
        errors.append(f"Anchor 2 failed: PT[25:34] = '{text_97[25:34]}' != 'NORTHEAST'")
    
    # PT[63:74] == BERLINCLOCK
    if text_97[63:74] != "BERLINCLOCK":
        errors.append(f"Anchor 3 failed: PT[63:74] = '{text_97[63:74]}' != 'BERLINCLOCK'")
    
    if errors:
        print("ERROR: Anchor verification failed!")
        for e in errors:
            print(f"  - {e}")
        # Let's check what we have at those positions
        print(f"\nActual at [21:25]: '{text_97[21:25]}'")
        print(f"Actual at [25:34]: '{text_97[25:34]}'")  
        print(f"Actual at [63:74]: '{text_97[63:74]}'")
        print(f"\nFull text: {text_97}")
        return
    
    print("✅ All anchors verified")
    print(f"✅ Length: {len(text_97)} chars")
    
    # Show head and tail
    print(f"Head [0:74]: {text_97[:74]}")
    print(f"Tail [74:97]: {text_97[74:]}")
    
    # Create Confirm directory structure
    confirm_dir = Path("runs/confirm") / label
    confirm_dir.mkdir(parents=True, exist_ok=True)
    
    # Write plaintext_97.txt
    plaintext_path = confirm_dir / "plaintext_97.txt"
    with open(plaintext_path, 'w') as f:
        f.write(text_97)
    
    print(f"\n📝 Written: {plaintext_path}")
    
    # Also save metadata for tracking
    metadata = {
        "label": label,
        "seed_u64": candidate['seed_u64'],
        "weights_sha256": candidate['weights_sha256'],
        "source_bundle": str(bundle_dir),
        "text_final_original": text_final,
        "text_cleaned": text_clean,
        "text_length_original": len(text_clean),
        "plaintext_97": text_97,
        "anchors_verified": {
            "EAST": text_97[21:25],
            "NORTHEAST": text_97[25:34],
            "BERLINCLOCK": text_97[63:74]
        },
        "head_window": text_97[:74],
        "tail": text_97[74:]
    }
    
    metadata_path = confirm_dir / "metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"📋 Metadata saved: {metadata_path}")


if __name__ == "__main__":
    main()