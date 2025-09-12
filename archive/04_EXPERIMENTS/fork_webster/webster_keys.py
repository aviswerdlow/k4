#!/usr/bin/env python3
"""
webster_keys.py

Fork WEBSTER - Testing Webster's dictionary reference keys.
Sanborn mentioned Webster's - exploring dictionary-based keys.
"""

from typing import List, Tuple, Dict, Optional

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

class WebsterCipher:
    """Cipher using Webster's dictionary references."""
    
    def __init__(self):
        self.ciphertext = K4_CIPHERTEXT
        
        # Generate dictionary-based keys
        self.dict_keys = self.generate_dictionary_keys()
    
    def generate_dictionary_keys(self) -> Dict[str, str]:
        """Generate keys from Webster's dictionary concepts."""
        keys = {}
        
        # Words related to ABSCISSA (our confirmed key)
        keys['ABSCISSA'] = 'ABSCISSA'
        keys['ORDINATE'] = 'ORDINATE'
        keys['AXIS'] = 'AXIS'
        keys['COORDINATE'] = 'COORDINATE'
        keys['CARTESIAN'] = 'CARTESIAN'
        keys['GRAPH'] = 'GRAPH'
        keys['PLOT'] = 'PLOT'
        
        # Dictionary terms
        keys['DEFINITION'] = 'DEFINITION'
        keys['ETYMOLOGY'] = 'ETYMOLOGY'
        keys['SYNONYM'] = 'SYNONYM'
        keys['ANTONYM'] = 'ANTONYM'
        keys['WEBSTER'] = 'WEBSTER'
        keys['DICTIONARY'] = 'DICTIONARY'
        keys['LEXICON'] = 'LEXICON'
        
        # Words related to HEAT (found in middle segment)
        keys['HEAT'] = 'HEAT'
        keys['TEMPERATURE'] = 'TEMPERATURE'
        keys['THERMAL'] = 'THERMAL'
        keys['CALORIC'] = 'CALORIC'
        keys['WARMTH'] = 'WARMTH'
        keys['FIRE'] = 'FIRE'
        keys['ENERGY'] = 'ENERGY'
        
        # Cryptographic terms from dictionary
        keys['CIPHER'] = 'CIPHER'
        keys['CODE'] = 'CODE'
        keys['CRYPTOGRAM'] = 'CRYPTOGRAM'
        keys['ENCODE'] = 'ENCODE'
        keys['DECODE'] = 'DECODE'
        keys['ENCRYPT'] = 'ENCRYPT'
        keys['DECRYPT'] = 'DECRYPT'
        
        # Page numbers as keys (common dictionary references)
        keys['PAGE_ONE'] = 'ONE'
        keys['PAGE_TWO'] = 'TWO'
        keys['PAGE_THREE'] = 'THREE'
        keys['PAGE_HUNDRED'] = 'HUNDRED'
        keys['PAGE_THOUSAND'] = 'THOUSAND'
        
        # Common dictionary abbreviations
        keys['ABBR_N'] = 'NOUN'
        keys['ABBR_V'] = 'VERB'
        keys['ABBR_ADJ'] = 'ADJECTIVE'
        keys['ABBR_ADV'] = 'ADVERB'
        keys['ABBR_PREP'] = 'PREPOSITION'
        
        # Words from K1-K3 that might be in dictionary
        keys['PALIMPSEST'] = 'PALIMPSEST'
        keys['SHADOW'] = 'SHADOW'
        keys['FORCES'] = 'FORCES'
        keys['IQLUSION'] = 'IQLUSION'  # Deliberate misspelling from K1
        keys['ILLUSION'] = 'ILLUSION'  # Correct spelling
        keys['UNDERGROUND'] = 'UNDERGROUND'
        
        # Mathematical dictionary terms
        keys['ALGEBRA'] = 'ALGEBRA'
        keys['GEOMETRY'] = 'GEOMETRY'
        keys['CALCULUS'] = 'CALCULUS'
        keys['TRIGONOMETRY'] = 'TRIGONOMETRY'
        keys['ALGORITHM'] = 'ALGORITHM'
        
        # Geographic terms (relevant to coordinates)
        keys['LATITUDE'] = 'LATITUDE'
        keys['LONGITUDE'] = 'LONGITUDE'
        keys['MERIDIAN'] = 'MERIDIAN'
        keys['EQUATOR'] = 'EQUATOR'
        keys['GEOGRAPHY'] = 'GEOGRAPHY'
        
        return keys
    
    def page_number_to_key(self, page: int) -> str:
        """Convert page number to alphabetic key."""
        # Method 1: Direct number to letters
        key = ''
        while page > 0:
            key = chr(ord('A') + (page % 26)) + key
            page //= 26
        return key if key else 'A'
    
    def word_position_key(self, word: str, position: int) -> str:
        """Create key from word's position in dictionary."""
        # Simulate: word at position creates offset
        base = word[:3] if len(word) >= 3 else word
        offset = str(position % 100)
        return base + offset
    
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
    
    def dictionary_cipher(self, text: str, key: str) -> str:
        """Dictionary-based substitution cipher."""
        # Create substitution based on dictionary order
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        key_letters = ''.join(dict.fromkeys(key.upper()))  # Remove duplicates
        
        # Build substitution alphabet
        sub_alphabet = key_letters
        for c in alphabet:
            if c not in sub_alphabet:
                sub_alphabet += c
        
        # Decrypt
        plaintext = []
        for c in text:
            if c.isalpha():
                idx = alphabet.index(c.upper())
                plaintext.append(sub_alphabet[idx])
            else:
                plaintext.append(c)
        
        return ''.join(plaintext)
    
    def score_plaintext(self, text: str) -> Dict:
        """Score plaintext quality."""
        # Common words
        words_found = []
        common_words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'HIS', 'HER', 'THAT',
                       'HAVE', 'FROM', 'THEY', 'WILL', 'WOULD', 'THERE', 'THEIR',
                       'HEAT', 'COLD', 'NORTH', 'SOUTH', 'EAST', 'WEST', 'TIME',
                       'WEBSTER', 'DICTIONARY', 'PAGE', 'WORD', 'DEFINITION']
        
        for word in common_words:
            if word in text:
                words_found.append(word)
        
        # Vowel ratio
        vowels = sum(1 for c in text if c in 'AEIOU')
        vowel_ratio = vowels / len(text) if len(text) > 0 else 0
        
        # Score
        score = len(words_found) * 10
        if 0.35 <= vowel_ratio <= 0.45:
            score += 5
        
        # Bonus for dictionary-related words
        dict_words = ['WEBSTER', 'DICTIONARY', 'PAGE', 'DEFINITION', 'WORD']
        if any(w in words_found for w in dict_words):
            score += 10
        
        return {
            'score': score,
            'words': words_found,
            'vowel_ratio': round(vowel_ratio, 3),
            'text': text
        }
    
    def test_webster_keys(self):
        """Test Webster's dictionary-based keys."""
        print("\n" + "="*60)
        print("TESTING WEBSTER'S DICTIONARY KEYS")
        print("="*60)
        
        best_results = {'HEAD': None, 'MIDDLE': None, 'TAIL': None}
        
        for zone_name, (start, end) in ZONES.items():
            zone_ct = self.ciphertext[start:end]
            zone_best_score = 0
            
            print(f"\n{zone_name} Zone:")
            
            for key_name, key in self.dict_keys.items():
                if not key:
                    continue
                
                # Test three cipher types
                for method in ['vigenere', 'beaufort', 'dictionary']:
                    if method == 'vigenere':
                        pt = self.vigenere_decrypt(zone_ct, key)
                    elif method == 'beaufort':
                        pt = self.beaufort_decrypt(zone_ct, key)
                    else:
                        pt = self.dictionary_cipher(zone_ct, key)
                    
                    score_data = self.score_plaintext(pt)
                    
                    if score_data['score'] > zone_best_score:
                        zone_best_score = score_data['score']
                        best_results[zone_name] = {
                            'key': key_name,
                            'method': method,
                            'score': score_data['score'],
                            'words': score_data['words'],
                            'text': pt[:30]
                        }
            
            if best_results[zone_name]:
                res = best_results[zone_name]
                print(f"  Best: {res['method']} with {res['key']}")
                print(f"    Score: {res['score']}")
                print(f"    Words: {res['words']}")
                print(f"    Sample: {res['text']}...")
        
        return best_results
    
    def test_page_references(self):
        """Test page number references as keys."""
        print("\n" + "="*60)
        print("TESTING PAGE NUMBER REFERENCES")
        print("="*60)
        
        # Test specific page numbers that might be significant
        test_pages = [
            1,      # First page
            97,     # Length of K4
            314,    # Pi reference
            1337,   # Elite/leet
            1990,   # Year of dedication
            389,    # From coordinates (38.9)
            771,    # From coordinates (77.1)
        ]
        
        results = []
        
        for page in test_pages:
            key = self.page_number_to_key(page)
            
            # Test on middle segment (where ABSCISSA works)
            middle_ct = self.ciphertext[34:63]
            pt = self.vigenere_decrypt(middle_ct, key)
            
            score_data = self.score_plaintext(pt)
            
            if score_data['score'] > 0 or score_data['words']:
                results.append({
                    'page': page,
                    'key': key,
                    'score': score_data['score'],
                    'words': score_data['words'],
                    'text': pt[:20]
                })
        
        if results:
            results.sort(key=lambda x: x['score'], reverse=True)
            print("\nBest page number results:")
            for res in results[:3]:
                print(f"  Page {res['page']} (key={res['key']}): Score={res['score']}")
                print(f"    Words: {res['words']}")
                print(f"    Text: {res['text']}...")
        
        return results
    
    def test_definition_lookup(self):
        """Test using word definitions as keys."""
        print("\n" + "="*60)
        print("TESTING DEFINITION-BASED KEYS")
        print("="*60)
        
        # Simulate dictionary definitions
        definitions = {
            'ABSCISSA': 'HORIZONTAL',  # X-axis is horizontal
            'ORDINATE': 'VERTICAL',     # Y-axis is vertical
            'HEAT': 'ENERGY',           # Heat is a form of energy
            'CIPHER': 'SECRET',         # Cipher means secret writing
            'KRYPTOS': 'HIDDEN',        # Greek for hidden
            'PALIMPSEST': 'REUSED',     # Manuscript page reused
        }
        
        results = []
        
        for word, definition in definitions.items():
            # Test each zone
            for zone_name, (start, end) in ZONES.items():
                zone_ct = self.ciphertext[start:end]
                pt = self.vigenere_decrypt(zone_ct, definition)
                
                score_data = self.score_plaintext(pt)
                
                if score_data['score'] > 10:
                    results.append({
                        'word': word,
                        'definition': definition,
                        'zone': zone_name,
                        'score': score_data['score'],
                        'words': score_data['words'],
                        'text': pt[:25]
                    })
        
        if results:
            results.sort(key=lambda x: x['score'], reverse=True)
            print("\nBest definition-based results:")
            for res in results[:5]:
                print(f"\n{res['word']} → {res['definition']} on {res['zone']}:")
                print(f"  Score: {res['score']}")
                print(f"  Words: {res['words']}")
                print(f"  Text: {res['text']}...")
        
        return results

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("FORK WEBSTER - DICTIONARY REFERENCE KEY TESTING")
    print("Exploring Webster's dictionary connections")
    print("="*70)
    
    cipher = WebsterCipher()
    
    # Test 1: Dictionary word keys
    webster_results = cipher.test_webster_keys()
    
    # Test 2: Page number references
    page_results = cipher.test_page_references()
    
    # Test 3: Definition-based keys
    def_results = cipher.test_definition_lookup()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    print("\nBest keys by zone:")
    for zone in ['HEAD', 'MIDDLE', 'TAIL']:
        if webster_results[zone]:
            res = webster_results[zone]
            print(f"{zone}: {res['key']} ({res['method']}) - Score: {res['score']}")
            if res['words']:
                print(f"  Words: {res['words']}")
    
    if any(r['score'] > 30 for r in [webster_results.get(z, {}) for z in ZONES]):
        print("\n🎯 PROMISING WEBSTER KEY FOUND!")
    
    print("\n" + "="*70)
    print("FORK WEBSTER COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()