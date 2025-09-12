#!/usr/bin/env python3
"""
Fork K - Two-Clock OTP Main Runner
Tests Berlin Clock + Urania Clock combination as running key for K4
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from berlin_clock import BerlinClock
from urania_clock import UraniaTimeZones
from keystream_mappers import KeystreamMapper

class ForkKRunner:
    def __init__(self, master_seed: int = 1337):
        """Initialize Fork K runner"""
        self.master_seed = master_seed
        self.berlin = BerlinClock()
        self.urania = UraniaTimeZones()
        self.mapper = KeystreamMapper()
        
        # K4 ciphertext
        self.k4_ct = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
        
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
        
        # Validation words
        self.function_words = {'WE', 'ARE', 'AT', 'BY', 'TO', 'THE', 'IS', 'OF', 'IN'}
        self.tail_words = {'ANGLE', 'ARC', 'JOY', 'MEASURE', 'THE'}
        
        # Results storage
        self.results = []
        self.test_count = 0
    
    def check_anchors(self, plaintext: str) -> bool:
        """Check if plaintext has correct anchors"""
        for anchor_name, anchor_data in self.anchors.items():
            start = anchor_data['start']
            expected = anchor_data['text']
            
            for i, expected_char in enumerate(expected):
                if start + i >= len(plaintext):
                    return False
                if plaintext[start + i] != expected_char:
                    return False
        
        return True
    
    def check_head_sanity(self, head: str) -> Tuple[bool, Dict]:
        """Check head (0-20) for English characteristics"""
        info = {
            'consonant_runs': 0,
            'function_words': [],
            'ok': False
        }
        
        # Check consonant runs
        vowels = 'AEIOU'
        max_run = 0
        current_run = 0
        
        for char in head:
            if char not in vowels:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 0
        
        info['consonant_runs'] = max_run
        
        # Check function words
        for word in self.function_words:
            if word in head:
                info['function_words'].append(word)
        
        # Pass if no 5+ consonant run and at least 1 function word
        info['ok'] = max_run < 5 and len(info['function_words']) > 0
        
        return info['ok'], info
    
    def check_tail_sanity(self, tail: str) -> Tuple[bool, Dict]:
        """Check tail (74-96) for patterns"""
        info = {
            'flint_matches': 0,
            'tail_words': [],
            'consonant_runs': 0,
            'ok': False
        }
        
        # Check for Flint-like pattern "THE...ARC"
        flint_pattern = "THEMEASUREOFANANGLEISTH"[:23]
        matches = sum(1 for i in range(min(23, len(tail))) if tail[i] == flint_pattern[i])
        info['flint_matches'] = matches
        
        # Check tail words
        for word in self.tail_words:
            if word in tail:
                info['tail_words'].append(word)
        
        # Check consonant runs
        vowels = 'AEIOU'
        max_run = 0
        current_run = 0
        
        for char in tail:
            if char not in vowels:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 0
        
        info['consonant_runs'] = max_run
        
        # Pass if Flint-like OR (no 5+ consonant run and has tail words)
        info['ok'] = (matches >= 11) or (max_run < 5 and len(info['tail_words']) > 0)
        
        return info['ok'], info
    
    def decrypt_with_keystream(self, keystream: List[int], family: str) -> str:
        """Decrypt K4 using keystream and cipher family"""
        decrypt_fn = self.families[family]
        plaintext = []
        
        for i in range(97):
            c_char = self.k4_ct[i]
            k_val = keystream[i]
            k_char = chr(k_val + ord('A'))
            p_char = decrypt_fn(c_char, k_char)
            plaintext.append(p_char)
        
        return ''.join(plaintext)
    
    def test_configuration(self, dt: datetime, dst_mengen: str, dst_urania: str,
                          method: str, params: Dict, family: str) -> Dict:
        """Test a single configuration"""
        self.test_count += 1
        
        # Generate clock states
        berlin_encodings = self.berlin.get_all_encodings(dt)
        urania_encodings = self.urania.get_all_encodings(dt, dst_mode=dst_urania)
        
        # Select encoding based on params
        berlin_enc = params.get('berlin_enc', 'B-color')
        urania_enc = params.get('urania_enc', 'U-hour')
        
        berlin_vector = berlin_encodings.get(berlin_enc, berlin_encodings['B-color'])
        urania_vector = urania_encodings.get(urania_enc, urania_encodings['U-hour'])
        
        # Generate keystream
        keystream = self.mapper.generate_keystream(berlin_vector, urania_vector, method, params)
        
        # Decrypt
        plaintext = self.decrypt_with_keystream(keystream, family)
        
        # Check anchors
        anchors_ok = self.check_anchors(plaintext)
        
        # Extract sections
        head = plaintext[:21] if len(plaintext) >= 21 else plaintext
        tail = plaintext[74:97] if len(plaintext) >= 97 else ''
        
        # Check sanity
        head_ok, head_info = self.check_head_sanity(head) if anchors_ok else (False, {})
        tail_ok, tail_info = self.check_tail_sanity(tail) if anchors_ok else (False, {})
        
        # Count unknowns (non-anchor positions without clear English)
        unknowns = 50  # Start with non-anchor count
        if head_ok:
            unknowns -= 21
        if tail_ok:
            unknowns -= 23
        
        # Create result card
        result = {
            'fork': 'K',
            'dt_base': dt.isoformat(),
            'dt_mode': {'dst_mengen': dst_mengen, 'dst_urania': dst_urania},
            'gen': {
                'method': method,
                'pre_map': f"{berlin_enc}|{urania_enc}",
                'params': params
            },
            'family': family,
            'anchors_ok': anchors_ok,
            'head_ok': head_ok,
            'tail_ok': tail_ok,
            'unknowns_after': unknowns,
            'plaintext_sample': plaintext[:50] if anchors_ok else '',
            'head_info': head_info if anchors_ok else {},
            'tail_info': tail_info if anchors_ok else {}
        }
        
        return result
    
    def scan_timestamp(self, base_dt: datetime, window_minutes: int = 90,
                       step_minutes: int = 1) -> List[datetime]:
        """Generate scan window around base timestamp"""
        timestamps = []
        
        for offset in range(-window_minutes, window_minutes + 1, step_minutes):
            dt = base_dt + timedelta(minutes=offset)
            timestamps.append(dt)
        
        return timestamps
    
    def run_timestamp_sweep(self, base_dt: datetime, max_tests: int = 1000) -> List[Dict]:
        """Run sweep for a single base timestamp"""
        results = []
        
        print(f"\n=== Testing timestamp: {base_dt} ===")
        
        # DST modes
        dst_modes = [('off', 'off'), ('on', 'on'), ('off', 'on'), ('on', 'off')]
        
        # Scan window (limited for initial testing)
        scan_window = 30  # ±30 minutes instead of ±90
        timestamps = self.scan_timestamp(base_dt, scan_window, 5)  # 5-minute steps
        
        # Method configurations
        method_configs = [
            ('direct_concat', {'jitter': 0, 'berlin_enc': 'B-color', 'urania_enc': 'U-hour'}),
            ('direct_concat', {'jitter': 1, 'berlin_enc': 'B-bin', 'urania_enc': 'U-scaled'}),
            ('alt_streams', {'start_with': 'berlin', 'drift': 0, 'berlin_enc': 'B-color', 'urania_enc': 'U-hour'}),
            ('alt_streams', {'start_with': 'urania', 'drift': 1, 'berlin_enc': 'B-rowcount', 'urania_enc': 'U-hour'}),
            ('pointwise', {'operation': 'sum', 'berlin_enc': 'B-color', 'urania_enc': 'U-hour'}),
            ('pointwise', {'operation': 'xor', 'quantize': True, 'berlin_enc': 'B-bin', 'urania_enc': 'U-hour'}),
            ('matrix_gen', {'alpha': 1, 'beta': 1, 'seed': 'unit', 'berlin_enc': 'B-color', 'urania_enc': 'U-hour'}),
            ('matrix_gen', {'alpha': 1, 'beta': 5, 'seed': 'kryptos', 'berlin_enc': 'B-color', 'urania_enc': 'U-scaled'})
        ]
        
        # Test combinations
        for dt in timestamps[:10]:  # Limit timestamps for initial test
            for dst_m, dst_u in dst_modes[:2]:  # Just test off/off and on/on first
                for method, params in method_configs[:4]:  # Test first 4 methods
                    for family in ['vigenere', 'beaufort', 'varbf']:
                        if self.test_count >= max_tests:
                            break
                        
                        result = self.test_configuration(dt, dst_m, dst_u, method, params, family)
                        
                        # Track promising results
                        if result['anchors_ok']:
                            results.append(result)
                            print(f"  Anchors OK: {dt.strftime('%H:%M')} {dst_m}/{dst_u} {method} {family}")
                            if result['head_ok']:
                                print(f"    HEAD OK! Words: {result['head_info'].get('function_words', [])}")
                            if result['tail_ok']:
                                print(f"    TAIL OK! Words: {result['tail_info'].get('tail_words', [])}")
                        
                        # Success criteria
                        if result['anchors_ok'] and result['head_ok'] and result['tail_ok']:
                            print(f"*** SUCCESS! Unknowns: {result['unknowns_after']} ***")
                            print(f"    Config: {result}")
        
        return results
    
    def run_all_timestamps(self) -> List[Dict]:
        """Run tests for all target timestamps"""
        all_results = []
        
        # Target timestamps
        timestamps = [
            datetime(1990, 11, 3, 14, 0, 0),   # Dedication day EST (as local)
            datetime(1989, 11, 9, 18, 53, 0),  # Wall opening Berlin
            datetime(1990, 1, 8, 12, 0, 0),    # Sanborn birthday noon
            datetime(1989, 11, 9, 12, 0, 0),   # UTC noon proxy
        ]
        
        for base_dt in timestamps:
            results = self.run_timestamp_sweep(base_dt, max_tests=500)
            all_results.extend(results)
            
            if results:
                print(f"  Found {len(results)} configurations with correct anchors")
        
        return all_results
    
    def save_results(self, results: List[Dict]):
        """Save results to NDJSON and CSV"""
        output_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Save NDJSON
        ndjson_path = os.path.join(output_dir, 'K_RESULTS.ndjson')
        with open(ndjson_path, 'w') as f:
            for result in results:
                f.write(json.dumps(result) + '\n')
        print(f"\nSaved {len(results)} results to {ndjson_path}")
        
        # Save summary CSV
        csv_path = os.path.join(output_dir, 'K_SUMMARY.csv')
        with open(csv_path, 'w') as f:
            f.write("dt_base,dst_mode,method,family,anchors_ok,head_ok,tail_ok,unknowns\n")
            for r in results:
                dt = r['dt_base'][:19]
                dst = f"{r['dt_mode']['dst_mengen']}/{r['dt_mode']['dst_urania']}"
                method = r['gen']['method']
                family = r['family']
                anchors = 'Y' if r['anchors_ok'] else 'N'
                head = 'Y' if r['head_ok'] else 'N'
                tail = 'Y' if r['tail_ok'] else 'N'
                unknowns = r['unknowns_after']
                f.write(f"{dt},{dst},{method},{family},{anchors},{head},{tail},{unknowns}\n")
        print(f"Saved summary to {csv_path}")


def main():
    """Run Fork K testing"""
    runner = ForkKRunner()
    
    print("=== Fork K - Two-Clock OTP Testing ===")
    print("Berlin Clock (Mengenlehreuhr) + Urania World Time Clock")
    print("=" * 60)
    
    # Run all tests
    results = runner.run_all_timestamps()
    
    # Analyze results
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total tests: {runner.test_count}")
    print(f"Configurations with correct anchors: {len(results)}")
    
    if results:
        # Check for success
        successes = [r for r in results if r['anchors_ok'] and r['head_ok'] and r['tail_ok']]
        soft_passes = [r for r in results if r['anchors_ok'] and r['head_ok'] and r['unknowns_after'] < 35]
        
        print(f"Hard passes (all criteria): {len(successes)}")
        print(f"Soft passes (anchors + head): {len(soft_passes)}")
        
        # Save results
        runner.save_results(results)
        
        # Show best result
        if successes:
            best = min(successes, key=lambda x: x['unknowns_after'])
            print(f"\nBest result: {best['unknowns_after']} unknowns")
            print(f"  Config: {best['gen']}")
        elif soft_passes:
            best = min(soft_passes, key=lambda x: x['unknowns_after'])
            print(f"\nBest soft pass: {best['unknowns_after']} unknowns")
            print(f"  Config: {best['gen']}")
    else:
        print("No configurations preserved anchors - clean negative result")
        
        # Still save empty results for documentation
        runner.save_results([])


if __name__ == "__main__":
    main()