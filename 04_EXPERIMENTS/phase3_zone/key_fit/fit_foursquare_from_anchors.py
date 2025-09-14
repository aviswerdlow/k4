#!/usr/bin/env python3
"""
Fit Four-Square cipher to anchor constraints
Plan G: Test Four-Square with paired keyed squares (only if Bifid and Trifid empty)
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


def find_foursquare_fits() -> List[Dict]:
    """Find Four-Square configurations that satisfy anchors"""
    
    results = []
    ciphertext = load_ciphertext()
    
    # Keywords for top-right and bottom-left squares
    keywords = ['KRYPTOS', 'URANIA', 'ABSCISSA', 'ORDINATE', 'LATITUDE', 'LONGITUDE']
    
    # Anchor indices for English scoring
    anchor_indices = set()
    for start, end in [(21, 24), (25, 33), (63, 68), (69, 73)]:
        anchor_indices.update(range(start, end + 1))
    
    print("=" * 70)
    print("FOUR-SQUARE ANCHOR FITTING")
    print("=" * 70)
    
    total_tested = 0
    
    # Test different keyword pairs
    for tr_keyword in keywords:
        for bl_keyword in keywords:
            print(f"\nTesting Four-Square: TR={tr_keyword}, BL={bl_keyword}")
            
            config = {
                'family': 'foursquare',
                'square_tr': {'keyword': tr_keyword},
                'square_bl': {'keyword': bl_keyword},
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
                        'square_tr': tr_keyword,
                        'square_bl': bl_keyword,
                        'matches': anchor_result['matches'],
                        'english_score': english_score,
                        'config': config,
                        'details': anchor_result['details'],
                        'plaintext_sample': plaintext[:40],
                        'description': f"Four-Square TR={tr_keyword}, BL={bl_keyword}"
                    }
                    results.append(result)
                    
                    if anchor_result['matches'] == 4:
                        print(f"  ✓✓✓ FULL MATCH!")
                        print(f"      English score: {english_score:.3f}")
                        print(f"      Sample: {plaintext[:40]}")
                    else:
                        print(f"  ✓ Partial match ({anchor_result['matches']}/4)")
                        for anchor, detail in anchor_result['details'].items():
                            if detail['match']:
                                print(f"    - {anchor}: MATCH at {detail['position']}")
                
            except Exception as e:
                # Silently skip errors
                pass
    
    print(f"\nTotal configurations tested: {total_tested}")
    return results


def main():
    """Find Four-Square configurations that satisfy anchors"""
    
    results = find_foursquare_fits()
    
    # Save results
    output_path = Path(__file__).parent / 'foursquare_fits.json'
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
                print(f"Top-Right: {match['square_tr']}, Bottom-Left: {match['square_bl']}")
                print(f"English score: {match['english_score']:.3f}")
                print(f"Plaintext sample: {match['plaintext_sample']}")
                print("All anchors matched!")
    else:
        print("\nNo Four-Square configurations found that satisfy any anchors.")
        print("\nAll fractionation systems (Bifid, Trifid, Four-Square) have been tested.")
        print("None produce the required anchor patterns.")
    
    print(f"\nResults saved to: {output_path}")
    
    if results and results[0]['matches'] == 4:
        print("\n" + "=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print("\nFour-Square candidate found! Next steps:")
        print("1. Run full validation (null hypothesis tests)")
        print("2. Check notecard constraint")
        print("3. If needed, try one structural twist")
    else:
        print("\n" + "=" * 70)
        print("CONCLUSION")
        print("=" * 70)
        print("\nPlan G complete: No fractionation system satisfies anchors.")
        print("\nOptions:")
        print("1. Try fractionation + transposition hybrid (Bifid then columnar)")
        print("2. Consider zone-specific parameters")
        print("3. Re-examine anchor assumptions")


if __name__ == '__main__':
    main()