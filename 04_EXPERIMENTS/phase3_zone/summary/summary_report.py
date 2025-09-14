#!/usr/bin/env python3
"""
Summary Report Generator - Analyze control grid results
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / '03_SOLVERS'))
from zone_mask_v1.scripts.zone_runner import ZoneRunner

# Function words to check outside control span
FUNCTION_WORDS = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 
                  'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'ITS', 'CAN', 'HAD',
                  'HAS', 'HIS', 'HOW', 'MAN', 'NEW', 'NOW', 'OLD', 'SEE',
                  'WAY', 'WHO', 'OIL', 'USE', 'MAY', 'SAY', 'SHE', 'TOO']

def find_function_words(text: str, exclude_start: int = 60, exclude_end: int = 76) -> List[Tuple[str, int]]:
    """Find function words outside the control span"""
    found = []
    text = text.upper()
    
    for word in FUNCTION_WORDS:
        idx = 0
        while True:
            idx = text.find(word, idx)
            if idx == -1:
                break
            # Check if outside control span
            if idx + len(word) <= exclude_start or idx >= exclude_end:
                found.append((word, idx))
            idx += 1
    
    return found

def score_english_excluding_control(text: str) -> float:
    """Score English excluding positions 60-76"""
    if not text:
        return 0
    
    # Remove control span
    text_parts = text[:60] + text[76:] if len(text) > 76 else text[:60]
    text_parts = text_parts.upper()
    
    score = 0
    # Common trigrams
    for tri in ['THE', 'AND', 'ING', 'HER', 'HAT', 'HIS', 'THA', 'ERE', 'FOR', 'ENT']:
        score += text_parts.count(tri) * 3
    
    # Common bigrams
    for bi in ['TH', 'HE', 'IN', 'ER', 'AN', 'ED', 'ND', 'TO', 'EN', 'ES']:
        score += text_parts.count(bi)
    
    return score / len(text_parts) if text_parts else 0

def test_manifest(manifest_path: Path) -> Dict[str, Any]:
    """Test a single manifest and collect metrics"""
    try:
        # Load ciphertext
        ct_path = Path(__file__).parent.parent.parent.parent / '02_DATA' / 'ciphertext_97.txt'
        with open(ct_path, 'r') as f:
            ciphertext = f.read().strip().upper()
        
        # Run decryption
        runner = ZoneRunner(str(manifest_path))
        runner.ciphertext = ciphertext
        plaintext = runner.decrypt()
        
        # Check BERLINCLOCK
        berlin_check = plaintext[63:74] == 'BERLINCLOCK'
        
        # Find function words
        function_words = find_function_words(plaintext)
        
        # Score excluding control
        score_excl = score_english_excluding_control(plaintext)
        
        # Round-trip check
        roundtrip = runner.verify_roundtrip()
        
        return {
            'manifest': manifest_path.name,
            'path': str(manifest_path),
            'berlinclock': berlin_check,
            'roundtrip': roundtrip,
            'control_text': plaintext[63:74],
            'function_words': function_words,
            'function_count': len(function_words),
            'score_excl_control': score_excl,
            'head_preview': plaintext[0:20],
            'mid_preview': plaintext[34:54],
            'tail_preview': plaintext[74:94]
        }
    except Exception as e:
        return {
            'manifest': manifest_path.name,
            'path': str(manifest_path),
            'error': str(e)
        }

def run_summary():
    """Generate summary report for control grid"""
    print("CONTROL GRID SUMMARY REPORT")
    print("=" * 70)
    
    # Test control grid manifests
    grid_dir = Path(__file__).parent.parent / 'configs' / 'control_grid'
    results = []
    
    if grid_dir.exists():
        for manifest_path in sorted(grid_dir.glob('*.json')):
            print(f"\nTesting {manifest_path.name}...")
            result = test_manifest(manifest_path)
            results.append(result)
            
            if result.get('berlinclock'):
                print(f"  ✅ BERLINCLOCK found")
            else:
                print(f"  ❌ Control: {result.get('control_text', 'ERROR')}")
            
            if result.get('function_words'):
                print(f"  📝 Function words: {result['function_count']} found")
                for word, pos in result['function_words'][:3]:
                    print(f"     '{word}' at position {pos}")
    
    # Also test R4 for comparison
    r4_path = Path(__file__).parent.parent.parent.parent / '01_PUBLISHED' / 'candidates' / 'zone_mask_v1_R4' / 'manifest.json'
    if r4_path.exists():
        print(f"\nTesting R4 (baseline)...")
        r4_result = test_manifest(r4_path)
        results.append(r4_result)
    
    # Sort by function word count and score
    results.sort(key=lambda x: (x.get('function_count', 0), x.get('score_excl_control', 0)), reverse=True)
    
    print("\n" + "=" * 70)
    print("TOP 5 CANDIDATES:")
    print("=" * 70)
    
    for i, r in enumerate(results[:5]):
        if 'error' not in r:
            print(f"\n{i+1}. {r['manifest']}")
            print(f"   Path: {r['path']}")
            print(f"   BERLINCLOCK: {'✅ YES' if r['berlinclock'] else '❌ NO'}")
            print(f"   Round-trip: {'✅ PASS' if r['roundtrip'] else '❌ FAIL'}")
            print(f"   Function words outside control: {r['function_count']}")
            if r['function_words']:
                words_str = ', '.join([f"'{w}' @{p}" for w, p in r['function_words'][:3]])
                print(f"   Examples: {words_str}")
            print(f"   Score (excl control): {r['score_excl_control']:.4f}")
            print(f"   HEAD[0:20]: {r['head_preview']}")
            print(f"   MID[34:54]: {r['mid_preview']}")
    
    print("\n" + "=" * 70)
    print("DECISION CRITERIA:")
    print("  ✅ BERLINCLOCK at 63-73")
    print("  ✅ Round-trip validation")
    print("  ✅ Function words outside control span")
    print("  ✅ Null hypothesis p < 0.01")
    
    # Identify candidates for null testing
    candidates = [r for r in results if r.get('berlinclock') and r.get('roundtrip') and r.get('function_count', 0) > 0]
    
    if candidates:
        print(f"\n{len(candidates)} candidates ready for null hypothesis testing:")
        for c in candidates:
            print(f"  - {c['manifest']}")
    else:
        print("\n⚠️ No candidates meet basic criteria for null testing")
    
    return results

def main():
    results = run_summary()
    
    # Save results
    output_path = Path(__file__).parent / 'control_grid_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_path}")

if __name__ == '__main__':
    main()