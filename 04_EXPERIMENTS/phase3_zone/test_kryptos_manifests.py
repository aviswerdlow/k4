#!/usr/bin/env python3
"""
Test manifests with KRYPTOS tableau
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent / '03_SOLVERS'))
from zone_mask_v1.scripts.zone_runner import ZoneRunner


def test_manifest(manifest_path: Path) -> Dict[str, Any]:
    """Test a single manifest"""
    # Load manifest
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    # Load ciphertext
    ct_path = Path(__file__).parent.parent.parent / '02_DATA' / 'ciphertext_97.txt'
    with open(ct_path, 'r') as f:
        ciphertext = f.read().strip().upper()
    
    # Run decryption
    runner = ZoneRunner()
    runner.manifest = manifest
    runner.ciphertext = ciphertext
    
    try:
        plaintext = runner.decrypt()
        
        # Check for BERLINCLOCK at positions 63-73
        control_text = plaintext[63:74]
        berlin_found = control_text == 'BERLINCLOCK'
        
        # Check round-trip
        roundtrip = runner.verify_roundtrip()
        
        # Count function words
        function_words = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL']
        word_count = sum(1 for word in function_words if word in plaintext)
        
        # Calculate score
        score = 0
        for tri in ['THE', 'AND', 'ING', 'HER', 'HAT']:
            score += plaintext.count(tri) * 3
        for bi in ['TH', 'HE', 'IN', 'ER', 'AN']:
            score += plaintext.count(bi)
        
        return {
            'manifest': manifest_path.name,
            'tableau': manifest.get('cipher', {}).get('tableau', 'unknown'),
            'family': manifest.get('cipher', {}).get('family', 'unknown'),
            'key': manifest.get('cipher', {}).get('keys', {}).get('mid', 'unknown'),
            'berlinclock': berlin_found,
            'control_text': control_text,
            'roundtrip': roundtrip,
            'function_words': word_count,
            'score': score,
            'head_preview': plaintext[0:20],
            'mid_preview': plaintext[34:54],
            'tail_preview': plaintext[74:94]
        }
    except Exception as e:
        return {
            'manifest': manifest_path.name,
            'error': str(e),
            'berlinclock': False
        }


def main():
    """Test all KRYPTOS tableau manifests"""
    print("=" * 70)
    print("TESTING MANIFESTS WITH KRYPTOS TABLEAU")
    print("=" * 70)
    
    # Find all manifests
    manifest_dir = Path(__file__).parent / 'configs' / 'kryptos_tableau'
    manifests = list(manifest_dir.glob('*.json'))
    
    if not manifests:
        print("No manifests found!")
        return
    
    results = []
    for manifest_path in manifests:
        print(f"\nTesting: {manifest_path.name}")
        result = test_manifest(manifest_path)
        results.append(result)
        
        if 'error' in result:
            print(f"  ERROR: {result['error']}")
        else:
            berlin_str = "✅ BERLIN" if result['berlinclock'] else "❌"
            rt_str = "✅" if result['roundtrip'] else "❌"
            print(f"  {berlin_str} | RT: {rt_str} | Score: {result['score']}")
            print(f"  Control: {result['control_text']}")
            print(f"  HEAD: {result['head_preview']}")
            print(f"  MID:  {result['mid_preview']}")
    
    # Sort by BERLINCLOCK first, then score
    results.sort(key=lambda x: (x.get('berlinclock', False), x.get('score', 0)), reverse=True)
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    berlin_count = sum(1 for r in results if r.get('berlinclock'))
    print(f"\nBERLINCLOCK found: {berlin_count}/{len(results)}")
    
    if berlin_count > 0:
        print("\n✅ BERLINCLOCK MANIFESTS:")
        for r in results:
            if r.get('berlinclock'):
                print(f"  {r['manifest']}")
                print(f"    Family: {r['family']}, Key: {r['key']}")
                print(f"    Round-trip: {r['roundtrip']}, Score: {r['score']}")
    
    print("\nTOP 3 BY SCORE:")
    for i, r in enumerate(results[:3]):
        if 'error' not in r:
            print(f"\n{i+1}. {r['manifest']}")
            print(f"   Control: {r['control_text']}")
            print(f"   Score: {r['score']}, Function words: {r['function_words']}")
            print(f"   HEAD: {r['head_preview']}")
    
    # Key insights
    print("\n" + "=" * 70)
    print("KEY INSIGHTS")
    print("=" * 70)
    print("\nRequired key substrings (from unit tests):")
    print("  Vigenere with KRYPTOS: SYMLWRQOYBQ at MID[29-39]")
    print("  Beaufort with KRYPTOS: HYSSRSHDNLQ at MID[29-39]")
    print("\nThese substrings don't appear in standard dictionary words.")
    print("The KRYPTOS tableau changes the game but natural keys still elusive.")


if __name__ == '__main__':
    main()