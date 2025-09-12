#!/usr/bin/env python3
"""
anchor_null_test.py

Test hypothesis that anchors (EAST, NORTHEAST, BERLIN, CLOCK) are not plaintext
but nulls/padding/markers that should be removed or ignored.
"""

from typing import List, Tuple, Dict

# K4 ciphertext
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def char_to_num(c: str) -> int:
    """Convert A-Z to 0-25."""
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    """Convert 0-25 to A-Z."""
    return chr((n % 26) + ord('A'))

class AnchorNullTester:
    """Test anchors as nulls hypothesis."""
    
    def __init__(self):
        self.ciphertext = K4_CIPHERTEXT
        
        # Define anchor positions
        self.anchor_ranges = [
            (21, 25),   # EAST
            (25, 34),   # NORTHEAST  
            (63, 69),   # BERLIN
            (69, 74)    # CLOCK
        ]
        
        # All anchor positions
        self.anchor_positions = set()
        for start, end in self.anchor_ranges:
            self.anchor_positions.update(range(start, end))
    
    def extract_non_anchor_text(self) -> str:
        """Extract only non-anchor positions."""
        non_anchor = []
        for i, c in enumerate(self.ciphertext):
            if i not in self.anchor_positions:
                non_anchor.append(c)
        
        return ''.join(non_anchor)
    
    def extract_with_anchor_replacement(self, replacement: str = 'X') -> str:
        """Replace anchor positions with a specific character."""
        result = list(self.ciphertext)
        for pos in self.anchor_positions:
            result[pos] = replacement
        return ''.join(result)
    
    def extract_segments(self) -> Dict[str, str]:
        """Extract text segments between/around anchors."""
        segments = {
            'head': self.ciphertext[0:21],          # Before EAST
            'between_east_berlin': self.ciphertext[34:63],  # Between NORTHEAST and BERLIN
            'tail': self.ciphertext[74:],           # After CLOCK
            'non_anchor_full': '',                  # All non-anchor positions
            'reordered': ''                          # Head + middle + tail
        }
        
        segments['non_anchor_full'] = self.extract_non_anchor_text()
        segments['reordered'] = segments['head'] + segments['between_east_berlin'] + segments['tail']
        
        return segments
    
    def vigenere_decrypt(self, text: str, key: str) -> str:
        """Simple Vigenère decryption."""
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
        """Simple Beaufort decryption."""
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
    
    def analyze_segment_properties(self, text: str) -> Dict:
        """Analyze properties of text segment."""
        if not text:
            return {'length': 0}
        
        # Vowel count
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
        
        # Common bigrams
        bigrams = ['TH', 'HE', 'IN', 'ER', 'AN', 'RE', 'ED', 'ON', 'ES', 'ST']
        bigram_count = sum(1 for bg in bigrams if bg in text)
        
        # Common words
        words = ['THE', 'AND', 'ARE', 'YOU', 'WE', 'IN', 'IT', 'IS', 'BE', 'TO']
        word_count = sum(1 for word in words if word in text)
        
        return {
            'length': len(text),
            'vowel_ratio': round(vowel_ratio, 3),
            'max_consonant_run': max_consonant_run,
            'bigram_count': bigram_count,
            'word_count': word_count,
            'text_sample': text[:30] if len(text) > 30 else text
        }
    
    def test_null_hypothesis(self):
        """Test various null hypothesis interpretations."""
        print("\n" + "="*60)
        print("TESTING ANCHORS AS NULLS/MARKERS")
        print("="*60)
        
        # Extract segments
        segments = self.extract_segments()
        
        print(f"\nOriginal ciphertext length: {len(self.ciphertext)}")
        print(f"Anchor positions: {len(self.anchor_positions)}")
        print(f"Non-anchor positions: {len(self.ciphertext) - len(self.anchor_positions)}")
        
        # Test keys
        test_keys = [
            "KRYPTOS",
            "PALIMPSEST", 
            "ABSCISSA",
            "YARD",
            "BERLIN",
            "CLOCK",
            "NORTHEAST"
        ]
        
        results = []
        
        for segment_name, segment_text in segments.items():
            if not segment_text:
                continue
            
            print(f"\n{segment_name.upper()} (length={len(segment_text)}):")
            print(f"  Raw: {segment_text[:40]}...")
            
            best_score = 0
            best_result = None
            
            for key in test_keys:
                # Try Vigenère
                pt_vig = self.vigenere_decrypt(segment_text, key)
                props_vig = self.analyze_segment_properties(pt_vig)
                
                # Try Beaufort
                pt_beau = self.beaufort_decrypt(segment_text, key)
                props_beau = self.analyze_segment_properties(pt_beau)
                
                # Score based on properties
                score_vig = (
                    (1 if 0.3 <= props_vig['vowel_ratio'] <= 0.5 else 0) * 10 +
                    (1 if props_vig['max_consonant_run'] <= 5 else 0) * 10 +
                    props_vig['bigram_count'] * 2 +
                    props_vig['word_count'] * 5
                )
                
                score_beau = (
                    (1 if 0.3 <= props_beau['vowel_ratio'] <= 0.5 else 0) * 10 +
                    (1 if props_beau['max_consonant_run'] <= 5 else 0) * 10 +
                    props_beau['bigram_count'] * 2 +
                    props_beau['word_count'] * 5
                )
                
                if score_vig > best_score:
                    best_score = score_vig
                    best_result = {
                        'method': 'vigenere',
                        'key': key,
                        'plaintext': pt_vig,
                        'properties': props_vig,
                        'score': score_vig
                    }
                
                if score_beau > best_score:
                    best_score = score_beau
                    best_result = {
                        'method': 'beaufort',
                        'key': key,
                        'plaintext': pt_beau,
                        'properties': props_beau,
                        'score': score_beau
                    }
            
            if best_result:
                print(f"  Best: {best_result['method']} with {best_result['key']}")
                print(f"    Score: {best_result['score']}")
                print(f"    Plaintext: {best_result['properties']['text_sample']}...")
                print(f"    Vowel ratio: {best_result['properties']['vowel_ratio']}")
                print(f"    Max consonants: {best_result['properties']['max_consonant_run']}")
                
                results.append({
                    'segment': segment_name,
                    **best_result
                })
        
        return results
    
    def test_anchor_as_key_indicators(self):
        """Test if anchors indicate key changes."""
        print("\n" + "="*60)
        print("TESTING ANCHORS AS KEY INDICATORS")
        print("="*60)
        
        # Hypothesis: Different keys for different sections
        # Section 1: 0-21 (before EAST)
        # Section 2: 34-63 (between NORTHEAST and BERLIN)
        # Section 3: 74-97 (after CLOCK)
        
        sections = [
            (0, 21, "HEAD"),
            (34, 63, "MIDDLE"),
            (74, 97, "TAIL")
        ]
        
        # Keys might be related to the anchors
        key_mappings = [
            ("EAST", "HEAD"),
            ("NORTHEAST", "HEAD"),
            ("BERLIN", "MIDDLE"),
            ("CLOCK", "TAIL"),
            ("KRYPTOS", "ALL")
        ]
        
        for anchor_key, section_name in key_mappings:
            print(f"\nTrying key '{anchor_key}' for section '{section_name}':")
            
            for start, end, sec_name in sections:
                if section_name != "ALL" and section_name != sec_name:
                    continue
                
                section_text = self.ciphertext[start:end]
                
                # Decrypt with this key
                pt_vig = self.vigenere_decrypt(section_text, anchor_key)
                pt_beau = self.beaufort_decrypt(section_text, anchor_key)
                
                # Check for readable text
                props_vig = self.analyze_segment_properties(pt_vig)
                props_beau = self.analyze_segment_properties(pt_beau)
                
                if props_vig['word_count'] > 0 or props_vig['max_consonant_run'] <= 4:
                    print(f"  Vigenère {sec_name}: {pt_vig[:30]}...")
                    print(f"    Words found: {props_vig['word_count']}")
                
                if props_beau['word_count'] > 0 or props_beau['max_consonant_run'] <= 4:
                    print(f"  Beaufort {sec_name}: {pt_beau[:30]}...")
                    print(f"    Words found: {props_beau['word_count']}")

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("ANCHOR NULL HYPOTHESIS TESTING")
    print("Testing if anchors are nulls/markers rather than plaintext")
    print("="*70)
    
    tester = AnchorNullTester()
    
    # Test null hypothesis
    null_results = tester.test_null_hypothesis()
    
    # Test key indicator hypothesis
    tester.test_anchor_as_key_indicators()
    
    # Find best overall result
    if null_results:
        best = max(null_results, key=lambda x: x['score'])
        print("\n" + "="*60)
        print("BEST RESULT")
        print("="*60)
        print(f"Segment: {best['segment']}")
        print(f"Method: {best['method']} with key {best['key']}")
        print(f"Score: {best['score']}")
        print(f"Plaintext sample: {best['properties']['text_sample']}...")
        
        if best['score'] > 30:
            print("\n🎯 PROMISING RESULT FOUND - INVESTIGATE FURTHER!")
    
    print("\n" + "="*70)
    print("TESTING COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()