#!/usr/bin/env python3
"""
Mask Discovery - Automated pattern detection for K4 ciphertext
"""

import json
import argparse
from collections import Counter
from pathlib import Path
import sys
import os

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def analyze_periodicity(text: str, max_period: int = 12) -> dict:
    """Analyze text for periodic patterns"""
    results = {}
    
    for period in range(2, max_period + 1):
        # Split text into period groups
        groups = [[] for _ in range(period)]
        for i, char in enumerate(text):
            groups[i % period].append(char)
        
        # Analyze each group's frequency distribution
        group_stats = []
        for group in groups:
            freq = Counter(group)
            entropy = -sum((c/len(group)) * (c/len(group)) for c in freq.values() if c > 0)
            group_stats.append({
                'size': len(group),
                'unique': len(freq),
                'entropy': entropy,
                'top_chars': freq.most_common(3)
            })
        
        # Calculate variance in entropy across groups
        entropies = [g['entropy'] for g in group_stats]
        mean_entropy = sum(entropies) / len(entropies)
        variance = sum((e - mean_entropy) ** 2 for e in entropies) / len(entropies)
        
        results[period] = {
            'variance': variance,
            'mean_entropy': mean_entropy,
            'groups': group_stats
        }
    
    return results


def analyze_diagonal_patterns(text: str, rows: int = 7, cols: int = 14) -> dict:
    """Analyze diagonal patterns in grid arrangement"""
    # Create grid
    grid = []
    idx = 0
    for r in range(rows):
        row = []
        for c in range(cols):
            if idx < len(text):
                row.append(text[idx])
                idx += 1
            else:
                row.append('')
        grid.append(row)
    
    results = {}
    
    # Test different diagonal steps
    steps = [(1, 1), (1, 2), (2, 1), (1, -1)]
    
    for step in steps:
        diagonals = []
        
        # Starting points
        if step[1] >= 0:
            starts = [(0, c) for c in range(cols)] + [(r, 0) for r in range(1, rows)]
        else:
            starts = [(0, c) for c in range(cols)] + [(r, cols-1) for r in range(1, rows)]
        
        for start_r, start_c in starts:
            diagonal = []
            r, c = start_r, start_c
            
            while 0 <= r < rows and 0 <= c < cols:
                if grid[r][c]:
                    diagonal.append(grid[r][c])
                r += step[0]
                c += step[1]
            
            if diagonal:
                diagonals.append(''.join(diagonal))
        
        # Analyze diagonal patterns
        freq_analysis = []
        for diag in diagonals:
            freq = Counter(diag)
            freq_analysis.append({
                'length': len(diag),
                'unique': len(freq),
                'pattern': diag[:10] + '...' if len(diag) > 10 else diag
            })
        
        results[str(step)] = {
            'diagonal_count': len(diagonals),
            'analysis': freq_analysis[:5]  # First 5 diagonals
        }
    
    return results


def discover_berlinclock_mask(text: str, target_indices: list) -> dict:
    """Discover mask based on BERLINCLOCK positions"""
    target = "BERLINCLOCK"
    
    # Extract characters at target indices
    if all(i < len(text) for i in target_indices):
        extracted = ''.join(text[i] for i in target_indices[:len(target)])
        
        # Try to find a pattern that would transform extracted to target
        # This is a simplified pattern matcher
        patterns = []
        
        # Check if it's already BERLINCLOCK (no mask needed)
        if extracted == target:
            patterns.append({'type': 'none', 'confidence': 1.0})
        
        # Check for simple substitution
        mapping = {}
        for i, (e, t) in enumerate(zip(extracted, target)):
            if e in mapping and mapping[e] != t:
                break
            mapping[e] = t
        else:
            patterns.append({'type': 'substitution', 'mapping': mapping, 'confidence': 0.7})
        
        return {
            'extracted': extracted,
            'target': target,
            'patterns': patterns
        }
    
    return {'error': 'Invalid indices'}


def main():
    parser = argparse.ArgumentParser(description='Discover masks in K4 ciphertext')
    parser.add_argument('--ct', required=True, help='Path to ciphertext file')
    parser.add_argument('--out', required=True, help='Output directory for reports')
    parser.add_argument('--zones', action='store_true', help='Analyze by zones')
    
    args = parser.parse_args()
    
    # Load ciphertext
    with open(args.ct, 'r') as f:
        ciphertext = f.read().strip().upper()
    
    print(f"Analyzing ciphertext: {len(ciphertext)} characters")
    
    # Create output directory
    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {
        'ciphertext_length': len(ciphertext),
        'analysis': {}
    }
    
    # Periodicity analysis
    print("Analyzing periodicity...")
    period_results = analyze_periodicity(ciphertext)
    
    # Find best periods (lowest variance)
    best_periods = sorted(period_results.items(), key=lambda x: x[1]['variance'])[:3]
    results['analysis']['periodicity'] = {
        'best_periods': [{'period': p, 'variance': r['variance']} for p, r in best_periods],
        'full_results': period_results
    }
    
    print(f"Best periods: {[p for p, _ in best_periods]}")
    
    # Diagonal pattern analysis
    print("Analyzing diagonal patterns...")
    diag_results = analyze_diagonal_patterns(ciphertext)
    results['analysis']['diagonals'] = diag_results
    
    # BERLINCLOCK mask discovery
    print("Analyzing BERLINCLOCK positions...")
    control_indices = list(range(64, 74))
    berlin_results = discover_berlinclock_mask(ciphertext, control_indices)
    results['analysis']['berlinclock'] = berlin_results
    
    # Zone analysis if requested
    if args.zones:
        print("Analyzing zones...")
        zones = {
            'head': (0, 20),
            'mid': (34, 62),
            'tail': (74, 96)
        }
        
        zone_results = {}
        for zone_name, (start, end) in zones.items():
            zone_text = ciphertext[start:end+1]
            zone_results[zone_name] = {
                'length': len(zone_text),
                'periodicity': analyze_periodicity(zone_text, 6)
            }
        
        results['analysis']['zones'] = zone_results
    
    # Generate recommended masks
    recommendations = []
    
    # Based on periodicity
    for period, _ in best_periods[:2]:
        recommendations.append({
            'type': f'period{period}',
            'params': {'period': period},
            'reason': f'Low variance at period {period}'
        })
    
    # Based on grid structure
    recommendations.append({
        'type': 'diag_weave',
        'params': {'rows': 7, 'cols': 14, 'step': [1, 1]},
        'reason': 'Standard diagonal weave for 7x14 grid'
    })
    
    results['recommendations'] = recommendations
    
    # Save results
    output_file = output_dir / 'mask_discovery_report.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    print(f"\nRecommended masks:")
    for rec in recommendations:
        print(f"  - {rec['type']}: {rec['reason']}")


if __name__ == '__main__':
    main()