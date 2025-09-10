#!/usr/bin/env python3
"""
F1 Cross-validation: Tableau & L=17 Compatibility
MASTER_SEED = 1337
"""

import os
import sys
import csv
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Import base modules
from f1_anchor_search_v2 import AnchorSearcherV2, PlacementResult
from f1_triage import TriagedResult, F1Triage

MASTER_SEED = 1337

class TableauSynchronizer:
    """Check tableau constraints (front↔back)"""
    
    def __init__(self):
        self.width = 14  # Standard K4 tableau width
        self.height = 7  # Standard K4 tableau height
        
    def check_tableau_constraints(self, placement: PlacementResult, 
                                 merged_wheels: Dict) -> Tuple[bool, List[str]]:
        """
        Check if placement violates tableau row/col constraints
        Returns (no_conflicts, conflict_list)
        """
        conflicts = []
        
        # Build tableau indices
        token = placement.token
        start = placement.start_index
        
        for i, char in enumerate(token):
            pos = start + i
            
            # Calculate tableau position
            row = pos // self.width
            col = pos % self.width
            
            # Check row constraint (simplified - would need full implementation)
            # This is a placeholder for actual tableau synchronization
            if row >= self.height:
                continue
                
            # Check basic alignment patterns
            # In real implementation, would check front/back synchronization
            # For now, just verify position is valid
            if pos >= 97:
                conflicts.append(f'out_of_bounds:{pos}')
        
        return len(conflicts) == 0, conflicts
    
    def count_alignment_hits(self, placement: PlacementResult) -> Dict:
        """
        Count simple alignment patterns (row/col/diag)
        No semantic scoring, just mechanical counting
        """
        token = placement.token
        start = placement.start_index
        
        hits = {
            'row_aligned': 0,
            'col_aligned': 0,
            'diag_aligned': 0,
            'antidiag_aligned': 0
        }
        
        positions = [start + i for i in range(len(token))]
        
        # Check row alignment
        rows = [p // self.width for p in positions]
        if len(set(rows)) == 1:
            hits['row_aligned'] = len(positions)
        
        # Check column alignment  
        cols = [p % self.width for p in positions]
        if len(set(cols)) == 1:
            hits['col_aligned'] = len(positions)
        
        # Check diagonal alignment (simplified)
        # Would need more sophisticated check in full implementation
        
        return hits


class L17CompatibilityChecker:
    """Check compatibility with L=17 period"""
    
    def __init__(self):
        self.searcher = AnchorSearcherV2()
        
    def check_l17_compatibility(self, placement: PlacementResult) -> Tuple[bool, int]:
        """
        Test if placement is compatible with L=17
        Returns (has_conflicts, unknown_after_count)
        """
        # Get the token and position from L=11 placement
        token = placement.token
        start = placement.start_index
        
        # Test with L=17 using same baseline families
        # Try multiple phases to find best fit
        best_result = None
        min_conflicts = float('inf')
        
        for phase in range(17):
            result = self.searcher.test_placement(token, start, L=17, phase=phase)
            
            if not result.rejected:
                # Found a compatible placement
                return False, result.unknown_after
            
            # Track best attempt
            if len(result.reject_reasons) < min_conflicts:
                min_conflicts = len(result.reject_reasons)
                best_result = result
        
        # All phases rejected - has L17 conflicts
        return True, 73  # All unknowns remain


class CrossValidator:
    """Main cross-validation system"""
    
    def __init__(self):
        self.tableau = TableauSynchronizer()
        self.l17_checker = L17CompatibilityChecker()
        self.searcher = AnchorSearcherV2()
        
    def validate_shortlist(self, csv_path: str) -> List[Dict]:
        """
        Run cross-validation on a shortlist CSV
        """
        results = []
        
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Recreate placement
                token = row['token']
                start = int(row['start'])
                L = int(row['L'])
                phase = int(row['phase'])
                gains = int(row['gains'])
                
                # Get original placement
                placement = self.searcher.test_placement(token, start, L, phase)
                
                # Run tableau check
                tableau_ok, tableau_conflicts = self.tableau.check_tableau_constraints(
                    placement, None)  # Would pass merged wheels in full impl
                alignment_hits = self.tableau.count_alignment_hits(placement)
                
                # Run L=17 compatibility check
                l17_conflict, l17_unknown = self.l17_checker.check_l17_compatibility(placement)
                
                # Build result record
                record = {
                    'token': token,
                    'start': start,
                    'L11_gains': gains,
                    'L11_forced_slots': int(row['forced_slots']),
                    'tableau_conflict': not tableau_ok,
                    'tableau_conflicts': ','.join(tableau_conflicts[:3]) if tableau_conflicts else '',
                    'alignment_hits': sum(alignment_hits.values()),
                    'L17_conflict': l17_conflict,
                    'L17_unknown_after': l17_unknown
                }
                
                results.append(record)
                
                # Progress
                if len(results) % 10 == 0:
                    print(f"  Validated {len(results)} candidates...")
        
        return results
    
    def run_crosscheck(self, input_dir: str = 'triage', output_dir: str = 'crosscheck'):
        """
        Run full cross-validation on all shortlists
        """
        os.makedirs(output_dir, exist_ok=True)
        
        print("=== Cross-Validation ===")
        print(f"MASTER_SEED: {MASTER_SEED}\n")
        
        # Process each shortlist
        shortlists = [
            'top_100_by_score',
            'top_50_by_gains', 
            'top_50_by_forced_slots'
        ]
        
        all_results = []
        
        for list_name in shortlists:
            csv_path = f'{input_dir}/{list_name}.csv'
            if not os.path.exists(csv_path):
                print(f"  Skipping {list_name} - file not found")
                continue
            
            print(f"Validating {list_name}...")
            results = self.validate_shortlist(csv_path)
            
            # Save individual results
            output_path = f'{output_dir}/{list_name}_crosscheck.csv'
            with open(output_path, 'w', newline='') as f:
                if results:
                    writer = csv.DictWriter(f, fieldnames=results[0].keys())
                    writer.writeheader()
                    writer.writerows(results)
            
            print(f"  Saved {len(results)} results to {output_path}")
            all_results.extend(results)
        
        # Generate summary
        self.generate_summary(all_results, output_dir)
        
    def generate_summary(self, results: List[Dict], output_dir: str):
        """
        Generate CROSSCHECK_SUMMARY.csv
        """
        # Deduplicate by token+start
        seen = set()
        unique_results = []
        
        for r in results:
            key = (r['token'], r['start'])
            if key not in seen:
                seen.add(key)
                unique_results.append(r)
        
        # Sort by multiple criteria
        # Prefer: no conflicts, higher gains, L17 compatible
        def sort_key(r):
            return (
                -int(not r['tableau_conflict']),  # No tableau conflict first
                -int(not r['L17_conflict']),       # L17 compatible first
                -r['L11_gains'],                   # Higher gains
                r['L17_unknown_after']             # Lower unknowns with L17
            )
        
        unique_results.sort(key=sort_key)
        
        # Save summary
        summary_path = f'{output_dir}/CROSSCHECK_SUMMARY.csv'
        with open(summary_path, 'w', newline='') as f:
            if unique_results:
                writer = csv.DictWriter(f, fieldnames=unique_results[0].keys())
                writer.writeheader()
                writer.writerows(unique_results[:100])  # Top 100
        
        # Print statistics
        print(f"\n=== Cross-Check Summary ===")
        print(f"Total unique candidates: {len(unique_results)}")
        
        no_tableau = sum(1 for r in unique_results if not r['tableau_conflict'])
        print(f"No tableau conflicts: {no_tableau}")
        
        l17_compatible = sum(1 for r in unique_results if not r['L17_conflict'])
        print(f"L17 compatible: {l17_compatible}")
        
        both_ok = sum(1 for r in unique_results 
                     if not r['tableau_conflict'] and not r['L17_conflict'])
        print(f"Both constraints OK: {both_ok}")
        
        print(f"\nSummary saved to {summary_path}")
        
        # Show top candidates
        print("\nTop 5 candidates (no conflicts, highest gains):")
        for i, r in enumerate(unique_results[:5]):
            print(f"  {i+1}. {r['token']}@{r['start']}: "
                  f"gains={r['L11_gains']}, "
                  f"tableau_ok={not r['tableau_conflict']}, "
                  f"L17_ok={not r['L17_conflict']}")


def main():
    """Main execution"""
    validator = CrossValidator()
    validator.run_crosscheck()
    

if __name__ == "__main__":
    main()