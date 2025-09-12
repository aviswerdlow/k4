#!/usr/bin/env python3
"""Create zip bundles for each test case"""

import os
import zipfile
from pathlib import Path

def create_zip_bundle(case_dir, output_dir):
    """Create a zip bundle for a test case"""
    
    case_name = os.path.basename(case_dir)
    zip_name = f"crib_drop_berlin_{case_name}.zip"
    zip_path = os.path.join(output_dir, zip_name)
    
    # Files to include in the zip (in this order)
    files_to_zip = [
        "anchors.json",
        "WHEELS.json",
        "derived_pt.txt",
        "EXPLAIN_63_73.txt",
        "RESULT.json",
        "RECEIPTS.json",
        "MANIFEST.sha256"
    ]
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filename in files_to_zip:
            filepath = os.path.join(case_dir, filename)
            if os.path.exists(filepath):
                # Add file with a sensible archive name
                arcname = f"{case_name}/{filename}"
                zipf.write(filepath, arcname)
                print(f"  Added {filename}")
            else:
                print(f"  Warning: {filename} not found")
    
    # Get zip file size
    size_bytes = os.path.getsize(zip_path)
    size_kb = size_bytes / 1024
    
    print(f"Created {zip_name} ({size_kb:.1f} KB)")
    return zip_path

def main():
    base_dir = "04_EXPERIMENTS/forum_tests/crib_drop_berlin"
    
    cases = [
        "drop_berlin",
        "drop_clock",
        "drop_both",
        "drop_berlin_single_letter"
    ]
    
    print("Creating zip bundles for forum distribution...")
    print()
    
    created_zips = []
    for case in cases:
        case_dir = os.path.join(base_dir, case)
        if os.path.exists(case_dir):
            print(f"Processing {case}:")
            zip_path = create_zip_bundle(case_dir, base_dir)
            created_zips.append(zip_path)
            print()
        else:
            print(f"Error: {case_dir} not found")
    
    print("=" * 50)
    print("All zip bundles created!")
    print()
    print("Files ready for distribution:")
    for zip_path in created_zips:
        print(f"  - {os.path.basename(zip_path)}")

if __name__ == "__main__":
    main()