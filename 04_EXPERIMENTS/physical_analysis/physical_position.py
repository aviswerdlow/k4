#!/usr/bin/env python3
"""
Physical Position Analysis
Tests physical/spatial patterns in K4 unknown positions
Includes modular arithmetic, clustering, and distance analysis
"""

import json
import os
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

MASTER_SEED = 1337

class PhysicalAnalysis:
    """Analyze physical position patterns in K4"""
    
    def __init__(self):
        self.seed = MASTER_SEED
        self.load_k4_data()
        
    def load_k4_data(self):
        """Load K4 configuration"""
        # Define anchors
        self.anchors = []
        for start, end in [(21, 24), (25, 33), (63, 68), (69, 73)]:
            for i in range(start, end + 1):
                self.anchors.append(i)
        
        # Define unknowns
        tail = list(range(74, 97))
        constrained = set(self.anchors) | set(tail)
        self.unknowns = [i for i in range(97) if i not in constrained]
        
        # Physical layout (approximate based on sculpture)
        # Assuming 97 chars could be arranged in rows
        # Common arrangements: 7x14-5, 8x12+1, 10x10-3
        self.layouts = {
            '7x14': {'rows': 7, 'cols': 14},
            '8x12': {'rows': 8, 'cols': 12},
            '10x10': {'rows': 10, 'cols': 10},
            'linear': {'rows': 1, 'cols': 97}
        }
    
    def position_to_grid(self, index: int, layout: str) -> Tuple[int, int]:
        """Convert linear index to grid position"""
        if layout not in self.layouts:
            layout = 'linear'
        
        rows = self.layouts[layout]['rows']
        cols = self.layouts[layout]['cols']
        
        row = index // cols
        col = index % cols
        
        return row, col
    
    def test_modular_intervals(self) -> Dict:
        """Test regular interval patterns in unknowns"""
        results = {
            'mechanism': 'modular_intervals',
            'patterns': {}
        }
        
        # Test modulo k for various k
        test_moduli = [3, 4, 5, 6, 7, 8, 9, 11, 17]
        
        for k in test_moduli:
            # Group unknowns by modulo k
            mod_groups = {}
            for idx in self.unknowns:
                mod_val = idx % k
                if mod_val not in mod_groups:
                    mod_groups[mod_val] = []
                mod_groups[mod_val].append(idx)
            
            # Analyze distribution
            group_sizes = [len(g) for g in mod_groups.values()]
            
            # Check for regular patterns
            is_regular = len(set(group_sizes)) <= 2  # At most 2 different sizes
            max_diff = max(group_sizes) - min(group_sizes) if group_sizes else 0
            
            pattern_info = {
                'modulus': k,
                'groups': len(mod_groups),
                'distribution': dict(Counter(group_sizes)),
                'is_regular': is_regular,
                'max_size_diff': max_diff,
                'positions_by_mod': mod_groups
            }
            
            results['patterns'][f'mod_{k}'] = pattern_info
            
            # Check if this modulus creates a strong pattern
            if is_regular and max_diff <= 1:
                print(f"Regular pattern found: mod {k} creates {len(mod_groups)} groups")
        
        return results
    
    def test_distance_from_anchors(self) -> Dict:
        """Analyze distance patterns from anchor positions"""
        results = {
            'mechanism': 'anchor_distances',
            'patterns': {}
        }
        
        # Calculate distances for each unknown
        distance_data = []
        
        for unk_idx in self.unknowns:
            # Find nearest anchor
            min_dist = float('inf')
            nearest_anchor = None
            
            for anc_idx in self.anchors:
                dist = abs(unk_idx - anc_idx)
                if dist < min_dist:
                    min_dist = dist
                    nearest_anchor = anc_idx
            
            distance_data.append({
                'unknown_idx': unk_idx,
                'nearest_anchor': nearest_anchor,
                'distance': min_dist
            })
        
        # Analyze distance distribution
        distances = [d['distance'] for d in distance_data]
        
        results['patterns']['nearest_distances'] = {
            'min': min(distances),
            'max': max(distances),
            'mean': np.mean(distances),
            'median': np.median(distances),
            'distribution': dict(Counter(distances))
        }
        
        # Check for clustering
        # Unknowns within distance d of anchors
        for threshold in [5, 10, 15, 20]:
            close_unknowns = [d for d in distance_data if d['distance'] <= threshold]
            results['patterns'][f'within_{threshold}'] = {
                'count': len(close_unknowns),
                'percentage': len(close_unknowns) / len(self.unknowns) * 100,
                'indices': [d['unknown_idx'] for d in close_unknowns]
            }
        
        # Group by nearest anchor
        by_anchor = {}
        for d in distance_data:
            anc = d['nearest_anchor']
            if anc not in by_anchor:
                by_anchor[anc] = []
            by_anchor[anc].append(d['unknown_idx'])
        
        results['patterns']['by_nearest_anchor'] = by_anchor
        
        return results
    
    def test_physical_clusters(self) -> Dict:
        """Test for physical clustering patterns"""
        results = {
            'mechanism': 'physical_clusters',
            'patterns': {}
        }
        
        # Test each layout
        for layout_name, layout in self.layouts.items():
            if layout_name == 'linear':
                continue  # Skip linear for clustering
            
            # Convert positions to grid
            unknown_grid = []
            for idx in self.unknowns:
                row, col = self.position_to_grid(idx, layout_name)
                unknown_grid.append((row, col, idx))
            
            # Find clusters (connected components)
            clusters = []
            used = set()
            
            for row, col, idx in unknown_grid:
                if idx in used:
                    continue
                
                # Start new cluster
                cluster = [idx]
                queue = [(row, col)]
                used.add(idx)
                
                while queue:
                    r, c = queue.pop(0)
                    
                    # Check neighbors
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = r + dr, c + dc
                        
                        # Find if neighbor is unknown
                        for ur, uc, uidx in unknown_grid:
                            if ur == nr and uc == nc and uidx not in used:
                                cluster.append(uidx)
                                queue.append((nr, nc))
                                used.add(uidx)
                
                if len(cluster) > 1:  # Only keep multi-element clusters
                    clusters.append(cluster)
            
            results['patterns'][layout_name] = {
                'layout': f"{layout['rows']}x{layout['cols']}",
                'num_clusters': len(clusters),
                'cluster_sizes': [len(c) for c in clusters],
                'largest_cluster': max(clusters, key=len) if clusters else [],
                'isolated_unknowns': len([c for c in clusters if len(c) == 1])
            }
        
        return results
    
    def test_morse_alignment(self) -> Dict:
        """Test alignment with morse code phrases if coordinates available"""
        results = {
            'mechanism': 'morse_alignment',
            'patterns': {}
        }
        
        # Known morse phrases from Kryptos
        morse_phrases = {
            'VIRTUALLY_INVISIBLE': 'Located on plaza side',
            'T_IS_YOUR_POSITION': 'Contains position reference',
            'SHADOW_FORCES': 'On compass rose'
        }
        
        # Without exact coordinates, test conceptual alignments
        # Look for T positions in unknowns
        t_related = []
        
        # Positions that might relate to 'T IS YOUR POSITION'
        # These would need actual physical coordinates to test properly
        
        results['patterns']['morse_phrases'] = morse_phrases
        results['patterns']['note'] = 'Physical coordinates needed for precise alignment'
        
        return results
    
    def generate_result_cards(self, test_results: List[Dict]) -> List[Dict]:
        """Generate result cards for all tests"""
        cards = []
        
        for result in test_results:
            mechanism = result.get('mechanism', 'unknown')
            
            # Physical tests don't directly determine positions
            # They identify patterns that could be used with other mechanisms
            
            card = {
                "mechanism": f"PhysicalAnalysis/{mechanism}",
                "unknowns_before": len(self.unknowns),
                "unknowns_after": len(self.unknowns),  # No direct determination
                "anchors_preserved": True,
                "new_positions_determined": [],
                "indices_before": self.unknowns.copy(),
                "indices_after": self.unknowns.copy(),
                "parameters": result.get('patterns', {}),
                "seed": MASTER_SEED,
                "notes": f"Physical pattern analysis: {mechanism}"
            }
            
            cards.append(card)
        
        return cards
    
    def create_visualizations(self, output_dir: str):
        """Create visualization plots"""
        fig = plt.figure(figsize=(12, 10))
        
        # Plot 1: Unknown position distribution
        ax1 = plt.subplot(2, 2, 1)
        ax1.bar(range(97), [1 if i in self.unknowns else 0 for i in range(97)], 
                color=['red' if i in self.unknowns else 'lightgray' for i in range(97)])
        ax1.set_title('Unknown Positions (Red)', fontsize=10)
        ax1.set_xlabel('Position Index')
        ax1.set_ylabel('Unknown')
        
        # Mark anchors
        for idx in self.anchors:
            ax1.axvline(x=idx, color='green', alpha=0.3, linestyle='--')
        
        # Plot 2: Distance from nearest anchor
        ax2 = plt.subplot(2, 2, 2)
        distances = []
        for unk in self.unknowns:
            min_dist = min(abs(unk - anc) for anc in self.anchors)
            distances.append(min_dist)
        
        ax2.hist(distances, bins=15, color='blue', alpha=0.7)
        ax2.set_title('Distance from Nearest Anchor', fontsize=10)
        ax2.set_xlabel('Distance')
        ax2.set_ylabel('Count')
        
        # Plot 3: Modular patterns
        ax3 = plt.subplot(2, 2, 3)
        mod_results = []
        for k in [3, 5, 7, 11, 17]:
            groups = {}
            for idx in self.unknowns:
                mod_val = idx % k
                if mod_val not in groups:
                    groups[mod_val] = 0
                groups[mod_val] += 1
            
            # Calculate uniformity (lower is more uniform)
            uniformity = np.std(list(groups.values()))
            mod_results.append(uniformity)
        
        ax3.bar(['mod 3', 'mod 5', 'mod 7', 'mod 11', 'mod 17'], mod_results, color='purple', alpha=0.7)
        ax3.set_title('Modular Pattern Uniformity (lower = more uniform)', fontsize=10)
        ax3.set_ylabel('Standard Deviation')
        
        # Plot 4: Summary statistics
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""Physical Analysis Summary
        -------------------------
        Total unknowns: {len(self.unknowns)}
        Total anchors: {len(self.anchors)}
        
        Unknown ranges:
        - Head (0-20): {len([u for u in self.unknowns if u <= 20])} unknowns
        - Mid (34-62): {len([u for u in self.unknowns if 34 <= u <= 62])} unknowns
        - Gap (21-73): anchors only
        
        Nearest anchor stats:
        - Min distance: {min(distances)}
        - Max distance: {max(distances)}
        - Mean distance: {np.mean(distances):.1f}
        """
        
        ax4.text(0.1, 0.5, summary_text, fontsize=9, family='monospace', va='center')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/physical_analysis.pdf', format='pdf')
        plt.close()
    
    def run_all_tests(self, output_dir: str):
        """Run all physical analysis tests"""
        os.makedirs(output_dir, exist_ok=True)
        
        print("Running physical position analysis...")
        
        all_results = []
        
        # Test 1: Modular intervals
        print("\n1. Testing modular intervals...")
        mod_results = self.test_modular_intervals()
        all_results.append(mod_results)
        
        # Test 2: Distance from anchors
        print("2. Testing distance patterns...")
        dist_results = self.test_distance_from_anchors()
        all_results.append(dist_results)
        
        # Test 3: Physical clusters
        print("3. Testing physical clusters...")
        cluster_results = self.test_physical_clusters()
        all_results.append(cluster_results)
        
        # Test 4: Morse alignment
        print("4. Testing morse alignment...")
        morse_results = self.test_morse_alignment()
        all_results.append(morse_results)
        
        # Generate result cards
        cards = self.generate_result_cards(all_results)
        
        # Save individual result cards
        for i, card in enumerate(cards):
            mechanism = all_results[i]['mechanism']
            with open(f"{output_dir}/result_{mechanism}.json", 'w') as f:
                json.dump(card, f, indent=2)
        
        # Save combined analysis
        with open(f"{output_dir}/PHYS_CLUSTER.json", 'w') as f:
            json.dump({
                'seed': MASTER_SEED,
                'unknowns': len(self.unknowns),
                'anchors': len(self.anchors),
                'tests': all_results
            }, f, indent=2)
        
        # Create visualizations
        self.create_visualizations(output_dir)
        
        print(f"\nResults saved to {output_dir}/")
        print("Physical analysis complete (patterns documented for composite testing)")


def main():
    """Main execution"""
    print("=== Physical Position Analysis ===")
    print(f"MASTER_SEED: {MASTER_SEED}\n")
    
    analyzer = PhysicalAnalysis()
    
    print(f"Configuration:")
    print(f"  Unknowns: {len(analyzer.unknowns)} positions")
    print(f"  Anchors: {len(analyzer.anchors)} positions")
    print(f"  Layouts tested: {list(analyzer.layouts.keys())}\n")
    
    analyzer.run_all_tests('output')


if __name__ == "__main__":
    main()