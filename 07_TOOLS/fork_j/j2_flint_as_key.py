#!/usr/bin/env python3
"""
Fork J.2 - Flint as Running Key to Decrypt K4
Tests if Flint sources can decrypt K4 to produce valid English with anchors preserved
"""

import json
import os
from typing import Dict, List, Tuple, Optional
from flint_sources import FlintSources

class J2FlintAsKey:
    def __init__(self, master_seed: int = 1337):
        self.master_seed = master_seed
        self.flint = FlintSources()
        
        # K4 ciphertext
        self.k4_ct = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
        
        # Known anchors
        self.anchors = {
            'EAST': {'start': 21, 'end': 24, 'text': 'EAST'},
            'NORTHEAST': {'start': 25, 'end': 33, 'text': 'NORTHEAST'},
            'BERLIN': {'start': 63, 'end': 68, 'text': 'BERLIN'},
            'CLOCK': {'start': 69, 'end': 73, 'text': 'CLOCK'}
        }
        
        # Cipher families (decryption direction)
        self.families = {
            'vigenere': lambda c, k: chr((ord(c) - ord(k)) % 26 + ord('A')),
            'beaufort': lambda c, k: chr((ord(k) - ord(c)) % 26 + ord('A')),
            'varbf': lambda c, k: chr((ord(c) + ord(k) - 2*ord('A')) % 26 + ord('A'))
        }
        
        # English validation
        self.common_bigrams = {'TH', 'HE', 'IN', 'ER', 'AN', 'ED', 'ND', 'TO', 'EN', 'ES',
                               'ST', 'AR', 'OU', 'IT', 'TE', 'NG', 'ON', 'AT', 'AL', 'LE'}
        self.common_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL',
                            'WITH', 'FROM', 'HAVE', 'THIS', 'THAT', 'BEEN'}
        
        # Results storage
        self.results = []
    
    def check_anchors(self, plaintext: str, key_source: str, family: str, offset: int) -> bool:
        """Verify if key source produces correct anchors"""
        # Get key material
        key_stream = self.flint.key_sources.get(key_source, '')
        if not key_stream:
            return False
        
        # Check if we have enough key material
        if offset + 97 > len(key_stream):
            return False
        
        # Get decryption function
        decrypt_fn = self.families[family]
        
        # Check each anchor
        for anchor_name, anchor_data in self.anchors.items():
            start = anchor_data['start']
            expected = anchor_data['text']
            
            for i, expected_char in enumerate(expected):
                pos = start + i
                c_char = self.k4_ct[pos]
                k_char = key_stream[offset + pos]
                
                # Decrypt
                p_char = decrypt_fn(c_char, k_char)
                
                if p_char != expected_char:
                    return False
        
        return True
    
    def decrypt_with_key(self, key_source: str, family: str, offset: int) -> Tuple[str, Dict]:
        """Decrypt K4 using Flint key source"""
        result = {
            'key_source': key_source,
            'family': family,
            'offset': offset,
            'plaintext': '',
            'head': '',
            'anchors_ok': False,
            'english_score': 0.0,
            'bigrams_found': [],
            'words_found': [],
            'consonant_runs': 0
        }
        
        # Get key material
        key_stream = self.flint.key_sources.get(key_source, '')
        if not key_stream or offset + 97 > len(key_stream):
            return '', result
        
        # First check if anchors work
        if not self.check_anchors('', key_source, family, offset):
            return '', result
        
        result['anchors_ok'] = True
        
        # Decrypt full text
        decrypt_fn = self.families[family]
        plaintext = []
        
        for i in range(97):
            c_char = self.k4_ct[i]
            k_char = key_stream[offset + i]
            p_char = decrypt_fn(c_char, k_char)
            plaintext.append(p_char)
        
        plaintext_str = ''.join(plaintext)
        result['plaintext'] = plaintext_str
        result['head'] = plaintext_str[:21]
        
        # Analyze head for English characteristics
        head = result['head']
        
        # Check bigrams
        for i in range(len(head) - 1):
            bigram = head[i:i+2]
            if bigram in self.common_bigrams:
                result['bigrams_found'].append(bigram)
        
        # Check for words
        for word in self.common_words:
            if word in head:
                result['words_found'].append(word)
        
        # Check consonant runs
        vowels = 'AEIOU'
        max_consonant_run = 0
        current_run = 0
        for char in head:
            if char not in vowels:
                current_run += 1
                max_consonant_run = max(max_consonant_run, current_run)
            else:
                current_run = 0
        result['consonant_runs'] = max_consonant_run
        
        # Calculate English score
        bigram_score = len(result['bigrams_found']) / 10.0  # Normalize to ~1.0
        word_score = len(result['words_found']) * 2.0  # Words count more
        consonant_penalty = max(0, 1.0 - (max_consonant_run - 3) / 4.0) if max_consonant_run > 3 else 1.0
        
        result['english_score'] = (bigram_score + word_score) * consonant_penalty
        
        return plaintext_str, result
    
    def sweep_configurations(self, max_tests: int = 2000) -> List[Dict]:
        """Sweep through key source/family/offset combinations"""
        test_count = 0
        results = []
        
        print("=== J.2 - Flint as Running Key Testing ===\n")
        
        # Test each key source
        for source_name in self.flint.key_sources.keys():
            source_len = len(self.flint.key_sources[source_name])
            if source_len < 97:
                continue
            
            print(f"\nTesting key source: {source_name} (length={source_len})")
            
            # Calculate max offset
            max_offset = source_len - 97
            
            # Determine sweep strategy based on source length
            if source_len < 200:
                # Dense sweep for short sources
                offsets = list(range(min(max_offset + 1, 100)))
            else:
                # Sparse sweep for long sources
                offsets = list(range(0, min(max_offset + 1, 500), 7))
                # Add some specific offsets
                offsets.extend([7, 13, 17, 29, 97])
                offsets = sorted(set(o for o in offsets if o <= max_offset))
            
            for family in ['vigenere', 'beaufort', 'varbf']:
                promising_results = []
                
                for offset in offsets:
                    if test_count >= max_tests:
                        break
                    
                    plaintext, result = self.decrypt_with_key(source_name, family, offset)
                    test_count += 1
                    
                    if result['anchors_ok']:
                        # Anchors preserved - check English quality
                        if result['english_score'] > 0.5:
                            promising_results.append(result)
                            print(f"  {family}+{offset}: anchors OK, score={result['english_score']:.2f}")
                            print(f"    Head: {result['head']}")
                            
                            if result['words_found']:
                                print(f"    Words: {result['words_found']}")
                            
                            if result['english_score'] > 2.0:
                                print(f"    *** HIGH SCORE ***")
                                results.append(result)
                
                # Fine sweep around best results
                if promising_results:
                    promising_results.sort(key=lambda x: x['english_score'], reverse=True)
                    
                    for best in promising_results[:3]:
                        base_offset = best['offset']
                        
                        # Search ±3 around best
                        for delta in [-3, -2, -1, 1, 2, 3]:
                            fine_offset = base_offset + delta
                            if fine_offset < 0 or fine_offset > max_offset:
                                continue
                            if test_count >= max_tests:
                                break
                            
                            plaintext, result = self.decrypt_with_key(source_name, family, fine_offset)
                            test_count += 1
                            
                            if result['anchors_ok'] and result['english_score'] > best['english_score']:
                                print(f"    Refined: offset {fine_offset}, score={result['english_score']:.2f}")
                                results.append(result)
        
        print(f"\n\nTotal tests: {test_count}")
        print(f"High-scoring configurations: {len(results)}")
        
        return results
    
    def analyze_results(self, results: List[Dict]):
        """Analyze and report results"""
        if not results:
            print("\n=== No High-Scoring Configurations ===")
            print("Flint key sources preserve anchors but don't produce convincing English")
            return
        
        print("\n=== High-Scoring Configurations ===")
        results.sort(key=lambda x: x['english_score'], reverse=True)
        
        for r in results[:10]:  # Top 10
            print(f"\n{r['key_source']} + {r['family']} @ offset {r['offset']}")
            print(f"  English score: {r['english_score']:.2f}")
            print(f"  Head: {r['head']}")
            print(f"  Bigrams: {r['bigrams_found']}")
            print(f"  Words: {r['words_found']}")
            print(f"  Max consonant run: {r['consonant_runs']}")
            
            # Show a bit more plaintext for context
            if r['plaintext']:
                print(f"  First 50: {r['plaintext'][:50]}")
    
    def save_results(self, results: List[Dict]):
        """Save results to JSON"""
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(output_dir, 'j2_results.json')
        
        # Sort by score before saving
        results.sort(key=lambda x: x['english_score'], reverse=True)
        
        with open(output_path, 'w') as f:
            json.dump(results[:50], f, indent=2)  # Save top 50
        
        print(f"\nResults saved to {output_path}")


def main():
    """Run J.2 testing"""
    j2 = J2FlintAsKey()
    
    # Run sweep
    results = j2.sweep_configurations(max_tests=2000)
    
    # Analyze
    j2.analyze_results(results)
    
    # Save
    if results:
        j2.save_results(results)
    
    # Summary
    print("\n" + "=" * 60)
    print("J.2 SUMMARY")
    print("=" * 60)
    if results:
        print(f"Found {len(results)} configurations with English score > 2.0")
        best = max(results, key=lambda x: x['english_score'])
        print(f"Best: {best['key_source']} + {best['family']} @ {best['offset']}")
        print(f"Score: {best['english_score']:.2f}")
        print(f"Head: {best['head']}")
    else:
        print("No configurations produce convincing English from Flint keys")
        print("Anchors can be preserved but head remains non-English")


if __name__ == "__main__":
    main()