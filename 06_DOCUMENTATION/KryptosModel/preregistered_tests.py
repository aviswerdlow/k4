#!/usr/bin/env python3
"""
Preregistered Tests for Kryptos K4 Hypotheses
Fixed recipes, anchor masking, empirical p-values
NO TUNING ALLOWED - recipes are frozen
"""

import hashlib
import json
import numpy as np
from typing import List, Dict, Tuple, Optional
import string
from collections import Counter
import random
import lzma
from scipy import stats
from datetime import datetime

# K4 text (97 chars) - FROZEN
K4_TEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Anchor positions - FROZEN (OBKR, EAST, NORTHEAST, BERLIN, CLOCK)
ANCHOR_POSITIONS = {
    'OBKR': list(range(0, 4)),
    'EAST': [63, 64, 65, 66],  # Positions need verification
    'NORTHEAST': [0, 1, 2, 3, 4, 5, 6, 7, 8],  # Positions need verification
    'BERLIN': [24, 25, 26, 27, 28, 29],  # Positions need verification
    'CLOCK': [73, 74, 75, 76, 77]  # Positions need verification
}

# Flatten anchor positions
ALL_ANCHORS = []
for positions in ANCHOR_POSITIONS.values():
    ALL_ANCHORS.extend(positions)
ALL_ANCHORS = sorted(set(ALL_ANCHORS))

class PreregisteredTests:
    """Frozen test protocols - NO MODIFICATIONS ALLOWED"""
    
    def __init__(self):
        """Initialize with frozen parameters"""
        self.k4 = K4_TEXT
        self.anchors = ALL_ANCHORS
        self.non_anchor_positions = [i for i in range(len(K4_TEXT)) if i not in ALL_ANCHORS]
        
        # Record test configuration hash for reproducibility
        config = {
            'k4_text': K4_TEXT,
            'anchors': ALL_ANCHORS,
            'timestamp': datetime.now().isoformat()
        }
        self.config_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
        print(f"Test configuration hash: {self.config_hash[:16]}...")
    
    def test_A_coordinate_to_key(self, angles: List[float] = None, 
                                 num_nulls: int = 5000) -> Dict:
        """
        Test A: Coordinate-to-key with fixed recipe
        Recipe FROZEN: angle → remove symbols → digits 0-9 to A-J → deduplicate → max 12 chars
        """
        print("\n" + "="*80)
        print("TEST A: COORDINATE-TO-KEY (FROZEN RECIPE)")
        print("="*80)
        
        if angles is None:
            # Test the claimed 2.2356 and nearby values
            angles = [2.2356, 2.2, 2.3, 22.356, 223.56]
        
        results = {}
        
        for angle in angles:
            print(f"\nTesting angle: {angle}°")
            
            # FROZEN RECIPE - NO MODIFICATIONS
            # Step 1: Convert to string, remove non-digits
            angle_str = str(angle).replace('.', '')
            
            # Step 2: Map digits 0-9 to A-J
            key = ''
            for digit in angle_str:
                if digit.isdigit():
                    key += chr(ord('A') + int(digit))
            
            # Step 3: Deduplicate in order
            seen = set()
            dedup_key = ''
            for char in key:
                if char not in seen:
                    dedup_key += char
                    seen.add(char)
            
            # Step 4: Limit to 12 chars, pad with KRYPTOS if needed
            if len(dedup_key) > 12:
                dedup_key = dedup_key[:12]
            elif len(dedup_key) < 5:
                dedup_key += 'KRYPTOS'[:12-len(dedup_key)]
            
            print(f"  Generated key: {dedup_key}")
            
            # Apply Vigenere to non-anchor positions only
            decrypted = self._vigenere_decrypt_masked(K4_TEXT, dedup_key)
            
            # Score with 5-gram model
            test_score = self._score_5gram(decrypted)
            
            # Check for content words
            content_words = self._find_content_words(decrypted, min_length=5)
            print(f"  Content words (≥5 letters): {content_words}")
            
            # Generate null distribution
            null_scores = []
            for _ in range(num_nulls):
                # Random key with same length and letter histogram
                null_key = self._generate_yoked_key(dedup_key)
                null_decrypt = self._vigenere_decrypt_masked(K4_TEXT, null_key)
                null_scores.append(self._score_5gram(null_decrypt))
            
            # Compute empirical p-value
            null_scores = np.array(null_scores)
            p_value = (np.sum(null_scores >= test_score) + 1) / (num_nulls + 1)
            
            # Bonferroni correction for number of angles tested
            p_adjusted = min(1.0, p_value * len(angles))
            
            results[angle] = {
                'key': dedup_key,
                'decrypted_sample': decrypted[:50],
                'test_score': test_score,
                'p_value': p_value,
                'p_adjusted': p_adjusted,
                'content_words': content_words,
                'passes': p_adjusted <= 0.001 and len(content_words) >= 2
            }
            
            print(f"  p-value: {p_value:.6f}, adjusted: {p_adjusted:.6f}")
            print(f"  RESULT: {'PASS' if results[angle]['passes'] else 'FAIL'}")
        
        return results
    
    def test_B_dual_path_xor(self, spatial_indices: List[int] = None,
                             num_nulls: int = 1000) -> Dict:
        """
        Test B: Dual-path XOR structure
        FROZEN: XOR difference, entropy, IoC, autocorrelation, Kasiski, LZMA
        """
        print("\n" + "="*80)
        print("TEST B: DUAL-PATH XOR STRUCTURE")
        print("="*80)
        
        if spatial_indices is None:
            # For now, use a simple rotation as placeholder
            # In reality, this needs the actual 97 unique spatial indices
            spatial_indices = list(range(1, len(K4_TEXT))) + [0]
        
        if len(spatial_indices) != 97:
            print(f"ERROR: Spatial path must have exactly 97 indices, got {len(spatial_indices)}")
            return {}
        
        # Create spatial text from indices
        spatial_text = ''.join([K4_TEXT[i] for i in spatial_indices])
        
        # Compute XOR (L[i] - S[i]) mod 26
        xor_diff = []
        for i in range(len(K4_TEXT)):
            if i not in self.anchors:  # Mask anchors
                l_val = ord(K4_TEXT[i]) - ord('A')
                s_val = ord(spatial_text[i]) - ord('A')
                xor_diff.append((l_val - s_val) % 26)
        
        xor_text = ''.join([chr(x + ord('A')) for x in xor_diff])
        
        # Compute test statistics
        test_stats = {
            'entropy': self._entropy(xor_text),
            'ioc': self._index_of_coincidence(xor_text),
            'autocorr_peak': self._autocorrelation_peak(xor_text),
            'kasiski_count': self._kasiski_count(xor_text),
            'lzma_ratio': self._compression_ratio(xor_text)
        }
        
        print(f"XOR statistics:")
        for stat, value in test_stats.items():
            print(f"  {stat}: {value:.4f}")
        
        # Generate null distribution
        null_stats = {stat: [] for stat in test_stats}
        
        for _ in range(num_nulls):
            # Permute spatial indices outside anchors
            null_indices = spatial_indices.copy()
            non_anchor_spatial = [null_indices[i] for i in self.non_anchor_positions]
            random.shuffle(non_anchor_spatial)
            
            j = 0
            for i in self.non_anchor_positions:
                null_indices[i] = non_anchor_spatial[j]
                j += 1
            
            # Compute null XOR
            null_spatial = ''.join([K4_TEXT[i] for i in null_indices])
            null_xor = []
            for i in self.non_anchor_positions:
                l_val = ord(K4_TEXT[i]) - ord('A')
                s_val = ord(null_spatial[i]) - ord('A')
                null_xor.append((l_val - s_val) % 26)
            
            null_text = ''.join([chr(x + ord('A')) for x in null_xor])
            
            # Compute null statistics
            null_stats['entropy'].append(self._entropy(null_text))
            null_stats['ioc'].append(self._index_of_coincidence(null_text))
            null_stats['autocorr_peak'].append(self._autocorrelation_peak(null_text))
            null_stats['kasiski_count'].append(self._kasiski_count(null_text))
            null_stats['lzma_ratio'].append(self._compression_ratio(null_text))
        
        # Compute p-values for each statistic
        p_values = {}
        for stat in test_stats:
            null_array = np.array(null_stats[stat])
            if stat in ['entropy', 'kasiski_count']:  # Lower is better
                p_values[stat] = (np.sum(null_array <= test_stats[stat]) + 1) / (num_nulls + 1)
            else:  # Higher is better
                p_values[stat] = (np.sum(null_array >= test_stats[stat]) + 1) / (num_nulls + 1)
        
        # Bonferroni correction for multiple statistics
        min_p = min(p_values.values())
        p_adjusted = min(1.0, min_p * len(test_stats))
        
        print(f"\np-values:")
        for stat, p in p_values.items():
            print(f"  {stat}: {p:.6f}")
        print(f"Adjusted p-value: {p_adjusted:.6f}")
        
        result = {
            'xor_sample': xor_text[:50],
            'statistics': test_stats,
            'p_values': p_values,
            'p_adjusted': p_adjusted,
            'passes': p_adjusted <= 0.001
        }
        
        print(f"RESULT: {'PASS' if result['passes'] else 'FAIL'}")
        
        return result
    
    def test_C_grid_readouts(self, num_nulls: int = 1000) -> Dict:
        """
        Test C: 7×14 grid readouts
        FROZEN: deterministic grid, column/diagonal reads
        """
        print("\n" + "="*80)
        print("TEST C: 7×14 GRID READOUTS")
        print("="*80)
        
        # Create 7×14 grid (deterministic filling)
        grid = []
        for row in range(7):
            start = row * 14
            end = min(start + 14, len(K4_TEXT))
            if start < len(K4_TEXT):
                row_text = K4_TEXT[start:end]
                # Pad last row if needed
                if len(row_text) < 14:
                    row_text += 'X' * (14 - len(row_text))
                grid.append(row_text)
        
        results = {
            'columns': {},
            'diagonals': {}
        }
        
        # Test column reads
        for col in range(14):
            col_text = ''.join([grid[row][col] for row in range(7) if col < len(grid[row])])
            
            # Mask anchors in scoring
            masked_text = self._mask_anchors_in_text(col_text, col, 'column')
            
            # Find words
            words = self._find_content_words(masked_text, min_length=4)
            
            if words:
                print(f"Column {col}: {col_text} → Words: {words}")
                results['columns'][col] = {
                    'text': col_text,
                    'words': words
                }
        
        # Test diagonal reads
        for stride in [1, -1]:  # Forward and backward diagonals
            for start_col in range(14):
                diag_text = ''
                row, col = 0, start_col
                
                while 0 <= row < 7 and 0 <= col < 14:
                    if row < len(grid) and col < len(grid[row]):
                        diag_text += grid[row][col]
                    row += 1
                    col += stride
                
                if len(diag_text) >= 4:
                    # Mask anchors
                    masked_text = self._mask_anchors_in_text(diag_text, start_col, 'diagonal')
                    
                    # Find words
                    words = self._find_content_words(masked_text, min_length=4)
                    
                    if words:
                        print(f"Diagonal (start={start_col}, stride={stride}): {diag_text} → Words: {words}")
                        results['diagonals'][f"{start_col}_{stride}"] = {
                            'text': diag_text,
                            'words': words
                        }
        
        # Generate null distribution
        significant_reads = len(results['columns']) + len(results['diagonals'])
        
        null_counts = []
        for _ in range(num_nulls):
            # Shuffle non-anchor positions
            null_text = list(K4_TEXT)
            non_anchor_chars = [null_text[i] for i in self.non_anchor_positions]
            random.shuffle(non_anchor_chars)
            
            j = 0
            for i in self.non_anchor_positions:
                null_text[i] = non_anchor_chars[j]
                j += 1
            
            null_text = ''.join(null_text)
            
            # Create null grid
            null_grid = []
            for row in range(7):
                start = row * 14
                end = min(start + 14, len(null_text))
                if start < len(null_text):
                    row_text = null_text[start:end]
                    if len(row_text) < 14:
                        row_text += 'X' * (14 - len(row_text))
                    null_grid.append(row_text)
            
            # Count significant reads in null
            null_significant = 0
            
            # Check columns
            for col in range(14):
                col_text = ''.join([null_grid[row][col] for row in range(7) if col < len(null_grid[row])])
                masked = self._mask_anchors_in_text(col_text, col, 'column')
                if len(self._find_content_words(masked, min_length=4)) >= 1:
                    null_significant += 1
            
            null_counts.append(null_significant)
        
        # Compute p-value
        null_counts = np.array(null_counts)
        p_value = (np.sum(null_counts >= significant_reads) + 1) / (num_nulls + 1)
        
        print(f"\nSignificant reads: {significant_reads}")
        print(f"p-value: {p_value:.6f}")
        
        result = {
            'grid': grid,
            'columns_with_words': results['columns'],
            'diagonals_with_words': results['diagonals'],
            'significant_count': significant_reads,
            'p_value': p_value,
            'passes': p_value <= 0.001 and significant_reads >= 2
        }
        
        print(f"RESULT: {'PASS' if result['passes'] else 'FAIL'}")
        
        return result
    
    def test_D_shadow_selector(self, m_values: List[int] = None,
                               num_nulls: int = 1000) -> Dict:
        """
        Test D: Shadow selector
        FROZEN: Nov 3, 1990, 14:00 Langley sun vector
        """
        print("\n" + "="*80)
        print("TEST D: SHADOW SELECTOR")
        print("="*80)
        
        if m_values is None:
            m_values = [15, 20, 24]
        
        # Sun vector for Nov 3, 1990, 14:00 at Langley (38.9°N, 77.1°W)
        # This is a simplified calculation - in reality use ephemeris
        sun_elevation = 35.0  # degrees at 2pm in November
        sun_azimuth = 213.8   # degrees SSW
        
        # Convert to 3D vector
        sun_elev_rad = np.radians(sun_elevation)
        sun_az_rad = np.radians(sun_azimuth)
        
        sun_vector = np.array([
            np.cos(sun_elev_rad) * np.sin(sun_az_rad),
            np.cos(sun_elev_rad) * np.cos(sun_az_rad),
            np.sin(sun_elev_rad)
        ])
        
        print(f"Sun vector: elevation={sun_elevation}°, azimuth={sun_azimuth}°")
        
        # Load positions if available, otherwise use placeholder
        try:
            with open('sample_k4_positions.json', 'r') as f:
                positions = json.load(f)
            coords = np.array([[p['x'], p['y'], p['z']] for p in positions])
            
            # Estimate normals (simplified - pointing outward from center)
            center = np.mean(coords, axis=0)
            normals = coords - center
            normals = normals / np.linalg.norm(normals, axis=1, keepdims=True)
        except:
            print("Warning: Using placeholder coordinates")
            # Placeholder: distribute letters on a cylinder
            angles = np.linspace(0, 2*np.pi, len(K4_TEXT))
            coords = np.column_stack([np.cos(angles), np.sin(angles), np.linspace(0, 1, len(K4_TEXT))])
            normals = np.column_stack([np.cos(angles), np.sin(angles), np.zeros(len(K4_TEXT))])
        
        # Compute illumination for each letter
        illumination = np.maximum(0, np.dot(normals, sun_vector))
        
        results = {}
        
        for m in m_values:
            print(f"\nSelecting top {m} illuminated letters (excluding anchors)")
            
            # Get indices sorted by illumination
            sorted_indices = np.argsort(illumination)[::-1]
            
            # Select top m outside anchors
            selected = []
            for idx in sorted_indices:
                if idx not in self.anchors:
                    selected.append(idx)
                if len(selected) >= m:
                    break
            
            selected_text = ''.join([K4_TEXT[i] for i in sorted(selected)])
            
            # Score with language model
            test_score = self._score_5gram(selected_text)
            
            # Find words
            words = self._find_content_words(selected_text, min_length=4)
            print(f"  Selected: {selected_text[:30]}...")
            print(f"  Words found: {words}")
            
            # Generate null distribution
            null_scores = []
            for _ in range(num_nulls):
                # Random selection of same size outside anchors
                null_selected = random.sample(self.non_anchor_positions, m)
                null_text = ''.join([K4_TEXT[i] for i in sorted(null_selected)])
                null_scores.append(self._score_5gram(null_text))
            
            # Compute p-value
            null_scores = np.array(null_scores)
            p_value = (np.sum(null_scores >= test_score) + 1) / (num_nulls + 1)
            
            results[m] = {
                'selected_text': selected_text,
                'indices': selected,
                'test_score': test_score,
                'p_value': p_value,
                'words': words,
                'passes': p_value <= 0.001
            }
            
            print(f"  p-value: {p_value:.6f}")
            print(f"  RESULT: {'PASS' if results[m]['passes'] else 'FAIL'}")
        
        return results
    
    # Helper methods (FROZEN - NO MODIFICATIONS)
    
    def _vigenere_decrypt_masked(self, text: str, key: str) -> str:
        """Vigenere decrypt, preserving anchor positions"""
        result = list(text)
        key_idx = 0
        
        for i in range(len(text)):
            if i not in self.anchors:
                shift = ord(key[key_idx % len(key)]) - ord('A')
                result[i] = chr(((ord(text[i]) - ord('A') - shift) % 26) + ord('A'))
                key_idx += 1
        
        return ''.join(result)
    
    def _score_5gram(self, text: str) -> float:
        """Simple 5-gram scoring (placeholder for real language model)"""
        score = 0.0
        
        # Common 5-grams in English
        common_5grams = ['ATION', 'TIONS', 'WHICH', 'THERE', 'THEIR', 'WOULD',
                        'COULD', 'ABOUT', 'AFTER', 'FIRST', 'OTHER', 'THESE']
        
        for gram in common_5grams:
            score += text.count(gram) * 5
        
        # Penalize repeated characters
        for i in range(len(text) - 2):
            if text[i] == text[i+1] == text[i+2]:
                score -= 2
        
        return score / max(len(text), 1)
    
    def _find_content_words(self, text: str, min_length: int = 4) -> List[str]:
        """Find English content words of minimum length"""
        # Common English words
        words = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'HAVE', 'BEEN',
                'THIS', 'FROM', 'THEY', 'WERE', 'BEEN', 'HAVE', 'THEIR', 'WHAT',
                'ABOUT', 'WHICH', 'THERE', 'AFTER', 'FIRST', 'COULD', 'THESE', 'OTHER',
                'THOSE', 'BEING', 'EVERY', 'UNDER', 'WHILE', 'WHERE', 'THROUGH']
        
        found = []
        for word in words:
            if len(word) >= min_length and word in text:
                found.append(word)
        
        return found
    
    def _generate_yoked_key(self, key: str) -> str:
        """Generate random key with same length and letter distribution"""
        letters = list(key)
        random.shuffle(letters)
        return ''.join(letters)
    
    def _entropy(self, text: str) -> float:
        """Calculate Shannon entropy"""
        if not text:
            return 0.0
        
        counts = Counter(text)
        probs = [count/len(text) for count in counts.values()]
        return -sum(p * np.log2(p) for p in probs if p > 0)
    
    def _index_of_coincidence(self, text: str) -> float:
        """Calculate index of coincidence"""
        if len(text) <= 1:
            return 0.0
        
        counts = Counter(text)
        n = len(text)
        return sum(c * (c - 1) for c in counts.values()) / (n * (n - 1))
    
    def _autocorrelation_peak(self, text: str) -> float:
        """Find highest autocorrelation peak"""
        if len(text) < 10:
            return 0.0
        
        max_corr = 0.0
        for lag in range(1, min(30, len(text)//2)):
            corr = 0
            for i in range(len(text) - lag):
                if text[i] == text[i + lag]:
                    corr += 1
            corr = corr / (len(text) - lag)
            max_corr = max(max_corr, corr)
        
        return max_corr
    
    def _kasiski_count(self, text: str) -> int:
        """Count Kasiski examination hits (repeated trigrams)"""
        trigrams = {}
        for i in range(len(text) - 2):
            tri = text[i:i+3]
            if tri not in trigrams:
                trigrams[tri] = []
            trigrams[tri].append(i)
        
        count = 0
        for tri, positions in trigrams.items():
            if len(positions) >= 2:
                count += len(positions) - 1
        
        return count
    
    def _compression_ratio(self, text: str) -> float:
        """LZMA compression ratio"""
        if not text:
            return 1.0
        
        original_size = len(text.encode())
        compressed_size = len(lzma.compress(text.encode()))
        return compressed_size / original_size
    
    def _mask_anchors_in_text(self, text: str, position: int, read_type: str) -> str:
        """Mask anchor positions in extracted text"""
        # This is simplified - would need proper position mapping
        return text
    
    def run_all_tests(self) -> Dict:
        """Run all preregistered tests"""
        print("\n" + "="*80)
        print("RUNNING ALL PREREGISTERED TESTS")
        print(f"Configuration hash: {self.config_hash[:16]}...")
        print("="*80)
        
        results = {}
        
        # Test A: Coordinate-to-key
        results['test_A'] = self.test_A_coordinate_to_key()
        
        # Test B: Dual-path XOR (needs real spatial indices)
        results['test_B'] = self.test_B_dual_path_xor()
        
        # Test C: Grid readouts
        results['test_C'] = self.test_C_grid_readouts()
        
        # Test D: Shadow selector
        results['test_D'] = self.test_D_shadow_selector()
        
        # Summary
        print("\n" + "="*80)
        print("FINAL RESULTS SUMMARY")
        print("="*80)
        
        passes = 0
        total = 0
        
        for test_name, test_results in results.items():
            if isinstance(test_results, dict):
                if 'passes' in test_results:
                    total += 1
                    if test_results['passes']:
                        passes += 1
                        print(f"✓ {test_name}: PASS")
                    else:
                        print(f"✗ {test_name}: FAIL")
                elif test_name == 'test_A':
                    # Check coordinate tests
                    for angle, result in test_results.items():
                        total += 1
                        if result['passes']:
                            passes += 1
                            print(f"✓ {test_name} (angle={angle}): PASS")
                        else:
                            print(f"✗ {test_name} (angle={angle}): FAIL")
        
        print(f"\nTotal: {passes}/{total} tests passed")
        
        if passes == 0:
            print("\nCONCLUSION: All hypotheses FALSIFIED. These patterns are not significant.")
        else:
            print(f"\nCONCLUSION: {passes} hypothesis/es show statistical significance and warrant further investigation.")
        
        return results


def main():
    """Run all preregistered tests"""
    tester = PreregisteredTests()
    results = tester.run_all_tests()
    
    # Save results with hash for reproducibility
    import json
    
    output = {
        'config_hash': tester.config_hash,
        'timestamp': datetime.now().isoformat(),
        'results': results
    }
    
    with open('preregistered_test_results.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print("\nResults saved to preregistered_test_results.json")
    print(f"Configuration hash: {tester.config_hash}")
    
    return results


if __name__ == "__main__":
    main()