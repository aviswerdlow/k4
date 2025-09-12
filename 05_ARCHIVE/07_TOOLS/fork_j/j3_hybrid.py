#!/usr/bin/env python3
"""
Fork J.3 - Hybrid Running Key Combinations
Tests mixed Flint and K1-K3 sources as running keys for different zones
"""

import json
import os
from typing import Dict, List, Tuple, Optional
from flint_sources import FlintSources

class J3Hybrid:
    def __init__(self, master_seed: int = 1337):
        self.master_seed = master_seed
        self.flint = FlintSources()
        
        # K4 ciphertext
        self.k4_ct = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
        
        # K1-K3 sources
        self.K1_PT = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
        self.K2_PT = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONXDOESLANGLEYKNOWABOUTTHISXTHEYSHOULDITSBURIEDOUTTHERESOMEWHEREXWHOKNOWSTHEEXACTLOCATIONONLYWWTHISWASHISLASTMESSAGEXTHIRTYEIGHTDEGREESFIFTYSEVENMINUTESSIXPOINTFIVESECONDSORTHSEVENTYSEVENDEGREESEIGHTMINUTESFORTYFOURSECONDSWESTIDBYROWSLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADEATINYBREACHINTHEUPPERLEFTHANDCORNERANDTHENWIDENINGTHEHOLEALITTLEIINSERTEDTHECANDLEANDPEEREDINTHEHOTAIRSTRIKINGMYFAIRCAUSEDTHEFLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHINEMERGEDFROMTHEMISTXCANYOUSEEANYTHINGQ"
        self.K3_PT = "SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADEATINYBREACHINTHEUPPERLEFTHANDCORNERANDTHENWIDENINGTHEHOLEALITTLEIINSERTEDTHECANDLEANDPEEREDINTHEHOTAIRSTRIKINGMYFAIRCAUSEDTHEFLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHINEMERGEDFROMTHEMISTXCANYOUSEEANYTHINGQ"
        
        # Zone definitions
        self.zones = {
            'Z0': {'start': 0, 'end': 20, 'name': 'head'},      # Head
            'Z1': {'start': 21, 'end': 24, 'name': 'EAST'},     # EAST
            'Z2': {'start': 25, 'end': 33, 'name': 'NORTHEAST'}, # NORTHEAST
            'Z3': {'start': 34, 'end': 62, 'name': 'middle'},   # Between anchors
            'Z4': {'start': 63, 'end': 68, 'name': 'BERLIN'},   # BERLIN
            'Z5': {'start': 69, 'end': 73, 'name': 'CLOCK'},    # CLOCK
            'Z6': {'start': 74, 'end': 96, 'name': 'tail'}      # Tail
        }
        
        # Known anchors
        self.anchors = {
            'EAST': {'start': 21, 'end': 24, 'text': 'EAST'},
            'NORTHEAST': {'start': 25, 'end': 33, 'text': 'NORTHEAST'},
            'BERLIN': {'start': 63, 'end': 68, 'text': 'BERLIN'},
            'CLOCK': {'start': 69, 'end': 73, 'text': 'CLOCK'}
        }
        
        # Cipher families
        self.families = {
            'vigenere': lambda c, k: chr((ord(c) - ord(k)) % 26 + ord('A')),
            'beaufort': lambda c, k: chr((ord(k) - ord(c)) % 26 + ord('A')),
            'varbf': lambda c, k: chr((ord(c) + ord(k) - 2*ord('A')) % 26 + ord('A'))
        }
        
        # All available key sources
        self.all_sources = {}
        self.all_sources.update(self.flint.key_sources)
        self.all_sources['K1'] = self.K1_PT
        self.all_sources['K2'] = self.K2_PT
        self.all_sources['K3'] = self.K3_PT
        self.all_sources['K1K2K3'] = self.K1_PT + self.K2_PT + self.K3_PT
        
        # English validation
        self.common_bigrams = {'TH', 'HE', 'IN', 'ER', 'AN', 'ED', 'ND', 'TO', 'EN', 'ES'}
        self.common_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL'}
        
        # Results storage
        self.results = []
    
    def decrypt_zone(self, zone_name: str, key_source: str, family: str, 
                     offset: int, reset: bool = False) -> Tuple[str, bool]:
        """Decrypt a specific zone with given key configuration"""
        zone = self.zones[zone_name]
        start = zone['start']
        end = zone['end']
        length = end - start + 1
        
        # Get key stream
        key_stream = self.all_sources.get(key_source, '')
        if not key_stream:
            return '?' * length, False
        
        # Calculate effective offset
        if reset:
            # Reset offset at zone boundary
            effective_offset = offset
        else:
            # Continue from global position
            effective_offset = offset + start
        
        # Check if we have enough key material
        if effective_offset + length > len(key_stream):
            return '?' * length, False
        
        # Decrypt
        decrypt_fn = self.families[family]
        plaintext = []
        
        for i in range(length):
            c_char = self.k4_ct[start + i]
            k_char = key_stream[effective_offset + i]
            p_char = decrypt_fn(c_char, k_char)
            plaintext.append(p_char)
        
        return ''.join(plaintext), True
    
    def check_zone_anchors(self, zone_name: str, plaintext: str) -> bool:
        """Check if zone contains correct anchors"""
        zone = self.zones[zone_name]
        
        # Check each anchor that overlaps with this zone
        for anchor_name, anchor_data in self.anchors.items():
            anchor_start = anchor_data['start']
            anchor_end = anchor_data['end']
            
            # Check if anchor overlaps with zone
            if anchor_start >= zone['start'] and anchor_end <= zone['end']:
                # Calculate position within zone
                zone_offset = anchor_start - zone['start']
                anchor_text = anchor_data['text']
                
                # Check if plaintext matches
                for i, expected_char in enumerate(anchor_text):
                    if zone_offset + i >= len(plaintext):
                        return False
                    if plaintext[zone_offset + i] != expected_char:
                        return False
        
        return True
    
    def test_hybrid_configuration(self, config: Dict) -> Dict:
        """Test a hybrid zone configuration"""
        result = {
            'config': config,
            'plaintext': '',
            'head': '',
            'tail': '',
            'anchors_ok': True,
            'english_score': 0.0,
            'bigrams_found': [],
            'words_found': [],
            'status': 'failed'
        }
        
        plaintext_parts = []
        
        # Decrypt each zone
        for zone_name in ['Z0', 'Z1', 'Z2', 'Z3', 'Z4', 'Z5', 'Z6']:
            zone_config = config.get(zone_name, {})
            
            # Get configuration for this zone
            key_source = zone_config.get('source', 'K1K2K3')
            family = zone_config.get('family', 'vigenere')
            offset = zone_config.get('offset', 0)
            reset = zone_config.get('reset', False)
            
            # Decrypt zone
            zone_text, success = self.decrypt_zone(zone_name, key_source, family, offset, reset)
            
            if not success:
                return result
            
            # Check anchors in this zone
            if not self.check_zone_anchors(zone_name, zone_text):
                result['anchors_ok'] = False
                return result
            
            plaintext_parts.append(zone_text)
        
        # Combine plaintext
        result['plaintext'] = ''.join(plaintext_parts)
        result['head'] = result['plaintext'][:21]
        result['tail'] = result['plaintext'][74:]
        
        # Analyze English quality
        head = result['head']
        
        # Check bigrams
        for i in range(len(head) - 1):
            bigram = head[i:i+2]
            if bigram in self.common_bigrams:
                result['bigrams_found'].append(bigram)
        
        # Check words
        for word in self.common_words:
            if word in head:
                result['words_found'].append(word)
        
        # Calculate score
        bigram_score = len(result['bigrams_found']) / 5.0
        word_score = len(result['words_found']) * 2.0
        result['english_score'] = bigram_score + word_score
        
        if result['english_score'] > 1.0:
            result['status'] = 'promising'
        
        return result
    
    def test_strategy_1(self) -> List[Dict]:
        """Strategy 1: Flint for non-anchor zones, K1-K3 for anchors"""
        results = []
        
        print("\n=== Strategy 1: Flint for content, K1-K3 for anchors ===")
        
        # Try different Flint sources for head/middle/tail
        flint_sources = ['Flint_Fieldbook', 'Flint_Def28', 'Flint_Composite']
        k_sources = ['K1', 'K2', 'K3', 'K1K2K3']
        
        for flint_src in flint_sources:
            for k_src in k_sources:
                for family in ['vigenere', 'beaufort', 'varbf']:
                    # Build configuration
                    config = {
                        'Z0': {'source': flint_src, 'family': family, 'offset': 0},    # Head from Flint
                        'Z1': {'source': k_src, 'family': family, 'offset': 21},        # EAST from K
                        'Z2': {'source': k_src, 'family': family, 'offset': 25},        # NORTHEAST from K
                        'Z3': {'source': flint_src, 'family': family, 'offset': 21},   # Middle from Flint
                        'Z4': {'source': k_src, 'family': family, 'offset': 63},        # BERLIN from K
                        'Z5': {'source': k_src, 'family': family, 'offset': 69},        # CLOCK from K
                        'Z6': {'source': flint_src, 'family': family, 'offset': 50}    # Tail from Flint
                    }
                    
                    result = self.test_hybrid_configuration(config)
                    
                    if result['anchors_ok'] and result['english_score'] > 0:
                        print(f"  {flint_src}/{k_src}/{family}: score={result['english_score']:.2f}")
                        if result['english_score'] > 1.0:
                            results.append(result)
        
        return results
    
    def test_strategy_2(self) -> List[Dict]:
        """Strategy 2: Different sources for each zone with resets"""
        results = []
        
        print("\n=== Strategy 2: Zone-specific sources with resets ===")
        
        # Define zone-specific source preferences
        zone_sources = {
            'Z0': ['Flint_Fieldbook', 'K1', 'K2'],  # Head
            'Z1': ['K1K2K3', 'K2', 'K3'],            # EAST
            'Z2': ['K1K2K3', 'K2', 'K3'],            # NORTHEAST
            'Z3': ['Flint_Def28', 'K3', 'K1K2K3'],   # Middle
            'Z4': ['K1K2K3', 'K1', 'K2'],            # BERLIN
            'Z5': ['K1K2K3', 'K1', 'K2'],            # CLOCK
            'Z6': ['Flint_Composite', 'K3', 'K2']    # Tail
        }
        
        # Test a subset of combinations
        test_count = 0
        max_tests = 500
        
        for family in ['vigenere', 'beaufort']:
            for z0_src in zone_sources['Z0'][:2]:
                for z3_src in zone_sources['Z3'][:2]:
                    for z6_src in zone_sources['Z6'][:2]:
                        if test_count >= max_tests:
                            break
                        
                        # Use K1K2K3 for all anchor zones
                        config = {
                            'Z0': {'source': z0_src, 'family': family, 'offset': 0, 'reset': True},
                            'Z1': {'source': 'K1K2K3', 'family': family, 'offset': 0, 'reset': True},
                            'Z2': {'source': 'K1K2K3', 'family': family, 'offset': 4, 'reset': False},
                            'Z3': {'source': z3_src, 'family': family, 'offset': 0, 'reset': True},
                            'Z4': {'source': 'K1K2K3', 'family': family, 'offset': 50, 'reset': True},
                            'Z5': {'source': 'K1K2K3', 'family': family, 'offset': 56, 'reset': False},
                            'Z6': {'source': z6_src, 'family': family, 'offset': 0, 'reset': True}
                        }
                        
                        result = self.test_hybrid_configuration(config)
                        test_count += 1
                        
                        if result['anchors_ok'] and result['english_score'] > 0.5:
                            print(f"  Config {test_count}: score={result['english_score']:.2f}")
                            if result['english_score'] > 1.0:
                                results.append(result)
        
        return results
    
    def run_all_strategies(self) -> List[Dict]:
        """Run all hybrid strategies"""
        all_results = []
        
        print("=== J.3 - Hybrid Running Key Testing ===")
        
        # Strategy 1: Flint for content, K1-K3 for anchors
        results1 = self.test_strategy_1()
        all_results.extend(results1)
        print(f"Strategy 1: {len(results1)} promising configurations")
        
        # Strategy 2: Zone-specific sources with resets
        results2 = self.test_strategy_2()
        all_results.extend(results2)
        print(f"Strategy 2: {len(results2)} promising configurations")
        
        return all_results
    
    def analyze_results(self, results: List[Dict]):
        """Analyze and report results"""
        if not results:
            print("\n=== No Promising Hybrid Configurations ===")
            print("Hybrid approaches preserve anchors but don't produce convincing English")
            return
        
        print("\n=== Promising Hybrid Configurations ===")
        results.sort(key=lambda x: x['english_score'], reverse=True)
        
        for i, r in enumerate(results[:5], 1):  # Top 5
            print(f"\nConfiguration {i} (score={r['english_score']:.2f}):")
            print(f"  Head: {r['head']}")
            print(f"  Tail: {r['tail']}")
            print(f"  Bigrams: {r['bigrams_found']}")
            print(f"  Words: {r['words_found']}")
            
            # Show zone configuration
            print("  Zone config:")
            for zone_name in ['Z0', 'Z3', 'Z6']:  # Key zones
                zone_cfg = r['config'].get(zone_name, {})
                print(f"    {zone_name}: {zone_cfg.get('source', 'N/A')}")
    
    def save_results(self, results: List[Dict]):
        """Save results to JSON"""
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(output_dir, 'j3_results.json')
        
        # Sort by score before saving
        results.sort(key=lambda x: x['english_score'], reverse=True)
        
        # Simplify config for storage
        saved_results = []
        for r in results[:20]:  # Save top 20
            saved_result = {
                'english_score': r['english_score'],
                'head': r['head'],
                'tail': r['tail'],
                'bigrams_found': r['bigrams_found'],
                'words_found': r['words_found'],
                'zone_sources': {
                    'Z0': r['config']['Z0']['source'],
                    'Z3': r['config']['Z3']['source'],
                    'Z6': r['config']['Z6']['source']
                }
            }
            saved_results.append(saved_result)
        
        with open(output_path, 'w') as f:
            json.dump(saved_results, f, indent=2)
        
        print(f"\nResults saved to {output_path}")


def main():
    """Run J.3 hybrid testing"""
    j3 = J3Hybrid()
    
    # Run all strategies
    results = j3.run_all_strategies()
    
    # Analyze
    j3.analyze_results(results)
    
    # Save
    if results:
        j3.save_results(results)
    
    # Summary
    print("\n" + "=" * 60)
    print("J.3 SUMMARY")
    print("=" * 60)
    if results:
        print(f"Found {len(results)} promising hybrid configurations")
        best = max(results, key=lambda x: x['english_score'])
        print(f"Best score: {best['english_score']:.2f}")
        print(f"Head: {best['head']}")
    else:
        print("No hybrid configurations produce convincing English")
        print("Anchors preserved but heads remain non-English")


if __name__ == "__main__":
    main()