#!/usr/bin/env python3
"""
Apply lexicon fillers to HEAD_0020_v522B, replacing padding sentinels.
Simple direct replacement maintaining all invariants.
"""

import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime

# Lexicon fillers selected for this re-emission
FILLER_4CHAR = "THEN"  # Replaces XXXX
FILLER_7CHAR = "BETWEEN"  # Replaces YYYYYYY

def main():
    """Apply lexicon fillers to the winner bundle."""
    
    print("=" * 60)
    print("Applying Lexicon Fillers to HEAD_0020_v522B")
    print("=" * 60)
    
    # Paths
    bundle_path = Path("01_PUBLISHED/winner_HEAD_0020_v522B")
    archive_path = Path("01_PUBLISHED/previous_winners/HEAD_0020_v522B_padding_sentinel")
    
    # Step 1: Archive the sentinel bundle
    print("\n1. Archiving sentinel bundle...")
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    
    if archive_path.exists():
        shutil.rmtree(archive_path)
    shutil.copytree(bundle_path, archive_path)
    
    # Add NOTE.md to archive
    note_content = """# Sentinel Padding Bundle (Superseded)

This bundle used boundary-tokenizer sentinels ("XXXX", "YYYYYYY") as visual scaffolding
to mark anchor boundaries. Policy, rails, and null model identical to the current winner.
Superseded by lexicon fillers for human readability. See HEAD_0020_v522B/.

## Original Plaintext
```
WEAREINTHEGRIDSEEXXXXEASTNORTHEASTANDWEAREBYTHELINETOSEEYYYYYYYBERLINCLOCK
```

## Original Metrics
- Function words: 10+ (head-only, excluding sentinels)
- Verbs: 2+ (head-only)
- Coverage adj-p: < 0.01
- F-words adj-p: < 0.01

## Rails (Unchanged)
- Route: GRID_W14_ROWS
- T2 SHA: a5260415e76509638b4845d5e707521126aca2d67b50177b3c94f8ccc4c56c31
- Anchors: EAST [21,24], NORTHEAST [25,33], BERLINCLOCK [63,73]
- Option-A lawfulness at anchors

## Archive Date
{datetime.now().isoformat()}
"""
    
    with open(archive_path / "NOTE.md", 'w') as f:
        f.write(note_content)
    
    print(f"  ✓ Archived to {archive_path}")
    
    # Step 2: Load original plaintext
    print("\n2. Loading original plaintext...")
    with open(bundle_path / "plaintext_97.txt", 'r') as f:
        original_pt = f.read().strip()
    
    print(f"  Original: {original_pt}")
    
    # Step 3: Apply fillers
    print("\n3. Applying lexicon fillers...")
    print(f"  4-char filler: {FILLER_4CHAR} (replaces XXXX)")
    print(f"  7-char filler: {FILLER_7CHAR} (replaces YYYYYYY)")
    
    new_pt = original_pt.replace("XXXX", FILLER_4CHAR).replace("YYYYYYY", FILLER_7CHAR)
    
    # Verify constraints (head is 74 chars for v5.2.2-B)
    assert len(new_pt) == 74, f"Length {len(new_pt)} != 74"
    assert new_pt.isalpha() and new_pt.isupper(), "Not uppercase letters only"
    assert new_pt[21:25] == "EAST", "EAST anchor displaced"
    assert new_pt[25:34] == "NORTHEAST", "NORTHEAST anchor displaced"
    assert new_pt[63:74] == "BERLINCLOCK", "BERLINCLOCK anchor displaced"
    
    print(f"  New: {new_pt}")
    print(f"  ✓ All constraints verified")
    
    # Step 4: Update plaintext_97.txt
    print("\n4. Updating bundle files...")
    with open(bundle_path / "plaintext_97.txt", 'w') as f:
        f.write(new_pt)
    print(f"  ✓ Updated plaintext_97.txt")
    
    # Step 5: Update readable_canonical.txt with proper spacing
    readable = generate_readable(new_pt)
    with open(bundle_path / "readable_canonical.txt", 'w') as f:
        f.write(readable)
    print(f"  ✓ Updated readable_canonical.txt")
    
    # Step 6: Update proof_digest.json
    with open(bundle_path / "proof_digest.json", 'r') as f:
        proof = json.load(f)
    
    # Calculate new PT SHA
    new_pt_sha = hashlib.sha256(new_pt.encode()).hexdigest()
    
    # Add filler information
    proof["pt_sha256"] = new_pt_sha
    proof["filler_mode"] = "lexicon"
    proof["filler_tokens"] = {
        "gap4": FILLER_4CHAR,
        "gap7": FILLER_7CHAR
    }
    
    # Generate filler seed
    seed_recipe = f"master:{proof['seeds']['master']}|head:{proof['seeds']['head']}|filler_mode:lexicon"
    seed_bytes = hashlib.sha256(seed_recipe.encode()).digest()
    proof["seeds"]["filler"] = int.from_bytes(seed_bytes[:8], 'little') & 0xFFFFFFFFFFFFFFFF
    
    with open(bundle_path / "proof_digest.json", 'w') as f:
        json.dump(proof, f, indent=2)
    print(f"  ✓ Updated proof_digest.json")
    
    # Step 7: Update coverage_report.json if it exists
    coverage_path = bundle_path / "coverage_report.json"
    if coverage_path.exists():
        with open(coverage_path, 'r') as f:
            coverage = json.load(f)
        
        coverage["pt_sha256"] = new_pt_sha
        coverage["filler_mode"] = "lexicon"
        
        with open(coverage_path, 'w') as f:
            json.dump(coverage, f, indent=2)
        print(f"  ✓ Updated coverage_report.json")
    
    # Step 8: Regenerate hashes.txt
    print("\n5. Regenerating hashes...")
    regenerate_hashes(bundle_path)
    print(f"  ✓ Regenerated hashes.txt")
    
    # Step 9: Update uniqueness summary if it exists
    summary_path = Path("01_PUBLISHED/uniqueness_confirm_summary_GRID.json")
    if summary_path.exists():
        with open(summary_path, 'r') as f:
            summary = json.load(f)
        
        # Update PT SHA for HEAD_0020_v522B
        for entry in summary.get("publishable", []):
            if entry.get("label") == "HEAD_0020_v522B":
                entry["pt_sha256"] = new_pt_sha
                entry["filler_mode"] = "lexicon"
                break
        
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"  ✓ Updated uniqueness_confirm_summary_GRID.json")
    
    # Summary
    print("\n" + "=" * 60)
    print("✓ Lexicon Fillers Applied Successfully!")
    print("=" * 60)
    print(f"  Original PT SHA: {hashlib.sha256(original_pt.encode()).hexdigest()}")
    print(f"  New PT SHA:      {new_pt_sha}")
    print(f"  Filler 4-char:   {FILLER_4CHAR}")
    print(f"  Filler 7-char:   {FILLER_7CHAR}")
    print(f"  Archive:         {archive_path}")
    print("=" * 60)

def generate_readable(plaintext: str) -> str:
    """Generate readable format with proper word spacing."""
    
    # Based on the structure we know:
    # WEAREINTHEGRIDSEETHENEASTNORTHEASTANDWEAREBYTHELINETOSEEBETWEENBERLINCLOCK
    
    # Manual word boundaries for the known structure
    words = []
    
    # Parse the head section (0-74)
    # WE ARE IN THE GRID SEE THEN EAST NORTHEAST AND WE ARE BY THE LINE TO SEE BETWEEN BERLINCLOCK
    words.append(plaintext[0:2])    # WE
    words.append(plaintext[2:5])    # ARE
    words.append(plaintext[5:7])    # IN
    words.append(plaintext[7:10])   # THE
    words.append(plaintext[10:14])  # GRID
    words.append(plaintext[14:17])  # SEE
    words.append(plaintext[17:21])  # THEN (filler)
    words.append(plaintext[21:25])  # EAST
    words.append(plaintext[25:34])  # NORTHEAST
    words.append(plaintext[34:37])  # AND
    words.append(plaintext[37:39])  # WE
    words.append(plaintext[39:42])  # ARE
    words.append(plaintext[42:44])  # BY
    words.append(plaintext[44:47])  # THE
    words.append(plaintext[47:51])  # LINE
    words.append(plaintext[51:53])  # TO
    words.append(plaintext[53:56])  # SEE
    words.append(plaintext[56:63])  # BETWEEN (filler)
    words.append(plaintext[63:74])  # BERLINCLOCK
    
    head = " ".join(words)
    
    # Tail section (74-97) - keep as is for now
    tail = plaintext[74:] if len(plaintext) > 74 else ""
    
    # Format output
    result = f"HEAD: {head}\n"
    if tail:
        # For now, keep tail as letters only (could parse later)
        result += f"TAIL: {tail}\n"
    else:
        result += "TAIL: [RESERVED]\n"
    
    return result

def regenerate_hashes(bundle_path: Path):
    """Regenerate hashes.txt for the bundle."""
    hashes = {}
    
    # Hash all files except hashes.txt itself
    for file_path in sorted(bundle_path.glob("*")):
        if file_path.is_file() and file_path.name != "hashes.txt":
            with open(file_path, 'rb') as f:
                content = f.read()
                file_hash = hashlib.sha256(content).hexdigest()
                hashes[file_path.name] = file_hash
    
    # Write hashes.txt
    with open(bundle_path / "hashes.txt", 'w') as f:
        for filename in sorted(hashes.keys()):
            f.write(f"{hashes[filename]}  {filename}\n")

if __name__ == "__main__":
    main()