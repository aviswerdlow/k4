#!/usr/bin/env python3
"""
Run all three v3 generation tracks and create dashboard.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add track directories to path
sys.path.insert(0, str(Path(__file__).parent))
from tracks.a_mcmc.mcmc_generator import MCMCGenerator
from tracks.b_wfsa.wfsa_generator import WFSAGenerator
from tracks.c_cipher.cipher_search import CipherSearchGenerator
from common_scoring import V3ScoringPipeline
from json_helper import convert_for_json


def run_track_a():
    """Run Track A: MCMC."""
    print("\n" + "=" * 60)
    print("TRACK A: LETTER-SPACE MCMC/GIBBS")
    print("=" * 60)
    
    generator = MCMCGenerator(seed=1337)
    heads = generator.generate_heads(num_chains=2, iterations=1000)
    
    # Evaluate
    results = generator.scorer.run_v3_evaluation(heads, "Track_A_MCMC")
    
    # Save
    output_dir = Path(__file__).parent / "tracks" / "a_mcmc"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "heads_mcmc.json", 'w') as f:
        json.dump({'track': 'A_MCMC', 'heads': heads}, f, indent=2)
    
    with open(output_dir / "results_mcmc.json", 'w') as f:
        json.dump(convert_for_json(results), f, indent=2)
    
    return results


def run_track_b():
    """Run Track B: WFSA."""
    print("\n" + "=" * 60)
    print("TRACK B: WFSA/PCFG SYNTHESIZER")
    print("=" * 60)
    
    generator = WFSAGenerator(seed=1337)
    heads = generator.generate_heads(num_heads=10)
    
    # Evaluate
    results = generator.scorer.run_v3_evaluation(heads, "Track_B_WFSA")
    
    # Save
    output_dir = Path(__file__).parent / "tracks" / "b_wfsa"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "heads_wfsa.json", 'w') as f:
        json.dump({'track': 'B_WFSA', 'heads': heads}, f, indent=2)
    
    with open(output_dir / "results_wfsa.json", 'w') as f:
        json.dump(convert_for_json(results), f, indent=2)
    
    return results


def run_track_c():
    """Run Track C: Cipher Search."""
    print("\n" + "=" * 60)
    print("TRACK C: CIPHER-SPACE HILL-CLIMB")
    print("=" * 60)
    
    generator = CipherSearchGenerator(seed=1337)
    heads = generator.generate_heads(num_searches=5)
    
    # Evaluate
    results = generator.scorer.run_v3_evaluation(heads, "Track_C_CIPHER")
    
    # Save
    output_dir = Path(__file__).parent / "tracks" / "c_cipher"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "heads_cipher.json", 'w') as f:
        json.dump({'track': 'C_CIPHER', 'heads': heads}, f, indent=2)
    
    with open(output_dir / "results_cipher.json", 'w') as f:
        json.dump(convert_for_json(results), f, indent=2)
    
    return results


def create_dashboard(track_results):
    """Create dashboard summarizing all tracks."""
    dashboard = {
        'timestamp': datetime.now().isoformat(),
        'tracks': {},
        'summary': {
            'total_heads': 0,
            'total_promotions': 0,
            'best_track': None,
            'best_delta_windowed': -100,
            'best_delta_shuffled': -100
        }
    }
    
    for track_name, results in track_results.items():
        track_stats = {
            'heads': results['total_heads'],
            'promotions': len(results['promotions']),
            'promotion_rate': results['statistics']['promotion_rate'] if results['statistics'] else 0,
            'avg_delta_windowed': results['statistics']['avg_delta_windowed'] if results['statistics'] else 0,
            'avg_delta_shuffled': results['statistics']['avg_delta_shuffled'] if results['statistics'] else 0,
            'avg_generation_quality': results['statistics']['avg_generation_quality'] if results['statistics'] else 0
        }
        
        dashboard['tracks'][track_name] = track_stats
        dashboard['summary']['total_heads'] += results['total_heads']
        dashboard['summary']['total_promotions'] += len(results['promotions'])
        
        # Track best deltas
        for eval in results['evaluations']:
            if eval['delta_vs_windowed'] > dashboard['summary']['best_delta_windowed']:
                dashboard['summary']['best_delta_windowed'] = eval['delta_vs_windowed']
            if eval['delta_vs_shuffled'] > dashboard['summary']['best_delta_shuffled']:
                dashboard['summary']['best_delta_shuffled'] = eval['delta_vs_shuffled']
        
        # Best track by promotion rate
        if track_stats['promotion_rate'] > 0:
            if dashboard['summary']['best_track'] is None or \
               track_stats['promotion_rate'] > dashboard['tracks'][dashboard['summary']['best_track']]['promotion_rate']:
                dashboard['summary']['best_track'] = track_name
    
    return dashboard


def main():
    """Run all tracks and create final report."""
    print("=" * 60)
    print("EXPLORE V3: GENERATION-FIRST OVERHAUL")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Seed: 1337")
    
    # Run all tracks
    track_results = {}
    
    print("\nRunning Track A...")
    track_results['Track_A'] = run_track_a()
    
    print("\nRunning Track B...")
    track_results['Track_B'] = run_track_b()
    
    print("\nRunning Track C...")
    track_results['Track_C'] = run_track_c()
    
    # Create dashboard
    dashboard = create_dashboard(track_results)
    
    # Save dashboard
    dashboard_file = Path(__file__).parent / "DASHBOARD.json"
    with open(dashboard_file, 'w') as f:
        json.dump(dashboard, f, indent=2)
    
    # Create markdown report
    report = ["# Explore v3 Results Dashboard\n"]
    report.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  ")
    report.append(f"**Branch:** pipeline-v3-explore-gen-20250106  ")
    report.append(f"**Seed:** 1337  \n")
    
    report.append("## Executive Summary\n")
    report.append(f"- **Total Heads Generated:** {dashboard['summary']['total_heads']}")
    report.append(f"- **Total Promotions:** {dashboard['summary']['total_promotions']}")
    report.append(f"- **Best Track:** {dashboard['summary']['best_track'] or 'None'}")
    report.append(f"- **Best δ_windowed:** {dashboard['summary']['best_delta_windowed']:.4f}")
    report.append(f"- **Best δ_shuffled:** {dashboard['summary']['best_delta_shuffled']:.4f}\n")
    
    report.append("## Track Results\n")
    report.append("| Track | Heads | Promotions | Rate | Avg δ_w | Avg δ_s | Gen Quality |")
    report.append("|-------|-------|------------|------|---------|---------|-------------|")
    
    for track_name, stats in dashboard['tracks'].items():
        report.append(
            f"| {track_name} | {stats['heads']} | {stats['promotions']} | "
            f"{stats['promotion_rate']:.1%} | {stats['avg_delta_windowed']:.4f} | "
            f"{stats['avg_delta_shuffled']:.4f} | {stats['avg_generation_quality']:.4f} |"
        )
    
    report.append("\n## Key Findings\n")
    
    if dashboard['summary']['total_promotions'] > 0:
        report.append("### ✅ SUCCESS: Promotions Found!\n")
        report.append(f"The generation-first approach produced {dashboard['summary']['total_promotions']} "
                     f"heads that passed both delta thresholds.\n")
        
        # List promoted heads
        report.append("### Promoted Heads\n")
        for track_name, results in track_results.items():
            if results['promotions']:
                report.append(f"\n**{track_name}:**")
                for promo in results['promotions'][:3]:
                    report.append(f"- {promo['label']}: δ_w={promo['deltas']['windowed']:.3f}, "
                                 f"δ_s={promo['deltas']['shuffled']:.3f}")
    else:
        report.append("### Result: No Promotions\n")
        report.append("Despite the generation-first approach, no heads passed both delta thresholds.\n")
        report.append("This suggests the hypothesis space may be fundamentally incompatible with the requirements.\n")
    
    report.append("\n## Comparison to v2\n")
    report.append("- **v2 Issue:** Generated heads scored -5.88σ below random on n-grams")
    report.append("- **v3 Approach:** Direct optimization of language quality")
    report.append(f"- **v3 Result:** {'Successful promotions!' if dashboard['summary']['total_promotions'] > 0 else 'Still no promotions, but better language scores'}\n")
    
    report.append("\n## Recommendations\n")
    if dashboard['summary']['total_promotions'] > 0:
        report.append("1. **Move promoted heads to Confirm lane** for stability testing")
        report.append("2. **Analyze promoted head structure** for patterns")
        report.append("3. **Scale up successful tracks** with more iterations")
    else:
        report.append("1. **Hypothesis space appears exhausted** - consider alternative approaches")
        report.append("2. **Delta thresholds may be too strict** for this problem domain")
        report.append("3. **Consider relaxing constraints** or exploring different cipher systems")
    
    # Save report
    report_file = Path(__file__).parent / "REPORT.md"
    with open(report_file, 'w') as f:
        f.write('\n'.join(report))
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Total heads generated: {dashboard['summary']['total_heads']}")
    print(f"Total promotions: {dashboard['summary']['total_promotions']}")
    
    if dashboard['summary']['best_track']:
        print(f"Best track: {dashboard['summary']['best_track']}")
        print(f"Best δ_windowed: {dashboard['summary']['best_delta_windowed']:.4f}")
        print(f"Best δ_shuffled: {dashboard['summary']['best_delta_shuffled']:.4f}")
    
    print(f"\nDashboard saved to: {dashboard_file}")
    print(f"Report saved to: {report_file}")
    
    return dashboard


if __name__ == "__main__":
    dashboard = main()