#!/usr/bin/env python3
"""
Create a forum packet for sharing Flint OTP test results
"""

import json
import zipfile
from pathlib import Path
import shutil


def create_forum_packet():
    """Create a ZIP file with key results for forum sharing"""
    base_path = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus")
    results_dir = base_path / "experiments/flint_otp/results"
    quotes_dir = base_path / "quotes"
    
    # Create temporary directory for packet contents
    packet_dir = base_path / "experiments/flint_otp/forum_packet"
    packet_dir.mkdir(exist_ok=True)
    
    # 1. Create summary document
    summary_path = packet_dir / "README.txt"
    with open(summary_path, 'w') as f:
        f.write("FLINT AS OTP - TEST RESULTS\n")
        f.write("=" * 50 + "\n\n")
        f.write("SUMMARY: All tests NEGATIVE. Flint cannot be used as OTP for K4.\n\n")
        
        f.write("WHAT WAS TESTED:\n")
        f.write("- Source: Abel Flint's 'A System of Geometry and Trigonometry' (1820)\n")
        f.write("- Method: One-time pad (OTP) with Vigenère and Beaufort decoding\n")
        f.write("- Constraints: EAST @ 21-24, NORTHEAST @ 25-33, BERLIN @ 63-68, CLOCK @ 69-73\n\n")
        
        f.write("RESULTS:\n")
        f.write("1. Five hand-picked 97-char quotes: ALL FAIL anchor constraints\n")
        f.write("2. Flint as plaintext with K1/K2/K3 keys: NO MATCHES\n")
        f.write("3. Systematic sweep of 2,281 windows: ZERO MATCHES\n\n")
        
        f.write("VERBATIM QUOTES TESTED (with page numbers):\n")
        f.write("-" * 50 + "\n")
        
        # Add the five candidates
        for letter in "ABCDE":
            cand_path = quotes_dir / f"candidate_{letter}.json"
            if cand_path.exists():
                with open(cand_path) as cf:
                    cand = json.load(cf)
                f.write(f"\nCandidate {letter} (Page {cand['page']}):\n")
                f.write(f"\"{cand['verbatim']}\"\n")
                f.write(f"Normalized (97 chars): {cand['normalized_AZ']}\n")
        
        f.write("\n" + "-" * 50 + "\n")
        f.write("HOW TO REPRODUCE:\n")
        f.write("1. Get Flint PDF from archive.org or similar source\n")
        f.write("2. Extract exact quotes from cited pages\n")
        f.write("3. Normalize to A-Z only (uppercase, no spaces)\n")
        f.write("4. Apply as OTP key: P = (C - K) mod 26 [Vigenère]\n")
        f.write("5. Check if anchors appear at required positions\n")
        f.write("6. Result: They don't. Anchors fail for all quotes.\n\n")
        
        f.write("CONCLUSION:\n")
        f.write("Flint's manual is NOT the OTP source for K4.\n")
        f.write("The anchor constraints eliminate all possibilities.\n")
    
    # 2. Copy key result files
    files_to_include = [
        (results_dir / "TOPLINE.md", "test_results_summary.md"),
        (results_dir / "RUN_MATRIX.csv", "five_candidates_results.csv"),
        (results_dir / "SWEEP_TOP_HITS.md", "sweep_results.md"),
        (base_path / "experiments/flint_otp/COMPREHENSIVE_REPORT.md", "full_report.md")
    ]
    
    for src, dst in files_to_include:
        if src.exists():
            shutil.copy(src, packet_dir / dst)
    
    # 3. Create quotes file
    quotes_file = packet_dir / "flint_quotes_tested.json"
    quotes_data = {
        "description": "Verbatim Flint quotes tested as OTP keys",
        "source": "A System of Geometry and Trigonometry by Abel Flint (1820)",
        "quotes": []
    }
    
    for letter in "ABCDE":
        cand_path = quotes_dir / f"candidate_{letter}.json"
        if cand_path.exists():
            with open(cand_path) as f:
                quotes_data["quotes"].append(json.load(f))
    
    with open(quotes_file, 'w') as f:
        json.dump(quotes_data, f, indent=2)
    
    # 4. Create ZIP file
    zip_path = base_path / "experiments/flint_otp/FORUM_PACKET.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in packet_dir.iterdir():
            if file_path.is_file():
                zf.write(file_path, file_path.name)
    
    # Clean up temp directory
    shutil.rmtree(packet_dir)
    
    print(f"Forum packet created: {zip_path}")
    print(f"Size: {zip_path.stat().st_size / 1024:.1f} KB")
    print("\nContents:")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for name in zf.namelist():
            info = zf.getinfo(name)
            print(f"  - {name} ({info.file_size} bytes)")


if __name__ == "__main__":
    create_forum_packet()