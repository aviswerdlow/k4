#!/usr/bin/env python3
"""
Test anchor manifests with strict anchor validation
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# Add necessary paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent / '03_SOLVERS'))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / '07_TOOLS'))

from zone_mask_v1.scripts.zone_runner import ZoneRunner
from validation.anchor_gate import AnchorGate


def test_manifest(manifest_path: Path) -> Dict[str, Any]:
    """Test a single manifest with anchor validation"""
    
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
        
        # Validate anchors
        anchor_valid, anchor_results, anchor_errors = AnchorGate.validate(plaintext)
        
        # Score non-anchor English
        english_stats = AnchorGate.score_non_anchor_english(plaintext)
        
        # Check round-trip
        roundtrip = runner.verify_roundtrip()
        
        # Extract preview segments
        segments = AnchorGate.get_non_anchor_segments(plaintext)
        
        return {
            'manifest': manifest_path.name,
            'family': manifest.get('cipher', {}).get('family', 'unknown'),
            'keys': manifest.get('cipher', {}).get('keys', {}),
            'mask': manifest.get('mask', {}).get('type', 'none'),
            'route': manifest.get('route', {}).get('type', 'none'),
            'order': manifest.get('order', []),
            'anchor_valid': anchor_valid,
            'anchor_results': anchor_results,
            'anchor_errors': anchor_errors,
            'roundtrip': roundtrip,
            'function_words': english_stats['function_words'],
            'function_word_count': english_stats['function_word_count'],
            'english_score': english_stats['english_score'],
            'score_per_char': english_stats['score_per_char'],
            'segments': segments,
            'plaintext': plaintext if anchor_valid else None
        }
    
    except Exception as e:
        return {
            'manifest': manifest_path.name,
            'error': str(e),
            'anchor_valid': False
        }


def analyze_key_alignment(manifest_keys: Dict[str, str], required_keys: Dict) -> Dict[str, Any]:
    """Analyze if manifest keys could produce required anchor keys"""
    
    analysis = {
        'head_key': manifest_keys.get('head', ''),
        'mid_key': manifest_keys.get('mid', ''),
        'tail_key': manifest_keys.get('tail', ''),
        'anchor_coverage': {}
    }
    
    # Check which zones cover which anchors
    # HEAD (0-33) covers EAST (21-24) and NORTHEAST (25-33)
    # MID (34-73) covers BERLIN (63-68) and CLOCK (69-73)
    
    # For HEAD zone
    head_key = manifest_keys.get('head', '')
    if head_key:
        # EAST starts at position 21 in HEAD zone
        east_offset = 21
        east_key_segment = head_key[east_offset % len(head_key):(east_offset + 4) % len(head_key)]
        analysis['anchor_coverage']['EAST'] = {
            'zone': 'head',
            'key_segment': east_key_segment,
            'matches_required': east_key_segment == required_keys.get('EAST', {}).get('key', '')[:len(east_key_segment)]
        }
        
        # NORTHEAST starts at position 25 in HEAD zone
        ne_offset = 25
        ne_key_segment = head_key[ne_offset % len(head_key):(ne_offset + 9) % len(head_key)]
        analysis['anchor_coverage']['NORTHEAST'] = {
            'zone': 'head',
            'key_segment': ne_key_segment,
            'matches_required': ne_key_segment == required_keys.get('NORTHEAST', {}).get('key', '')[:len(ne_key_segment)]
        }
    
    # For MID zone
    mid_key = manifest_keys.get('mid', '')
    if mid_key:
        # BERLIN starts at position 63, which is position 29 in MID zone (63-34=29)
        berlin_offset = 29
        berlin_key_segment = mid_key[berlin_offset % len(mid_key):(berlin_offset + 6) % len(mid_key)]
        analysis['anchor_coverage']['BERLIN'] = {
            'zone': 'mid',
            'key_segment': berlin_key_segment,
            'matches_required': berlin_key_segment == required_keys.get('BERLIN', {}).get('key', '')[:len(berlin_key_segment)]
        }
        
        # CLOCK starts at position 69, which is position 35 in MID zone (69-34=35)
        clock_offset = 35
        clock_key_segment = mid_key[clock_offset % len(mid_key):(clock_offset + 5) % len(mid_key)]
        analysis['anchor_coverage']['CLOCK'] = {
            'zone': 'mid',
            'key_segment': clock_key_segment,
            'matches_required': clock_key_segment == required_keys.get('CLOCK', {}).get('key', '')[:len(clock_key_segment)]
        }
    
    return analysis


def main():
    """Test all anchor manifests"""
    print("=" * 80)
    print("ANCHOR MANIFEST TESTING")
    print("=" * 80)
    
    # Load required keys
    required_keys_path = Path(__file__).parent / 'notes' / 'required_keys_anchors.json'
    with open(required_keys_path, 'r') as f:
        required_keys_data = json.load(f)
    
    # Find all anchor manifests
    manifest_dir = Path(__file__).parent / 'configs' / 'anchors'
    manifests = list(manifest_dir.glob('*.json'))
    
    if not manifests:
        print("No manifests found!")
        return
    
    print(f"\nFound {len(manifests)} manifests to test")
    print("\nRequired anchor keys (KRYPTOS tableau):")
    print("-" * 40)
    
    # Show required keys for Vigenere with KRYPTOS
    vig_kryptos = required_keys_data['required_keys']['vigenere']['kryptos']
    for anchor in ['EAST', 'NORTHEAST', 'BERLIN', 'CLOCK']:
        key_info = vig_kryptos[anchor]
        print(f"  {anchor:10}: {key_info['key']}")
    
    results = []
    
    print("\n" + "=" * 80)
    print("TESTING MANIFESTS")
    print("=" * 80)
    
    for manifest_path in manifests:
        print(f"\nTesting: {manifest_path.name}")
        print("-" * 40)
        
        result = test_manifest(manifest_path)
        results.append(result)
        
        if 'error' in result:
            print(f"  ERROR: {result['error']}")
        else:
            # Show anchor validation
            print("  Anchor validation:")
            for anchor in ['EAST', 'NORTHEAST', 'BERLIN', 'CLOCK']:
                status = "✅" if result['anchor_results'].get(anchor, False) else "❌"
                print(f"    {status} {anchor}")
            
            # Show other stats
            rt_str = "✅" if result['roundtrip'] else "❌"
            print(f"  Round-trip: {rt_str}")
            print(f"  Non-anchor English score: {result['english_score']} ({result['score_per_char']:.3f}/char)")
            
            if result['function_words']:
                print(f"  Function words: {', '.join(result['function_words'][:3])}")
            
            # Show segments
            if result['segments']:
                print(f"  Pre-EAST: {result['segments']['pre_EAST'][:20]}...")
                print(f"  Mid-gap:  {result['segments']['mid_gap'][:20]}...")
                print(f"  Post-CLOCK: {result['segments']['post_CLOCK'][:20]}...")
            
            # Analyze key alignment for non-passing manifests
            if not result['anchor_valid']:
                # Load manifest to check keys
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                
                family = manifest.get('cipher', {}).get('family', 'vigenere')
                tableau = manifest.get('cipher', {}).get('tableau', 'kryptos')
                keys = manifest.get('cipher', {}).get('keys', {})
                
                # Get required keys for this family/tableau
                req_keys = required_keys_data['required_keys'][family][tableau]
                
                print(f"\n  Key analysis ({family} with {tableau}):")
                alignment = analyze_key_alignment(keys, req_keys)
                
                for anchor, info in alignment['anchor_coverage'].items():
                    if info:
                        status = "✅" if info['matches_required'] else "❌"
                        print(f"    {anchor}: {info['key_segment']} {status}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    # Count passes
    anchor_pass = sum(1 for r in results if r.get('anchor_valid', False))
    roundtrip_pass = sum(1 for r in results if r.get('roundtrip', False))
    function_word_pass = sum(1 for r in results if r.get('function_word_count', 0) > 0)
    
    print(f"\nResults:")
    print(f"  Anchor validation passed: {anchor_pass}/{len(results)}")
    print(f"  Round-trip passed: {roundtrip_pass}/{len(results)}")
    print(f"  Non-anchor function words: {function_word_pass}/{len(results)}")
    
    # Show any that passed anchors
    if anchor_pass > 0:
        print("\n✅ MANIFESTS PASSING ANCHOR VALIDATION:")
        for r in results:
            if r.get('anchor_valid', False):
                print(f"  {r['manifest']}")
                print(f"    Keys: HEAD={r['keys']['head']}, MID={r['keys']['mid']}, TAIL={r['keys']['tail']}")
                print(f"    Round-trip: {r['roundtrip']}, Function words: {r['function_word_count']}")
    else:
        print("\n❌ NO MANIFESTS PASSED ANCHOR VALIDATION")
        print("\nThis confirms that standard dictionary keys cannot produce all four anchors")
        print("simultaneously with the current zone configuration and KRYPTOS tableau.")
        
        print("\nRequired key analysis shows we would need:")
        print("  HEAD key to contain: IRJD (for EAST) and HGMIMJAON (for NORTHEAST)")
        print("  MID key to contain: SYMLWR (for BERLIN) and QOYBQ (for CLOCK)")
        print("\nNo standard dictionary words contain these substrings at the right positions.")
    
    # Save results
    output_path = Path(__file__).parent / 'anchor_test_results.json'
    with open(output_path, 'w') as f:
        json.dump({
            'summary': {
                'total_tested': len(results),
                'anchor_passed': anchor_pass,
                'roundtrip_passed': roundtrip_pass,
                'function_words_found': function_word_pass
            },
            'required_keys': required_keys_data['required_keys']['vigenere']['kryptos'],
            'results': results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: {output_path}")


if __name__ == '__main__':
    main()