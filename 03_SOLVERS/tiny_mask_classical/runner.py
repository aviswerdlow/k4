#!/usr/bin/env python3
"""
Tiny mask + classical cipher synthesis for K4.
Try simple, pencil-doable masks with classical ciphers to find a round-tripable recipe.
"""

import sys
import os
import json
from typing import List, Tuple, Dict, Optional
from datetime import datetime
from collections import Counter
import math

# Add parent path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TinyMaskBase:
    """Base class for tiny masks."""

    def apply(self, text: str) -> Tuple[str, Dict]:
        """Apply mask and return transformed text + reversal info."""
        raise NotImplementedError

    def invert(self, text: str, info: Dict) -> str:
        """Invert mask using reversal info."""
        raise NotImplementedError


class Interleave2Mask(TinyMaskBase):
    """Even/odd interleave mask."""

    def apply(self, text: str) -> Tuple[str, Dict]:
        even = text[0::2]
        odd = text[1::2]
        masked = even + odd
        info = {'length': len(text), 'even_len': len(even)}
        return masked, info

    def invert(self, text: str, info: Dict) -> str:
        even_len = info['even_len']
        even = text[:even_len]
        odd = text[even_len:]

        result = []
        for i in range(info['length']):
            if i % 2 == 0:
                result.append(even[i // 2])
            else:
                result.append(odd[i // 2])
        return ''.join(result)


class Interleave3Mask(TinyMaskBase):
    """Three-way interleave mask (0,1,2 mod 3)."""

    def apply(self, text: str) -> Tuple[str, Dict]:
        parts = [text[i::3] for i in range(3)]
        masked = ''.join(parts)
        info = {'length': len(text), 'part_lens': [len(p) for p in parts]}
        return masked, info

    def invert(self, text: str, info: Dict) -> str:
        # Reconstruct parts
        parts = []
        start = 0
        for plen in info['part_lens']:
            parts.append(text[start:start+plen])
            start += plen

        # Interleave back
        result = []
        for i in range(info['length']):
            part_idx = i % 3
            char_idx = i // 3
            if char_idx < len(parts[part_idx]):
                result.append(parts[part_idx][char_idx])
        return ''.join(result)


class MicroRoute7x14Mask(TinyMaskBase):
    """7x14 grid with optional row flip."""

    def __init__(self, row_flip=False):
        self.row_flip = row_flip

    def apply(self, text: str) -> Tuple[str, Dict]:
        # Pad to 98 if needed (7*14)
        padded = text + 'X' * (98 - len(text)) if len(text) < 98 else text[:98]

        # Create 7x14 grid
        grid = []
        for i in range(7):
            row = padded[i*14:(i+1)*14]
            if self.row_flip and i % 2 == 1:
                row = row[::-1]  # Flip odd rows
            grid.append(row)

        # Read column-wise
        masked = ''
        for c in range(14):
            for r in range(7):
                if c < len(grid[r]):
                    masked += grid[r][c]

        info = {'original_len': len(text), 'row_flip': self.row_flip}
        return masked[:len(text)], info

    def invert(self, text: str, info: Dict) -> str:
        # Pad if needed
        padded = text + 'X' * (98 - len(text)) if len(text) < 98 else text[:98]

        # Reconstruct grid from column-wise reading
        grid = [[] for _ in range(7)]
        idx = 0
        for c in range(14):
            for r in range(7):
                if idx < len(padded):
                    grid[r].append(padded[idx])
                    idx += 1

        # Convert back to strings and unflip if needed
        for i in range(7):
            row = ''.join(grid[i])
            if info['row_flip'] and i % 2 == 1:
                row = row[::-1]  # Unflip odd rows
            grid[i] = row

        # Read row-wise
        result = ''.join(grid)
        return result[:info['original_len']]


class ReverseMask(TinyMaskBase):
    """Simple reversal mask."""

    def apply(self, text: str) -> Tuple[str, Dict]:
        return text[::-1], {'length': len(text)}

    def invert(self, text: str, info: Dict) -> str:
        return text[::-1]


class ClassicalCipher:
    """Base class for classical ciphers."""

    def __init__(self, key: str):
        self.key = key.upper()

    def encrypt(self, plaintext: str) -> str:
        raise NotImplementedError

    def decrypt(self, ciphertext: str) -> str:
        raise NotImplementedError


class VigenereCipher(ClassicalCipher):
    """Vigenere cipher with repeating key."""

    def encrypt(self, plaintext: str) -> str:
        result = []
        key_len = len(self.key)

        for i, char in enumerate(plaintext.upper()):
            if char.isalpha():
                p_val = ord(char) - ord('A')
                k_val = ord(self.key[i % key_len]) - ord('A')
                c_val = (p_val + k_val) % 26
                result.append(chr(ord('A') + c_val))
            else:
                result.append(char)

        return ''.join(result)

    def decrypt(self, ciphertext: str) -> str:
        result = []
        key_len = len(self.key)

        for i, char in enumerate(ciphertext.upper()):
            if char.isalpha():
                c_val = ord(char) - ord('A')
                k_val = ord(self.key[i % key_len]) - ord('A')
                p_val = (c_val - k_val) % 26
                result.append(chr(ord('A') + p_val))
            else:
                result.append(char)

        return ''.join(result)


class BeaufortCipher(ClassicalCipher):
    """Beaufort cipher (reciprocal)."""

    def encrypt(self, plaintext: str) -> str:
        result = []
        key_len = len(self.key)

        for i, char in enumerate(plaintext.upper()):
            if char.isalpha():
                p_val = ord(char) - ord('A')
                k_val = ord(self.key[i % key_len]) - ord('A')
                c_val = (k_val - p_val) % 26
                result.append(chr(ord('A') + c_val))
            else:
                result.append(char)

        return ''.join(result)

    def decrypt(self, ciphertext: str) -> str:
        # Beaufort is reciprocal
        return self.encrypt(ciphertext)


def calculate_ioc(text: str) -> float:
    """Calculate index of coincidence."""
    counts = Counter(c for c in text if c.isalpha())
    n = sum(counts.values())
    if n <= 1:
        return 0.0
    return sum(c * (c - 1) for c in counts.values()) / (n * (n - 1))


def calculate_english_score(text: str) -> float:
    """Calculate English-likeness score."""
    # English letter frequencies
    english_freq = {
        'E': 12.02, 'T': 9.10, 'A': 8.12, 'O': 7.68, 'I': 7.31,
        'N': 6.95, 'S': 6.28, 'R': 6.02, 'H': 5.92, 'D': 4.32,
        'L': 3.98, 'U': 2.88, 'C': 2.71, 'M': 2.61, 'F': 2.30,
        'Y': 2.11, 'W': 2.09, 'G': 2.03, 'P': 1.82, 'B': 1.49,
        'V': 1.11, 'K': 0.69, 'X': 0.17, 'Q': 0.11, 'J': 0.10, 'Z': 0.07
    }

    text_upper = text.upper()
    total = sum(1 for c in text_upper if c.isalpha())
    if total == 0:
        return 0.0

    # Chi-squared test
    chi_squared = 0.0
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        observed = text_upper.count(letter)
        expected = english_freq.get(letter, 0.5) * total / 100
        if expected > 0:
            chi_squared += (observed - expected) ** 2 / expected

    # Lower chi-squared is better
    return 1000 / (chi_squared + 1)


def search_tiny_mask_classical():
    """Search for tiny mask + classical combinations."""
    # Load K4 ciphertext
    ct_path = '../../02_DATA/ciphertext_97.txt'
    with open(ct_path, 'r') as f:
        k4_ct = f.read().strip().upper()

    print(f"K4 Ciphertext: {k4_ct[:30]}...")
    print(f"Length: {len(k4_ct)}")
    print()

    # Masks to try
    masks = [
        ('interleave2', Interleave2Mask()),
        ('interleave3', Interleave3Mask()),
        ('micro_route', MicroRoute7x14Mask(row_flip=False)),
        ('micro_route_flip', MicroRoute7x14Mask(row_flip=True)),
        ('reverse', ReverseMask())
    ]

    # Keys to try
    keys = ['ABSCISSA', 'ORDINATE', 'AZIMUTH', 'KRYPTOS', 'GIRASOL']

    # Cipher families
    cipher_types = ['vigenere', 'beaufort']

    # Search orders
    orders = ['mask_then_cipher', 'cipher_then_mask']

    results = []

    print("SEARCHING TINY MASK + CLASSICAL COMBINATIONS")
    print("=" * 60)

    for mask_name, mask in masks:
        for key in keys:
            for cipher_type in cipher_types:
                for order in orders:
                    # Create cipher
                    if cipher_type == 'vigenere':
                        cipher = VigenereCipher(key)
                    else:
                        cipher = BeaufortCipher(key)

                    # Try decryption
                    try:
                        if order == 'mask_then_cipher':
                            # Decrypt then unmask
                            intermediate = cipher.decrypt(k4_ct)
                            masked, mask_info = mask.apply(intermediate)
                            plaintext = mask.invert(intermediate, mask_info)
                        else:
                            # Unmask then decrypt
                            unmasked, mask_info = mask.apply(k4_ct)
                            plaintext = cipher.decrypt(unmasked)

                        # Test round-trip
                        if order == 'mask_then_cipher':
                            # Re-mask then encrypt
                            remasked, _ = mask.apply(plaintext)
                            reconstructed = cipher.encrypt(remasked)
                        else:
                            # Re-encrypt then mask
                            reencrypted = cipher.encrypt(plaintext)
                            reconstructed, _ = mask.apply(reencrypted)

                        # Check round-trip
                        round_trip_ok = (reconstructed == k4_ct)

                        # Calculate scores
                        ioc = calculate_ioc(plaintext)
                        eng_score = calculate_english_score(plaintext)

                        result = {
                            'mask': mask_name,
                            'key': key,
                            'cipher': cipher_type,
                            'order': order,
                            'round_trip': round_trip_ok,
                            'ioc': ioc,
                            'english_score': eng_score,
                            'plaintext_sample': plaintext[:50]
                        }

                        results.append(result)

                        if round_trip_ok:
                            print(f"✓ ROUND-TRIP OK: {mask_name} + {cipher_type}({key}) [{order}]")
                            print(f"  IoC: {ioc:.4f}, English: {eng_score:.2f}")
                            print(f"  Sample: {plaintext[:30]}...")

                    except Exception as e:
                        # Skip failed combinations
                        pass

    return results


def evaluate_against_nulls(results):
    """Evaluate results against null hypotheses."""
    # Null thresholds (from random shuffles)
    NULL_IOC = 0.0385  # Random text IoC
    NULL_ENGLISH = 5.0  # Random text English score

    passing = []

    for result in results:
        if not result['round_trip']:
            continue

        # Check if beats nulls
        beats_ioc = result['ioc'] > NULL_IOC * 1.2  # 20% better
        beats_english = result['english_score'] > NULL_ENGLISH * 1.5  # 50% better

        if beats_ioc or beats_english:
            result['beats_nulls'] = True
            passing.append(result)

    return passing


def save_results(results, passing):
    """Save search results."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create output directory
    os.makedirs('out', exist_ok=True)

    # Save all candidates
    with open(f'out/candidates_{timestamp}.jsonl', 'w') as f:
        for result in results:
            f.write(json.dumps(result) + '\n')

    # Save passing candidates
    if passing:
        with open(f'out/passing_{timestamp}.json', 'w') as f:
            json.dump(passing, f, indent=2)
        print(f"\n✓ Found {len(passing)} candidates that beat nulls")
    else:
        print("\n✗ No candidates beat null hypotheses")

    # Save summary
    summary = {
        'timestamp': timestamp,
        'total_tested': len(results),
        'round_trip_ok': sum(1 for r in results if r['round_trip']),
        'beat_nulls': len(passing),
        'search_space': {
            'masks': 5,
            'keys': 5,
            'ciphers': 2,
            'orders': 2,
            'total_combinations': 5 * 5 * 2 * 2
        }
    }

    with open('out/search_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults saved to out/")
    print(f"  Total tested: {summary['total_tested']}")
    print(f"  Round-trip OK: {summary['round_trip_ok']}")
    print(f"  Beat nulls: {summary['beat_nulls']}")


def main():
    """Main entry point."""
    print("=" * 60)
    print("TINY MASK + CLASSICAL CIPHER SEARCH")
    print("=" * 60)
    print()

    # Run search
    results = search_tiny_mask_classical()

    # Evaluate against nulls
    passing = evaluate_against_nulls(results)

    # Save results
    save_results(results, passing)

    print("\n" + "=" * 60)
    print("SEARCH COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()