#!/usr/bin/env python3
"""
Run high-priority manifests with fixed zones and check for BERLINCLOCK
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent / '03_SOLVERS'))
from zone_mask_v1.scripts.zone_runner import ZoneRunner

def score_english(text: str) -> int:
    """Basic English scoring"""
    score = 0
    text = text.upper()
    
    # Common trigrams
    for tri in ['THE', 'AND', 'ING', 'HER', 'HAT', 'HIS', 'THA', 'ERE', 'FOR', 'ENT']:
        score += text.count(tri) * 3
    
    # Common bigrams  
    for bi in ['TH', 'HE', 'IN', 'ER', 'AN', 'ED', 'ND', 'TO', 'EN', 'ES']:
        score += text.count(bi)
    
    return score

def run_manifest(manifest_path: Path, ct_path: Path) -> Dict[str, Any]:
    """Run a single manifest and return results"""
    with open(ct_path, 'r') as f:
        ciphertext = f.read().strip().upper()
    
    try:
        runner = ZoneRunner(str(manifest_path))
        runner.ciphertext = ciphertext
        
        plaintext = runner.decrypt()
        
        # Check BERLINCLOCK
        berlin_found = plaintext[63:74] == 'BERLINCLOCK'
        
        # Score zones
        head_score = score_english(plaintext[0:21])
        mid_score = score_english(plaintext[34:74])
        tail_score = score_english(plaintext[74:97])
        total_score = head_score + mid_score + tail_score
        
        # Round-trip
        roundtrip = runner.verify_roundtrip()
        
        return {
            'manifest': manifest_path.name,
            'berlinclock': berlin_found,
            'roundtrip': roundtrip,
            'total_score': total_score,
            'head_score': head_score,
            'mid_score': mid_score,
            'tail_score': tail_score,
            'head_preview': plaintext[0:20],
            'mid_preview': plaintext[34:54],
            'control': plaintext[63:74]
        }
    except Exception as e:
        return {
            'manifest': manifest_path.name,
            'error': str(e)
        }

def main():
    base_dir = Path(__file__).parent.parent
    config_dir = base_dir / '04_EXPERIMENTS' / 'phase3_zone' / 'configs'
    ct_path = base_dir / '02_DATA' / 'ciphertext_97.txt'
    
    print("RUNNING FIXED MANIFESTS")
    print("=" * 60)
    
    # Priority manifests to test
    priority = [
        'batch_a_A4.json',  # period-5, Vigenere, ABSCISSA
        'batch_a_A5.json',  # period-7, Beaufort, ABSCISSA  
        'batch_a_A6.json',  # period-5, Vigenere, LATITUDE
        'batch_a_A7.json',  # period-7, Beaufort, LONGITUDE
        'batch_b_B3.json',  # tumble, Vigenere, SHADOW/LIGHT
        'test_R4_aligned_berlin.json'  # Known working
    ]
    
    results = []
    for manifest_name in priority:
        manifest_path = config_dir / manifest_name
        if manifest_path.exists():
            print(f"\nTesting {manifest_name}...")
            result = run_manifest(manifest_path, ct_path)
            results.append(result)
            
            if result.get('berlinclock'):
                print(f"  ✅ BERLINCLOCK FOUND!")
            else:
                print(f"  Control: {result.get('control', 'ERROR')}")
            
            if result.get('roundtrip'):
                print(f"  ✓ Round-trip passes")
            
            print(f"  English score: {result.get('total_score', 0)}")
    
    # Sort by score
    results.sort(key=lambda x: x.get('total_score', 0), reverse=True)
    
    print("\n" + "=" * 60)
    print("TOP 3 BY ENGLISH SCORE:")
    for i, r in enumerate(results[:3]):
        print(f"\n{i+1}. {r['manifest']} (score: {r['total_score']})")
        print(f"   BERLIN: {r.get('berlinclock', False)}")
        print(f"   HEAD: {r.get('head_preview', 'N/A')}")
        print(f"   MID:  {r.get('mid_preview', 'N/A')}")
        print(f"   CTRL: {r.get('control', 'N/A')}")

if __name__ == '__main__':
    main()