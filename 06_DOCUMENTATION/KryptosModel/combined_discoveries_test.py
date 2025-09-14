#!/usr/bin/env python3
"""
Combined Discoveries Test - Pursuing the most promising geometric findings
Focus on function words, XOR patterns, and coordinate interpretations
"""

import json
import numpy as np
from typing import List, Dict, Tuple
import string
from collections import Counter
import itertools

# K4 text (97 chars)
K4_TEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Row-extracted text from 3D structure
ROW_TEXT = "SBLUHGOXOURKBOPQQVRLFWBBFILOQJSQTWTOSSKGNRDULKJTAWZZKESSITTPMVNBYAWFNIDPFWGKZTXKDCJDIGAUUHUKEKCAR"

# XOR result between linear and row texts
XOR_RESULT = "PKLQRBPPBRQLKPSORKCZRRZCKROSUPEQYLRRLYQEPUFNKKCPJJXHWZPLOXMTZXZXXQNOFKFYNZQERCSUGCYEUCYQTYCDQCKHT"

class CombinedDiscoveriesTest:
    """Test framework for combining geometric discoveries"""
    
    def __init__(self, positions_file: str = "sample_k4_positions.json"):
        """Initialize with 3D positions and discovered patterns"""
        with open(positions_file, 'r') as f:
            self.positions = json.load(f)
        
        self.coords = np.array([[p['x'], p['y'], p['z']] for p in self.positions])
        self.letters = [p['char'] for p in self.positions]
        
        # Function words discovered
        self.linear_words = ["AND", "NOW"]
        self.spatial_words = ["BUT", "WHO"]
        self.column_words = ["WHO"]
        
        # Key length from anchor vector
        self.key_length = 22
        self.coordinate_key = 2.2356
        
    def analyze_function_word_combinations(self) -> Dict:
        """Test combinations of discovered function words"""
        print("\n[1] FUNCTION WORD COMBINATIONS")
        print("=" * 60)
        
        all_words = self.linear_words + self.spatial_words
        unique_words = list(set(all_words))
        
        results = {
            'phrases': [],
            'patterns': []
        }
        
        # Test different phrase combinations
        phrases = [
            " ".join(["AND", "NOW", "WHO", "BUT"]),
            " ".join(["WHO", "AND", "NOW", "BUT"]),
            " ".join(["NOW", "WHO", "BUT", "AND"]),
            " ".join(["BUT", "WHO", "AND", "NOW"])
        ]
        
        for phrase in phrases:
            print(f"Testing phrase: '{phrase}'")
            
            # Check if it could be an instruction or key phrase
            if "WHO" in phrase and "NOW" in phrase:
                results['phrases'].append({
                    'phrase': phrase,
                    'type': 'question/instruction',
                    'significance': 'Possible query about timing or identity'
                })
            
            # Test as potential cipher key
            key = phrase.replace(" ", "")
            test_decrypt = self._apply_key_to_text(K4_TEXT, key)
            if self._check_for_words(test_decrypt):
                results['phrases'].append({
                    'phrase': phrase,
                    'type': 'cipher_key',
                    'decryption': test_decrypt[:50]
                })
        
        # Check for acrostic patterns
        initials = "".join([w[0] for w in unique_words])  # ANBW or similar
        print(f"\nAcrostic: {initials}")
        results['patterns'].append({
            'type': 'acrostic',
            'value': initials,
            'words': unique_words
        })
        
        return results
    
    def analyze_xor_patterns(self) -> Dict:
        """Analyze the XOR result for structured patterns"""
        print("\n[2] XOR PATTERN ANALYSIS")
        print("=" * 60)
        
        results = {
            'repetitions': [],
            'intervals': [],
            'structured_reads': []
        }
        
        # Find repetition patterns in XOR
        repetitions = [
            ("RBPP", XOR_RESULT.find("RBPP")),
            ("RQLK", XOR_RESULT.find("RQLK")),
            ("CZRR", XOR_RESULT.find("CZRR")),
            ("YLRR", XOR_RESULT.find("YLRR")),
            ("QE", [i for i in range(len(XOR_RESULT)-1) if XOR_RESULT[i:i+2] == "QE"])
        ]
        
        print("Repetition patterns found:")
        for pattern, pos in repetitions:
            if isinstance(pos, list):
                if len(pos) > 1:
                    intervals = [pos[i+1] - pos[i] for i in range(len(pos)-1)]
                    print(f"  {pattern}: positions {pos[:5]}..., intervals: {intervals[:5]}")
                    results['repetitions'].append({
                        'pattern': pattern,
                        'positions': pos,
                        'intervals': intervals
                    })
            elif pos >= 0:
                print(f"  {pattern}: position {pos}")
                results['repetitions'].append({
                    'pattern': pattern,
                    'position': pos
                })
        
        # Test reading at repetition intervals
        test_intervals = [5, 7, 11, 13, 17, 19, 22]
        
        for interval in test_intervals:
            extracted = XOR_RESULT[::interval]
            if len(extracted) > 3:
                score = self._english_score(extracted)
                if score > 0:
                    print(f"\nInterval {interval}: {extracted[:20]}... (score: {score:.2f})")
                    results['intervals'].append({
                        'interval': interval,
                        'text': extracted,
                        'score': score
                    })
        
        # Look for structured segments
        segment_length = 14  # Based on 7×14 grid
        for start in range(segment_length):
            segment = XOR_RESULT[start::segment_length]
            if self._has_structure(segment):
                results['structured_reads'].append({
                    'start': start,
                    'segment_length': segment_length,
                    'text': segment[:30],
                    'structure_type': 'periodic'
                })
        
        return results
    
    def test_shadow_selection(self) -> Dict:
        """Test shadow-based letter selection at dedication time"""
        print("\n[3] SHADOW-BASED SELECTION")
        print("=" * 60)
        
        # Dedication: Nov 3, 1990, 38.9°N, 77.1°W
        # Shadow angle at dedication time: 213.8°
        shadow_angle = 213.8
        
        results = {
            'shadow_paths': [],
            'grid_reads': [],
            'angular_selections': []
        }
        
        # Convert angle to radians
        angle_rad = np.radians(shadow_angle)
        
        # Project shadow direction onto x-z plane
        shadow_dir = np.array([np.cos(angle_rad), 0, np.sin(angle_rad)])
        
        # Project all positions onto shadow direction
        projections = np.dot(self.coords, shadow_dir)
        
        # Sort by projection to get shadow ordering
        shadow_order = np.argsort(projections)
        
        # Test different shadow-based selections
        
        # 1. Every 21st letter along shadow
        shadow_21 = shadow_order[::21]
        text_21 = ''.join([self.letters[i] for i in shadow_21])
        print(f"Every 21st along shadow: {text_21}")
        results['shadow_paths'].append({
            'method': 'every_21st',
            'angle': shadow_angle,
            'text': text_21
        })
        
        # 2. Letters where shadow crosses grid lines (7×14)
        grid_crossings = self._find_grid_crossings(shadow_order, 7, 14)
        if grid_crossings:
            crossing_text = ''.join([self.letters[i] for i in grid_crossings[:20]])
            print(f"Grid crossings: {crossing_text}")
            results['grid_reads'].append({
                'method': 'grid_crossings',
                'text': crossing_text
            })
        
        # 3. Select at angular intervals matching coordinate
        angular_step = self.coordinate_key  # 2.2356 degrees
        selected_angles = []
        current_angle = 0
        
        while current_angle < 360:
            # Find letter closest to this angle
            target_angle_rad = np.radians(current_angle)
            target_dir = np.array([np.cos(target_angle_rad), 0, np.sin(target_angle_rad)])
            
            # Project positions onto this direction
            angle_projections = np.dot(self.coords, target_dir)
            closest_idx = np.argmax(angle_projections)
            selected_angles.append(closest_idx)
            
            current_angle += angular_step
        
        angular_text = ''.join([self.letters[i] for i in selected_angles[:30]])
        print(f"Angular selection (step={angular_step}°): {angular_text[:30]}...")
        results['angular_selections'].append({
            'step': angular_step,
            'text': angular_text
        })
        
        return results
    
    def test_coordinate_interpretations(self) -> Dict:
        """Test different interpretations of the 2.2356 coordinate"""
        print("\n[4] COORDINATE INTERPRETATIONS")
        print("=" * 60)
        
        coord = self.coordinate_key  # 2.2356
        
        results = {
            'decimal_degrees': [],
            'time_based': [],
            'mathematical': [],
            'grid_based': []
        }
        
        # 1. As decimal degrees
        print(f"Testing {coord}° as rotation/selection angle...")
        
        # Rotate text by this angle (in character positions)
        rotation = int(coord * len(K4_TEXT) / 360)
        rotated = K4_TEXT[rotation:] + K4_TEXT[:rotation]
        print(f"Rotated by {rotation} positions: {rotated[:30]}...")
        results['decimal_degrees'].append({
            'rotation': rotation,
            'text': rotated
        })
        
        # 2. As time (2:23:56)
        hours, remainder = divmod(coord * 3600, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        print(f"\nAs time: {time_str}")
        
        # Use as offset pattern
        time_offsets = [2, 23, 56]
        time_selected = []
        pos = 0
        for i, offset in enumerate(itertools.cycle(time_offsets)):
            if pos >= len(K4_TEXT):
                break
            time_selected.append(K4_TEXT[pos])
            pos += offset
            if len(time_selected) >= 30:
                break
        
        time_text = ''.join(time_selected)
        print(f"Time-based selection: {time_text}")
        results['time_based'].append({
            'time': time_str,
            'pattern': time_offsets,
            'text': time_text
        })
        
        # 3. As mathematical constant
        # 2.2356 ≈ √5 = 2.236...
        sqrt5 = np.sqrt(5)
        phi = (1 + sqrt5) / 2  # Golden ratio
        
        print(f"\nMathematical relationships:")
        print(f"  {coord} ≈ √5 = {sqrt5:.4f}")
        print(f"  Related to φ = {phi:.4f}")
        
        # Use golden ratio for selection
        golden_positions = []
        pos = 0
        for i in range(20):
            pos = int(pos + phi * 5) % len(K4_TEXT)
            golden_positions.append(pos)
        
        golden_text = ''.join([K4_TEXT[p] for p in golden_positions])
        print(f"Golden ratio selection: {golden_text}")
        results['mathematical'].append({
            'constant': 'sqrt(5)',
            'value': sqrt5,
            'text': golden_text
        })
        
        # 4. As grid coordinate (row 2, column 23-24)
        row = int(coord)  # 2
        col_start = int((coord - row) * 100)  # 23
        
        # Map to 7×14 grid
        if row < 7 and col_start < 14:
            grid_pos = row * 14 + col_start
            if grid_pos < len(K4_TEXT):
                grid_selection = K4_TEXT[grid_pos::7]  # Every 7th from this position
                print(f"\nGrid position ({row}, {col_start}): {grid_selection[:20]}...")
                results['grid_based'].append({
                    'row': row,
                    'column': col_start,
                    'text': grid_selection
                })
        
        return results
    
    def test_98_character_significance(self) -> Dict:
        """Test the significance of the 98-character spatial path (K4 + 1)"""
        print("\n[5] 98-CHARACTER PATH ANALYSIS")
        print("=" * 60)
        
        results = {
            'padding_tests': [],
            'delimiter_tests': [],
            'coordinate_notations': []
        }
        
        # The spatial path has 98 characters (K4 + 1)
        # This could indicate:
        
        # 1. A null character or padding
        test_texts = [
            K4_TEXT + " ",  # Space padding
            K4_TEXT + "X",  # X as null
            K4_TEXT + "Q",  # Q as null (common in cryptography)
            " " + K4_TEXT,  # Leading padding
        ]
        
        for i, test in enumerate(test_texts):
            if len(test) == 98:
                # Try 7×14 grid arrangement
                grid = []
                for row in range(7):
                    grid.append(test[row*14:(row+1)*14])
                
                # Check for patterns in grid
                diagonals = self._extract_diagonals(grid)
                for diag in diagonals:
                    if self._check_for_words(diag):
                        print(f"Padding test {i}: Found pattern in diagonal: {diag}")
                        results['padding_tests'].append({
                            'type': f'padding_{i}',
                            'diagonal': diag
                        })
        
        # 2. As delimiter between two 49-character messages
        if len(K4_TEXT) >= 98:
            first_49 = K4_TEXT[:49]
            second_49 = K4_TEXT[49:98] if len(K4_TEXT) >= 98 else K4_TEXT[49:] + "X" * (98 - len(K4_TEXT))
            
            print(f"\nTwo 49-char segments:")
            print(f"  First:  {first_49}")
            print(f"  Second: {second_49}")
            
            # Check if they relate
            xor_49 = ''.join([chr(ord(a) ^ ord(b)) for a, b in zip(first_49, second_49)])
            if self._has_structure(xor_49):
                results['delimiter_tests'].append({
                    'type': '49+49',
                    'xor': xor_49[:20],
                    'structure': True
                })
        
        # 3. As coordinate notation (98 = 2×49 or 7×14)
        coordinates = [
            (7, 14),  # Grid dimensions
            (2, 49),  # Two halves
            (98, 1),  # Linear
        ]
        
        for rows, cols in coordinates:
            if rows * cols == 98:
                print(f"\nCoordinate system {rows}×{cols}:")
                # Test reading pattern
                for r in range(min(3, rows)):
                    row_text = K4_TEXT[r*cols:(r+1)*cols] if r*cols < len(K4_TEXT) else ""
                    if row_text:
                        print(f"  Row {r}: {row_text[:20]}...")
                        if self._check_for_words(row_text):
                            results['coordinate_notations'].append({
                                'system': f'{rows}x{cols}',
                                'row': r,
                                'text': row_text
                            })
        
        return results
    
    def combine_paths_for_solution(self) -> Dict:
        """Attempt to combine linear and spatial paths for complete solution"""
        print("\n[6] COMBINED PATH ANALYSIS")
        print("=" * 60)
        
        results = {
            'interleaved': [],
            'key_plaintext': [],
            'modular': []
        }
        
        # 1. Interleave the two paths
        interleaved = ""
        for i in range(min(len(K4_TEXT), len(ROW_TEXT))):
            interleaved += K4_TEXT[i] + ROW_TEXT[i]
        
        print(f"Interleaved: {interleaved[:40]}...")
        results['interleaved'].append({
            'method': 'alternating',
            'text': interleaved
        })
        
        # 2. Use one as key, other as ciphertext
        # Try ROW_TEXT as key for K4_TEXT
        key = ROW_TEXT[:self.key_length]  # Use first 22 chars as key
        decrypted = self._vigenere_decrypt(K4_TEXT, key)
        print(f"\nUsing spatial as key: {decrypted[:40]}...")
        if self._check_for_words(decrypted):
            results['key_plaintext'].append({
                'key_source': 'spatial',
                'text': decrypted,
                'words_found': True
            })
        
        # Try K4_TEXT as key for ROW_TEXT
        key = K4_TEXT[:self.key_length]
        decrypted = self._vigenere_decrypt(ROW_TEXT, key)
        print(f"Using linear as key: {decrypted[:40]}...")
        if self._check_for_words(decrypted):
            results['key_plaintext'].append({
                'key_source': 'linear',
                'text': decrypted,
                'words_found': True
            })
        
        # 3. Modular arithmetic combination
        combined = ""
        for i in range(min(len(K4_TEXT), len(ROW_TEXT))):
            c1 = ord(K4_TEXT[i]) - ord('A')
            c2 = ord(ROW_TEXT[i]) - ord('A')
            # Various operations
            combined += chr(((c1 + c2) % 26) + ord('A'))
        
        print(f"\nModular sum: {combined[:40]}...")
        if self._check_for_words(combined):
            results['modular'].append({
                'operation': 'sum',
                'text': combined
            })
        
        return results
    
    # Helper methods
    def _apply_key_to_text(self, text: str, key: str) -> str:
        """Apply key to text using Vigenere cipher"""
        if not key:
            return text
        
        result = []
        key = key.upper().replace(" ", "")
        key_index = 0
        
        for char in text:
            if char.isalpha():
                shift = ord(key[key_index % len(key)]) - ord('A')
                decoded = chr(((ord(char) - ord('A') - shift) % 26) + ord('A'))
                result.append(decoded)
                key_index += 1
            else:
                result.append(char)
        
        return ''.join(result)
    
    def _vigenere_decrypt(self, ciphertext: str, key: str) -> str:
        """Vigenere decryption"""
        return self._apply_key_to_text(ciphertext, key)
    
    def _check_for_words(self, text: str) -> bool:
        """Check if text contains common English words"""
        common_words = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'WITH',
                       'HAVE', 'THIS', 'FROM', 'THAT', 'WHAT', 'WHEN', 'WHO']
        text = text.upper()
        return any(word in text for word in common_words)
    
    def _english_score(self, text: str) -> float:
        """Score text for English-like properties"""
        text = text.upper()
        score = 0.0
        
        # Common bigrams
        common_bigrams = ['TH', 'HE', 'IN', 'ER', 'AN', 'ED', 'ND', 'TO', 'EN', 'ES']
        for bigram in common_bigrams:
            score += text.count(bigram) * 2
        
        # Common trigrams
        common_trigrams = ['THE', 'AND', 'ING', 'ION', 'TIO', 'ENT', 'ATI', 'FOR']
        for trigram in common_trigrams:
            score += text.count(trigram) * 3
        
        return score / max(len(text), 1)
    
    def _has_structure(self, text: str) -> bool:
        """Check if text has non-random structure"""
        if len(text) < 10:
            return False
        
        # Check for repetition
        for length in [2, 3, 4]:
            for i in range(len(text) - length * 2):
                pattern = text[i:i+length]
                if text.count(pattern) >= 3:
                    return True
        
        # Check for low entropy
        char_counts = Counter(text)
        if len(char_counts) < len(text) / 3:  # Few unique characters
            return True
        
        return False
    
    def _find_grid_crossings(self, order: np.ndarray, rows: int, cols: int) -> List[int]:
        """Find where shadow crosses grid lines"""
        crossings = []
        
        for i in order:
            row = i // cols
            col = i % cols
            
            # Check if at grid boundary
            if row % 3 == 0 or col % 7 == 0:  # Adjust these for different grid patterns
                crossings.append(i)
        
        return crossings
    
    def _extract_diagonals(self, grid: List[str]) -> List[str]:
        """Extract diagonals from a grid"""
        diagonals = []
        rows = len(grid)
        cols = len(grid[0]) if grid else 0
        
        # Main diagonals
        for start_col in range(cols):
            diag = ""
            r, c = 0, start_col
            while r < rows and c < cols:
                if c < len(grid[r]):
                    diag += grid[r][c]
                r += 1
                c += 1
            if diag:
                diagonals.append(diag)
        
        # Anti-diagonals
        for start_col in range(cols):
            diag = ""
            r, c = 0, start_col
            while r < rows and c >= 0:
                if c < len(grid[r]):
                    diag += grid[r][c]
                r += 1
                c -= 1
            if diag:
                diagonals.append(diag)
        
        return diagonals
    
    def run_all_tests(self) -> Dict:
        """Run all combined discovery tests"""
        print("\n" + "=" * 80)
        print("COMBINED DISCOVERIES TEST SUITE")
        print("=" * 80)
        
        all_results = {}
        
        # 1. Function word combinations
        all_results['function_words'] = self.analyze_function_word_combinations()
        
        # 2. XOR pattern analysis
        all_results['xor_patterns'] = self.analyze_xor_patterns()
        
        # 3. Shadow-based selection
        all_results['shadow_selection'] = self.test_shadow_selection()
        
        # 4. Coordinate interpretations
        all_results['coordinates'] = self.test_coordinate_interpretations()
        
        # 5. 98-character significance
        all_results['path_98'] = self.test_98_character_significance()
        
        # 6. Combined paths
        all_results['combined_paths'] = self.combine_paths_for_solution()
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY OF FINDINGS")
        print("=" * 80)
        
        significant_findings = []
        
        # Check each category for significant results
        for category, results in all_results.items():
            for key, value in results.items():
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            if item.get('words_found') or item.get('significance'):
                                significant_findings.append({
                                    'category': category,
                                    'type': key,
                                    'finding': item
                                })
        
        if significant_findings:
            print("\nSignificant discoveries:")
            for i, finding in enumerate(significant_findings, 1):
                print(f"\n{i}. {finding['category']} - {finding['type']}")
                print(f"   Details: {finding['finding']}")
        else:
            print("\nNo breakthrough discoveries yet, but several interesting patterns:")
            print("- Function words suggest instruction/query structure")
            print("- XOR shows repetitive patterns suggesting structure")
            print("- Shadow angles may encode selection pattern")
            print("- 98-character path indicates intentional design")
            print("- Dual paths likely encode related information")
        
        return all_results


def main():
    """Run the combined discoveries test suite"""
    
    tester = CombinedDiscoveriesTest()
    results = tester.run_all_tests()
    
    # Save results
    import json
    
    # Convert numpy arrays to lists for JSON
    def convert_for_json(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_for_json(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        else:
            return obj
    
    json_results = convert_for_json(results)
    
    with open('combined_discoveries_results.json', 'w') as f:
        json.dump(json_results, f, indent=2)
    
    print("\n\nResults saved to combined_discoveries_results.json")
    
    return results


if __name__ == "__main__":
    main()