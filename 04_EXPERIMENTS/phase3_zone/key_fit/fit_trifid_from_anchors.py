#!/usr/bin/env python3
"""
Fit Trifid cipher to anchor constraints
Plan G: Test Trifid with various cubes and periods (only if Bifid empty)
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Optional

# Add cipher_fractionation to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / '03_SOLVERS' / 'zone_mask_v1' / 'scripts'))
from cipher_fractionation import create_fractionation_cipher, decode


def load_ciphertext() -> str:
    """Load K4 ciphertext"""
    ct_path = Path(__file__).parent.parent.parent.parent / '02_DATA' / 'ciphertext_97.txt'
    with open(ct_path, 'r') as f:
        return f.read().strip().upper()


def test_anchors(plaintext: str) -> Dict:
    """
    Test if plaintext has correct anchors at expected positions
    
    Returns:
        Dictionary with match count and details
    """
    # Define anchors (0-based indices)
    anchors = [
        ('EAST', 21, 24),
        ('NORTHEAST', 25, 33),
        ('BERLIN', 63, 68),
        ('CLOCK', 69, 73)
    ]
    
    matches = 0
    details = {}
    
    for anchor_text, start, end in anchors:
        if start < len(plaintext) and end < len(plaintext):
            actual = plaintext[start:end+1]
            is_match = actual == anchor_text
            if is_match:
                matches += 1
            details[anchor_text] = {
                'expected': anchor_text,
                'actual': actual,
                'match': is_match,
                'position': f"{start}-{end}"
            }
        else:
            details[anchor_text] = {
                'expected': anchor_text,
                'actual': 'OUT_OF_RANGE',
                'match': False,
                'position': f"{start}-{end}"
            }
    
    return {'matches': matches, 'details': details}


def compute_english_score(text: str, exclude_indices: List[int] = None) -> float:
    """
    Compute English-likeness score for non-anchor text
    """
    if exclude_indices is None:
        exclude_indices = []
    
    common_bigrams = ['TH', 'HE', 'IN', 'ER', 'AN', 'RE', 'ED', 'ON', 'ES', 'ST',
                      'EN', 'AT', 'TO', 'NT', 'HA', 'ND', 'OU', 'EA', 'NG', 'AS']
    common_trigrams = ['THE', 'AND', 'ING', 'HER', 'HAT', 'HIS', 'THA', 'ERE',
                       'FOR', 'ENT', 'ION', 'TER', 'WAS', 'YOU', 'ITH', 'VER']
    
    non_anchor_text = ''.join(text[i] for i in range(len(text)) if i not in exclude_indices)
    
    if len(non_anchor_text) < 3:
        return 0.0
    
    score = 0
    
    for bigram in common_bigrams:
        score += non_anchor_text.count(bigram)
    
    for trigram in common_trigrams:
        score += non_anchor_text.count(trigram) * 2
    
    max_score = len(non_anchor_text) // 2
    if max_score > 0:
        return min(1.0, score / max_score)
    
    return 0.0


def find_trifid_fits() -> List[Dict]:
    """Find Trifid configurations that satisfy anchors"""
    
    results = []
    ciphertext = load_ciphertext()
    
    # Trifid alphabet options (27-letter)
    alphabet_options = [
        'kryptos27',  # KRYPTOS-based 27-letter
        'URANIA',     # URANIA-keyed
        'ABSCISSA',   # ABSCISSA-keyed
        'MERIDIAN'    # MERIDIAN-keyed
    ]
    
    # Periods to test
    periods = list(range(5, 16))  # 5 to 15
    
    # Anchor indices for English scoring
    anchor_indices = set()
    for start, end in [(21, 24), (25, 33), (63, 68), (69, 73)]:
        anchor_indices.update(range(start, end + 1))
    
    print("=" * 70)
    print("TRIFID ANCHOR FITTING")
    print("=" * 70)
    
    total_tested = 0
    
    for alphabet in alphabet_options:
        print(f"\nTesting Trifid alphabet: {alphabet}")
        
        for period in periods:
            config = {
                'family': 'trifid',
                'alphabet': alphabet,
                'period': period,
                'cipher_direction': 'decrypt'
            }
            
            total_tested += 1
            
            try:
                # Decrypt entire ciphertext
                plaintext = decode(ciphertext, config)
                
                # Test anchors
                anchor_result = test_anchors(plaintext)
                
                if anchor_result['matches'] > 0:
                    # Compute English score for non-anchor text
                    english_score = compute_english_score(plaintext, list(anchor_indices))
                    
                    result = {
                        'alphabet': alphabet,
                        'period': period,
                        'matches': anchor_result['matches'],
                        'english_score': english_score,
                        'config': config,
                        'details': anchor_result['details'],
                        'plaintext_sample': plaintext[:40],
                        'description': f"Trifid {alphabet} p={period}"
                    }
                    results.append(result)
                    
                    if anchor_result['matches'] == 4:
                        print(f"  ✓✓✓ FULL MATCH: period={period}")
                        print(f"      English score: {english_score:.3f}")
                        print(f"      Sample: {plaintext[:40]}")
                    else:
                        print(f"  ✓ Partial match ({anchor_result['matches']}/4): period={period}")
                        for anchor, detail in anchor_result['details'].items():
                            if detail['match']:
                                print(f"    - {anchor}: MATCH at {detail['position']}")
                
            except Exception as e:
                # Silently skip errors
                pass
    
    print(f"\nTotal configurations tested: {total_tested}")
    return results


def main():
    """Find Trifid configurations that satisfy anchors"""
    
    results = find_trifid_fits()
    
    # Save results
    output_path = Path(__file__).parent / 'trifid_fits.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if results:
        # Sort by matches then English score
        results.sort(key=lambda x: (x['matches'], x['english_score']), reverse=True)
        
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
            
            # Show top 3 by English score
            for cfg in sorted(configs, key=lambda x: x['english_score'], reverse=True)[:3]:
                print(f"  - {cfg['description']}, English score: {cfg['english_score']:.3f}")
                for anchor, detail in cfg['details'].items():
                    if detail['match']:
                        print(f"    ✓ {anchor} at {detail['position']}")
        
        # Check for full matches
        full_matches = [r for r in results if r['matches'] == 4]
        if full_matches:
            print("\n" + "!" * 70)
            print("SOLUTION CANDIDATE FOUND!")
            print("!" * 70)
            for match in full_matches:
                print(f"\n{match['description']}")
                print(f"Alphabet: {match['alphabet']}, Period: {match['period']}")
                print(f"English score: {match['english_score']:.3f}")
                print(f"Plaintext sample: {match['plaintext_sample']}")
                print("All anchors matched!")
    else:
        print("\nNo Trifid configurations found that satisfy any anchors.")
        print("Moving to Four-Square testing...")
    
    print(f"\nResults saved to: {output_path}")
    
    if results and results[0]['matches'] == 4:
        print("\n" + "=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print("\nTrifid candidate found! Next steps:")
        print("1. Run full validation (null hypothesis tests)")
        print("2. Check notecard constraint")
        print("3. If needed, try one structural twist")
    elif not results:
        print("\n" + "=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print("\nTrifid empty. Moving to Four-Square testing...")
        print("Run: fit_foursquare_from_anchors.py")


if __name__ == '__main__':
    main()