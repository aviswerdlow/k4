#!/usr/bin/env python3
"""
Front/Back Tableau Synchronizer
Maps K4 ciphertext positions to Kryptos tableau coordinates
Tests mechanical alignment patterns without semantics
"""

import json
import csv
import os
from typing import Dict, List, Tuple, Optional
import math

MASTER_SEED = 1337

class TableauSynchronizer:
    """Synchronize K4 positions with Kryptos tableau"""
    
    def __init__(self):
        self.seed = MASTER_SEED
        self.build_tableau()
        self.load_k4_data()
        
    def build_tableau(self):
        """Build the Kryptos keyed tableau"""
        # Standard Kryptos tableau with KRYPTOS keyword
        # Row order after keying (preserving the known structure)
        self.tableau = []
        
        # KRYPTOS keyword removes duplicates: K R Y P T O S
        keyword = "KRYPTOS"
        used = set(keyword)
        
        # First row starts with keyword
        first_row = list(keyword)
        
        # Add remaining letters
        for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if c not in used:
                first_row.append(c)
                used.add(c)
        
        # Generate full tableau (26x26)
        for shift in range(26):
            row = []
            for i in range(26):
                row.append(first_row[(i + shift) % 26])
            self.tableau.append(row)
        
        # Add the anomalous extra row (L row as noted)
        # This is row 27 (index 26) containing shifted alphabet
        extra_row = []
        for i in range(26):
            extra_row.append(chr(ord('A') + (i + 11) % 26))  # L-shift
        self.tableau.append(extra_row)
        
        # Save tableau
        self.save_tableau()
    
    def save_tableau(self):
        """Save tableau to JSON"""
        tableau_data = {
            "rows": len(self.tableau),
            "cols": 26,
            "data": self.tableau,
            "keyword": "KRYPTOS",
            "extra_row_index": 26,
            "extra_row_note": "L-shifted alphabet",
            "seed": MASTER_SEED
        }
        
        with open('tableau_matrix.json', 'w') as f:
            json.dump(tableau_data, f, indent=2)
    
    def load_k4_data(self):
        """Load K4 ciphertext and metadata"""
        with open('../../02_DATA/ciphertext_97.txt', 'r') as f:
            self.ciphertext = f.read().strip()
        
        # Define anchors
        self.anchors = []
        for start, end in [(21, 24), (25, 33), (63, 68), (69, 73)]:
            for i in range(start, end + 1):
                self.anchors.append(i)
        
        # Define unknowns
        tail = list(range(74, 97))
        constrained = set(self.anchors) | set(tail)
        self.unknowns = [i for i in range(97) if i not in constrained]
        
        # Anchor values
        self.anchor_values = {
            21: 'E', 22: 'A', 23: 'S', 24: 'T',
            25: 'N', 26: 'O', 27: 'R', 28: 'T', 29: 'H',
            30: 'E', 31: 'A', 32: 'S', 33: 'T',
            63: 'B', 64: 'E', 65: 'R', 66: 'L', 67: 'I', 68: 'N',
            69: 'C', 70: 'L', 71: 'O', 72: 'C', 73: 'K'
        }
    
    def compute_class(self, i: int) -> int:
        """Compute class for position i"""
        return ((i % 2) * 3) + (i % 3)
    
    def map_to_tableau(self, index: int) -> Tuple[int, int]:
        """
        Map ciphertext index to tableau coordinates
        Simple mapping: row = index // 26, col = index % 26
        """
        row = index // 26
        col = index % 26
        return row, col
    
    def get_tableau_value(self, row: int, col: int) -> str:
        """Get value at tableau position"""
        if row < len(self.tableau) and col < 26:
            return self.tableau[row][col]
        return '?'
    
    def build_sync_table(self) -> List[Dict]:
        """Build synchronization table for all positions"""
        sync_data = []
        
        for i in range(97):
            row, col = self.map_to_tableau(i)
            
            entry = {
                'index': i,
                'cipher_letter': self.ciphertext[i],
                'class': self.compute_class(i),
                'slot': i % 17,  # L=17
                'tableau_row': row,
                'tableau_col': col,
                'tableau_row_char': self.tableau[row][0] if row < len(self.tableau) else '?',
                'tableau_col_char': self.tableau[0][col],
                'tableau_value': self.get_tableau_value(row, col),
                'is_unknown': i in self.unknowns,
                'is_anchor': i in self.anchors
            }
            
            # Add anchor plaintext if known
            if i in self.anchor_values:
                entry['known_plaintext'] = self.anchor_values[i]
            
            sync_data.append(entry)
        
        return sync_data
    
    def test_straight_lines(self) -> Dict:
        """Test straight line patterns through anchors"""
        results = {
            'mechanism': 'straight_lines',
            'patterns_tested': [],
            'new_positions': []
        }
        
        # Get anchor tableau positions
        anchor_positions = []
        for idx in self.anchors:
            row, col = self.map_to_tableau(idx)
            anchor_positions.append((idx, row, col))
        
        # Test horizontal lines
        for _, row, _ in anchor_positions:
            pattern = f"horizontal_row_{row}"
            determined = []
            
            for unk_idx in self.unknowns:
                unk_row, unk_col = self.map_to_tableau(unk_idx)
                if unk_row == row:
                    # On same row as anchor
                    val = self.tableau[row][unk_col]
                    determined.append({'index': unk_idx, 'value': val, 'reason': pattern})
            
            if determined:
                results['patterns_tested'].append(pattern)
                results['new_positions'].extend(determined)
        
        # Test vertical lines
        for _, _, col in anchor_positions:
            pattern = f"vertical_col_{col}"
            determined = []
            
            for unk_idx in self.unknowns:
                unk_row, unk_col = self.map_to_tableau(unk_idx)
                if unk_col == col:
                    # On same column as anchor
                    val = self.tableau[unk_row][col] if unk_row < len(self.tableau) else '?'
                    if val != '?':
                        determined.append({'index': unk_idx, 'value': val, 'reason': pattern})
            
            if determined:
                results['patterns_tested'].append(pattern)
                results['new_positions'].extend(determined)
        
        return results
    
    def test_diagonals(self) -> Dict:
        """Test diagonal patterns through anchors"""
        results = {
            'mechanism': 'diagonals',
            'patterns_tested': [],
            'new_positions': []
        }
        
        # Get anchor positions
        anchor_positions = []
        for idx in self.anchors:
            row, col = self.map_to_tableau(idx)
            anchor_positions.append((idx, row, col))
        
        # Test NW-SE diagonals
        for _, row, col in anchor_positions:
            pattern = f"diagonal_nw_se_from_{row}_{col}"
            determined = []
            
            for unk_idx in self.unknowns:
                unk_row, unk_col = self.map_to_tableau(unk_idx)
                
                # Check if on same NW-SE diagonal
                if (unk_row - row) == (unk_col - col):
                    if 0 <= unk_row < len(self.tableau) and 0 <= unk_col < 26:
                        val = self.tableau[unk_row][unk_col]
                        determined.append({'index': unk_idx, 'value': val, 'reason': pattern})
            
            if determined:
                results['patterns_tested'].append(pattern)
                results['new_positions'].extend(determined)
        
        # Test NE-SW diagonals
        for _, row, col in anchor_positions:
            pattern = f"diagonal_ne_sw_from_{row}_{col}"
            determined = []
            
            for unk_idx in self.unknowns:
                unk_row, unk_col = self.map_to_tableau(unk_idx)
                
                # Check if on same NE-SW diagonal
                if (unk_row - row) == -(unk_col - col):
                    if 0 <= unk_row < len(self.tableau) and 0 <= unk_col < 26:
                        val = self.tableau[unk_row][unk_col]
                        determined.append({'index': unk_idx, 'value': val, 'reason': pattern})
            
            if determined:
                results['patterns_tested'].append(pattern)
                results['new_positions'].extend(determined)
        
        return results
    
    def test_spirals(self) -> Dict:
        """Test spiral patterns from central points"""
        results = {
            'mechanism': 'spirals',
            'patterns_tested': [],
            'new_positions': []
        }
        
        # Find central T if it exists
        central_points = []
        
        # Check for T in tableau center region
        for row in range(12, 15):  # Center rows
            for col in range(12, 15):  # Center cols
                if row < len(self.tableau) and self.tableau[row][col] == 'T':
                    central_points.append((row, col))
        
        # If no central T, use geometric center
        if not central_points:
            central_points = [(13, 13)]  # Geometric center
        
        # Test spiral from each center
        for center_row, center_col in central_points:
            pattern = f"spiral_from_{center_row}_{center_col}"
            
            # Build spiral path (fixed radius increments)
            spiral_positions = []
            for radius in range(1, 8):  # Test radii 1-7
                # Generate points at this radius
                for angle_step in range(8 * radius):  # More points at larger radii
                    angle = (angle_step * 2 * math.pi) / (8 * radius)
                    row = int(center_row + radius * math.sin(angle))
                    col = int(center_col + radius * math.cos(angle))
                    
                    if 0 <= row < len(self.tableau) and 0 <= col < 26:
                        spiral_positions.append((row, col))
            
            # Check if any unknowns fall on spiral
            determined = []
            for unk_idx in self.unknowns:
                unk_row, unk_col = self.map_to_tableau(unk_idx)
                
                if (unk_row, unk_col) in spiral_positions:
                    val = self.tableau[unk_row][unk_col]
                    determined.append({'index': unk_idx, 'value': val, 'reason': pattern})
            
            if determined:
                results['patterns_tested'].append(pattern)
                results['new_positions'].extend(determined)
        
        return results
    
    def generate_result_card(self, test_name: str, test_results: Dict) -> Dict:
        """Generate result card for a test"""
        new_positions = test_results.get('new_positions', [])
        
        # Check if anchors would be preserved
        anchors_preserved = True  # Mechanical tests don't modify anchors
        
        result_card = {
            "mechanism": f"TableauSync/{test_name}",
            "unknowns_before": len(self.unknowns),
            "unknowns_after": len(self.unknowns) - len(new_positions),
            "anchors_preserved": anchors_preserved,
            "new_positions_determined": [p['index'] for p in new_positions],
            "indices_before": self.unknowns.copy(),
            "indices_after": [i for i in self.unknowns if i not in [p['index'] for p in new_positions]],
            "parameters": {
                "test_type": test_name,
                "patterns_tested": test_results.get('patterns_tested', []),
                "tableau_size": f"{len(self.tableau)}x26"
            },
            "seed": MASTER_SEED,
            "notes": f"Tableau synchronization test: {test_name}"
        }
        
        return result_card
    
    def run_all_tests(self, output_dir: str):
        """Run all tableau sync tests"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Build sync table
        sync_data = self.build_sync_table()
        
        # Save sync table CSV
        with open(f"{output_dir}/k4_tableau_sync.csv", 'w', newline='') as f:
            if sync_data:
                # Define all fieldnames to include optional fields
                fieldnames = [
                    'index', 'cipher_letter', 'class', 'slot',
                    'tableau_row', 'tableau_col', 'tableau_row_char',
                    'tableau_col_char', 'tableau_value', 
                    'is_unknown', 'is_anchor', 'known_plaintext'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(sync_data)
        
        print("Sync table saved to k4_tableau_sync.csv")
        
        # Run alignment tests
        all_results = []
        
        # Test 1: Straight lines
        print("\nTesting straight lines...")
        straight_results = self.test_straight_lines()
        card = self.generate_result_card('straight_lines', straight_results)
        all_results.append(card)
        with open(f"{output_dir}/result_straight_lines.json", 'w') as f:
            json.dump(card, f, indent=2)
        
        # Test 2: Diagonals
        print("Testing diagonals...")
        diagonal_results = self.test_diagonals()
        card = self.generate_result_card('diagonals', diagonal_results)
        all_results.append(card)
        with open(f"{output_dir}/result_diagonals.json", 'w') as f:
            json.dump(card, f, indent=2)
        
        # Test 3: Spirals
        print("Testing spirals...")
        spiral_results = self.test_spirals()
        card = self.generate_result_card('spirals', spiral_results)
        all_results.append(card)
        with open(f"{output_dir}/result_spirals.json", 'w') as f:
            json.dump(card, f, indent=2)
        
        # Generate summary
        with open(f"{output_dir}/alignment_tests.json", 'w') as f:
            json.dump({
                'total_tests': len(all_results),
                'tests': all_results,
                'summary': {
                    'straight_lines': straight_results.get('new_positions', []),
                    'diagonals': diagonal_results.get('new_positions', []),
                    'spirals': spiral_results.get('new_positions', [])
                }
            }, f, indent=2)
        
        # Report results
        total_determined = sum(len(r['new_positions_determined']) for r in all_results)
        
        if total_determined > 0:
            print(f"\n✓ Determined {total_determined} positions through tableau alignment")
        else:
            print("\n✗ No positions determined (clean negative)")
        
        return total_determined > 0


def main():
    """Main execution"""
    print("=== Tableau Synchronization Tests ===")
    print(f"MASTER_SEED: {MASTER_SEED}\n")
    
    sync = TableauSynchronizer()
    
    print(f"Configuration:")
    print(f"  Tableau: {len(sync.tableau)} rows x 26 columns")
    print(f"  Unknowns: {len(sync.unknowns)} positions")
    print(f"  Anchors: {len(sync.anchors)} positions\n")
    
    # Run tests
    has_hits = sync.run_all_tests('output')
    
    if has_hits:
        print("\n🎯 SUCCESS: Found tableau alignments that determine positions!")
    else:
        print("\n📊 Clean negative result documented")
    
    print("\nResults saved to output/")


if __name__ == "__main__":
    main()