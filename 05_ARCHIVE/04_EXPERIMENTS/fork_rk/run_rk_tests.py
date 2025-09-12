#!/usr/bin/env python3
"""
run_rk_tests.py

Fork RK - Main test runner for running-key ciphers.
Tests K1-K3 plaintexts as non-periodic key material.
"""

import json
import hashlib
import csv
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from running_key_cipher import (
    RunningKeyCipher, SegmentedRunningKey,
    generate_running_keys, generate_segmented_keys,
    K1_PLAINTEXT, K2_PLAINTEXT, K3_PLAINTEXT
)

# Constants
MASTER_SEED = 1337
random.seed(MASTER_SEED)

# Common English words for validation
COMMON_WORDS = [
    'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER',
    'WAS', 'ONE', 'OUR', 'OUT', 'HAD', 'HAS', 'HIS', 'HOW', 'ITS', 'MAY',
    'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WAY', 'WHO', 'BOY', 'DID', 'ITS',
    'LET', 'PUT', 'SAY', 'SHE', 'TOO', 'USE', 'THAT', 'WITH', 'HAVE',
    'THIS', 'WILL', 'YOUR', 'FROM', 'THEY', 'KNOW', 'WANT', 'BEEN', 'GOOD',
    'MUCH', 'SOME', 'TIME', 'VERY', 'WHEN', 'COME', 'HERE', 'JUST', 'LIKE',
    'LONG', 'MAKE', 'MANY', 'OVER', 'SUCH', 'TAKE', 'THAN', 'THEM', 'WELL',
    'LINE', 'NORTH', 'EAST', 'WEST', 'SOUTH', 'ANGLE', 'BEARING', 'MERIDIAN',
    'TRUE', 'MAGNETIC', 'YARD', 'GRID', 'WE', 'ARE', 'IN', 'AT', 'BE', 'IT'
]

class RunningKeyTester:
    """Main test orchestrator for Fork RK."""
    
    def __init__(self):
        self.ciphertext = self.load_ciphertext()
        self.anchors = self.load_anchors()
        self.ct_sha256 = hashlib.sha256(self.ciphertext.encode()).hexdigest()
        
        self.results_dir = Path("04_EXPERIMENTS/fork_rk/results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.all_results = []
        self.passing_results = []
        self.test_count = 0
    
    def load_ciphertext(self) -> str:
        """Load K4 ciphertext."""
        path = Path("02_DATA/ciphertext_97.txt")
        if not path.exists():
            # Fallback ciphertext for testing
            return "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
        
        with open(path, 'r') as f:
            return f.read().strip()
    
    def load_anchors(self) -> Dict:
        """Load anchor positions."""
        path = Path("02_DATA/anchors/four_anchors.json")
        if not path.exists():
            # Fallback anchors
            return {
                "EAST": [21, 24],
                "NORTHEAST": [25, 33],
                "BERLIN": [63, 68],
                "CLOCK": [69, 73]
            }
        
        with open(path, 'r') as f:
            return json.load(f)
    
    def validate_anchors(self, plaintext: str) -> Tuple[bool, List[str]]:
        """Validate anchor preservation."""
        failures = []
        
        # Check each anchor
        if plaintext[21:25] != "EAST":
            failures.append(f"EAST: Expected 'EAST' at 21-24, got '{plaintext[21:25]}'")
        
        if plaintext[25:34] != "NORTHEAST":
            failures.append(f"NORTHEAST: Expected 'NORTHEAST' at 25-33, got '{plaintext[25:34]}'")
        
        if plaintext[63:69] != "BERLIN":
            failures.append(f"BERLIN: Expected 'BERLIN' at 63-68, got '{plaintext[63:69]}'")
        
        if plaintext[69:74] != "CLOCK":
            failures.append(f"CLOCK: Expected 'CLOCK' at 69-73, got '{plaintext[69:74]}'")
        
        return len(failures) == 0, failures
    
    def compute_metrics(self, plaintext: str) -> Dict:
        """Compute quality metrics."""
        head = plaintext[:21]
        
        # Vowel ratio
        vowels = sum(1 for c in head if c in 'AEIOU')
        vowel_ratio = round(vowels / len(head), 2) if len(head) > 0 else 0
        
        # Max consonant run
        max_run = 0
        current_run = 0
        for c in head:
            if c not in 'AEIOU':
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 0
        
        # Find real words
        words_found = []
        test_text = plaintext[:21] + plaintext[34:63] + plaintext[74:]  # Exclude anchors
        
        for word in COMMON_WORDS:
            if len(word) >= 2 and word in test_text:
                words_found.append(word)
        
        # Bigram score
        common_bigrams = ['TH', 'HE', 'IN', 'ER', 'AN', 'RE', 'ED', 'ON', 
                         'ES', 'ST', 'EN', 'AT', 'TO', 'NT', 'HA', 'ND']
        bigram_count = sum(1 for bg in common_bigrams if bg in plaintext)
        
        return {
            'vowel_ratio': vowel_ratio,
            'max_consonant_run': max_run,
            'words_found': words_found[:10],  # Limit to 10
            'word_count': len(words_found),
            'bigram_score': bigram_count,
            'head_text': head
        }
    
    def run_negative_controls(self, key_config: Dict, family: str) -> Dict:
        """Run negative control tests."""
        controls = {
            'scrambled_anchors_failed': None,
            'random_key_failed': None
        }
        
        # 1. Scrambled anchors test
        scrambled_ct = list(self.ciphertext)
        for i in range(21, 34):  # Scramble anchor regions
            scrambled_ct[i] = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        scrambled_ct = ''.join(scrambled_ct)
        
        # Test with scrambled
        if 'zones' in key_config:
            cipher = SegmentedRunningKey(key_config['zones'])
        else:
            cipher = RunningKeyCipher(key_config['key_text'], key_config['offset'])
        
        if family == 'vigenere':
            scrambled_plain = cipher.decrypt_vigenere(scrambled_ct)
        elif family == 'beaufort':
            scrambled_plain = cipher.decrypt_beaufort(scrambled_ct)
        else:
            scrambled_plain = cipher.decrypt_variant_beaufort(scrambled_ct)
        
        scrambled_valid, _ = self.validate_anchors(scrambled_plain)
        controls['scrambled_anchors_failed'] = not scrambled_valid
        
        # 2. Random key test
        random_key = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=100))
        random_cipher = RunningKeyCipher(random_key, 0)
        
        if family == 'vigenere':
            random_plain = random_cipher.decrypt_vigenere(self.ciphertext)
        elif family == 'beaufort':
            random_plain = random_cipher.decrypt_beaufort(self.ciphertext)
        else:
            random_plain = random_cipher.decrypt_variant_beaufort(self.ciphertext)
        
        random_valid, _ = self.validate_anchors(random_plain)
        controls['random_key_failed'] = not random_valid
        
        return controls
    
    def test_configuration(self, key_name: str, key_config: Dict, family: str):
        """Test a single configuration."""
        self.test_count += 1
        
        # Create cipher
        if 'zones' in key_config:
            # Segmented key
            cipher = SegmentedRunningKey(key_config['zones'])
            test_id = f"RK-{key_config['name']}-{family}"
        else:
            # Simple running key
            cipher = RunningKeyCipher(key_config['key_text'], key_config['offset'])
            test_id = f"RK-{key_name}-offset{key_config['offset']}-{family}"
        
        # Decrypt
        if family == 'vigenere':
            plaintext = cipher.decrypt_vigenere(self.ciphertext)
        elif family == 'beaufort':
            plaintext = cipher.decrypt_beaufort(self.ciphertext)
        else:  # variant_beaufort
            plaintext = cipher.decrypt_variant_beaufort(self.ciphertext)
        
        # Validate anchors
        anchors_valid, anchor_failures = self.validate_anchors(plaintext)
        
        # Compute metrics
        metrics = self.compute_metrics(plaintext)
        
        # Run controls if promising
        controls = {}
        if anchors_valid or metrics['max_consonant_run'] <= 4:
            controls = self.run_negative_controls(key_config, family)
        
        # Create result card
        result = {
            'id': test_id,
            'key_name': key_name,
            'family': family,
            'offset': key_config.get('offset', 0),
            'anchors': {
                'preserved': anchors_valid,
                'failures': anchor_failures if not anchors_valid else []
            },
            'plaintext_head': plaintext[:21],
            'plaintext_full': plaintext if anchors_valid else None,
            'metrics': metrics,
            'controls': controls,
            'repro': {
                'seed': MASTER_SEED,
                'ct_sha256': self.ct_sha256
            }
        }
        
        # Save result
        self.save_result(result)
        self.all_results.append(result)
        
        # Check acceptance criteria
        if anchors_valid and metrics['max_consonant_run'] <= 4 and metrics['word_count'] > 0:
            self.passing_results.append(result)
            print(f"    ✓ {test_id}: CANDIDATE FOUND!")
            print(f"      Head: {plaintext[:21]}")
            print(f"      Words: {', '.join(metrics['words_found'][:5])}")
        elif anchors_valid:
            print(f"    ✓ {test_id}: Anchors preserved (but head poor)")
        elif metrics['max_consonant_run'] <= 4 and metrics['word_count'] > 0:
            print(f"    ~ {test_id}: Good head but anchors failed")
        
        if self.test_count % 50 == 0:
            print(f"  Processed {self.test_count} tests...")
    
    def save_result(self, result: Dict):
        """Save individual result card."""
        result_path = self.results_dir / f"{result['id']}.json"
        with open(result_path, 'w') as f:
            json.dump(result, f, indent=2)
    
    def run_rk_tests(self):
        """Run all RK tests."""
        print("\n" + "="*70)
        print("FORK RK - RUNNING KEY TESTS")
        print("="*70)
        
        # Generate all key variants
        running_keys = generate_running_keys()
        
        # Test families
        families = ['vigenere', 'beaufort', 'variant_beaufort']
        
        # Test RK1, RK2, RK3 with various offsets
        print("\nTesting simple running keys...")
        for key_name in ['RK1', 'RK2', 'RK3', 'RK123', 'RK_MISSPELL']:
            if key_name not in running_keys:
                continue
            
            key_text = running_keys[key_name]
            
            # Test different offsets (0 to min(len(key)-1, 30))
            max_offset = min(len(key_text) - 1, 30)
            for offset in range(0, max_offset + 1, 5):  # Step by 5 for efficiency
                key_config = {
                    'key_text': key_text,
                    'offset': offset
                }
                
                for family in families:
                    self.test_configuration(key_name, key_config, family)
        
        # Test special segments
        print("\nTesting special key segments...")
        for key_name in ['RK2_INVISIBLE', 'RK2_COORDINATES']:
            if key_name not in running_keys:
                continue
            
            key_text = running_keys[key_name]
            
            # Test with fewer offsets for shorter keys
            max_offset = min(len(key_text) - 1, 15)
            for offset in range(0, max_offset + 1, 3):
                key_config = {
                    'key_text': key_text,
                    'offset': offset
                }
                
                for family in families:
                    self.test_configuration(key_name, key_config, family)
        
        # Test segmented keys
        print("\nTesting segmented keys (RKmix)...")
        segmented_configs = generate_segmented_keys()
        
        for seg_config in segmented_configs:
            for family in families:
                self.test_configuration('RKseg', seg_config, family)
        
        print(f"\nTotal tests: {self.test_count}")
        print(f"Candidates found: {len(self.passing_results)}")
    
    def generate_summary(self):
        """Generate summary reports."""
        # CSV summary
        csv_path = Path("04_EXPERIMENTS/fork_rk/RUN_SUMMARY.csv")
        
        with open(csv_path, 'w', newline='') as f:
            fieldnames = ['id', 'key_name', 'family', 'offset', 
                         'anchors_passed', 'head_text', 'max_cc_run', 
                         'words_found', 'word_count', 'controls_passed']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in self.all_results:
                controls_passed = all(result['controls'].values()) if result['controls'] else False
                writer.writerow({
                    'id': result['id'],
                    'key_name': result['key_name'],
                    'family': result['family'],
                    'offset': result['offset'],
                    'anchors_passed': result['anchors']['preserved'],
                    'head_text': result['plaintext_head'],
                    'max_cc_run': result['metrics']['max_consonant_run'],
                    'words_found': ','.join(result['metrics']['words_found'][:3]),
                    'word_count': result['metrics']['word_count'],
                    'controls_passed': controls_passed
                })
        
        print(f"\nCSV summary saved to: {csv_path}")
        
        # Ranked summary
        self.generate_ranked_summary()
    
    def generate_ranked_summary(self):
        """Generate ranked summary of best results."""
        report_path = Path("04_EXPERIMENTS/fork_rk/RANKED_SUMMARY.md")
        
        # Sort results by quality
        scored_results = []
        for result in self.all_results:
            score = 0
            if result['anchors']['preserved']:
                score += 100
            score -= result['metrics']['max_consonant_run'] * 5
            score += result['metrics']['word_count'] * 3
            score += result['metrics']['bigram_score']
            
            scored_results.append((score, result))
        
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        with open(report_path, 'w') as f:
            f.write("# Fork RK - Ranked Summary\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total tests: {self.test_count}\n")
            f.write(f"Candidates (anchors + good head): {len(self.passing_results)}\n\n")
            
            if self.passing_results:
                f.write("## CANDIDATES FOUND\n\n")
                for i, result in enumerate(self.passing_results[:10], 1):
                    f.write(f"### Candidate {i}: {result['id']}\n")
                    f.write(f"- Key: {result['key_name']} (offset {result['offset']})\n")
                    f.write(f"- Family: {result['family']}\n")
                    f.write(f"- Head: `{result['plaintext_head']}`\n")
                    f.write(f"- Words found: {', '.join(result['metrics']['words_found'][:5])}\n")
                    f.write(f"- Max consonant run: {result['metrics']['max_consonant_run']}\n")
                    if result['plaintext_full']:
                        f.write(f"- Full plaintext:\n```\n{result['plaintext_full']}\n```\n")
                    f.write("\n")
            else:
                f.write("## Top 10 Results (by score)\n\n")
                for i, (score, result) in enumerate(scored_results[:10], 1):
                    f.write(f"### Result {i} (score: {score}): {result['id']}\n")
                    f.write(f"- Head: `{result['plaintext_head']}`\n")
                    f.write(f"- Anchors: {'✓' if result['anchors']['preserved'] else '✗'}\n")
                    f.write(f"- Max consonant run: {result['metrics']['max_consonant_run']}\n")
                    f.write(f"- Words: {', '.join(result['metrics']['words_found'][:3]) if result['metrics']['words_found'] else 'none'}\n\n")
            
            f.write("## Acceptance Criteria\n")
            f.write("- All four anchors preserved exactly\n")
            f.write("- Head (0-20) max consonant run ≤ 4\n")
            f.write("- At least 1 real word found\n")
            f.write("- Negative controls passed\n")
        
        print(f"Ranked summary saved to: {report_path}")

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("FORK RK - RUNNING KEY CIPHER TEST SUITE")
    print("Non-periodic keys from K1-K3 plaintexts")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Master seed: {MASTER_SEED}")
    
    tester = RunningKeyTester()
    tester.run_rk_tests()
    tester.generate_summary()
    
    print("\n" + "="*70)
    print("TESTING COMPLETE")
    print(f"Total tests: {tester.test_count}")
    print(f"Candidates found: {len(tester.passing_results)}")
    if tester.passing_results:
        print("\n🎯 CANDIDATES REQUIRE FURTHER ANALYSIS!")
    print("="*70)

if __name__ == "__main__":
    main()