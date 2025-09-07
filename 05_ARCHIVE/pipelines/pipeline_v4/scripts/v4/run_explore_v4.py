#!/usr/bin/env python3
"""
Track A5: Explore v4 main orchestration and scoring.
Runs the full pipeline and generates EXPLORE_MATRIX.csv.
"""

import json
import csv
import hashlib
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import numpy as np

# Add parent for v2 imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from experiments.pipeline_v2.scripts.explore.run_family import ExplorePipeline

# Import v4 components
from gen_blinded_mcmc import BlindedMCMCGenerator
from saliency_map import SaliencyMapper, process_heads
from place_anchors_pareto import ParetoAnchorPlacer, process_heads_with_placement
from neutral_repair import NeutralMoveRepairer, process_heads_with_repair


class ExploreV4Pipeline:
    """
    Main v4 pipeline orchestrator.
    """
    
    def __init__(self, seed: int = 1337):
        self.seed = seed
        
        # Initialize v2 scorer for delta computation
        self.scorer = ExplorePipeline(seed)
        
        # Track statistics
        self.stats = {
            'total_processed': 0,
            'within_epsilon_0.10': 0,
            'within_epsilon_0.05': 0,
            'delta_passers': 0
        }
    
    def run_track_a(
        self,
        n_chains: int = 5,
        mcmc_iterations: int = 5000,
        n_heads_to_process: int = 50
    ) -> Dict:
        """
        Run complete Track A pipeline.
        
        Returns:
            Dictionary with all results
        """
        print("=" * 60)
        print("TRACK A: BLINDED-FIRST MCMC + SALIENCY")
        print("=" * 60)
        
        output_dir = Path(__file__).parent.parent.parent / "runs" / "track_a"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Generate blinded heads
        print("\nStep 1: Generating blinded-first heads...")
        generator = BlindedMCMCGenerator(self.seed)
        heads = generator.generate_heads(n_chains=n_chains, iterations=mcmc_iterations)
        
        # Save heads
        heads_file = output_dir / "blinded_heads.json"
        with open(heads_file, 'w') as f:
            json.dump({
                'track': 'A1_BLINDED_MCMC',
                'total_generated': len(heads),
                'kept': min(200, len(heads)),
                'heads': heads[:200]
            }, f, indent=2)
        
        # Step 2: Compute saliency maps
        print("\nStep 2: Computing saliency maps...")
        saliency_results = process_heads(heads_file, output_dir, n_heads=n_heads_to_process)
        
        # Step 3: Pareto anchor placement
        print("\nStep 3: Placing anchors with Pareto optimization...")
        saliency_file = output_dir / "SALIENCY.json"
        placement_results = process_heads_with_placement(
            saliency_file, output_dir, n_heads=n_heads_to_process
        )
        
        # Step 4: Neutral-move repair
        print("\nStep 4: Applying neutral-move repair...")
        placement_file = output_dir / "pareto_placements.json"
        repair_results = process_heads_with_repair(
            placement_file, saliency_file, output_dir, n_heads=n_heads_to_process
        )
        
        # Step 5: Explore scoring
        print("\nStep 5: Running Explore scoring...")
        explore_results = self.score_repaired_heads(repair_results, output_dir)
        
        return {
            'heads_generated': len(heads),
            'heads_processed': len(repair_results),
            'explore_results': explore_results,
            'statistics': self.stats
        }
    
    def score_repaired_heads(self, repair_results: List[Dict], output_dir: Path) -> List[Dict]:
        """
        Score repaired heads through Explore pipeline.
        """
        explore_results = []
        
        # Prepare CSV
        csv_file = output_dir / "EXPLORE_MATRIX.csv"
        fieldnames = [
            'label', 'grid', 'anchor_mode', 
            'delta_vs_windowed', 'delta_vs_shuffled',
            'z_ngram_blind', 'pass_deltas', 
            'within_eps_0.10', 'within_eps_0.05',
            'repair_improvement', 'saliency_mean'
        ]
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for i, repair_result in enumerate(repair_results):
                if i % 10 == 0:
                    print(f"  Scoring head {i+1}/{len(repair_results)}...")
                
                text = repair_result['repaired_text']
                label = repair_result['label']
                
                # Run through Explore scorer with different policies
                policies = [
                    {"name": "fixed", "window_radius": 0, "typo_budget": 0},
                    {"name": "windowed_r2", "window_radius": 2, "typo_budget": 0},
                    {"name": "windowed_r3", "window_radius": 3, "typo_budget": 0},
                    {"name": "windowed_r4", "window_radius": 4, "typo_budget": 0},
                    {"name": "shuffled", "window_radius": 100, "typo_budget": 2}
                ]
                
                # Run anchor modes
                mode_results = self.scorer.run_anchor_modes(text, policies)
                
                # Check epsilon bands
                within_0_10 = (
                    abs(mode_results['delta_vs_windowed'] - 0.05) <= 0.10 and
                    abs(mode_results['delta_vs_shuffled'] - 0.10) <= 0.10
                )
                within_0_05 = (
                    abs(mode_results['delta_vs_windowed'] - 0.05) <= 0.05 and
                    abs(mode_results['delta_vs_shuffled'] - 0.10) <= 0.05
                )
                
                # Update statistics
                self.stats['total_processed'] += 1
                if within_0_10:
                    self.stats['within_epsilon_0.10'] += 1
                if within_0_05:
                    self.stats['within_epsilon_0.05'] += 1
                if mode_results['pass_deltas']:
                    self.stats['delta_passers'] += 1
                
                # Write to CSV
                row = {
                    'label': label,
                    'grid': 'v4_track_a',
                    'anchor_mode': mode_results.get('best_mode', 'fixed'),
                    'delta_vs_windowed': mode_results['delta_vs_windowed'],
                    'delta_vs_shuffled': mode_results['delta_vs_shuffled'],
                    'z_ngram_blind': mode_results.get('scores_by_mode', {}).get('fixed', {}).get('z_ngram', 0),
                    'pass_deltas': mode_results['pass_deltas'],
                    'within_eps_0.10': within_0_10,
                    'within_eps_0.05': within_0_05,
                    'repair_improvement': repair_result['repair_improvement'],
                    'saliency_mean': 0  # Would need to pass through
                }
                
                writer.writerow(row)
                explore_results.append({
                    'label': label,
                    'text': text,
                    'mode_results': mode_results,
                    'repair_stats': repair_result['repair_stats'],
                    'epsilon_bands': {
                        '0.10': within_0_10,
                        '0.05': within_0_05
                    }
                })
        
        print(f"\nSaved Explore matrix to {csv_file}")
        
        # Check stop rule
        if self.stats['within_epsilon_0.10'] < 5 and self.stats['total_processed'] >= 100:
            print("\nSTOP RULE TRIGGERED: <5 heads within ε=0.10 after 100 candidates")
        
        return explore_results
    
    def generate_dashboard(self, track_results: Dict, output_dir: Path):
        """
        Generate consolidated dashboard.
        """
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'track': 'A_BLINDED_SALIENCY',
            'statistics': self.stats,
            'summary': {
                'heads_generated': track_results['heads_generated'],
                'heads_processed': track_results['heads_processed'],
                'delta_passers': self.stats['delta_passers'],
                'within_0.10': self.stats['within_epsilon_0.10'],
                'within_0.05': self.stats['within_epsilon_0.05'],
                'pass_rate': self.stats['delta_passers'] / max(1, self.stats['total_processed'])
            }
        }
        
        dashboard_file = output_dir / "DASHBOARD.json"
        with open(dashboard_file, 'w') as f:
            json.dump(dashboard, f, indent=2)
        
        print(f"\nSaved dashboard to {dashboard_file}")
        
        return dashboard
    
    def generate_report(self, track_results: Dict, dashboard: Dict, output_dir: Path):
        """
        Generate Explore report.
        """
        report = []
        report.append("# Explore v4 Track A Report")
        report.append("")
        report.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append(f"**Track:** A - Blinded-first MCMC + Saliency")
        report.append(f"**Seed:** {self.seed}")
        report.append("")
        
        report.append("## Summary")
        report.append("")
        report.append(f"- Heads generated: {track_results['heads_generated']}")
        report.append(f"- Heads processed: {track_results['heads_processed']}")
        report.append(f"- Delta passers: {self.stats['delta_passers']}")
        report.append(f"- Within ε=0.10: {self.stats['within_epsilon_0.10']}")
        report.append(f"- Within ε=0.05: {self.stats['within_epsilon_0.05']}")
        report.append(f"- Pass rate: {dashboard['summary']['pass_rate']:.1%}")
        report.append("")
        
        report.append("## Key Findings")
        report.append("")
        
        if self.stats['delta_passers'] > 0:
            report.append("### ✅ SUCCESS: Found delta passers!")
            report.append("")
            report.append(f"The sensitivity-aware approach successfully generated "
                         f"{self.stats['delta_passers']} heads that pass both delta thresholds.")
        else:
            report.append("### Result: No delta passers")
            report.append("")
            report.append("Despite sensitivity-aware placement and repair, "
                         "no heads passed both delta thresholds.")
        
        report.append("")
        report.append("## Stop Rule Status")
        report.append("")
        
        if self.stats['within_epsilon_0.10'] < 5 and self.stats['total_processed'] >= 100:
            report.append("**TRIGGERED:** <5 heads within ε=0.10 after 100 candidates")
        else:
            report.append("Not triggered")
        
        report.append("")
        report.append("## Recommendations")
        report.append("")
        
        if self.stats['delta_passers'] > 0:
            report.append("1. Move delta passers to orbit analysis")
            report.append("2. Run 1k nulls on stable candidates")
            report.append("3. Consider promotion to Confirm lane")
        elif self.stats['within_epsilon_0.10'] >= 5:
            report.append("1. Continue with Track B (Pareto MCMC)")
            report.append("2. Analyze near-misses for patterns")
            report.append("3. Consider adjusting Pareto weights")
        else:
            report.append("1. Stop Track A (stop rule triggered)")
            report.append("2. Move to Track B/C")
            report.append("3. Consider more aggressive generation")
        
        # Save report
        report_file = output_dir / "EXPLORE_REPORT.md"
        with open(report_file, 'w') as f:
            f.write('\n'.join(report))
        
        print(f"\nSaved report to {report_file}")
        
        return report


def main():
    """Run Track A pipeline."""
    print("=" * 60)
    print("EXPLORE V4 - TRACK A EXECUTION")
    print("=" * 60)
    
    pipeline = ExploreV4Pipeline(seed=1337)
    
    # Run Track A with reduced parameters for testing
    track_results = pipeline.run_track_a(
        n_chains=2,           # Reduced for testing
        mcmc_iterations=1000, # Reduced for testing
        n_heads_to_process=10 # Reduced for testing
    )
    
    # Generate outputs
    output_dir = Path(__file__).parent.parent.parent / "runs" / "track_a"
    dashboard = pipeline.generate_dashboard(track_results, output_dir)
    report = pipeline.generate_report(track_results, dashboard, output_dir)
    
    # Create reproducibility documentation
    repro_file = output_dir / "REPRO_STEPS.md"
    with open(repro_file, 'w') as f:
        f.write("# Reproducibility Steps\n\n")
        f.write(f"**Global Seed:** 1337\n")
        f.write(f"**Branch:** pipeline-v4-explore-sensitivity-20250106\n")
        f.write(f"**Commit:** 9ce4d3b\n\n")
        f.write("## Commands\n\n")
        f.write("```bash\n")
        f.write("cd experiments/pipeline_v4/scripts/v4\n")
        f.write("python3 run_explore_v4.py\n")
        f.write("```\n\n")
        f.write("## Per-worker seeds\n\n")
        f.write("- Chain 0: 1337\n")
        f.write("- Chain 1: 2337\n")
        f.write("- Null worker 0: 1337\n")
        f.write("- Null worker 1: 2337\n")
    
    print("\n" + "=" * 60)
    print("TRACK A COMPLETE")
    print("=" * 60)
    print(f"Delta passers: {pipeline.stats['delta_passers']}")
    print(f"Within ε=0.10: {pipeline.stats['within_epsilon_0.10']}")
    print(f"Within ε=0.05: {pipeline.stats['within_epsilon_0.05']}")
    
    return track_results


if __name__ == "__main__":
    results = main()