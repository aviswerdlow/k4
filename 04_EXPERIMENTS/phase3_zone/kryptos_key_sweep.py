#!/usr/bin/env python3
"""
Key sweep with KRYPTOS tableau
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent / '03_SOLVERS'))
from zone_mask_v1.scripts.zone_runner import ZoneRunner

# Test keys
KEYS = [
    'ABSCISSA', 'ORDINATE', 'AZIMUTH',
    'LATITUDE', 'LONGITUDE',
    'TANGENT', 'SECANT', 'RADIAN', 'DEGREE',
    'SHADOW', 'LIGHT', 'LODESTONE', 'GIRASOL',
    'URANIA', 'WELTZEIT', 'ALEXANDERPLATZ',
    'KRYPTOS', 'PALIMPSEST', 'BERLINCLOCK'
]


def create_manifest(key: str, family: str, phase: int) -> Dict:
    """Create a manifest with KRYPTOS tableau"""
    # Apply phase rotation to MID key
    mid_key = key[phase:] + key[:phase] if phase > 0 else key
    
    return {
        "zones": {
            "head": {"start": 0, "end": 33},
            "mid": {"start": 34, "end": 73},
            "tail": {"start": 74, "end": 96}
        },
        "control": {
            "mode": "content",
            "indices": [63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73]
        },
        "cipher": {
            "family": family,
            "tableau": "kryptos",  # Use KRYPTOS tableau
            "keys": {
                "head": "KRYPTOS",
                "mid": mid_key,
                "tail": "PALIMPSEST"
            },
            "schedule": "static",
            "cipher_direction": "decrypt"
        }
    }


def test_manifest(manifest: Dict, name: str) -> Dict[str, Any]:
    """Test a manifest"""
    try:
        # Load ciphertext
        ct_path = Path(__file__).parent.parent.parent / '02_DATA' / 'ciphertext_97.txt'
        with open(ct_path, 'r') as f:
            ciphertext = f.read().strip().upper()
        
        # Run decryption
        runner = ZoneRunner()
        runner.manifest = manifest
        runner.ciphertext = ciphertext
        
        plaintext = runner.decrypt()
        
        # Check BERLINCLOCK
        control_text = plaintext[63:74]
        berlin_found = control_text == 'BERLINCLOCK'
        
        # Round-trip check
        roundtrip = runner.verify_roundtrip()
        
        # Score
        score = 0
        for tri in ['THE', 'AND', 'ING', 'HER', 'HAT']:
            score += plaintext.count(tri) * 3
        for bi in ['TH', 'HE', 'IN', 'ER', 'AN']:
            score += plaintext.count(bi)
        
        return {
            'name': name,
            'berlinclock': berlin_found,
            'control_text': control_text,
            'roundtrip': roundtrip,
            'score': score,
            'head_preview': plaintext[0:20],
            'mid_preview': plaintext[34:54],
            'plaintext': plaintext if berlin_found else None
        }
    except Exception as e:
        return {
            'name': name,
            'error': str(e),
            'berlinclock': False
        }


def main():
    """Run key sweep with KRYPTOS tableau"""
    print("=" * 70)
    print("KEY SWEEP WITH KRYPTOS TABLEAU")
    print("=" * 70)
    
    results = []
    families = ['vigenere', 'beaufort']
    
    total_tests = 0
    berlin_count = 0
    
    print("\nTesting keys with KRYPTOS tableau...")
    
    for key in KEYS:
        for family in families:
            # Test all phases
            for phase in range(len(key)):
                manifest = create_manifest(key, family, phase)
                name = f"{family[:3]}_{key}_ph{phase}"
                
                result = test_manifest(manifest, name)
                results.append(result)
                total_tests += 1
                
                if result.get('berlinclock'):
                    berlin_count += 1
                    print(f"  ✅ BERLINCLOCK: {name}")
                    print(f"     Round-trip: {result['roundtrip']}")
    
    # Sort by BERLINCLOCK first, then score
    results.sort(key=lambda x: (x.get('berlinclock', False), x.get('score', 0)), reverse=True)
    
    print(f"\nTotal tests: {total_tests}")
    print(f"BERLINCLOCK found: {berlin_count}")
    
    # Show top results
    print("\nTOP 5 RESULTS:")
    print("-" * 70)
    
    for i, r in enumerate(results[:5]):
        if 'error' not in r:
            berlin_str = "✅" if r.get('berlinclock') else "❌"
            rt_str = "✅" if r.get('roundtrip') else "❌"
            print(f"\n{i+1}. {r['name']}")
            print(f"   BERLIN: {berlin_str} | RT: {rt_str} | Score: {r['score']}")
            print(f"   Control: {r['control_text']}")
            print(f"   HEAD: {r['head_preview']}")
            print(f"   MID:  {r['mid_preview']}")
    
    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    
    if berlin_count == 0:
        print("\n❌ No natural BERLINCLOCK found with KRYPTOS tableau either.")
        print("\nThis confirms that even with the KRYPTOS-keyed tableau,")
        print("standard dictionary keys don't produce BERLINCLOCK naturally.")
        print("\nRequired key substrings (from analysis):")
        print("  Vigenere: SYMLWRQOYBQ")
        print("  Beaufort: HYSSRSHDNLQ")
        print("\nThese appear to be artificial or derived keys.")
    else:
        print(f"\n✅ Found {berlin_count} BERLINCLOCK solutions!")
        for r in results:
            if r.get('berlinclock'):
                print(f"  {r['name']}")
    
    # Save results
    output_path = Path(__file__).parent / 'kryptos_sweep_results.json'
    with open(output_path, 'w') as f:
        json.dump(results[:20], f, indent=2)
    
    print(f"\nResults saved to: {output_path}")


if __name__ == '__main__':
    main()