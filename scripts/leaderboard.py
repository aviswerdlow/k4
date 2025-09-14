#!/usr/bin/env python3
"""
Leaderboard - Scan runs and rank candidates by null margins and criteria
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
import argparse
from datetime import datetime


class Leaderboard:
    """Rank K4 solution candidates"""
    
    def __init__(self, runs_dir: str = "04_EXPERIMENTS/phase3_zone/runs"):
        self.runs_dir = Path(runs_dir)
        self.candidates = []
    
    def scan_runs(self):
        """Scan all run directories for receipts"""
        for run_dir in self.runs_dir.glob("ts_*"):
            receipts_file = run_dir / "receipts.json"
            manifest_file = run_dir / "manifest.json"
            
            if receipts_file.exists():
                try:
                    with open(receipts_file) as f:
                        receipts = json.load(f)
                    
                    # Extract key metrics
                    candidate = {
                        'dir': run_dir.name,
                        'path': str(run_dir),
                        'manifest': str(manifest_file) if manifest_file.exists() else None,
                        'roundtrip': receipts.get('roundtrip_valid', False),
                        'berlin': receipts.get('berlinclock_verified', False),
                        'timestamp': receipts.get('timestamp', ''),
                        'score': 0
                    }
                    
                    # Add null test results if present
                    null_key_file = run_dir / "null_key.json"
                    null_seg_file = run_dir / "null_seg.json"
                    
                    if null_key_file.exists():
                        with open(null_key_file) as f:
                            null_key = json.load(f)
                            candidate['p_key'] = null_key.get('p_value', 1.0)
                            candidate['z_key'] = null_key.get('z_score', 0)
                    else:
                        candidate['p_key'] = 1.0
                        candidate['z_key'] = 0
                    
                    if null_seg_file.exists():
                        with open(null_seg_file) as f:
                            null_seg = json.load(f)
                            candidate['p_seg'] = null_seg.get('best_p_value', 1.0)
                            candidate['z_seg'] = null_seg.get('best_z_score', 0)
                    else:
                        candidate['p_seg'] = 1.0
                        candidate['z_seg'] = 0
                    
                    # Add K5 gate results if present
                    k5_file = run_dir / "k5_gate.json"
                    if k5_file.exists():
                        with open(k5_file) as f:
                            k5 = json.load(f)
                            candidate['k5_score'] = k5.get('k5_readiness', {}).get('score', 0)
                            candidate['k5_ready'] = k5.get('k5_readiness', {}).get('k5_ready', False)
                    else:
                        candidate['k5_score'] = 0
                        candidate['k5_ready'] = False
                    
                    # Calculate composite score
                    candidate['score'] = self.calculate_score(candidate)
                    
                    self.candidates.append(candidate)
                    
                except Exception as e:
                    print(f"Error reading {run_dir}: {e}")
    
    def calculate_score(self, candidate: Dict[str, Any]) -> float:
        """Calculate composite score for ranking"""
        score = 0
        
        # Critical requirements (binary)
        if candidate['roundtrip']:
            score += 1000
        if candidate['berlin']:
            score += 1000
        
        # Null test performance (higher z-score = better)
        score += candidate['z_key'] * 10
        score += candidate['z_seg'] * 10
        
        # P-value bonus (lower = better)
        if candidate['p_key'] < 0.01:
            score += 200
        if candidate['p_seg'] < 0.01:
            score += 200
        if candidate['p_key'] < 0.001:
            score += 100
        if candidate['p_seg'] < 0.001:
            score += 100
        
        # K5 readiness
        score += candidate['k5_score']
        
        return score
    
    def filter_valid(self) -> List[Dict[str, Any]]:
        """Filter only valid candidates"""
        return [c for c in self.candidates if 
                c['roundtrip'] and 
                c['berlin'] and 
                c['p_key'] < 0.01 and 
                c['p_seg'] < 0.01]
    
    def display(self, top_n: int = 10, valid_only: bool = False):
        """Display leaderboard"""
        # Sort by score
        ranked = sorted(self.candidates, key=lambda x: x['score'], reverse=True)
        
        if valid_only:
            ranked = self.filter_valid()
            if not ranked:
                print("❌ No candidates meet all validity criteria")
                return
        
        # Display header
        print("\n" + "=" * 120)
        print("K4 SOLUTION LEADERBOARD")
        print("=" * 120)
        print(f"{'Rank':<5} {'Run ID':<25} {'Score':<8} {'RT':<3} {'BER':<3} "
              f"{'P(key)':<8} {'Z(key)':<7} {'P(seg)':<8} {'Z(seg)':<7} {'K5':<3}")
        print("-" * 120)
        
        # Display top candidates
        for i, candidate in enumerate(ranked[:top_n], 1):
            rt = "✓" if candidate['roundtrip'] else "✗"
            ber = "✓" if candidate['berlin'] else "✗"
            k5 = "✓" if candidate['k5_ready'] else "-"
            
            print(f"{i:<5} {candidate['dir'][:25]:<25} {candidate['score']:<8.1f} "
                  f"{rt:<3} {ber:<3} "
                  f"{candidate['p_key']:<8.4f} {candidate['z_key']:<7.2f} "
                  f"{candidate['p_seg']:<8.4f} {candidate['z_seg']:<7.2f} "
                  f"{k5:<3}")
        
        # Summary statistics
        print("-" * 120)
        valid_count = len(self.filter_valid())
        print(f"Total runs: {len(self.candidates)} | Valid candidates: {valid_count}")
        
        # Best candidate details
        if ranked and ranked[0]['score'] > 0:
            print("\n🏆 BEST CANDIDATE:")
            best = ranked[0]
            print(f"   Run: {best['dir']}")
            print(f"   Manifest: {best['manifest']}")
            print(f"   Score: {best['score']:.1f}")
            print(f"   Null margins: P(key)={best['p_key']:.4f}, P(seg)={best['p_seg']:.4f}")
            
            # Check if it passes all criteria
            if best['roundtrip'] and best['berlin'] and best['p_key'] < 0.01 and best['p_seg'] < 0.01:
                print(f"   Status: ✅ READY FOR ANTIPODES CHECK")
            else:
                failures = []
                if not best['roundtrip']:
                    failures.append("round-trip")
                if not best['berlin']:
                    failures.append("BERLINCLOCK")
                if best['p_key'] >= 0.01:
                    failures.append("key null test")
                if best['p_seg'] >= 0.01:
                    failures.append("segment null test")
                print(f"   Status: ❌ FAILS: {', '.join(failures)}")
    
    def export_csv(self, output_file: str):
        """Export results to CSV for analysis"""
        import csv
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Run', 'Score', 'Roundtrip', 'Berlin', 'P_Key', 'Z_Key', 
                           'P_Seg', 'Z_Seg', 'K5_Score', 'Manifest'])
            
            for c in sorted(self.candidates, key=lambda x: x['score'], reverse=True):
                writer.writerow([
                    c['dir'], c['score'], c['roundtrip'], c['berlin'],
                    c['p_key'], c['z_key'], c['p_seg'], c['z_seg'],
                    c['k5_score'], c['manifest']
                ])
        
        print(f"Results exported to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='K4 Solution Leaderboard')
    parser.add_argument('--runs', default='04_EXPERIMENTS/phase3_zone/runs', 
                       help='Directory containing run results')
    parser.add_argument('--top', type=int, default=10, help='Number of top candidates to show')
    parser.add_argument('--valid-only', action='store_true', help='Show only valid candidates')
    parser.add_argument('--export', help='Export results to CSV file')
    
    args = parser.parse_args()
    
    # Create and populate leaderboard
    board = Leaderboard(args.runs)
    board.scan_runs()
    
    # Display results
    board.display(args.top, args.valid_only)
    
    # Export if requested
    if args.export:
        board.export_csv(args.export)
    
    # Quick commands for best candidate
    valid = board.filter_valid()
    if valid:
        best = valid[0]
        print("\n📋 QUICK COMMANDS FOR BEST CANDIDATE:")
        print(f"   make phase3-antipodes MANIFEST={best['manifest']}")
        print(f"   make notecard MANIFEST={best['manifest']}")
        print(f"   make verify-rt MANIFEST={best['manifest']}")


if __name__ == '__main__':
    main()