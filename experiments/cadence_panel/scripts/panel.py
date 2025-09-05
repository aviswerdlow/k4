#!/usr/bin/env python3
"""
panel.py - Main driver for cadence panel analysis
Compares candidate heads to K1-K3 style metrics
"""

import json
import argparse
import csv
import sys
import os
from pathlib import Path
from datetime import datetime
import numpy as np

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from metrics import (
    compute_all_metrics,
    compute_z_scores,
    compute_combined_score,
    load_function_words
)


def load_reference_metrics(ref_path):
    """Load reference metrics from bootstrap analysis"""
    with open(ref_path, 'r') as f:
        return json.load(f)


def load_candidate_heads(heads_dir):
    """
    Load all candidate head files from directory.
    
    Returns:
        dict: label -> head_text mapping
    """
    heads = {}
    heads_path = Path(heads_dir)
    
    for head_file in heads_path.glob('*.txt'):
        label = head_file.stem
        with open(head_file, 'r') as f:
            head_text = f.read().strip()
        
        # Ensure exactly 75 characters
        if len(head_text) < 75:
            print(f"Warning: {label} has {len(head_text)} chars, padding with spaces")
            head_text = head_text.ljust(75)
        elif len(head_text) > 75:
            print(f"Warning: {label} has {len(head_text)} chars, truncating to 75")
            head_text = head_text[:75]
        
        heads[label] = head_text
    
    return heads


def generate_report(results, ref_data, output_dir):
    """
    Generate markdown report with tables and narrative.
    
    Args:
        results: list of result dicts for each candidate
        ref_data: reference metrics data
        output_dir: where to save the report
    """
    report_lines = []
    
    # Header
    report_lines.append("# Cadence Panel Report")
    report_lines.append(f"\nGenerated: {datetime.now().isoformat()}")
    report_lines.append(f"\nReference parameters:")
    report_lines.append(f"- Bootstrap windows: {ref_data['parameters']['n_windows_per_k']} per K text")
    report_lines.append(f"- Window size: {ref_data['parameters']['window_size']} tokens")
    report_lines.append(f"- Seed: {ref_data['parameters']['seed']}")
    report_lines.append(f"- Total reference windows: {ref_data['parameters']['total_windows']}")
    
    # Executive Summary
    report_lines.append("\n## Executive Summary")
    report_lines.append("\nThis panel compares candidate K4 heads to the style of K1-K3 using multiple metrics.")
    report_lines.append("**This is a report-only analysis and does not change any gating decisions.**")
    
    # Sort results by CCS score
    results_sorted = sorted(results, key=lambda x: x['ccs'], reverse=True)
    
    # Summary Table
    report_lines.append("\n## Combined Cadence Scores (CCS)")
    report_lines.append("\n| Candidate | CCS | J_content | J_content_lev1 | Cosine_Bi | Cosine_Tri | Has_Quirks |")
    report_lines.append("|-----------|-----|-----------|----------------|-----------|------------|------------|")
    
    for r in results_sorted:
        quirks_str = "Yes" if r['metrics']['has_quirks'] else "No"
        report_lines.append(
            f"| {r['label']:<25} | {r['ccs']:>6.3f} | "
            f"{r['metrics']['J_content']:>6.4f} | {r['metrics']['J_content_lev1']:>6.4f} | "
            f"{r['metrics']['cosine_bigram']:>6.4f} | {r['metrics']['cosine_trigram']:>6.4f} | "
            f"{quirks_str:^10} |"
        )
    
    # Detailed Metrics Table
    report_lines.append("\n## Detailed Metrics (Raw Values)")
    report_lines.append("\n| Candidate | χ²_WordLen | JS_WordLen | V:C_Ratio | FW_Mean_Gap | FW_CV | X/100 |")
    report_lines.append("|-----------|------------|------------|-----------|-------------|-------|-------|")
    
    for r in results_sorted:
        m = r['metrics']
        report_lines.append(
            f"| {r['label']:<25} | {m['chi2_wordlen']:>7.4f} | {m['js_wordlen']:>7.4f} | "
            f"{m.get('vc_ratio', m.get('vc_vc_ratio', 0)):>6.3f} | {m['fw_mean_gap']:>7.2f} | {m['fw_cv']:>5.3f} | "
            f"{m['x_per_100_head']:>5.2f} |"
        )
    
    # Z-Scores Table
    report_lines.append("\n## Z-Scores (Deviation from K1-K3)")
    report_lines.append("\n| Candidate | z_J_content | z_Cosine_Bi | z_Cosine_Tri | z_χ²_WordLen | z_V:C | z_FW_Gap |")
    report_lines.append("|-----------|-------------|-------------|--------------|--------------|-------|----------|")
    
    for r in results_sorted:
        z = r['z_scores']
        report_lines.append(
            f"| {r['label']:<25} | "
            f"{z.get('z_J_content', 0):>+7.3f} | "
            f"{z.get('z_cosine_bigram', 0):>+7.3f} | "
            f"{z.get('z_cosine_trigram', 0):>+7.3f} | "
            f"{z.get('z_chi2_wordlen', 0):>+7.3f} | "
            f"{z.get('z_vc_ratio', z.get('z_vc_vc_ratio', 0)):>+6.3f} | "
            f"{z.get('z_fw_mean_gap', 0):>+6.3f} |"
        )
    
    # Orthographic Quirks Analysis
    report_lines.append("\n## Orthographic Quirks Analysis")
    
    any_quirks = any(r['quirks_detail']['has_quirks'] for r in results)
    if not any_quirks:
        report_lines.append("\nNo K-style orthographic quirks detected in any candidate.")
    else:
        for r in results_sorted:
            if r['quirks_detail']['has_quirks'] or r['quirks_detail']['quirks_recovered']:
                report_lines.append(f"\n### {r['label']}")
                if r['quirks_detail']['quirks_found']:
                    report_lines.append(f"- Direct quirks found: {r['quirks_detail']['quirks_found']}")
                if r['quirks_detail']['quirks_recovered']:
                    report_lines.append(f"- Distance-1 recoveries: {r['quirks_detail']['quirks_recovered']}")
    
    # CCS Weight Documentation
    report_lines.append("\n## Combined Cadence Score (CCS) Weights")
    report_lines.append("\nThe CCS is computed as a weighted sum of z-scores:")
    report_lines.append("```")
    report_lines.append("CCS = 0.25*z(J_content) + 0.10*z(J_content_lev1)")
    report_lines.append("    + 0.20*z(cosine_bigram) + 0.15*z(cosine_trigram)")
    report_lines.append("    - 0.10*|z(χ²_wordlen)| - 0.10*|z(V:C_ratio)|")
    report_lines.append("    - 0.05*|z(FW_mean_gap)| - 0.05*|z(FW_CV)|")
    report_lines.append("```")
    
    # Notes
    report_lines.append("\n## Notes")
    report_lines.append("\n1. All metrics computed on head positions 0-74 only (seam excluded)")
    report_lines.append("2. Tokenization uses canonical cuts with no inferred splits")
    report_lines.append("3. Reference distributions from 2000 bootstrap windows per K text")
    report_lines.append("4. Levenshtein-1 tolerance included as secondary metric only")
    report_lines.append("5. This analysis is report-only and does not change gating decisions")
    
    # Write report
    report_path = Path(output_dir) / "CADENCE_PANEL_REPORT.md"
    with open(report_path, 'w') as f:
        f.write('\n'.join(report_lines))
    
    print(f"Report written to: {report_path}")
    
    return report_path


def main():
    parser = argparse.ArgumentParser(description='Run cadence panel analysis')
    parser.add_argument('--heads_dir', required=True, help='Directory with candidate head files')
    parser.add_argument('--ref', required=True, help='Path to reference metrics JSON')
    parser.add_argument('--cuts', required=True, help='Path to canonical_cuts.json')
    parser.add_argument('--fwords', required=True, help='Path to function_words.txt')
    parser.add_argument('--k1', default='experiments/cadence_panel/data/K1.txt', help='Path to K1.txt')
    parser.add_argument('--k2', default='experiments/cadence_panel/data/K2.txt', help='Path to K2.txt')
    parser.add_argument('--k3', default='experiments/cadence_panel/data/K3.txt', help='Path to K3.txt')
    parser.add_argument('--out', required=True, help='Output directory')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load reference metrics
    print("Loading reference metrics...")
    ref_data = load_reference_metrics(args.ref)
    ref_stats = ref_data['reference_stats']
    
    # Load K texts
    k_texts = []
    for kfile in [args.k1, args.k2, args.k3]:
        with open(kfile, 'r') as f:
            k_texts.append(f.read())
    
    # Load candidate heads
    print("Loading candidate heads...")
    heads = load_candidate_heads(args.heads_dir)
    print(f"Found {len(heads)} candidate heads")
    
    # Process each candidate
    results = []
    
    for label, head_text in heads.items():
        print(f"\nProcessing: {label}")
        
        # Compute metrics
        metrics, quirks_detail = compute_all_metrics(
            head_text, k_texts, args.cuts, args.fwords
        )
        
        # Add Jaccard metrics against K vocabulary
        # These need special handling since they compare to full K vocab
        k_vocab = set(ref_stats.get('k_vocab', []))
        if k_vocab:
            # Simplified computation for reference
            # In practice, these would be computed in compute_all_metrics
            # For now, use existing values
            pass
        
        # Compute z-scores
        z_scores = compute_z_scores(metrics, ref_stats)
        
        # Compute CCS
        ccs = compute_combined_score(metrics, z_scores)
        
        # Store results
        results.append({
            'label': label,
            'metrics': metrics,
            'z_scores': z_scores,
            'ccs': ccs,
            'quirks_detail': quirks_detail
        })
        
        print(f"  CCS: {ccs:.3f}")
    
    # Save summary CSV
    csv_path = output_dir / "cadence_panel_summary.csv"
    
    with open(csv_path, 'w', newline='') as f:
        # Prepare fieldnames
        if results:
            fieldnames = ['label', 'ccs'] + list(results[0]['metrics'].keys())
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for r in results:
                row = {'label': r['label'], 'ccs': r['ccs']}
                row.update(r['metrics'])
                writer.writerow(row)
    
    print(f"\nSummary CSV written to: {csv_path}")
    
    # Generate report
    report_path = generate_report(results, ref_data, output_dir)
    
    # Save detailed JSON results
    json_path = output_dir / "cadence_panel_detailed.json"
    with open(json_path, 'w') as f:
        json.dump({
            'generated': datetime.now().isoformat(),
            'parameters': {
                'heads_dir': str(args.heads_dir),
                'ref_path': str(args.ref),
                'cuts_path': str(args.cuts),
                'fwords_path': str(args.fwords)
            },
            'results': results
        }, f, indent=2)
    
    print(f"Detailed JSON written to: {json_path}")
    
    # Print summary
    print("\n" + "="*60)
    print("CADENCE PANEL ANALYSIS COMPLETE")
    print("="*60)
    print(f"Candidates analyzed: {len(results)}")
    
    # Top 3 by CCS
    results_sorted = sorted(results, key=lambda x: x['ccs'], reverse=True)
    print("\nTop 3 by Combined Cadence Score:")
    for i, r in enumerate(results_sorted[:3], 1):
        print(f"  {i}. {r['label']}: CCS = {r['ccs']:.3f}")
    
    print(f"\nOutputs:")
    print(f"  - Report: {report_path}")
    print(f"  - Summary CSV: {csv_path}")
    print(f"  - Detailed JSON: {json_path}")


if __name__ == '__main__':
    main()