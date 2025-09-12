#!/usr/bin/env python3
"""
run_dt14_tests.py

Fork DT14 - Main test runner for double transposition with L=14.
Tests anchor-aware chaining with columnar transposition.
"""

import json
import hashlib
import csv
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from double_transposition import (
    DoubleTransposition, generate_dt_keys
)

# Constants
MASTER_SEED = 1337
random.seed(MASTER_SEED)

# Common English words for validation
COMMON_WORDS = [
    'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER',
    'WAS', 'ONE', 'OUR', 'OUT', 'HAD', 'HAS', 'HIS', 'HOW', 'ITS', 'MAY',
    'LINE', 'NORTH', 'EAST', 'WEST', 'SOUTH', 'ANGLE', 'BEARING', 'TRUE',
    'GRID', 'WE', 'IN', 'AT', 'BE', 'IT', 'YARD', 'MAGNETIC', 'WEBSTER'
]

# Four-letter words specifically
FOUR_LETTER_WORDS = [
    'EAST', 'WEST', 'LINE', 'TRUE', 'YARD', 'GRID', 'THAT', 'WITH', 'HAVE',
    'THIS', 'WILL', 'YOUR', 'FROM', 'THEY', 'KNOW', 'WANT', 'BEEN', 'GOOD',
    'MUCH', 'SOME', 'TIME', 'VERY', 'WHEN', 'COME', 'HERE', 'JUST', 'LIKE',
    'LONG', 'MAKE', 'MANY', 'OVER', 'SUCH', 'TAKE', 'THAN', 'THEM', 'WELL'
]

class DT14Tester:
    """Main test orchestrator for Fork DT14."""
    
    def __init__(self):
        self.ciphertext = self.load_ciphertext()
        self.anchors = self.load_anchors()
        self.ct_sha256 = hashlib.sha256(self.ciphertext.encode()).hexdigest()
        
        self.results_dir = Path("04_EXPERIMENTS/fork_dt14/results")
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
        if len(plaintext) < 74:
            return False, ["Plaintext too short"]
        
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
        if len(plaintext) < 21:
            return {
                'vowel_ratio': 0,
                'max_consonant_run': 99,
                'four_letter_words': [],
                'word_count': 0,
                'bigram_score': 0,
                'head_text': plaintext
            }
        
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
        
        # Find four-letter words
        four_letter = []
        test_text = plaintext[:21] + plaintext[34:63] + plaintext[74:] if len(plaintext) > 74 else plaintext
        
        for word in FOUR_LETTER_WORDS:
            if word in test_text:
                four_letter.append(word)
        
        # Any words
        words_found = []
        for word in COMMON_WORDS:
            if len(word) >= 2 and word in test_text:
                words_found.append(word)
        
        # Bigram score
        common_bigrams = ['TH', 'HE', 'IN', 'ER', 'AN', 'RE', 'ED', 'ON']
        bigram_count = sum(1 for bg in common_bigrams if bg in plaintext)
        
        # Calculate bigram improvement vs random
        random_expected = len(common_bigrams) * 2 / 26  # Expected in random text
        bigram_improvement = bigram_count - random_expected
        
        return {
            'vowel_ratio': vowel_ratio,
            'max_consonant_run': max_run,
            'four_letter_words': four_letter[:5],
            'word_count': len(words_found),
            'bigram_score': bigram_count,
            'bigram_improvement': round(bigram_improvement, 2),
            'head_text': head
        }
    
    def test_dt_configuration(self, config: Dict, chain_key: str, 
                             chain_type: str, order: str):
        """Test a single DT configuration."""
        self.test_count += 1
        
        # Create double transposition
        dt = DoubleTransposition(
            config['key1'], config['key2'],
            config.get('cols1'), config.get('cols2')
        )
        
        # Check anchor feasibility
        if not dt.check_anchor_feasibility(self.anchors):
            # Skip if anchors can't be preserved
            return
        
        # Decrypt based on chain type
        try:
            if chain_type == 'none':
                plaintext = dt.decrypt_with_inverse(self.ciphertext)
                test_id = f"DT14-{config['name']}-plain"
            elif chain_type == 'vigenere':
                plaintext = dt.decrypt_chained_vigenere(self.ciphertext, chain_key, order)
                test_id = f"DT14-{config['name']}-VIG-{chain_key[:4]}-{order}"
            elif chain_type == 'beaufort':
                plaintext = dt.decrypt_chained_beaufort(self.ciphertext, chain_key, order)
                test_id = f"DT14-{config['name']}-BEAU-{chain_key[:4]}-{order}"
            else:
                return
        except Exception as e:
            # Skip on errors (e.g., incompatible dimensions)
            return
        
        # Validate anchors
        anchors_valid, anchor_failures = self.validate_anchors(plaintext)
        
        # Compute metrics
        metrics = self.compute_metrics(plaintext)
        
        # Check acceptance criteria
        accept = (
            anchors_valid and 
            metrics['max_consonant_run'] <= 4 and
            len(metrics['four_letter_words']) > 0 and
            metrics['bigram_improvement'] > 0
        )
        
        # Create result card
        result = {
            'id': test_id,
            'config': config,
            'chain_type': chain_type,
            'chain_key': chain_key if chain_type != 'none' else None,
            'order': order if chain_type != 'none' else None,
            'anchors': {
                'preserved': anchors_valid,
                'failures': anchor_failures if not anchors_valid else []
            },
            'plaintext_head': plaintext[:21] if len(plaintext) >= 21 else plaintext,
            'plaintext_full': plaintext if accept else None,
            'metrics': metrics,
            'accepted': accept,
            'repro': {
                'seed': MASTER_SEED,
                'ct_sha256': self.ct_sha256
            }
        }
        
        # Save result
        self.save_result(result)
        self.all_results.append(result)
        
        if accept:
            self.passing_results.append(result)
            print(f"    ✓✓ {test_id}: CANDIDATE FOUND!")
            print(f"       Head: {plaintext[:21]}")
            print(f"       4-letter words: {', '.join(metrics['four_letter_words'])}")
        elif anchors_valid:
            print(f"    ✓ {test_id}: Anchors preserved")
        elif metrics['max_consonant_run'] <= 4 and len(metrics['four_letter_words']) > 0:
            print(f"    ~ {test_id}: Good metrics but anchors failed")
        
        if self.test_count % 100 == 0:
            print(f"  Processed {self.test_count} tests...")
    
    def save_result(self, result: Dict):
        """Save individual result card."""
        result_path = self.results_dir / f"{result['id']}.json"
        with open(result_path, 'w') as f:
            json.dump(result, f, indent=2)
    
    def run_dt14_tests(self):
        """Run all DT14 tests."""
        print("\n" + "="*70)
        print("FORK DT14 - DOUBLE TRANSPOSITION TESTS")
        print("="*70)
        
        # Generate DT configurations
        dt_configs = generate_dt_keys()
        
        # Chain keys for Vigenère/Beaufort
        chain_keys = [
            "KRYPTOS",
            "PALIMPSEST", 
            "ABSCISSA",
            "YARD",
            "BERLINCLOCK",
            "NORTHEAST"
        ]
        
        # Test each DT configuration
        print(f"\nTesting {len(dt_configs)} DT configurations...")
        
        for config in dt_configs:
            # Test plain DT (no chain)
            self.test_dt_configuration(config, None, 'none', None)
            
            # Test with Vigenère chains
            for chain_key in chain_keys[:3]:  # Limit for speed
                # (DT^-1) ∘ VIG
                self.test_dt_configuration(config, chain_key, 'vigenere', 'dt_first')
                # VIG ∘ (DT^-1)
                self.test_dt_configuration(config, chain_key, 'vigenere', 'vig_first')
            
            # Test with Beaufort chains
            for chain_key in chain_keys[:3]:  # Limit for speed
                # (DT^-1) ∘ BEAU
                self.test_dt_configuration(config, chain_key, 'beaufort', 'dt_first')
                # BEAU ∘ (DT^-1)
                self.test_dt_configuration(config, chain_key, 'beaufort', 'beau_first')
        
        print(f"\nTotal tests: {self.test_count}")
        print(f"Candidates found: {len(self.passing_results)}")
    
    def generate_summary(self):
        """Generate summary reports."""
        # CSV summary
        csv_path = Path("04_EXPERIMENTS/fork_dt14/RUN_SUMMARY.csv")
        
        with open(csv_path, 'w', newline='') as f:
            fieldnames = ['id', 'key1', 'key2', 'cols1', 'cols2', 'chain_type',
                         'anchors_passed', 'head_text', 'max_cc_run', 
                         'four_letter_words', 'bigram_improvement', 'accepted']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in self.all_results:
                writer.writerow({
                    'id': result['id'],
                    'key1': result['config']['key1'],
                    'key2': result['config']['key2'],
                    'cols1': result['config'].get('cols1', ''),
                    'cols2': result['config'].get('cols2', ''),
                    'chain_type': result['chain_type'],
                    'anchors_passed': result['anchors']['preserved'],
                    'head_text': result['plaintext_head'],
                    'max_cc_run': result['metrics']['max_consonant_run'],
                    'four_letter_words': ','.join(result['metrics']['four_letter_words']),
                    'bigram_improvement': result['metrics']['bigram_improvement'],
                    'accepted': result['accepted']
                })
        
        print(f"\nCSV summary saved to: {csv_path}")
        
        # Top candidates report
        self.generate_top_candidates()
    
    def generate_top_candidates(self):
        """Generate report of top 10 candidates."""
        report_path = Path("04_EXPERIMENTS/fork_dt14/TOP_CANDIDATES.md")
        
        # Sort by quality
        scored = []
        for result in self.all_results:
            score = 0
            if result['anchors']['preserved']:
                score += 100
            score -= result['metrics']['max_consonant_run'] * 5
            score += len(result['metrics']['four_letter_words']) * 10
            score += result['metrics']['bigram_improvement'] * 2
            scored.append((score, result))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        
        with open(report_path, 'w') as f:
            f.write("# Fork DT14 - Top Candidates\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total tests: {self.test_count}\n")
            f.write(f"Accepted candidates: {len(self.passing_results)}\n\n")
            
            if self.passing_results:
                f.write("## ACCEPTED CANDIDATES\n\n")
                for i, result in enumerate(self.passing_results[:10], 1):
                    f.write(f"### Candidate {i}: {result['id']}\n")
                    f.write(f"- Keys: {result['config']['key1']} / {result['config']['key2']}\n")
                    f.write(f"- Columns: {result['config'].get('cols1')} / {result['config'].get('cols2')}\n")
                    f.write(f"- Head: `{result['plaintext_head']}`\n")
                    f.write(f"- 4-letter words: {', '.join(result['metrics']['four_letter_words'])}\n")
                    f.write(f"- Bigram improvement: {result['metrics']['bigram_improvement']}\n")
                    if result['plaintext_full']:
                        f.write(f"- Full plaintext:\n```\n{result['plaintext_full']}\n```\n")
                    f.write("\n")
            else:
                f.write("## Top 10 Results (none accepted)\n\n")
                for i, (score, result) in enumerate(scored[:10], 1):
                    f.write(f"### Result {i} (score: {score:.1f}): {result['id']}\n")
                    f.write(f"- Head: `{result['plaintext_head']}`\n")
                    f.write(f"- Anchors: {'✓' if result['anchors']['preserved'] else '✗'}\n")
                    f.write(f"- Max consonant run: {result['metrics']['max_consonant_run']}\n")
                    f.write(f"- 4-letter words: {', '.join(result['metrics']['four_letter_words']) if result['metrics']['four_letter_words'] else 'none'}\n\n")
        
        print(f"Top candidates saved to: {report_path}")

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("FORK DT14 - DOUBLE TRANSPOSITION TEST SUITE")
    print("L=14 focus with anchor-aware chaining")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Master seed: {MASTER_SEED}")
    
    tester = DT14Tester()
    tester.run_dt14_tests()
    tester.generate_summary()
    
    print("\n" + "="*70)
    print("TESTING COMPLETE")
    print(f"Total tests: {tester.test_count}")
    print(f"Accepted candidates: {len(tester.passing_results)}")
    if tester.passing_results:
        print("\n🎯 CANDIDATES REQUIRE FURTHER ANALYSIS!")
    print("="*70)

if __name__ == "__main__":
    main()