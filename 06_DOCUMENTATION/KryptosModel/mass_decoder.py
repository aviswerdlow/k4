#!/usr/bin/env python3
"""
MASS Decoder - Method-Agnostic Shift Search for K4
Constrained by sculpture-derived schedules
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
import hashlib
from collections import Counter
import itertools

# Configuration
ROOT = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/06_DOCUMENTATION/KryptosModel")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
rng = np.random.default_rng(20250913)

# Standard alphabet
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# KRYPTOS tableau (unique alphabet from keyword)
def make_kryptos_tableau():
    keyword = "KRYPTOS"
    seen = set()
    tableau = []
    for c in keyword:
        if c not in seen:
            tableau.append(c)
            seen.add(c)
    for c in ALPHA:
        if c not in seen:
            tableau.append(c)
    return ''.join(tableau)

KRYPTOS = make_kryptos_tableau()  # "KRYPTOSABCDEFGHIJLMNQUVWXZ"

# Cipher families
def vigenere_encrypt(pt_char, key_val, alphabet=ALPHA):
    """Vigenère: CT = (PT + K) mod N"""
    pt_idx = alphabet.index(pt_char)
    ct_idx = (pt_idx + key_val) % len(alphabet)
    return alphabet[ct_idx]

def vigenere_decrypt(ct_char, key_val, alphabet=ALPHA):
    """Vigenère: PT = (CT - K) mod N"""
    ct_idx = alphabet.index(ct_char)
    pt_idx = (ct_idx - key_val) % len(alphabet)
    return alphabet[pt_idx]

def beaufort_encrypt(pt_char, key_val, alphabet=ALPHA):
    """Beaufort: CT = (K - PT) mod N"""
    pt_idx = alphabet.index(pt_char)
    ct_idx = (key_val - pt_idx) % len(alphabet)
    return alphabet[ct_idx]

def beaufort_decrypt(ct_char, key_val, alphabet=ALPHA):
    """Beaufort: PT = (K - CT) mod N (self-inverse)"""
    ct_idx = alphabet.index(ct_char)
    pt_idx = (key_val - ct_idx) % len(alphabet)
    return alphabet[pt_idx]

# Language model (simplified)
def simple_lm_score(text):
    """5-gram proxy with function word bonuses"""
    if not text:
        return 0.0

    score = 0.0

    # Function word bonuses
    function_words = ['THE', 'AND', 'OF', 'TO', 'IN', 'A', 'IS', 'IT', 'FOR', 'WITH',
                      'BE', 'AS', 'AT', 'BY', 'OR', 'AN', 'FROM', 'BUT', 'NOT', 'CAN']

    for word in function_words:
        count = text.count(word)
        score += count * len(word) * 0.5

    # Basic frequency scoring
    english_freq = {
        'E': 12.7, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0, 'N': 6.7,
        'S': 6.3, 'H': 6.1, 'R': 6.0, 'D': 4.3, 'L': 4.0, 'C': 2.8,
        'U': 2.8, 'M': 2.4, 'W': 2.4, 'F': 2.2, 'G': 2.0, 'Y': 2.0,
        'P': 1.9, 'B': 1.5, 'V': 1.0, 'K': 0.8, 'J': 0.15, 'X': 0.15,
        'Q': 0.10, 'Z': 0.07
    }

    for char in text:
        score += english_freq.get(char, 0) / 100

    # Common bigrams
    common_bigrams = ['TH', 'HE', 'IN', 'ER', 'AN', 'RE', 'ED', 'ON', 'ES', 'ST',
                       'EN', 'AT', 'TO', 'NT', 'HA', 'ND', 'OU', 'EA', 'NG', 'AS']
    for bigram in common_bigrams:
        count = sum(1 for i in range(len(text)-1) if text[i:i+2] == bigram)
        score += count * 0.3

    return score / len(text)

def key_complexity(shifts):
    """Measure complexity of shift pattern"""
    # Count distinct values
    distinct = len(set(shifts))

    # Count change points
    changes = sum(1 for i in range(1, len(shifts)) if shifts[i] != shifts[i-1])

    # Penalty for long periods unless pre-registered
    period = detect_period(shifts)
    period_penalty = 0
    if period and period > 11 and period not in [24, 28]:
        period_penalty = 5

    return distinct + changes * 0.5 + period_penalty

def detect_period(shifts):
    """Detect if shifts have a period"""
    for p in range(2, min(26, len(shifts)//2)):
        if all(shifts[i] == shifts[i % p] for i in range(len(shifts))):
            return p
    return None

class MASSDecoder:
    def __init__(self, ct_text, anchors, schedules):
        self.ct = ct_text
        self.n = len(ct_text)
        self.anchors = anchors  # {(start, end, plaintext), ...}
        self.schedules = schedules

        # Precompute anchor constraints
        self.anchor_constraints = {}
        for start, end, anchor_pt in anchors:
            for i, pt_char in enumerate(anchor_pt):
                self.anchor_constraints[start + i] = pt_char

    def decode_with_schedule(self, schedule_class, alphabet, mapping, n_seeds=16):
        """Decode using a specific schedule class"""

        if schedule_class == "relief_two_lane":
            mask = self.schedules["relief_mask"]
            return self.two_lane_search(mask, alphabet, mapping, n_seeds, "relief")

        elif schedule_class == "wobble_two_lane":
            mask = self.schedules["wobble_mask"]
            return self.two_lane_search(mask, alphabet, mapping, n_seeds, "wobble")

        elif schedule_class == "seam_toggle":
            seams = self.schedules["seam_indices"]
            return self.seam_toggle_search(seams, alphabet, mapping, n_seeds)

        elif schedule_class == "short_period":
            period = self.schedules.get("gap_period", 5)
            return self.periodic_search(period, alphabet, mapping, n_seeds)

        elif schedule_class == "unconstrained":
            return self.unconstrained_search(alphabet, mapping, n_seeds)

        else:
            raise ValueError(f"Unknown schedule class: {schedule_class}")

    def two_lane_search(self, mask, alphabet, mapping, n_seeds, label):
        """Search with two-lane constraint"""
        best_score = -float('inf')
        best_result = None

        decrypt_fn = vigenere_decrypt if mapping == "vigenere" else beaufort_decrypt

        for seed in range(n_seeds):
            # Random initial lane values
            lane0_val = rng.integers(0, 26)
            lane1_val = rng.integers(0, 26)

            # Build shift array
            shifts = np.zeros(self.n, dtype=int)
            for i in range(self.n):
                if i in self.anchor_constraints:
                    # Compute required shift for anchor
                    ct_char = self.ct[i]
                    pt_char = self.anchor_constraints[i]
                    # Find shift that produces pt_char
                    for k in range(26):
                        if decrypt_fn(ct_char, k, alphabet) == pt_char:
                            shifts[i] = k
                            break
                else:
                    shifts[i] = lane1_val if mask[i] else lane0_val

            # Decode
            pt = ''.join(decrypt_fn(self.ct[i], shifts[i], alphabet) for i in range(self.n))

            # Score
            lm_score = simple_lm_score(pt)
            complexity = key_complexity(shifts)
            total_score = lm_score - 0.1 * complexity

            if total_score > best_score:
                best_score = total_score
                best_result = {
                    'pt': pt,
                    'shifts': shifts.tolist(),
                    'score': total_score,
                    'lm_score': lm_score,
                    'complexity': complexity,
                    'lane0': lane0_val,
                    'lane1': lane1_val,
                    'schedule': f"{label}_two_lane"
                }

        return best_result

    def seam_toggle_search(self, seams, alphabet, mapping, n_seeds):
        """Search with mapping toggle at seams"""
        best_score = -float('inf')
        best_result = None

        for seed in range(n_seeds):
            # Random key values
            base_shift = rng.integers(0, 26)

            # Random toggle pattern at seams
            toggles = rng.choice([0, 1], size=len(seams))

            # Build shifts with toggles
            shifts = np.full(self.n, base_shift, dtype=int)
            current_mapping = mapping

            pt_chars = []
            for i in range(self.n):
                if i in self.anchor_constraints:
                    pt_chars.append(self.anchor_constraints[i])
                else:
                    # Check if we toggle at this position
                    if i in seams:
                        seam_idx = seams.index(i)
                        if toggles[seam_idx]:
                            current_mapping = "beaufort" if current_mapping == "vigenere" else "vigenere"

                    decrypt_fn = vigenere_decrypt if current_mapping == "vigenere" else beaufort_decrypt
                    pt_chars.append(decrypt_fn(self.ct[i], shifts[i], alphabet))

            pt = ''.join(pt_chars)

            # Score
            lm_score = simple_lm_score(pt)
            complexity = len(seams) * 0.5  # Penalty for toggles
            total_score = lm_score - 0.1 * complexity

            if total_score > best_score:
                best_score = total_score
                best_result = {
                    'pt': pt,
                    'shifts': shifts.tolist(),
                    'score': total_score,
                    'lm_score': lm_score,
                    'complexity': complexity,
                    'toggles': toggles.tolist(),
                    'schedule': 'seam_toggle'
                }

        return best_result

    def periodic_search(self, period, alphabet, mapping, n_seeds):
        """Search with periodic key"""
        best_score = -float('inf')
        best_result = None

        decrypt_fn = vigenere_decrypt if mapping == "vigenere" else beaufort_decrypt

        for seed in range(n_seeds):
            # Random periodic key
            key_values = rng.integers(0, 26, size=period)

            # Extend to full length
            shifts = np.array([key_values[i % period] for i in range(self.n)])

            # Apply anchor constraints
            for pos, pt_char in self.anchor_constraints.items():
                ct_char = self.ct[pos]
                for k in range(26):
                    if decrypt_fn(ct_char, k, alphabet) == pt_char:
                        shifts[pos] = k
                        # Update periodic key if possible
                        if pos % period < period:
                            key_values[pos % period] = k
                        break

            # Decode
            pt = ''.join(decrypt_fn(self.ct[i], shifts[i], alphabet) for i in range(self.n))

            # Score
            lm_score = simple_lm_score(pt)
            complexity = period  # Simple period penalty
            total_score = lm_score - 0.05 * complexity

            if total_score > best_score:
                best_score = total_score
                best_result = {
                    'pt': pt,
                    'shifts': shifts.tolist(),
                    'score': total_score,
                    'lm_score': lm_score,
                    'complexity': complexity,
                    'period': period,
                    'key': key_values.tolist(),
                    'schedule': f'period_{period}'
                }

        return best_result

    def unconstrained_search(self, alphabet, mapping, n_seeds):
        """Unconstrained search with anchors fixed"""
        best_score = -float('inf')
        best_result = None

        decrypt_fn = vigenere_decrypt if mapping == "vigenere" else beaufort_decrypt

        for seed in range(n_seeds):
            # Start with random shifts
            shifts = rng.integers(0, 26, size=self.n)

            # Apply anchor constraints
            for pos, pt_char in self.anchor_constraints.items():
                ct_char = self.ct[pos]
                for k in range(26):
                    if decrypt_fn(ct_char, k, alphabet) == pt_char:
                        shifts[pos] = k
                        break

            # Hill climb
            for iteration in range(100):
                improved = False
                for i in range(self.n):
                    if i in self.anchor_constraints:
                        continue

                    best_local = shifts[i]
                    best_local_score = -float('inf')

                    for k in range(26):
                        shifts[i] = k
                        pt = ''.join(decrypt_fn(self.ct[j], shifts[j], alphabet) for j in range(self.n))
                        score = simple_lm_score(pt) - 0.1 * key_complexity(shifts)

                        if score > best_local_score:
                            best_local_score = score
                            best_local = k
                            improved = True

                    shifts[i] = best_local

                if not improved:
                    break

            # Final decode and score
            pt = ''.join(decrypt_fn(self.ct[i], shifts[i], alphabet) for i in range(self.n))
            lm_score = simple_lm_score(pt)
            complexity = key_complexity(shifts)
            total_score = lm_score - 0.1 * complexity

            if total_score > best_score:
                best_score = total_score
                best_result = {
                    'pt': pt,
                    'shifts': shifts.tolist(),
                    'score': total_score,
                    'lm_score': lm_score,
                    'complexity': complexity,
                    'schedule': 'unconstrained'
                }

        return best_result

def verify_roundtrip(pt, shifts, ct_expected, alphabet, mapping):
    """Verify PT encrypts back to CT"""
    encrypt_fn = vigenere_encrypt if mapping == "vigenere" else beaufort_encrypt
    ct_result = ''.join(encrypt_fn(pt[i], shifts[i], alphabet) for i in range(len(pt)))
    return ct_result == ct_expected

def main():
    print("="*60)
    print("MASS Decoder for K4")
    print("="*60)
    print(f"Timestamp: {TIMESTAMP}")

    # Load K4 ciphertext
    ct_path = ROOT / "k4_ct.txt"
    ct_text = ct_path.read_text().strip()
    print(f"K4 CT: {ct_text[:50]}...")
    print(f"Length: {len(ct_text)}")

    # Load schedules
    schedules_path = ROOT / "02_exports/schedules_pre_registered.json"
    with open(schedules_path) as f:
        schedules = json.load(f)

    print("\nSchedules loaded:")
    print(f"  Relief mask: {sum(schedules['relief_mask'])} high positions")
    print(f"  Wobble mask: {sum(schedules['wobble_mask'])} on-center positions")
    print(f"  Seam indices: {len(schedules['seam_indices'])} transitions")
    print(f"  Gap period: {schedules.get('gap_period', 'Not found')}")

    # Define anchors (BERLIN at [63:69), CLOCK at [69:74))
    anchors = [
        (63, 69, "BERLIN"),
        (69, 74, "CLOCK")
    ]

    print("\nAnchors:")
    for start, end, text in anchors:
        print(f"  [{start}:{end}): {text}")

    # Initialize decoder
    decoder = MASSDecoder(ct_text, anchors, schedules)

    # Test configurations
    alphabet_configs = [
        ("standard", ALPHA),
        ("kryptos", KRYPTOS)
    ]

    mapping_configs = ["vigenere", "beaufort"]

    schedule_classes = [
        "relief_two_lane",
        "wobble_two_lane",
        "seam_toggle",
        "short_period"
    ]

    # Run searches
    results = []
    output_dir = ROOT / f"runs/k4_mass/{TIMESTAMP}"
    output_dir.mkdir(parents=True, exist_ok=True)

    for schedule_class in schedule_classes:
        print(f"\n{'='*40}")
        print(f"Schedule: {schedule_class}")
        print('='*40)

        for alph_name, alphabet in alphabet_configs:
            for mapping in mapping_configs:
                config_name = f"{schedule_class}_{alph_name}_{mapping}"
                print(f"\nTrying: {config_name}")

                result = decoder.decode_with_schedule(schedule_class, alphabet, mapping, n_seeds=16)

                if result:
                    # Verify roundtrip
                    is_valid = verify_roundtrip(
                        result['pt'],
                        result['shifts'],
                        ct_text,
                        alphabet,
                        mapping
                    )

                    result['config'] = config_name
                    result['alphabet'] = alph_name
                    result['mapping'] = mapping
                    result['valid'] = is_valid

                    results.append(result)

                    print(f"  Score: {result['score']:.4f}")
                    print(f"  PT sample: {result['pt'][:40]}...")
                    print(f"  Valid roundtrip: {is_valid}")

                    if is_valid and "BERLIN" in result['pt'] and "CLOCK" in result['pt']:
                        print("  ✓ Contains anchors!")

    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)

    # Save best result
    if results and results[0]['valid']:
        best = results[0]

        # Save plaintext
        pt_path = output_dir / "pt_best.txt"
        pt_path.write_text(best['pt'])

        # Save shifts
        import pandas as pd
        shifts_df = pd.DataFrame({
            'index': range(len(best['shifts'])),
            'shift': best['shifts'],
            'schedule': best['schedule']
        })
        shifts_df.to_csv(output_dir / "k_best.csv", index=False)

        # Save receipts
        receipts = {
            'timestamp': TIMESTAMP,
            'ct_hash': hashlib.sha256(ct_text.encode()).hexdigest()[:16],
            'schedule_class': best['schedule'],
            'alphabet': best['alphabet'],
            'mapping': best['mapping'],
            'lm_score': best['lm_score'],
            'complexity': best['complexity'],
            'valid_roundtrip': best['valid'],
            'anchors_verified': "BERLIN" in best['pt'] and "CLOCK" in best['pt']
        }

        with open(output_dir / "mass_receipts.json", 'w') as f:
            json.dump(receipts, f, indent=2)

        print("\n" + "="*60)
        print("BEST RESULT")
        print("="*60)
        print(f"Config: {best['config']}")
        print(f"Score: {best['score']:.4f}")
        print(f"Valid: {best['valid']}")
        print(f"\nPlaintext:")
        print(best['pt'])
        print(f"\nSaved to: {output_dir}")
    else:
        print("\n⚠️ No valid solution found with current schedules")
        print("Consider running unconstrained search or adjusting parameters")

if __name__ == "__main__":
    main()