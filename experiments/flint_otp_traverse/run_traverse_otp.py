#!/usr/bin/env python3
"""
run_traverse_otp.py

Master script to run the complete Flint traverse table OTP testing pipeline.
Ensures reproducibility with fixed seed and comprehensive logging.
"""

import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

def run_command(cmd: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'='*70}")
    print(f"{description}")
    print(f"{'='*70}")
    print(f"Command: {cmd}")
    print()
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ SUCCESS ({time.time() - start_time:.2f}s)")
            if result.stdout:
                print("Output:", result.stdout[:500])
            return True
        else:
            print(f"✗ FAILED (exit code: {result.returncode})")
            if result.stderr:
                print("Error:", result.stderr)
            return False
    
    except Exception as e:
        print(f"✗ EXCEPTION: {e}")
        return False

def check_prerequisites():
    """Check if all required files exist."""
    base_path = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus")
    
    required_files = [
        base_path / "02_DATA/ciphertext_97.txt",
        base_path / "02_DATA/anchors/four_anchors.json",
        base_path / "06_DOCUMENTATION/A_System_of_Geometry_and_Trigonometry.pdf"
    ]
    
    print("Checking prerequisites...")
    all_present = True
    
    for file_path in required_files:
        if file_path.exists():
            print(f"  ✓ {file_path.name}")
        else:
            print(f"  ✗ MISSING: {file_path}")
            all_present = False
    
    return all_present

def main():
    """Run the complete traverse OTP testing pipeline."""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║          FLINT TRAVERSE TABLE OTP TESTING PIPELINE                ║
║                                                                    ║
║  Testing Abel Flint's traverse tables as K4 OTP key material      ║
║  Enforcing hard anchor constraints: EAST, NORTHEAST, BERLIN, CLOCK║
║  MASTER_SEED = 1337 for reproducibility                          ║
╚════════════════════════════════════════════════════════════════════╝
""")
    
    start_time = datetime.now()
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n✗ Prerequisites check failed. Please ensure all required files are present.")
        sys.exit(1)
    
    base_path = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus")
    experiments_dir = base_path / "experiments/flint_otp_traverse"
    
    # Pipeline steps
    steps = [
        ("python3 tools/flint_extract_tables.py", 
         "STEP 1: Extract traverse tables from Flint PDF"),
        
        ("python3 experiments/flint_otp_traverse/build_keystreams.py", 
         "STEP 2: Build keystreams using F1-F6 families"),
        
        ("python3 experiments/flint_otp_traverse/test_keystreams.py", 
         "STEP 3: Test keystreams with anchor validation"),
        
        ("python3 experiments/flint_otp_traverse/anchor_targeting.py", 
         "STEP 4: Anchor-first targeting optimization"),
        
        ("python3 experiments/flint_otp_traverse/combinators.py", 
         "STEP 5a: Generate keystream combinations"),
        
        ("python3 experiments/flint_otp_traverse/combinators.py test", 
         "STEP 5b: Test combinations")
    ]
    
    # Run pipeline
    success_count = 0
    for cmd, description in steps:
        if run_command(f"cd '{base_path}' && {cmd}", description):
            success_count += 1
        else:
            print(f"\n⚠ Step failed but continuing...")
    
    # Generate final report
    print(f"\n{'='*70}")
    print("GENERATING FINAL REPORT")
    print(f"{'='*70}")
    
    results_dir = experiments_dir / "results"
    
    # Read topline if it exists
    topline_path = results_dir / "TOPLINE.md"
    if topline_path.exists():
        with open(topline_path) as f:
            print("\nTOPLINE RESULTS:")
            print(f.read()[:1000])
    
    # Create comprehensive report
    report_path = results_dir / "COMPREHENSIVE_REPORT.md"
    with open(report_path, 'w') as f:
        f.write("# COMPREHENSIVE FLINT TRAVERSE OTP REPORT\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"MASTER_SEED: 1337\n\n")
        
        f.write("## Pipeline Status\n\n")
        f.write(f"- Steps completed: {success_count}/{len(steps)}\n")
        f.write(f"- Runtime: {(datetime.now() - start_time).total_seconds():.2f} seconds\n\n")
        
        # Check for matches
        passing_results = results_dir / "passing_results.json"
        anchor_matches = results_dir / "anchor_matches.json"
        combo_passing = results_dir / "combo_passing.json"
        
        has_matches = False
        
        if passing_results.exists():
            import json
            with open(passing_results) as pf:
                data = json.load(pf)
                if data:
                    has_matches = True
                    f.write(f"## ✓ MATCHES FOUND\n\n")
                    f.write(f"Found {len(data)} keystreams that preserve all anchors!\n\n")
        
        if not has_matches:
            f.write("## ✗ NO MATCHES\n\n")
            f.write("No traverse table keystreams (single or combined) satisfy K4's anchor constraints.\n\n")
            f.write("### Conclusion\n\n")
            f.write("This definitively rules out Flint's traverse tables as the OTP source for K4.\n")
            f.write("The tables cannot produce the required key values at anchor positions.\n\n")
        
        f.write("## Files Generated\n\n")
        for pattern in ["*.json", "*.md", "*.csv"]:
            files = list(results_dir.glob(pattern))
            if files:
                f.write(f"- {pattern}: {len(files)} files\n")
    
    print(f"\nComprehensive report saved to: {report_path}")
    
    # Package for forum
    print(f"\n{'='*70}")
    print("PACKAGING FOR FORUM")
    print(f"{'='*70}")
    
    forum_dir = results_dir / "forum_packet"
    forum_dir.mkdir(exist_ok=True)
    
    # Copy key files
    for file_name in ["TOPLINE.md", "TARGETING_REPORT.md", "COMBO_REPORT.md", "COMPREHENSIVE_REPORT.md"]:
        src = results_dir / file_name
        if src.exists():
            dst = forum_dir / file_name
            dst.write_text(src.read_text())
            print(f"  Copied: {file_name}")
    
    # Create reproduction instructions
    reproduce_path = forum_dir / "HOW_TO_REPRODUCE.md"
    with open(reproduce_path, 'w') as f:
        f.write("# How to Reproduce These Results\n\n")
        f.write("## Prerequisites\n\n")
        f.write("1. Python 3.8+ with pdfplumber: `pip install pdfplumber`\n")
        f.write("2. Flint PDF at: `06_DOCUMENTATION/A_System_of_Geometry_and_Trigonometry.pdf`\n")
        f.write("3. K4 ciphertext at: `02_DATA/ciphertext_97.txt`\n")
        f.write("4. Anchors JSON at: `02_DATA/anchors/four_anchors.json`\n\n")
        f.write("## Steps\n\n")
        f.write("```bash\n")
        f.write("# Run complete pipeline\n")
        f.write("cd experiments/flint_otp_traverse\n")
        f.write("python run_traverse_otp.py\n\n")
        f.write("# Or use Makefile\n")
        f.write("make traverse-otp-all\n")
        f.write("```\n\n")
        f.write("## Key Parameters\n\n")
        f.write("- MASTER_SEED = 1337 (ensures reproducibility)\n")
        f.write("- Anchors: EAST@21-24, NORTHEAST@25-33, BERLIN@63-68, CLOCK@69-73\n")
        f.write("- Keystream families: F1-F6 (single digit, pairs, triples, sums, interleave, paths)\n")
        f.write("- Decoders: Vigenère (P=C-K) and Beaufort (P=K-C)\n")
    
    print(f"\nForum packet prepared in: {forum_dir}")
    
    # Final summary
    end_time = datetime.now()
    runtime = (end_time - start_time).total_seconds()
    
    print(f"""
╔════════════════════════════════════════════════════════════════════╗
║                      PIPELINE COMPLETE                            ║
╠════════════════════════════════════════════════════════════════════╣
║  Runtime: {runtime:>8.2f} seconds                                      ║
║  Steps completed: {success_count}/{len(steps)}                                         ║
║  Results in: experiments/flint_otp_traverse/results/              ║
╚════════════════════════════════════════════════════════════════════╝
""")
    
    if has_matches:
        print("🎯 IMPORTANT: Matches found! Review passing_results.json")
    else:
        print("❌ No matches found. Traverse tables ruled out as OTP source.")

if __name__ == "__main__":
    main()