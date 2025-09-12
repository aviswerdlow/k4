#!/usr/bin/env python3
"""
Fork G v2 - Shared Preparation
Build tableau matrix, K4 sync, and spatial fixed points
"""

import json
import os
from typing import Dict, List, Tuple

class SharedPrep:
    def __init__(self):
        self.k4_ct = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
        self.output_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Known anchors
        self.anchors = {
            'EAST': (21, 24),
            'NORTHEAST': (25, 33),
            'BERLIN': (63, 68),
            'CLOCK': (69, 73)
        }
        
        # Anomalies from the sculpture
        self.anomalies = {
            'IQLUSION': 57,  # Q instead of L
            'UNDERGRUUND': None,  # In K3, not K4
            'DESPARATLY': None,  # In K3, not K4
            'YAR': 'raised',  # Raised letters on sculpture
            'EXTRA_L': 'tableau_row'  # Extra L row in tableau
        }
    
    def build_tableau_matrix(self) -> Dict:
        """Build the keyed Vigenère tableau with KRYPTOS key"""
        # Standard alphabet
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        
        # KRYPTOS-keyed alphabet (remove duplicates, preserve order)
        key = "KRYPTOS"
        seen = set()
        keyed_alphabet = []
        
        for char in key:
            if char not in seen:
                keyed_alphabet.append(char)
                seen.add(char)
        
        for char in alphabet:
            if char not in seen:
                keyed_alphabet.append(char)
                seen.add(char)
        
        # Build tableau with keyed alphabet as row headers
        # Include anomaly: extra 'L' row (appears twice)
        row_labels = list("KRYPTOS") + ['L'] + list("ABCDEFGHIJLMNQUVWXZ")  # Extra L, no repeated letters
        
        tableau = {}
        for i, row_label in enumerate(row_labels):
            row = []
            # Shift the keyed alphabet by the position of row_label
            shift = keyed_alphabet.index(row_label) if row_label in keyed_alphabet else 0
            for j in range(26):
                col_idx = (j + shift) % 26
                row.append(keyed_alphabet[col_idx])
            tableau[row_label] = row
        
        # Add column labels (standard A-Z)
        col_labels = list(alphabet)
        
        result = {
            'row_labels': row_labels,
            'col_labels': col_labels,
            'tableau': tableau,
            'keyed_alphabet': keyed_alphabet,
            'anomalies': {
                'extra_L_row': True,
                'mirrored_orientation': True,
                'key': key
            }
        }
        
        return result
    
    def build_k4_tableau_sync(self, tableau: Dict) -> List[Dict]:
        """Map K4 indices to tableau coordinates"""
        sync_data = []
        
        # For each position in K4
        for idx, ct_char in enumerate(self.k4_ct):
            # Find potential row/col coordinates on tableau
            # This is a placeholder - actual mapping depends on encryption method
            # For now, record the CT character and its position
            sync_entry = {
                'k4_index': idx,
                'ct_char': ct_char,
                'anchor': self._get_anchor_at(idx),
                'row_candidates': [],
                'col_candidates': []
            }
            
            # Find which rows contain this character
            for row_label, row_chars in tableau['tableau'].items():
                if ct_char in row_chars:
                    col_idx = row_chars.index(ct_char)
                    sync_entry['row_candidates'].append({
                        'row': row_label,
                        'col': tableau['col_labels'][col_idx]
                    })
            
            sync_data.append(sync_entry)
        
        return sync_data
    
    def _get_anchor_at(self, idx: int) -> str:
        """Check if index is part of an anchor"""
        for anchor_text, (start, end) in self.anchors.items():
            if start <= idx <= end:
                return f"{anchor_text}[{idx-start}]"
        return None
    
    def build_spatial_fixed_points(self) -> Dict:
        """Build spatial fixed points from anomalies"""
        fixed_points = {
            'misprints': [],
            'raised_letters': [],
            'extra_elements': [],
            'projections': {}
        }
        
        # IQLUSION misprint at position 57 (Q instead of L)
        fixed_points['misprints'].append({
            'position': 57,
            'expected': 'L',
            'actual': 'Q',
            'context': 'IQLUSION',
            'source': 'K4'
        })
        
        # YAR raised letters
        fixed_points['raised_letters'] = ['Y', 'A', 'R']
        
        # Extra L row in tableau
        fixed_points['extra_elements'].append({
            'type': 'tableau_row',
            'element': 'L',
            'description': 'Extra L row appears in tableau'
        })
        
        # Projections (modulo operations, overlays)
        fixed_points['projections'] = {
            'mod_97': [(i % 97) for i in range(97)],
            'panel_overlay': {
                'k1_k2_boundary': 'unknown',
                'k2_k3_boundary': 'unknown',
                'k3_k4_boundary': 'position_0'
            },
            'boundary_offsets': {
                'k4_start': 0,
                'k4_end': 96
            }
        }
        
        return fixed_points
    
    def save_all(self):
        """Save all preparation files"""
        # Build components
        tableau = self.build_tableau_matrix()
        sync = self.build_k4_tableau_sync(tableau)
        spatial = self.build_spatial_fixed_points()
        
        # Save tableau matrix
        tableau_path = os.path.join(self.output_dir, 'tableau_matrix.json')
        with open(tableau_path, 'w') as f:
            json.dump(tableau, f, indent=2)
        print(f"Saved tableau matrix to {tableau_path}")
        
        # Save K4 sync as CSV
        import csv
        sync_path = os.path.join(self.output_dir, 'k4_tableau_sync.csv')
        with open(sync_path, 'w', newline='') as f:
            fieldnames = ['k4_index', 'ct_char', 'anchor', 'row_col_pairs']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for entry in sync:
                row_col_pairs = ';'.join([f"{rc['row']},{rc['col']}" for rc in entry['row_candidates'][:3]])
                writer.writerow({
                    'k4_index': entry['k4_index'],
                    'ct_char': entry['ct_char'],
                    'anchor': entry['anchor'] or '',
                    'row_col_pairs': row_col_pairs
                })
        print(f"Saved K4 sync to {sync_path}")
        
        # Save spatial fixed points
        spatial_path = os.path.join(self.output_dir, 'spatial_fixed_points.json')
        with open(spatial_path, 'w') as f:
            json.dump(spatial, f, indent=2)
        print(f"Saved spatial fixed points to {spatial_path}")
        
        return tableau, sync, spatial


def main():
    prep = SharedPrep()
    tableau, sync, spatial = prep.save_all()
    
    # Print summary
    print("\n=== Shared Prep Summary ===")
    print(f"Tableau: {len(tableau['row_labels'])} rows x {len(tableau['col_labels'])} cols")
    print(f"K4 sync: {len(sync)} positions mapped")
    print(f"Spatial fixed points: {len(spatial['misprints'])} misprints, "
          f"{len(spatial['raised_letters'])} raised letters")
    print(f"Anomalies tracked: Extra L row, mirrored orientation")


if __name__ == "__main__":
    main()