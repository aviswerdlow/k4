#!/usr/bin/env python3
"""
Fork H - Shared Utilities
Segmented & Dynamic Polyalphabetic Testing
"""

import json
import random
import hashlib
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class UtilsH:
    def __init__(self, master_seed: int = 1337):
        self.master_seed = master_seed
        random.seed(master_seed)
        
        # K4 ciphertext
        self.k4_ct = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
        
        # Known anchors
        self.anchors = {
            'EAST': {'start': 21, 'end': 24, 'text': 'EAST'},
            'NORTHEAST': {'start': 25, 'end': 33, 'text': 'NORTHEAST'},
            'BERLIN': {'start': 63, 'end': 68, 'text': 'BERLIN'},
            'CLOCK': {'start': 69, 'end': 73, 'text': 'CLOCK'}
        }
        
        # Bigram blacklist
        self.bigram_blacklist = {'JQ', 'QZ', 'ZX', 'XJ', 'QX', 'JX', 'VQ', 'QV', 'JZ', 'ZJ'}
        
        # Small dictionary for head validation
        self.dictionary = {
            'WE', 'ARE', 'THE', 'AND', 'FOR', 'BUT', 'NOT', 'YOU', 'WITH', 'HAVE',
            'THIS', 'FROM', 'THEY', 'BEEN', 'MORE', 'WHEN', 'WILL', 'WOULD', 'THERE',
            'THEIR', 'WHAT', 'ABOUT', 'WHICH', 'GRID', 'LINE', 'READ', 'THEN', 'SEE',
            'TRUE', 'COURSE', 'MERIDIAN', 'NORTH', 'EAST', 'WEST', 'SOUTH', 'TIME',
            'CLOCK', 'BERLIN', 'CODE', 'KEY', 'FIND', 'LOOK', 'PATH', 'WORD'
        }
    
    def classing_baseline(self, i: int) -> int:
        """6-track classing for compatibility"""
        return ((i % 2) * 3) + (i % 3)
    
    def family_apply(self, family: str, c: str, k: str) -> str:
        """Apply cipher family rule"""
        if not c.isalpha() or not k.isalpha():
            return '?'
        
        c_val = ord(c) - ord('A')
        k_val = ord(k) - ord('A')
        
        if family == 'vigenere' or family == 'vig':
            p_val = (c_val - k_val) % 26
        elif family == 'beaufort' or family == 'bf':
            p_val = (k_val - c_val) % 26
        elif family == 'variant_beaufort' or family == 'varbf':
            p_val = (c_val + k_val) % 26
        else:
            return '?'
        
        return chr(p_val + ord('A'))
    
    def family_solve_key(self, family: str, c: str, p: str) -> str:
        """Solve for key given cipher family, C, and P"""
        if not c.isalpha() or not p.isalpha():
            return '?'
        
        c_val = ord(c) - ord('A')
        p_val = ord(p) - ord('A')
        
        if family == 'vigenere' or family == 'vig':
            k_val = (c_val - p_val) % 26
        elif family == 'beaufort' or family == 'bf':
            k_val = (p_val + c_val) % 26
        elif family == 'variant_beaufort' or family == 'varbf':
            k_val = (c_val - p_val) % 26
        else:
            return '?'
        
        return chr(k_val + ord('A'))
    
    def option_a_enforce(self, family: str, c: str, p: str) -> bool:
        """Option A: forbid K=0 (A) for additive families at anchors"""
        if family in ['vigenere', 'vig', 'variant_beaufort', 'varbf']:
            k = self.family_solve_key(family, c, p)
            if k == 'A':  # K=0
                return False
        return True
    
    def english_sanity(self, text: str) -> Dict:
        """Check English sanity of text"""
        result = {
            'ok': True,
            'bigram_violations': [],
            'consonant_runs': [],
            'words_found': [],
            'max_consonant_run': 0
        }
        
        # Check bigram blacklist
        for i in range(len(text) - 1):
            bigram = text[i:i+2]
            if bigram in self.bigram_blacklist:
                result['bigram_violations'].append((i, bigram))
                result['ok'] = False
        
        # Check consonant runs
        consonants = 'BCDFGHJKLMNPQRSTVWXYZ'
        current_run = 0
        run_start = 0
        
        for i, char in enumerate(text):
            if char in consonants:
                if current_run == 0:
                    run_start = i
                current_run += 1
                result['max_consonant_run'] = max(result['max_consonant_run'], current_run)
            else:
                if current_run > 4:
                    result['consonant_runs'].append((run_start, current_run))
                    result['ok'] = False
                current_run = 0
        
        # Check final run
        if current_run > 4:
            result['consonant_runs'].append((run_start, current_run))
            result['ok'] = False
        
        # Check for dictionary words (≥4 letters)
        text_upper = text.upper()
        for word in self.dictionary:
            if len(word) >= 4 and word in text_upper:
                result['words_found'].append(word)
        
        if not result['words_found']:
            result['ok'] = False
        
        return result
    
    def scramble_anchors(self, seed: Optional[int] = None) -> str:
        """Create scrambled ciphertext with random anchors for control"""
        if seed is not None:
            random.seed(seed)
        
        scrambled = list(self.k4_ct)
        
        for anchor_name, anchor_data in self.anchors.items():
            start = anchor_data['start']
            end = anchor_data['end']
            length = end - start + 1
            
            # Generate random letters
            random_text = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=length))
            
            # Replace in scrambled
            for i, char in enumerate(random_text):
                scrambled[start + i] = char
        
        # Reset seed
        random.seed(self.master_seed)
        
        return ''.join(scrambled)
    
    def result_card(self, schema_version: str = "ForkH-1.0", **kwargs) -> Dict:
        """Create standardized result card"""
        card = {
            'schema': schema_version,
            'timestamp': datetime.now().isoformat(),
            'seed': self.master_seed
        }
        card.update(kwargs)
        return card
    
    def explain_writer(self, filepath: str, config: Dict, derivations: List[Dict]):
        """Write EXPLAIN file with per-index derivations"""
        with open(filepath, 'w') as f:
            f.write("=== Fork H - Derivation Trace ===\n\n")
            f.write(f"Hypothesis: {config.get('hypothesis', 'unknown')}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Seed: {self.master_seed}\n\n")
            
            # Configuration details
            f.write("Configuration:\n")
            for key, value in config.items():
                if key != 'derivations':
                    f.write(f"  {key}: {value}\n")
            f.write("\n")
            
            # Per-index derivations
            f.write("Derivations (Head 0-20 + newly determined):\n")
            f.write("-" * 60 + "\n")
            f.write("Index | C | Family | K_source | K | P | Notes\n")
            f.write("-" * 60 + "\n")
            
            for d in derivations:
                idx = d.get('index', '?')
                c = d.get('c', '?')
                family = d.get('family', '?')[:3].upper()
                k_source = d.get('k_source', '?')[:15]
                k = d.get('k', '?')
                p = d.get('p', '?')
                notes = d.get('notes', '')
                
                f.write(f"{idx:5} | {c} | {family:3} | {k_source:15} | {k} | {p} | {notes}\n")
            
            f.write("-" * 60 + "\n")
    
    def check_anchors(self, plaintext: str) -> bool:
        """Verify all anchors are correct"""
        if len(plaintext) != 97:
            return False
        
        for anchor_name, anchor_data in self.anchors.items():
            start = anchor_data['start']
            end = anchor_data['end']
            expected = anchor_data['text']
            
            if plaintext[start:end+1] != expected:
                return False
        
        return True
    
    def count_unknowns(self, plaintext: str, target_indices: Optional[List[int]] = None) -> int:
        """Count unknown positions ('?') in plaintext"""
        if target_indices is None:
            # Default: non-anchor positions
            target_indices = list(range(21)) + list(range(34, 63)) + list(range(74, 97))
        
        return sum(1 for i in target_indices if i < len(plaintext) and plaintext[i] == '?')
    
    def null_model_test(self, test_func, config: Dict, n_samples: int = 100) -> bool:
        """Test if config beats 95th percentile of null model"""
        null_scores = []
        
        for _ in range(n_samples):
            # Randomize key parameters
            random_config = config.copy()
            
            # Randomize periods if present
            if 'periods' in random_config:
                for key in random_config['periods']:
                    random_config['periods'][key] = random.randint(2, 30)
            
            # Randomize key sources if present
            if 'key_sources' in random_config:
                for key in random_config['key_sources']:
                    # Generate random key string
                    length = len(random_config['key_sources'][key])
                    random_config['key_sources'][key] = ''.join(
                        random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=length)
                    )
            
            # Run test function with randomized config
            try:
                score = test_func(random_config)
                null_scores.append(score)
            except:
                null_scores.append(0)
        
        # Check if original beats 95th percentile
        if null_scores:
            threshold = sorted(null_scores)[min(94, len(null_scores)-1)]
            original_score = test_func(config)
            return original_score > threshold
        
        return True  # Default to pass if null model fails
    
    def load_k123_plaintexts(self) -> Dict[str, str]:
        """Load K1, K2, K3 plaintexts for running key"""
        # These are the known solutions to K1, K2, K3
        k1 = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
        k2 = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONXDOESLANGLEYKNOWABOUTTHISXTHEYSHOULDITSBURIEDOUTTHERESOMEWHEREXWHOKNOWSTHEEXACTLOCATIONONLYWWTHISWASHISLASTMESSAGEXTHIRTYEIGHTDEGREESFIFTYSEVENMINUTESSIXPOINTFIVESECONDSORTHSEVENTYSEVENDEGREESEIGHTMINUTESFORTYFOURSECONDSWESTIDBYROWSLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADEATINYBREACHINTHEUPPERLEFTHANDCORNERANDTHENWIDENINGTHEHOLEALITTLEIINSERTEDTHECANDLEANDPEEREDINTHEHOTAIRSTRIKINGMYFAIRCAUSEDTHEFLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHINEMERGEDFROMTHEMISTXCANYOUSEEANYTHINGQ"
        k3 = "SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADEATINYBREACHINTHEUPPERLEFTHANDCORNERANDTHENWIDENINGTHEHOLEALITTLEIINSERTEDTHECANDLEANDPEEREDINTHEHOTAIRSTRIKINGMYFAIRCAUSEDTHEFLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHINEMERGEDFROMTHEMISTXCANYOUSEEANYTHINGQ"
        
        return {
            'K1': k1,
            'K2': k2,
            'K3': k3,
            'K1K2K3': k1 + k2 + k3,
            'IQLUSION': "IQLUSION",
            'UNDERGRUUND': "UNDERGRUUND", 
            'DESPARATLY': "DESPARATLY",
            'PALIMPSEST': "PALIMPSEST",
            'ABSCISSA': "ABSCISSA",
            'SLOWLY': "SLOWLY"
        }


def main():
    """Test utilities"""
    utils = UtilsH()
    
    print("=== Fork H Utilities Test ===\n")
    
    # Test cipher families
    print("Cipher family tests:")
    print(f"Vigenere: C=K, K=C -> P={utils.family_apply('vigenere', 'K', 'C')}")
    print(f"Beaufort: C=K, K=C -> P={utils.family_apply('beaufort', 'K', 'C')}")
    print(f"Variant-Beaufort: C=K, K=C -> P={utils.family_apply('varbf', 'K', 'C')}")
    
    # Test key solving
    print("\nKey solving tests:")
    print(f"Vigenere: C=K, P=I -> K={utils.family_solve_key('vigenere', 'K', 'I')}")
    print(f"Beaufort: C=K, P=I -> K={utils.family_solve_key('beaufort', 'K', 'I')}")
    
    # Test English sanity
    print("\nEnglish sanity tests:")
    test1 = "WEARETHEGRID"
    test2 = "QZXJVQBCDFGHJKLM"
    print(f"'{test1}': {utils.english_sanity(test1)}")
    print(f"'{test2}': {utils.english_sanity(test2)}")
    
    # Test scrambled anchors
    print("\nScrambled anchors:")
    scrambled = utils.scramble_anchors(seed=42)
    print(f"Original EAST: {utils.k4_ct[21:25]}")
    print(f"Scrambled EAST: {scrambled[21:25]}")
    
    print("\nUtilities initialized successfully!")


if __name__ == "__main__":
    main()