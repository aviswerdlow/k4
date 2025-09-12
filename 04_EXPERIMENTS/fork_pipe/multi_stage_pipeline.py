#!/usr/bin/env python3
"""
multi_stage_pipeline.py

Fork PIPE - Multi-stage encryption pipeline per zone.
Testing 3+ stage operations based on zone independence.
"""

from typing import List, Tuple, Dict, Optional, Callable
import itertools

# K4 ciphertext
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Zone definitions
ZONES = {
    'HEAD': (0, 21),
    'MIDDLE': (34, 63),
    'TAIL': (74, 97)
}

def char_to_num(c: str) -> int:
    """Convert A-Z to 0-25."""
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    """Convert 0-25 to A-Z."""
    return chr((n % 26) + ord('A'))

class MultiStagePipeline:
    """Multi-stage encryption pipeline."""
    
    def __init__(self):
        self.ciphertext = K4_CIPHERTEXT
        
        # Available operations
        self.operations = {
            'vigenere': self.vigenere_decrypt,
            'beaufort': self.beaufort_decrypt,
            'caesar': self.caesar_decrypt,
            'atbash': self.atbash_decrypt,
            'transpose': self.transpose_decrypt,
            'reverse': self.reverse_decrypt,
            'rail_fence': self.rail_fence_decrypt,
            'autokey': self.autokey_decrypt
        }
        
        # Best known keys per zone
        self.zone_keys = {
            'HEAD': ['ORDINATE', 'WOOD', 'DEFINITION', 'LANGLEY'],
            'MIDDLE': ['ABSCISSA', 'CIA', 'HEAT'],  # ABSCISSA confirmed
            'TAIL': ['LATITUDE', 'ILLUSION', 'VIRGINIA', 'CLOCK']
        }
    
    def vigenere_decrypt(self, text: str, key: str) -> str:
        """Vigenère decryption."""
        if not key:
            return text
        plaintext = []
        key_len = len(key)
        
        for i, c in enumerate(text):
            if not c.isalpha():
                plaintext.append(c)
                continue
            
            c_val = char_to_num(c)
            k_val = char_to_num(key[i % key_len])
            p_val = (c_val - k_val) % 26
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)
    
    def beaufort_decrypt(self, text: str, key: str) -> str:
        """Beaufort decryption."""
        if not key:
            return text
        plaintext = []
        key_len = len(key)
        
        for i, c in enumerate(text):
            if not c.isalpha():
                plaintext.append(c)
                continue
            
            c_val = char_to_num(c)
            k_val = char_to_num(key[i % key_len])
            p_val = (k_val - c_val) % 26
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)
    
    def caesar_decrypt(self, text: str, key: str) -> str:
        """Caesar cipher decryption."""
        # Key should be a number or single letter
        if key.isdigit():
            shift = int(key) % 26
        elif len(key) == 1:
            shift = char_to_num(key)
        else:
            shift = 3  # Default
        
        plaintext = []
        for c in text:
            if not c.isalpha():
                plaintext.append(c)
                continue
            
            c_val = char_to_num(c)
            p_val = (c_val - shift) % 26
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)
    
    def atbash_decrypt(self, text: str, key: str = None) -> str:
        """Atbash cipher (reverse alphabet)."""
        plaintext = []
        for c in text:
            if not c.isalpha():
                plaintext.append(c)
                continue
            
            c_val = char_to_num(c)
            p_val = 25 - c_val
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)
    
    def transpose_decrypt(self, text: str, key: str) -> str:
        """Columnar transposition decryption."""
        # Key determines column order
        if not key or not key.isdigit():
            cols = 7  # Default
        else:
            cols = int(key)
        
        if cols <= 0 or cols > len(text):
            return text
        
        rows = (len(text) + cols - 1) // cols
        grid = [[''] * cols for _ in range(rows)]
        
        # Fill by columns
        idx = 0
        for col in range(cols):
            for row in range(rows):
                if idx < len(text):
                    grid[row][col] = text[idx]
                    idx += 1
        
        # Read by rows
        plaintext = []
        for row in grid:
            plaintext.extend(row)
        
        return ''.join(plaintext)
    
    def reverse_decrypt(self, text: str, key: str = None) -> str:
        """Simple reversal."""
        return text[::-1]
    
    def rail_fence_decrypt(self, text: str, key: str) -> str:
        """Rail fence cipher decryption."""
        if not key or not key.isdigit():
            rails = 3  # Default
        else:
            rails = int(key)
        
        if rails <= 1:
            return text
        
        # Create fence pattern
        fence = [['' for _ in range(len(text))] for _ in range(rails)]
        rail = 0
        direction = 1
        
        # Mark positions
        for col in range(len(text)):
            fence[rail][col] = '*'
            rail += direction
            if rail == rails - 1 or rail == 0:
                direction = -direction
        
        # Fill fence
        idx = 0
        for row in range(rails):
            for col in range(len(text)):
                if fence[row][col] == '*' and idx < len(text):
                    fence[row][col] = text[idx]
                    idx += 1
        
        # Read plaintext
        plaintext = []
        rail = 0
        direction = 1
        for col in range(len(text)):
            plaintext.append(fence[rail][col])
            rail += direction
            if rail == rails - 1 or rail == 0:
                direction = -direction
        
        return ''.join(plaintext)
    
    def autokey_decrypt(self, text: str, key: str) -> str:
        """Autokey cipher decryption."""
        if not key:
            return text
        
        plaintext = []
        extended_key = key
        
        for i, c in enumerate(text):
            if not c.isalpha():
                plaintext.append(c)
                continue
            
            if i < len(extended_key):
                k_val = char_to_num(extended_key[i])
            else:
                k_val = char_to_num(plaintext[i - len(key)])
            
            c_val = char_to_num(c)
            p_val = (c_val - k_val) % 26
            p_char = num_to_char(p_val)
            plaintext.append(p_char)
            
            if i >= len(key):
                extended_key += p_char
        
        return ''.join(plaintext)
    
    def apply_pipeline(self, text: str, stages: List[Tuple[str, str]]) -> str:
        """Apply multi-stage pipeline."""
        result = text
        
        for operation, key in stages:
            if operation in self.operations:
                result = self.operations[operation](result, key)
        
        return result
    
    def score_plaintext(self, text: str) -> Dict:
        """Score plaintext quality."""
        # Common words
        words_found = []
        common_words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'HIS', 'HER', 'THAT',
                       'HAVE', 'FROM', 'THEY', 'WILL', 'WOULD', 'THERE', 'THEIR',
                       'HEAT', 'COLD', 'NORTH', 'SOUTH', 'EAST', 'WEST', 'TIME']
        
        for word in common_words:
            if word in text:
                words_found.append(word)
        
        # Vowel ratio
        vowels = sum(1 for c in text if c in 'AEIOU')
        vowel_ratio = vowels / len(text) if len(text) > 0 else 0
        
        # Consonant runs
        max_consonant_run = 0
        current_run = 0
        for c in text:
            if c not in 'AEIOU':
                current_run += 1
                max_consonant_run = max(max_consonant_run, current_run)
            else:
                current_run = 0
        
        # Score
        score = len(words_found) * 10
        if 0.35 <= vowel_ratio <= 0.45:
            score += 5
        if max_consonant_run <= 4:
            score += 5
        
        return {
            'score': score,
            'words': words_found,
            'vowel_ratio': round(vowel_ratio, 3),
            'max_consonants': max_consonant_run,
            'text': text
        }
    
    def test_zone_pipelines(self):
        """Test different pipelines per zone."""
        print("\n" + "="*60)
        print("TESTING MULTI-STAGE PIPELINES PER ZONE")
        print("="*60)
        
        # Define pipeline configurations to test
        pipelines = {
            'HEAD': [
                [('transpose', '7'), ('vigenere', 'ORDINATE')],
                [('reverse', ''), ('beaufort', 'WOOD')],
                [('rail_fence', '3'), ('vigenere', 'LANGLEY')],
                [('caesar', '3'), ('transpose', '7'), ('vigenere', 'DEFINITION')],
                [('atbash', ''), ('vigenere', 'ORDINATE'), ('caesar', '13')]
            ],
            'MIDDLE': [
                [('vigenere', 'ABSCISSA')],  # Known working
                [('transpose', '7'), ('vigenere', 'ABSCISSA')],
                [('vigenere', 'CIA'), ('caesar', '3')],
                [('beaufort', 'HEAT'), ('reverse', ''), ('vigenere', 'ABSCISSA')]
            ],
            'TAIL': [
                [('transpose', '7'), ('beaufort', 'CLOCK')],
                [('reverse', ''), ('vigenere', 'VIRGINIA')],
                [('rail_fence', '3'), ('beaufort', 'LATITUDE')],
                [('vigenere', 'ILLUSION'), ('atbash', ''), ('caesar', '7')],
                [('autokey', 'CLOCK'), ('transpose', '5')]
            ]
        }
        
        best_results = {}
        
        for zone_name, (start, end) in ZONES.items():
            zone_ct = self.ciphertext[start:end]
            zone_best = None
            zone_best_score = 0
            
            print(f"\n{zone_name} Zone:")
            
            for pipeline in pipelines[zone_name]:
                result = self.apply_pipeline(zone_ct, pipeline)
                score_data = self.score_plaintext(result)
                
                if score_data['score'] > zone_best_score:
                    zone_best_score = score_data['score']
                    zone_best = {
                        'pipeline': pipeline,
                        'score': score_data['score'],
                        'words': score_data['words'],
                        'text': result[:30]
                    }
            
            if zone_best:
                best_results[zone_name] = zone_best
                print(f"  Best pipeline (score={zone_best['score']}):")
                for op, key in zone_best['pipeline']:
                    print(f"    → {op}({key if key else 'none'})")
                print(f"  Words: {zone_best['words']}")
                print(f"  Sample: {zone_best['text']}...")
        
        return best_results
    
    def test_full_message_pipeline(self):
        """Test complete message with zone-specific pipelines."""
        print("\n" + "="*60)
        print("TESTING FULL MESSAGE WITH ZONE PIPELINES")
        print("="*60)
        
        # Best known pipelines
        zone_pipelines = {
            'HEAD': [('transpose', '7'), ('vigenere', 'ORDINATE')],
            'MIDDLE': [('vigenere', 'ABSCISSA')],  # Confirmed
            'TAIL': [('transpose', '7'), ('beaufort', 'CLOCK')]
        }
        
        # Apply to each zone
        full_plaintext = list(self.ciphertext)
        
        for zone_name, (start, end) in ZONES.items():
            zone_ct = self.ciphertext[start:end]
            zone_pt = self.apply_pipeline(zone_ct, zone_pipelines[zone_name])
            
            # Replace in full plaintext
            for i, c in enumerate(zone_pt):
                full_plaintext[start + i] = c
        
        full_pt = ''.join(full_plaintext)
        
        print("\nZone-specific pipelines applied:")
        for zone, pipeline in zone_pipelines.items():
            print(f"{zone}: {' → '.join(f'{op}({key})' for op, key in pipeline)}")
        
        print(f"\nResulting plaintext:")
        print(f"HEAD: {full_pt[0:21]}")
        print(f"Anchors: {full_pt[21:34]}")
        print(f"MIDDLE: {full_pt[34:63]}")
        print(f"Anchors: {full_pt[63:74]}")
        print(f"TAIL: {full_pt[74:97]}")
        
        # Score full message
        score_data = self.score_plaintext(full_pt)
        print(f"\nFull message score: {score_data['score']}")
        print(f"Words found: {score_data['words']}")
        
        return full_pt
    
    def test_complex_pipelines(self):
        """Test 3+ stage complex pipelines."""
        print("\n" + "="*60)
        print("TESTING COMPLEX 3+ STAGE PIPELINES")
        print("="*60)
        
        # Focus on middle segment with ABSCISSA
        middle_ct = self.ciphertext[34:63]
        
        complex_pipelines = [
            # Pre-process, main cipher, post-process
            [('transpose', '7'), ('vigenere', 'ABSCISSA'), ('reverse', '')],
            [('rail_fence', '3'), ('vigenere', 'ABSCISSA'), ('caesar', '13')],
            [('atbash', ''), ('vigenere', 'ABSCISSA'), ('transpose', '5')],
            
            # Multiple substitutions
            [('caesar', '3'), ('vigenere', 'ABSCISSA'), ('beaufort', 'HEAT')],
            [('vigenere', 'CIA'), ('vigenere', 'ABSCISSA'), ('caesar', '7')],
            
            # Complex transposition chains
            [('transpose', '7'), ('rail_fence', '3'), ('vigenere', 'ABSCISSA')],
            [('reverse', ''), ('transpose', '5'), ('vigenere', 'ABSCISSA'), ('reverse', '')]
        ]
        
        results = []
        
        for pipeline in complex_pipelines:
            result = self.apply_pipeline(middle_ct, pipeline)
            score_data = self.score_plaintext(result)
            
            if score_data['score'] > 0 or score_data['words']:
                results.append({
                    'pipeline': pipeline,
                    'score': score_data['score'],
                    'words': score_data['words'],
                    'text': result[:25]
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        
        print("\nTop complex pipeline results:")
        for i, res in enumerate(results[:3]):
            print(f"\n{i+1}. Pipeline (score={res['score']}):")
            for op, key in res['pipeline']:
                print(f"   → {op}({key if key else 'none'})")
            print(f"   Words: {res['words']}")
            print(f"   Text: {res['text']}...")
        
        return results

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("FORK PIPE - MULTI-STAGE PIPELINE TESTING")
    print("Testing 3+ stage operations per zone")
    print("="*70)
    
    pipeline = MultiStagePipeline()
    
    # Test 1: Zone-specific pipelines
    zone_results = pipeline.test_zone_pipelines()
    
    # Test 2: Full message with zone pipelines
    full_result = pipeline.test_full_message_pipeline()
    
    # Test 3: Complex 3+ stage pipelines
    complex_results = pipeline.test_complex_pipelines()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    print("\nBest pipelines by zone:")
    for zone in ['HEAD', 'MIDDLE', 'TAIL']:
        if zone in zone_results:
            res = zone_results[zone]
            print(f"{zone}: Score={res['score']}")
            pipeline_str = ' → '.join(f"{op}({key})" for op, key in res['pipeline'])
            print(f"  Pipeline: {pipeline_str}")
            if res['words']:
                print(f"  Words: {res['words']}")
    
    if any(r['score'] > 30 for r in zone_results.values()):
        print("\n🎯 PROMISING PIPELINE CONFIGURATION FOUND!")
    
    print("\n" + "="*70)
    print("FORK PIPE COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()