#!/usr/bin/env python3
"""
Explore different keys with fixed zones to find better English
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent / '03_SOLVERS'))
from zone_mask_v1.scripts.zone_runner import ZoneRunner

# Extended key set for exploration
KEY_SET = [
    'ABSCISSA', 'ORDINATE', 'AZIMUTH', 'LATITUDE', 'LONGITUDE',
    'TANGENT', 'SECANT', 'SHADOW', 'LIGHT', 'LODESTONE', 
    'GIRASOL', 'ABSCISSAORDINATE', 'KRYPTOS', 'PALIMPSEST',
    'BERLINCLOCK', 'COMPASS', 'MAGNETIC', 'TRUE', 'DECLINATION'
]

def score_english(text: str) -> Tuple[float, List[str]]:
    """Score text for English and find words"""
    if not text:
        return 0, []
    
    text = text.upper()
    score = 0
    found_words = []
    
    # Check for important K4-related words
    important_words = [
        'BERLIN', 'CLOCK', 'LATITUDE', 'LONGITUDE', 'DEGREE', 'MINUTE', 'SECOND',
        'SHADOW', 'LIGHT', 'BETWEEN', 'SUBTLE', 'ABSENCE', 'ILLUSION', 'NUANCE',
        'SECRET', 'HIDDEN', 'TRUTH', 'KNOWLEDGE', 'POWER', 'LANGLEY', 'STATION',
        'EAST', 'WEST', 'NORTH', 'SOUTH', 'COMPASS', 'BEARING', 'AZIMUTH',
        'TIME', 'SPACE', 'DISTANCE', 'LOCATION', 'POSITION', 'COORDINATE'
    ]
    
    for word in important_words:
        if word in text:
            score += 50
            found_words.append(word)
    
    # Common trigrams
    for tri in ['THE', 'AND', 'ING', 'HER', 'HAT', 'HIS', 'THA', 'ERE', 'FOR', 'ENT',
               'ION', 'TIO', 'ATI', 'TER', 'ATE', 'EST', 'IVE', 'OUR', 'ITH', 'MEN']:
        count = text.count(tri)
        score += count * 3
    
    # Common bigrams
    for bi in ['TH', 'HE', 'IN', 'ER', 'AN', 'ED', 'ND', 'TO', 'EN', 'ES',
              'ST', 'RE', 'NT', 'ON', 'AT', 'OU', 'IT', 'TE', 'ET', 'NG']:
        count = text.count(bi)
        score += count
    
    return score, found_words

def test_key_combination(head_key: str, mid_key: str, tail_key: str, 
                        cipher_family: str = 'vigenere') -> Dict[str, Any]:
    """Test a specific key combination"""
    # Create manifest
    manifest = {
        'zones': {
            'head': {'start': 0, 'end': 20},
            'mid': {'start': 34, 'end': 73},
            'tail': {'start': 74, 'end': 96}
        },
        'control': {
            'mode': 'content',
            'indices': [63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73]
        },
        'cipher': {
            'family': cipher_family,
            'keys': {
                'head': head_key,
                'mid': mid_key,
                'tail': tail_key
            },
            'schedule': 'static'
        }
    }
    
    # Load ciphertext
    ct_path = Path(__file__).parent.parent / '02_DATA' / 'ciphertext_97.txt'
    with open(ct_path, 'r') as f:
        ciphertext = f.read().strip().upper()
    
    # Run decryption
    try:
        runner = ZoneRunner()
        runner.manifest = manifest
        runner.ciphertext = ciphertext
        
        plaintext = runner.decrypt()
        
        # Check for BERLINCLOCK
        control_text = plaintext[63:74]
        
        # Score zones
        head_score, head_words = score_english(plaintext[0:21])
        mid_score, mid_words = score_english(plaintext[34:74])
        tail_score, tail_words = score_english(plaintext[74:97])
        total_score = head_score + mid_score + tail_score
        
        # Find any 4+ letter words in MID beyond control
        mid_text = plaintext[34:63]  # Before control
        words_4plus = []
        
        # Check for common English words
        common_words = ['THAT', 'THIS', 'WITH', 'FROM', 'HAVE', 'BEEN', 'WILL', 
                       'WHAT', 'WHEN', 'WHERE', 'WHICH', 'THERE', 'THEIR', 'ABOUT']
        
        for word in common_words:
            if word in mid_text:
                words_4plus.append(word)
        
        return {
            'keys': f"{head_key}/{mid_key}/{tail_key}",
            'family': cipher_family,
            'total_score': total_score,
            'control': control_text,
            'head_preview': plaintext[0:20],
            'mid_preview': plaintext[34:54],
            'tail_preview': plaintext[74:94],
            'found_words': head_words + mid_words + tail_words,
            'words_4plus': words_4plus,
            'roundtrip': runner.verify_roundtrip()
        }
    except Exception as e:
        return {
            'keys': f"{head_key}/{mid_key}/{tail_key}",
            'error': str(e)
        }

def explore_keys():
    """Explore key combinations systematically"""
    print("KEY EXPLORATION WITH FIXED ZONES")
    print("=" * 60)
    
    results = []
    
    # Test priority combinations
    priority_combos = [
        ('KRYPTOS', 'ABSCISSA', 'PALIMPSEST'),
        ('KRYPTOS', 'ORDINATE', 'PALIMPSEST'),
        ('KRYPTOS', 'LATITUDE', 'PALIMPSEST'),
        ('KRYPTOS', 'LONGITUDE', 'PALIMPSEST'),
        ('SHADOW', 'LIGHT', 'COMPASS'),
        ('ABSCISSA', 'ORDINATE', 'AZIMUTH'),
        ('LATITUDE', 'LONGITUDE', 'COMPASS'),
        ('BERLINCLOCK', 'BERLINCLOCK', 'BERLINCLOCK'),
    ]
    
    print("\nTesting priority combinations...")
    for head, mid, tail in priority_combos:
        # Test with Vigenere
        result = test_key_combination(head, mid, tail, 'vigenere')
        results.append(result)
        
        # Test with Beaufort
        result = test_key_combination(head, mid, tail, 'beaufort')
        results.append(result)
        
        v_score = results[-2].get('total_score', 0)
        b_score = results[-1].get('total_score', 0)
        print(f"  {head}/{mid}/{tail}: V={v_score:.0f}, B={b_score:.0f}")
    
    # Sort by score
    results.sort(key=lambda x: x.get('total_score', 0), reverse=True)
    
    print("\n" + "=" * 60)
    print("TOP 5 BY ENGLISH SCORE:")
    for i, r in enumerate(results[:5]):
        if 'error' not in r:
            print(f"\n{i+1}. {r['keys']} ({r['family'][0].upper()}, score={r['total_score']:.0f})")
            print(f"   Control: {r['control']}")
            print(f"   MID: {r['mid_preview']}")
            if r.get('found_words'):
                print(f"   Words found: {', '.join(r['found_words'][:5])}")
            if r.get('words_4plus'):
                print(f"   4+ letter words in MID: {', '.join(r['words_4plus'])}")
    
    # Find any with BERLINCLOCK
    berlin_found = [r for r in results if r.get('control') == 'BERLINCLOCK']
    if berlin_found:
        print("\n" + "=" * 60)
        print("MANIFESTS WITH BERLINCLOCK:")
        for r in berlin_found:
            print(f"  {r['keys']} ({r['family'][0].upper()})")
    
    return results

def main():
    results = explore_keys()
    
    # Save results
    output_path = Path(__file__).parent.parent / '04_EXPERIMENTS' / 'phase3_zone' / 'runs' / 'key_exploration.json'
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_path}")

if __name__ == '__main__':
    main()