#!/usr/bin/env python3
"""
Validate that normalized quotes match their verbatim sources
Ensure all 97-char candidates are exactly 97 chars
"""

import json
from pathlib import Path


def normalize_az(text: str) -> str:
    """Normalize text to A-Z only, uppercase"""
    return ''.join(c.upper() for c in text if c.isalpha())


def validate_quotes():
    """Validate all extracted quotes"""
    base_path = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus")
    quotes_dir = base_path / "quotes"
    
    if not quotes_dir.exists():
        print("ERROR: quotes/ directory not found. Run flint_extract.py first.")
        return
    
    print("Validating extracted quotes...")
    print("=" * 60)
    
    # Check angle definition
    angle_path = quotes_dir / "angle_definition.json"
    if angle_path.exists():
        with open(angle_path) as f:
            angle_data = json.load(f)
        
        verbatim = angle_data["verbatim"]
        stored_norm = angle_data["normalized_AZ"]
        computed_norm = normalize_az(verbatim)
        
        print(f"\nAngle Definition:")
        print(f"  Page: {angle_data['page']}")
        print(f"  Verbatim length: {len(verbatim)}")
        print(f"  Normalized length: {angle_data['normalized_len']}")
        print(f"  Normalization match: {stored_norm == computed_norm}")
        
        if stored_norm != computed_norm:
            print(f"  ERROR: Normalization mismatch!")
            print(f"    Stored:   {stored_norm[:50]}...")
            print(f"    Computed: {computed_norm[:50]}...")
    
    # Check candidates A-E
    print("\n97-Character Candidates:")
    print("-" * 40)
    
    all_valid = True
    for letter in "ABCDE":
        cand_path = quotes_dir / f"candidate_{letter}.json"
        if not cand_path.exists():
            print(f"  Candidate {letter}: NOT FOUND")
            all_valid = False
            continue
        
        with open(cand_path) as f:
            cand_data = json.load(f)
        
        verbatim = cand_data["verbatim"]
        stored_norm = cand_data["normalized_AZ"]
        computed_norm = normalize_az(verbatim)
        
        is_valid = (
            stored_norm == computed_norm and
            len(stored_norm) == 97 and
            cand_data["normalized_len"] == 97
        )
        
        status = "✓ VALID" if is_valid else "✗ INVALID"
        print(f"\n  Candidate {letter}: {status}")
        print(f"    Page: {cand_data['page']}")
        print(f"    Section: {cand_data['section_note']}")
        print(f"    Verbatim: \"{verbatim[:40]}...\"")
        print(f"    Normalized length: {len(stored_norm)}")
        print(f"    Length check: {len(stored_norm) == 97}")
        print(f"    Normalization match: {stored_norm == computed_norm}")
        
        if not is_valid:
            all_valid = False
            if stored_norm != computed_norm:
                print(f"    ERROR: Normalization mismatch!")
                print(f"      First 50 stored:   {stored_norm[:50]}")
                print(f"      First 50 computed: {computed_norm[:50]}")
            if len(stored_norm) != 97:
                print(f"    ERROR: Length is {len(stored_norm)}, expected 97!")
    
    # Summary
    print("\n" + "=" * 60)
    if all_valid:
        print("✓ All candidates validated successfully!")
        print("  - All normalizations match verbatim sources")
        print("  - All 5 candidates are exactly 97 characters")
    else:
        print("✗ Validation failed! Check errors above.")
    
    # Save validation report
    validation = {
        "all_valid": all_valid,
        "angle_definition_found": angle_path.exists(),
        "candidates_found": [
            letter for letter in "ABCDE" 
            if (quotes_dir / f"candidate_{letter}.json").exists()
        ]
    }
    
    with open(quotes_dir / "validation_report.json", "w") as f:
        json.dump(validation, f, indent=2)
    
    print(f"\nValidation report saved to quotes/validation_report.json")


if __name__ == "__main__":
    validate_quotes()