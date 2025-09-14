#!/usr/bin/env python3
"""
Trace Pipeline - Use verbose mode to trace decrypt stages
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / '03_SOLVERS'))

from zone_mask_v1.scripts.zone_runner import ZoneRunner

def trace_manifest(manifest_path: str):
    """Trace a single manifest through the pipeline"""
    print(f"\n{'='*60}")
    print(f"TRACING: {Path(manifest_path).name}")
    print('='*60)
    
    # Load ciphertext
    ct_path = Path(__file__).parent.parent / '02_DATA' / 'ciphertext_97.txt'
    with open(ct_path, 'r') as f:
        ciphertext = f.read().strip().upper()
    
    # Create verbose runner
    runner = ZoneRunner(manifest_path, verbose=True)
    runner.ciphertext = ciphertext
    
    # Run decrypt with tracing
    plaintext = runner.decrypt()
    
    # Show MID zone result
    mid_start = runner.zones['mid'][0]
    mid_end = runner.zones['mid'][1]
    mid_text = plaintext[mid_start:mid_end+1]
    
    print(f"\nMID zone result: {mid_text[:30]}...")
    
    # Check for BERLINCLOCK
    control_indices = runner.control_indices
    if control_indices:
        control_text = ''.join([plaintext[i] for i in control_indices if i < len(plaintext)])
        print(f"Control text at indices {control_indices[:3]}...: {control_text}")
        if control_text == 'BERLINCLOCK':
            print("✅ BERLINCLOCK FOUND!")
    
    return plaintext

def main():
    # Test A4 manifest (period-5, Vigenere, ABSCISSA)
    manifest_a4 = Path(__file__).parent.parent / '04_EXPERIMENTS' / 'phase3_zone' / 'configs' / 'batch_a_A4.json'
    if manifest_a4.exists():
        trace_manifest(str(manifest_a4))
    
    # Test optimized A4 if it exists
    optimized_a4 = Path(__file__).parent.parent / '04_EXPERIMENTS' / 'phase3_zone' / 'runs' / 'A4_optimized.json'
    if optimized_a4.exists():
        trace_manifest(str(optimized_a4))

if __name__ == '__main__':
    main()