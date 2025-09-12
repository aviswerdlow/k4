#!/usr/bin/env python3
"""
Fork J.1 - Flint as Plaintext, K1-K3 as Running Key
Tests if Flint scaffolds can be encrypted to K4 using K1-K3 as running keys
"""

import json
import os
from typing import Dict, List, Tuple, Optional
from flint_sources import FlintSources

class J1FlintAsPT:
    def __init__(self, master_seed: int = 1337):
        self.master_seed = master_seed
        self.flint = FlintSources()
        
        # K4 ciphertext
        self.k4_ct = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
        
        # K1-K3 sources (normalized A-Z)
        self.K1_PT = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
        self.K2_PT = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONXDOESLANGLEYKNOWABOUTTHISXTHEYSHOULDITSBURIEDOUTTHERESOMEWHEREXWHOKNOWSTHEEXACTLOCATIONONLYWWTHISWASHISLASTMESSAGEXTHIRTYEIGHTDEGREESFIFTYSEVENMINUTESSIXPOINTFIVESECONDSORTHSEVENTYSEVENDEGREESEIGHTMINUTESFORTYFOURSECONDSWESTIDBYROWSLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADEATINYBREACHINTHEUPPERLEFTHANDCORNERANDTHENWIDENINGTHEHOLEALITTLEIINSERTEDTHECANDLEANDPEEREDINTHEHOTAIRSTRIKINGMYFAIRCAUSEDTHEFLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHINEMERGEDFROMTHEMISTXCANYOUSEEANYTHINGQ"
        self.K3_PT = "SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADEATINYBREACHINTHEUPPERLEFTHANDCORNERANDTHENWIDENINGTHEHOLEALITTLEIINSERTEDTHECANDLEANDPEEREDINTHEHOTAIRSTRIKINGMYFAIRCAUSEDTHEFLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHINEMERGEDFROMTHEMISTXCANYOUSEEANYTHINGQ"
        
        # Cipher families
        self.families = {
            'vigenere': lambda c, k: chr((ord(c) - ord(k)) % 26 + ord('A')),
            'beaufort': lambda c, k: chr((ord(k) - ord(c)) % 26 + ord('A')),
            'varbf': lambda c, k: chr((ord(c) + ord(k) - 2*ord('A')) % 26 + ord('A'))
        }
        
        # Results storage
        self.results = []
    
    def test_scaffold_with_key(self, scaffold_variant: str, key_source: str, 
                               family: str, offset: int) -> Dict:
        """Test if scaffold can be encrypted to K4 using key source"""
        result = {
            'scaffold': scaffold_variant,
            'key_source': key_source,
            'family': family,
            'offset': offset,
            'status': 'failed',
            'mismatches': [],
            'match_rate': 0.0
        }
        
        # Get scaffold (plaintext hypothesis)
        scaffold = self.flint.get_scaffold(scaffold_variant)
        if not scaffold or len(scaffold) != 97:
            result['reason'] = f'Invalid scaffold {scaffold_variant}'
            return result
        
        # Get key source
        if key_source == 'K1':
            key_stream = self.K1_PT
        elif key_source == 'K2':
            key_stream = self.K2_PT
        elif key_source == 'K3':
            key_stream = self.K3_PT
        elif key_source == 'K1K2K3':
            key_stream = self.K1_PT + self.K2_PT + self.K3_PT
        else:
            result['reason'] = f'Unknown key source {key_source}'
            return result
        
        # Check if offset is valid
        if offset + 97 > len(key_stream):
            result['reason'] = f'Offset {offset} too large for key length {len(key_stream)}'
            return result
        
        # Apply encryption and check if it matches K4
        cipher_fn = self.families[family]
        matches = 0
        
        for i in range(97):
            p_char = scaffold[i]
            k_char = key_stream[offset + i]
            
            # Encrypt plaintext with key to get expected ciphertext
            if family == 'vigenere':
                # C = P + K (mod 26)
                expected_c = chr((ord(p_char) + ord(k_char) - 2*ord('A')) % 26 + ord('A'))
            elif family == 'beaufort':
                # C = K - P (mod 26)
                expected_c = chr((ord(k_char) - ord(p_char)) % 26 + ord('A'))
            elif family == 'varbf':
                # C = P - K (mod 26) [variant beaufort]
                expected_c = chr((ord(p_char) - ord(k_char)) % 26 + ord('A'))
            else:
                expected_c = '?'
            
            actual_c = self.k4_ct[i]
            
            if expected_c == actual_c:
                matches += 1
            else:
                if len(result['mismatches']) < 10:  # Limit mismatches recorded
                    result['mismatches'].append({
                        'pos': i,
                        'expected': expected_c,
                        'actual': actual_c,
                        'p': p_char,
                        'k': k_char
                    })
        
        result['matches'] = matches
        result['match_rate'] = matches / 97.0
        
        # Success if high match rate (threshold can be adjusted)
        if matches >= 90:  # ~93% match rate
            result['status'] = 'success'
        
        return result
    
    def sweep_configurations(self, max_tests: int = 1000) -> List[Dict]:
        """Sweep through scaffold/key/family/offset combinations"""
        test_count = 0
        results = []
        
        print("=== J.1 - Flint as Plaintext Testing ===\n")
        
        # Test both scaffold variants
        for scaffold_variant in ['A', 'B']:
            print(f"\nTesting Scaffold {scaffold_variant}...")
            scaffold = self.flint.get_scaffold(scaffold_variant)
            print(f"  Head (0-20): {scaffold[:21]}")
            print(f"  Tail (74-96): {scaffold[74:]}")
            
            # Test each key source
            for key_source in ['K1', 'K2', 'K3', 'K1K2K3']:
                # Determine key length
                if key_source == 'K1':
                    key_len = len(self.K1_PT)
                elif key_source == 'K2':
                    key_len = len(self.K2_PT)
                elif key_source == 'K3':
                    key_len = len(self.K3_PT)
                else:
                    key_len = len(self.K1_PT + self.K2_PT + self.K3_PT)
                
                max_offset = max(0, key_len - 97)
                
                # Coarse sweep (step 7)
                coarse_offsets = list(range(0, min(max_offset + 1, 500), 7))
                if 0 not in coarse_offsets:
                    coarse_offsets.insert(0, 0)
                
                for family in ['vigenere', 'beaufort', 'varbf']:
                    print(f"\n  Testing {key_source} + {family}...")
                    
                    best_results = []
                    
                    # Coarse sweep
                    for offset in coarse_offsets:
                        if test_count >= max_tests:
                            break
                        
                        result = self.test_scaffold_with_key(
                            scaffold_variant, key_source, family, offset
                        )
                        test_count += 1
                        
                        if result['match_rate'] > 0.5:  # Track promising results
                            best_results.append(result)
                            print(f"    Offset {offset}: {result['match_rate']:.1%} match")
                        
                        if result['status'] == 'success':
                            print(f"    *** SUCCESS at offset {offset}! ***")
                            results.append(result)
                    
                    # Fine sweep around best results
                    if best_results and len(best_results) < 10:
                        best_results.sort(key=lambda x: x['match_rate'], reverse=True)
                        
                        for best in best_results[:3]:  # Refine top 3
                            base_offset = best['offset']
                            
                            # Search ±3 around best offset
                            for delta in [-3, -2, -1, 1, 2, 3]:
                                fine_offset = base_offset + delta
                                if fine_offset < 0 or fine_offset > max_offset:
                                    continue
                                if test_count >= max_tests:
                                    break
                                
                                result = self.test_scaffold_with_key(
                                    scaffold_variant, key_source, family, fine_offset
                                )
                                test_count += 1
                                
                                if result['match_rate'] > best['match_rate']:
                                    print(f"      Refined: offset {fine_offset} = {result['match_rate']:.1%}")
                                
                                if result['status'] == 'success':
                                    print(f"      *** REFINED SUCCESS at offset {fine_offset}! ***")
                                    results.append(result)
        
        print(f"\n\nTotal tests: {test_count}")
        print(f"Successful configurations: {len(results)}")
        
        return results
    
    def analyze_results(self, results: List[Dict]):
        """Analyze and report results"""
        if not results:
            print("\n=== No Successful Configurations ===")
            print("J.1 hypothesis (Flint as plaintext) does not produce K4")
            return
        
        print("\n=== Successful Configurations ===")
        for r in results:
            print(f"\nScaffold {r['scaffold']}: {r['key_source']} + {r['family']} @ offset {r['offset']}")
            print(f"  Match rate: {r['match_rate']:.1%}")
            if r['mismatches']:
                print(f"  First mismatches: {r['mismatches'][:3]}")
    
    def save_results(self, results: List[Dict]):
        """Save results to JSON"""
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(output_dir, 'j1_results.json')
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to {output_path}")


def main():
    """Run J.1 testing"""
    j1 = J1FlintAsPT()
    
    # Run sweep
    results = j1.sweep_configurations(max_tests=2000)
    
    # Analyze
    j1.analyze_results(results)
    
    # Save
    if results:
        j1.save_results(results)
    
    # Summary
    print("\n" + "=" * 60)
    print("J.1 SUMMARY")
    print("=" * 60)
    if results:
        print(f"Found {len(results)} successful configurations")
        best = max(results, key=lambda x: x['match_rate'])
        print(f"Best: {best['scaffold']} + {best['key_source']} + {best['family']} @ {best['offset']}")
        print(f"Match rate: {best['match_rate']:.1%}")
    else:
        print("No configurations successfully produce K4 from Flint scaffolds")
        print("J.1 hypothesis rejected - Flint is not the plaintext")


if __name__ == "__main__":
    main()