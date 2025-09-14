#!/usr/bin/env python3
"""
Key Sweep - Systematic key and phase exploration
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / '03_SOLVERS'))
from zone_mask_v1.scripts.zone_runner import ZoneRunner

# Expanded key list
KEYS = [
    'ABSCISSA', 'ORDINATE', 'AZIMUTH',
    'LATITUDE', 'LONGITUDE',
    'TANGENT', 'SECANT', 'RADIAN', 'DEGREE',
    'SHADOW', 'LIGHT', 'LODESTONE', 'GIRASOL',
    'URANIA', 'WELTZEIT', 'ALEXANDERPLATZ',
    'ABSCISSAORDINATE', 'BERLINCLOCK'  # probe only
]

# Function words to check
FUNCTION_WORDS = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL',
                  'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'ITS', 'CAN', 'HAD']

def create_manifest(key: str, family: str, phase: int, mask_type: str, order: List[str]) -> Dict:
    """Create a manifest for testing"""
    # Apply phase rotation to MID key
    mid_key = key[phase:] + key[:phase] if phase > 0 else key
    
    manifest = {
        "zones": {
            "head": {"start": 0, "end": 20},
            "mid": {"start": 34, "end": 73},
            "tail": {"start": 74, "end": 96}
        },
        "control": {
            "mode": "content",
            "indices": [63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73]
        },
        "order": order,
        "cipher": {
            "family": family,
            "keys": {
                "head": "KRYPTOS",  # Fixed for now
                "mid": mid_key,
                "tail": "PALIMPSEST"  # Fixed for now
            },
            "schedule": "static",
            "cipher_direction": "decrypt"
        }
    }
    
    # Add mask if not identity
    if mask_type != "identity":
        if mask_type == "period5":
            manifest["mask"] = {"type": "period5", "params": {}}
        elif mask_type == "diag_weave":
            manifest["mask"] = {"type": "diag_weave", "params": {"rows": 7, "cols": 14, "step": [1, 2]}}
    
    return manifest

def test_manifest(manifest: Dict, manifest_name: str) -> Dict[str, Any]:
    """Test a manifest and return results"""
    try:
        # Load ciphertext
        ct_path = Path(__file__).parent.parent.parent.parent / '02_DATA' / 'ciphertext_97.txt'
        with open(ct_path, 'r') as f:
            ciphertext = f.read().strip().upper()
        
        # Run decryption
        runner = ZoneRunner()
        runner.manifest = manifest
        runner.ciphertext = ciphertext
        
        plaintext = runner.decrypt()
        
        # Check BERLINCLOCK
        berlin_found = plaintext[63:74] == 'BERLINCLOCK'
        
        # Check for function words outside control
        function_words = []
        for word in FUNCTION_WORDS:
            # Check HEAD (0-20)
            if word in plaintext[0:21]:
                function_words.append((word, 'HEAD'))
            # Check MID before control (34-62)
            if word in plaintext[34:63]:
                function_words.append((word, 'MID-pre'))
            # Check TAIL (74-96)
            if word in plaintext[74:97]:
                function_words.append((word, 'TAIL'))
        
        # Score English (excluding control)
        score = 0
        test_text = plaintext[:63] + plaintext[74:]  # Exclude control region
        for tri in ['THE', 'AND', 'ING', 'HER', 'HAT', 'HIS', 'THA', 'ERE', 'FOR', 'ENT']:
            score += test_text.count(tri) * 3
        for bi in ['TH', 'HE', 'IN', 'ER', 'AN', 'ED', 'ND', 'TO', 'EN', 'ES']:
            score += test_text.count(bi)
        
        # Round-trip check
        roundtrip = runner.verify_roundtrip()
        
        return {
            'name': manifest_name,
            'berlinclock': berlin_found,
            'roundtrip': roundtrip,
            'function_words': function_words,
            'function_count': len(function_words),
            'score': score,
            'control_text': plaintext[63:74],
            'head_preview': plaintext[0:20],
            'mid_preview': plaintext[34:54],
            'tail_preview': plaintext[74:94],
            'plaintext': plaintext if berlin_found else None  # Only save if BERLIN found
        }
    except Exception as e:
        return {
            'name': manifest_name,
            'error': str(e),
            'berlinclock': False,
            'score': 0
        }

def run_sweep():
    """Run the key and phase sweep"""
    results = []
    configs_dir = Path(__file__).parent.parent / 'configs' / 'sweep'
    configs_dir.mkdir(exist_ok=True)
    
    print("KEY AND PHASE SWEEP")
    print("=" * 70)
    
    # Test parameters
    families = ['vigenere', 'beaufort']
    mask_types = ['identity', 'period5', 'diag_weave']
    orders = [['mask', 'cipher'], ['cipher', 'mask']]
    
    total_tests = 0
    berlin_found_count = 0
    
    for key in KEYS:
        print(f"\nTesting key: {key}")
        key_phases = range(len(key))  # Test all phases
        
        for family in families:
            for phase in key_phases:
                for mask_type in mask_types:
                    for order in orders:
                        # Skip cipher->mask with identity (no point)
                        if mask_type == 'identity' and order == ['cipher', 'mask']:
                            continue
                        
                        # Create manifest
                        manifest = create_manifest(key, family, phase, mask_type, order)
                        
                        # Generate name
                        order_str = 'mc' if order == ['mask', 'cipher'] else 'cm'
                        mask_str = 'id' if mask_type == 'identity' else ('p5' if mask_type == 'period5' else 'dw')
                        name = f"{mask_str}_{family[:3]}_{key}_ph{phase}_{order_str}"
                        
                        # Save manifest
                        manifest_path = configs_dir / f"{name}.json"
                        with open(manifest_path, 'w') as f:
                            json.dump(manifest, f, indent=2)
                        
                        # Test it
                        result = test_manifest(manifest, name)
                        results.append(result)
                        total_tests += 1
                        
                        if result.get('berlinclock'):
                            berlin_found_count += 1
                            print(f"  ✅ BERLINCLOCK: {name}")
                            print(f"     Function words: {result['function_count']}")
                            if result['function_words']:
                                words = ', '.join([f"{w[0]}({w[1]})" for w in result['function_words'][:3]])
                                print(f"     Words: {words}")
    
    # Sort by: BERLINCLOCK first, then function words, then score
    results.sort(key=lambda x: (
        x.get('berlinclock', False),
        x.get('function_count', 0),
        x.get('score', 0)
    ), reverse=True)
    
    print("\n" + "=" * 70)
    print(f"SWEEP COMPLETE: {total_tests} tests, {berlin_found_count} with BERLINCLOCK")
    print("=" * 70)
    
    # Save results
    output_path = Path(__file__).parent / 'sweep_results.json'
    with open(output_path, 'w') as f:
        json.dump(results[:20], f, indent=2)  # Save top 20
    
    return results

def print_leaderboard(results: List[Dict], top_n: int = 10):
    """Print leaderboard of results"""
    print("\nLEADERBOARD - TOP 10")
    print("=" * 70)
    
    for i, r in enumerate(results[:top_n]):
        if 'error' not in r:
            berlin_str = "✅ BERLIN" if r.get('berlinclock') else "❌"
            rt_str = "✅" if r.get('roundtrip') else "❌"
            
            print(f"\n{i+1}. {r['name']}")
            print(f"   {berlin_str} | RT: {rt_str} | Score: {r['score']} | Func words: {r['function_count']}")
            print(f"   Control: {r.get('control_text', 'ERROR')}")
            
            if r.get('function_words'):
                words = ', '.join([f"{w[0]}({w[1]})" for w in r['function_words'][:3]])
                print(f"   Words: {words}")
            
            print(f"   HEAD: {r.get('head_preview', 'N/A')}")
            print(f"   MID:  {r.get('mid_preview', 'N/A')}")

def main():
    results = run_sweep()
    print_leaderboard(results)
    
    # Report manifests ready for testing
    candidates = [r for r in results if r.get('berlinclock') and r.get('roundtrip') and r.get('function_count', 0) > 0]
    
    if candidates:
        print("\n" + "=" * 70)
        print(f"{len(candidates)} CANDIDATES FOR NULL TESTING:")
        for c in candidates[:5]:
            manifest_path = Path(__file__).parent.parent / 'configs' / 'sweep' / f"{c['name']}.json"
            print(f"  {manifest_path}")
    
    # Save top 3 paths
    top3_path = Path(__file__).parent / 'top3_manifests.txt'
    with open(top3_path, 'w') as f:
        for r in results[:3]:
            manifest_path = Path(__file__).parent.parent / 'configs' / 'sweep' / f"{r['name']}.json"
            f.write(f"{manifest_path}\n")
    
    print(f"\nTop 3 manifest paths saved to: {top3_path}")

if __name__ == '__main__':
    main()