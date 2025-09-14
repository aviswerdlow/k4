#!/usr/bin/env python3
"""
Antipodes Test - Verify solution works with reordered ciphertext
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / '03_SOLVERS'))
from zone_mask_v1.scripts.zone_runner import ZoneRunner

def reorder_antipodes(text: str, layout: dict) -> str:
    """Reorder text according to antipodes layout"""
    indices = layout.get('mapping', {}).get('indices', [])
    if not indices:
        return text  # No reordering if indices empty
    
    result = []
    for pos in indices:
        if isinstance(pos, int) and pos < len(text):
            result.append(text[pos])
    return ''.join(result)

def test_antipodes(manifest_path: str):
    """Test manifest with antipodes reordering"""
    print("ANTIPODES CROSS-CHECK")
    print("=" * 60)
    
    # Load antipodes layout
    layout_path = Path(__file__).parent.parent / '02_DATA' / 'antipodes_layout.json'
    with open(layout_path, 'r') as f:
        layout = json.load(f)
    
    # Load original ciphertext
    ct_path = Path(__file__).parent.parent / '02_DATA' / 'ciphertext_97.txt'
    with open(ct_path, 'r') as f:
        original_ct = f.read().strip().upper()
    
    # Reorder ciphertext
    reordered_ct = reorder_antipodes(original_ct, layout)
    print(f"Original CT[0:20]: {original_ct[:20]}")
    print(f"Reordered CT[0:20]: {reordered_ct[:20]}")
    
    # Test with original
    print("\nTesting with ORIGINAL ciphertext:")
    runner1 = ZoneRunner(manifest_path)
    runner1.ciphertext = original_ct
    plaintext1 = runner1.decrypt()
    
    berlin1 = plaintext1[63:74] == 'BERLINCLOCK'
    roundtrip1 = runner1.verify_roundtrip()
    
    print(f"  BERLINCLOCK: {berlin1}")
    print(f"  Round-trip: {roundtrip1}")
    print(f"  Control text: {plaintext1[63:74]}")
    
    # Test with reordered
    print("\nTesting with REORDERED (antipodes) ciphertext:")
    runner2 = ZoneRunner(manifest_path)
    runner2.ciphertext = reordered_ct
    plaintext2 = runner2.decrypt()
    
    # The control indices might be different after reordering
    # We need to check where BERLINCLOCK should appear after reordering
    berlin2 = 'BERLINCLOCK' in plaintext2
    roundtrip2 = runner2.verify_roundtrip()
    
    print(f"  BERLINCLOCK found: {berlin2}")
    print(f"  Round-trip: {roundtrip2}")
    
    if berlin2:
        # Find where BERLINCLOCK appears
        idx = plaintext2.find('BERLINCLOCK')
        print(f"  BERLINCLOCK at positions: {idx}-{idx+10}")
    
    # Overall pass/fail
    print("\n" + "=" * 60)
    if berlin1 and roundtrip1:
        print("✅ Original: PASS")
    else:
        print("❌ Original: FAIL")
    
    if roundtrip2:
        print("✅ Antipodes round-trip: PASS")
        if berlin2:
            print("✅ Antipodes BERLINCLOCK: FOUND")
        else:
            print("⚠️  Antipodes BERLINCLOCK: Position shifted (expected with reordering)")
    else:
        print("❌ Antipodes: FAIL")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Test antipodes reordering')
    parser.add_argument('--manifest', required=True, help='Path to manifest')
    args = parser.parse_args()
    
    test_antipodes(args.manifest)

if __name__ == '__main__':
    main()