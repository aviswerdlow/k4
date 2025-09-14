#!/usr/bin/env python3
"""
Fit autokey systems to anchor constraints
Plan F: Test autokey with various seed keys against anchors
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Optional

# Add cipher_families_autokey to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / '03_SOLVERS' / 'zone_mask_v1' / 'scripts'))
from cipher_families_autokey import create_autokey_cipher, decode


def load_ciphertext() -> str:
    """Load K4 ciphertext"""
    ct_path = Path(__file__).parent.parent.parent.parent / '02_DATA' / 'ciphertext_97.txt'
    with open(ct_path, 'r') as f:
        return f.read().strip().upper()


def test_anchor_decryption(config: Dict) -> bool:
    """
    Test if an autokey configuration correctly decrypts all anchors
    
    Returns:
        True if all anchors decrypt correctly
    """
    ciphertext = load_ciphertext()
    
    # Define anchors
    anchors = [
        ('EAST', 21, 24),
        ('NORTHEAST', 25, 33),
        ('BERLIN', 63, 68),
        ('CLOCK', 69, 73)
    ]
    
    # Test each anchor
    for anchor_text, start, end in anchors:
        # Extract ciphertext segment
        ct_segment = ciphertext[start:end+1]
        
        # Create a new cipher instance for each segment
        # This is important for autokey as the keystream depends on position
        # For a proper test, we'd need to decrypt from the beginning
        # but for now we'll test segment-by-segment
        try:
            # For autokey, we need to consider the full ciphertext up to this point
            # to build the correct keystream
            if start == 0:
                pt_segment = decode(ct_segment, config)
            else:
                # For segments not at the start, the autokey would have
                # already incorporated previous plaintext/ciphertext
                # This is a limitation of testing segments independently
                pt_segment = decode(ct_segment, config)
            
            if pt_segment != anchor_text:
                return False
        except Exception:
            return False
    
    return True


def test_full_decryption_at_anchors(config: Dict) -> Dict:
    """
    Test full decryption and check anchor positions
    
    Returns dict with anchor matches
    """
    ciphertext = load_ciphertext()
    
    # Decrypt entire ciphertext
    try:
        plaintext = decode(ciphertext, config)
    except Exception:
        return {'matches': 0, 'details': {}}
    
    # Check anchors
    anchors = [
        ('EAST', 21, 24),
        ('NORTHEAST', 25, 33),
        ('BERLIN', 63, 68),
        ('CLOCK', 69, 73)
    ]
    
    matches = 0
    details = {}
    
    for anchor_text, start, end in anchors:
        actual = plaintext[start:end+1]
        is_match = actual == anchor_text
        if is_match:
            matches += 1
        details[anchor_text] = {
            'expected': anchor_text,
            'actual': actual,
            'match': is_match
        }
    
    return {'matches': matches, 'details': details}


def find_autokey_fits() -> List[Dict]:
    """Find autokey configurations that satisfy all anchors"""
    
    results = []
    
    # Define search space
    families = ['vigenere', 'beaufort']
    modes = ['pt', 'ct']
    
    # Seed keys to test
    seed_keys = [
        'URANIA', 'WELTZEIT', 'MERIDIAN', 'AZIMUTH', 'SECANT',
        'TANGENT', 'RADIAN', 'DEGREE', 'LAT', 'LONG', 'LATLON',
        'GIRASOL', 'COMPASS', 'TRUE', 'MAGNET', 'BERLIN', 'CLOCK',
        'EAST', 'NORTHEAST', 'NORTH', 'SOUTH', 'WEST', 'KRYPTOS',
        'ABSCISSA', 'ORDINATE', 'LATITUDE', 'LONGITUDE'
    ]
    
    print("=" * 70)
    print("AUTOKEY ANCHOR FITTING")
    print("=" * 70)
    
    total_tested = 0
    
    for family in families:
        for mode in modes:
            mode_name = 'plaintext' if mode == 'pt' else 'ciphertext'
            print(f"\nTesting {family.upper()} {mode_name}-autokey...")
            
            for seed in seed_keys:
                config = {
                    'family': family,
                    'mode': mode,
                    'seed_key': seed,
                    'tableau': 'kryptos'
                }
                
                total_tested += 1
                
                # Test full decryption
                result = test_full_decryption_at_anchors(config)
                
                if result['matches'] > 0:
                    fit_result = {
                        'family': family,
                        'mode': mode_name,
                        'seed_key': seed,
                        'matches': result['matches'],
                        'config': config,
                        'details': result['details'],
                        'description': f"{family} {mode_name}-autokey, seed={seed}"
                    }
                    results.append(fit_result)
                    
                    if result['matches'] == 4:
                        print(f"  ✓✓✓ FULL MATCH: {fit_result['description']}")
                    else:
                        print(f"  ✓ Partial match ({result['matches']}/4): {fit_result['description']}")
                        for anchor, detail in result['details'].items():
                            if detail['match']:
                                print(f"    - {anchor}: MATCH")
    
    print(f"\nTotal configurations tested: {total_tested}")
    return results


def main():
    """Find autokey configurations that satisfy anchors"""
    
    results = find_autokey_fits()
    
    # Save results
    output_path = Path(__file__).parent / 'autokey_fits.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if results:
        # Sort by number of matches
        results.sort(key=lambda x: x['matches'], reverse=True)
        
        print(f"\nFound {len(results)} configurations with partial matches:")
        
        # Group by match count
        by_matches = {}
        for r in results:
            count = r['matches']
            if count not in by_matches:
                by_matches[count] = []
            by_matches[count].append(r)
        
        for count in sorted(by_matches.keys(), reverse=True):
            configs = by_matches[count]
            print(f"\n{count}/4 anchors matched: {len(configs)} configurations")
            for cfg in configs[:5]:  # Show first 5
                print(f"  - {cfg['description']}")
                for anchor, detail in cfg['details'].items():
                    if detail['match']:
                        print(f"    ✓ {anchor}")
        
        # Check for full matches
        full_matches = [r for r in results if r['matches'] == 4]
        if full_matches:
            print("\n" + "!" * 70)
            print("SOLUTION FOUND!")
            print("!" * 70)
            for match in full_matches:
                print(f"\n{match['description']}")
                print(f"Seed key: {match['seed_key']}")
                print("All anchors matched!")
    else:
        print("\nNo autokey configurations found that satisfy any anchors.")
        print("This suggests K4 may not use standard autokey ciphers,")
        print("or uses them with additional transformations.")
    
    print(f"\nResults saved to: {output_path}")
    
    if results and results[0]['matches'] == 4:
        print("\n" + "=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print("\nAutokey solution found! Next steps:")
        print("1. Generate full plaintext manifest")
        print("2. Validate against null hypothesis")
        print("3. Check for semantic coherence")
    else:
        print("\n" + "=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print("\nAutokey systems tested without full success.")
        print("Consider:")
        print("1. Fractionation systems (Bifid/Trifid)")
        print("2. Multiple independent keys for different zones")
        print("3. Non-classical cryptographic approaches")


if __name__ == '__main__':
    main()