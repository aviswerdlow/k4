#!/usr/bin/env python3
"""
Create blinded style comparison panel.
Compares K4 winner head to K1-K3 in random order, no labels.
Reviewers judge which text "feels most like Sanborn."
"""

import json
import random
from pathlib import Path
import hashlib
from datetime import datetime

# K1-K3 reference texts
K1_TEXT = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
K2_TEXT = "ITWASTOTALLYINVISIBLESHOWSTHATPOSSIBLETHEYDIDNOTKNOWABOUTYETQ"
K3_TEXT = "SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADEATINYBREACHINTHEUPPERLEFTHANDCORNERANDTHENWIDENNINGTHEHOLEAILITTLE"

# K4 winner head
K4_WINNER = "WECANSEETHETEXTISCODEEASTNORTHEASTSOUTHANDSOUTHWESTIFINDTHATITSAYSSLOWLY"

def prepare_blinded_samples():
    """
    Prepare samples for blind review.
    Returns list of samples with hidden IDs.
    """
    samples = [
        {'id': 'A', 'text': K1_TEXT, 'true_source': 'K1'},
        {'id': 'B', 'text': K2_TEXT, 'true_source': 'K2'},
        {'id': 'C', 'text': K3_TEXT, 'true_source': 'K3'},
        {'id': 'D', 'text': K4_WINNER, 'true_source': 'K4_winner'}
    ]
    
    # Shuffle for blind presentation
    random.seed(1337)  # Deterministic for reproducibility
    random.shuffle(samples)
    
    # Re-assign IDs after shuffle
    for i, sample in enumerate(samples):
        sample['presentation_id'] = chr(65 + i)  # A, B, C, D
    
    return samples

def create_reviewer_packet(samples, output_dir):
    """
    Create the packet for reviewers (no answers).
    """
    packet_lines = []
    packet_lines.append("# Blinded Style Comparison Panel")
    packet_lines.append("")
    packet_lines.append("**Instructions**: Review the four text samples below. Based on style, vocabulary,")
    packet_lines.append("and linguistic patterns, rank which samples feel most consistent with Sanborn's")
    packet_lines.append("cryptographic style as demonstrated in Kryptos.")
    packet_lines.append("")
    packet_lines.append("**Task**: Rank samples from 1 (most Sanborn-like) to 4 (least Sanborn-like)")
    packet_lines.append("")
    packet_lines.append("---")
    packet_lines.append("")
    
    for sample in samples:
        packet_lines.append(f"## Sample {sample['presentation_id']}")
        packet_lines.append("")
        # Present in chunks for readability
        text = sample['text']
        for i in range(0, len(text), 50):
            packet_lines.append(text[i:i+50])
        packet_lines.append("")
        packet_lines.append("**Your ranking**: ___")
        packet_lines.append("")
        packet_lines.append("---")
        packet_lines.append("")
    
    packet_lines.append("## Ranking Summary")
    packet_lines.append("")
    packet_lines.append("Most Sanborn-like:")
    packet_lines.append("1. Sample ___")
    packet_lines.append("2. Sample ___")
    packet_lines.append("3. Sample ___")
    packet_lines.append("4. Sample ___")
    packet_lines.append("Least Sanborn-like")
    packet_lines.append("")
    packet_lines.append("**Comments** (optional):")
    packet_lines.append("_" * 60)
    packet_lines.append("_" * 60)
    packet_lines.append("_" * 60)
    
    return '\n'.join(packet_lines)

def create_answer_key(samples, output_dir):
    """
    Create the answer key (for after review).
    """
    key_lines = []
    key_lines.append("# Blinded Panel Answer Key")
    key_lines.append("")
    key_lines.append("**DO NOT SHARE UNTIL AFTER REVIEW**")
    key_lines.append("")
    key_lines.append("## Sample Identities")
    key_lines.append("")
    key_lines.append("| Sample | Source | Description |")
    key_lines.append("|--------|--------|-------------|")
    
    for sample in samples:
        source = sample['true_source']
        if source == 'K4_winner':
            desc = "K4 winner head (positions 0-74)"
        else:
            desc = f"{source} plaintext (known Sanborn)"
        
        key_lines.append(f"| {sample['presentation_id']} | {source} | {desc} |")
    
    key_lines.append("")
    key_lines.append("## Expected Pattern")
    key_lines.append("")
    key_lines.append("If K4 winner is stylistically consistent with K1-K3, reviewers should not")
    key_lines.append("systematically rank it as different. Random distribution of rankings would")
    key_lines.append("suggest stylistic consistency.")
    key_lines.append("")
    key_lines.append("## Key Observations to Note")
    key_lines.append("")
    key_lines.append("1. Use of directional terms (K4 has compass directions)")
    key_lines.append("2. Sentence structure and flow")
    key_lines.append("3. Vocabulary complexity")
    key_lines.append("4. Thematic consistency")
    
    return '\n'.join(key_lines)

def main():
    """Create blinded style panel."""
    base_dir = Path(__file__).parent.parent
    output_dir = base_dir / "runs" / "2025-09-05" / "blinded_panel"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Creating Blinded Style Panel...")
    print("="*50)
    
    # Prepare samples
    samples = prepare_blinded_samples()
    
    # Create reviewer packet
    packet = create_reviewer_packet(samples, output_dir)
    packet_path = output_dir / "REVIEWER_PACKET.md"
    with open(packet_path, 'w') as f:
        f.write(packet)
    
    print("✓ Created reviewer packet")
    
    # Create answer key
    key = create_answer_key(samples, output_dir)
    key_path = output_dir / "ANSWER_KEY.md"
    with open(key_path, 'w') as f:
        f.write(key)
    
    print("✓ Created answer key (sealed)")
    
    # Save sample mapping
    mapping = {
        'creation_date': '2025-09-05',
        'seed': 1337,
        'samples': [
            {
                'presentation_id': s['presentation_id'],
                'true_source': s['true_source'],
                'text_length': len(s['text']),
                'text_hash': hashlib.sha256(s['text'].encode()).hexdigest()[:16]
            }
            for s in samples
        ]
    }
    
    mapping_path = output_dir / "sample_mapping.json"
    with open(mapping_path, 'w') as f:
        json.dump(mapping, f, indent=2)
    
    print("✓ Saved sample mapping")
    
    # Create summary
    summary_lines = []
    summary_lines.append("# Blinded Style Panel Summary")
    summary_lines.append("")
    summary_lines.append("**Created**: 2025-09-05")
    summary_lines.append("**Samples**: 4 (K1, K2, K3, K4_winner)")
    summary_lines.append("**Presentation**: Randomized, unlabeled")
    summary_lines.append("")
    summary_lines.append("## Purpose")
    summary_lines.append("")
    summary_lines.append("Test whether K4 winner head is stylistically consistent with known Sanborn plaintexts")
    summary_lines.append("from K1-K3. Blind presentation prevents bias.")
    summary_lines.append("")
    summary_lines.append("## Files Generated")
    summary_lines.append("")
    summary_lines.append("1. `REVIEWER_PACKET.md` - For reviewers (no answers)")
    summary_lines.append("2. `ANSWER_KEY.md` - Identity of samples (sealed until after review)")
    summary_lines.append("3. `sample_mapping.json` - Technical mapping details")
    summary_lines.append("")
    summary_lines.append("## Next Steps")
    summary_lines.append("")
    summary_lines.append("1. Distribute REVIEWER_PACKET.md to reviewers")
    summary_lines.append("2. Collect rankings")
    summary_lines.append("3. Analyze distribution of rankings")
    summary_lines.append("4. Reveal answer key")
    summary_lines.append("")
    summary_lines.append("**This is an optional stylistic analysis; does not affect technical results.**")
    
    summary_path = output_dir / "PANEL_SUMMARY.md"
    with open(summary_path, 'w') as f:
        f.write('\n'.join(summary_lines))
    
    print("\n" + '\n'.join(summary_lines))
    
    # Generate manifest
    manifest = []
    for file in sorted(output_dir.glob("**/*")):
        if file.is_file():
            with open(file, 'rb') as f:
                hash_val = hashlib.sha256(f.read()).hexdigest()
            rel_path = file.relative_to(output_dir)
            manifest.append(f"{hash_val}  {rel_path}")
    
    manifest_path = output_dir / "MANIFEST.sha256"
    with open(manifest_path, 'w') as f:
        f.write('\n'.join(manifest))
    
    print(f"\n✓ Blinded panel created in: {output_dir}")
    print("Ready for distribution to reviewers")

if __name__ == "__main__":
    main()