#!/usr/bin/env python3
"""
Holm adjustment for multiple hypothesis testing.
One-sided right-tail test with add-one correction.
"""

import numpy as np
from typing import List, Dict, Tuple

def compute_raw_p_value(observed_count: int, total_count: int, 
                        add_one: bool = True) -> float:
    """
    Compute raw p-value with add-one correction.
    
    Args:
        observed_count: Number of null values >= observed
        total_count: Total number of null samples
        add_one: Apply add-one correction
    
    Returns:
        Raw p-value
    """
    if add_one:
        return (observed_count + 1) / (total_count + 1)
    else:
        return observed_count / total_count if total_count > 0 else 1.0

def holm_correction(p_values: Dict[str, float], alpha: float = 0.01) -> Dict[str, Dict]:
    """
    Apply Holm correction for multiple hypothesis testing.
    
    Args:
        p_values: Dictionary of metric names to raw p-values
        alpha: Significance threshold
    
    Returns:
        Dictionary with adjusted p-values and decisions
    """
    m = len(p_values)
    
    if m == 0:
        return {}
    
    # Sort p-values
    sorted_metrics = sorted(p_values.items(), key=lambda x: x[1])
    
    results = {}
    
    for i, (metric, p_raw) in enumerate(sorted_metrics):
        # Holm adjustment
        alpha_adjusted = alpha / (m - i)
        p_adjusted = min(p_raw * (m - i), 1.0)
        
        # Decision
        reject = p_adjusted < alpha
        
        results[metric] = {
            'p_raw': p_raw,
            'p_adjusted': p_adjusted,
            'alpha_adjusted': alpha_adjusted,
            'reject_null': reject,
            'rank': i + 1
        }
        
        # If we fail to reject at this step, all remaining fail too
        if not reject:
            for j in range(i + 1, m):
                remaining_metric = sorted_metrics[j][0]
                remaining_p_raw = sorted_metrics[j][1]
                results[remaining_metric] = {
                    'p_raw': remaining_p_raw,
                    'p_adjusted': min(remaining_p_raw * (m - j), 1.0),
                    'alpha_adjusted': alpha / (m - j),
                    'reject_null': False,
                    'rank': j + 1
                }
            break
    
    return results

def run_null_hypothesis_test(observed_metrics: Dict[str, float],
                            null_distributions: Dict[str, List[float]],
                            alpha: float = 0.01,
                            add_one: bool = True) -> Dict:
    """
    Run null hypothesis testing with Holm correction.
    
    Args:
        observed_metrics: Observed metric values
        null_distributions: Lists of null values for each metric
        alpha: Significance threshold
        add_one: Use add-one correction
    
    Returns:
        Complete test results
    """
    # Compute raw p-values
    p_values = {}
    counts = {}
    
    for metric, observed in observed_metrics.items():
        if metric not in null_distributions:
            continue
        
        null_values = null_distributions[metric]
        n_nulls = len(null_values)
        
        # One-sided right-tail test
        n_greater_equal = sum(1 for v in null_values if v >= observed)
        
        p_raw = compute_raw_p_value(n_greater_equal, n_nulls, add_one)
        
        p_values[metric] = p_raw
        counts[metric] = {
            'observed': observed,
            'n_nulls': n_nulls,
            'n_greater_equal': n_greater_equal
        }
    
    # Apply Holm correction
    holm_results = holm_correction(p_values, alpha)
    
    # Combine results
    final_results = {
        'alpha': alpha,
        'add_one_correction': add_one,
        'metrics': {}
    }
    
    for metric in observed_metrics:
        if metric in holm_results:
            final_results['metrics'][metric] = {
                **counts[metric],
                **holm_results[metric]
            }
    
    # Overall decision
    all_rejected = all(
        r.get('reject_null', False) 
        for r in final_results['metrics'].values()
    )
    
    final_results['all_rejected'] = all_rejected
    final_results['publishable'] = all_rejected  # All must pass for publishability
    
    return final_results

def format_holm_report(results: Dict) -> str:
    """
    Format Holm test results as readable report.
    """
    lines = []
    lines.append("HOLM CORRECTION REPORT")
    lines.append("=" * 40)
    lines.append(f"Alpha: {results['alpha']}")
    lines.append(f"Add-one correction: {results['add_one_correction']}")
    lines.append("")
    
    for metric, data in results['metrics'].items():
        lines.append(f"\n{metric}:")
        lines.append(f"  Observed: {data['observed']:.4f}")
        lines.append(f"  Nulls ≥ observed: {data['n_greater_equal']}/{data['n_nulls']}")
        lines.append(f"  Raw p-value: {data['p_raw']:.6f}")
        lines.append(f"  Adjusted p-value: {data['p_adjusted']:.6f}")
        lines.append(f"  Decision: {'REJECT' if data['reject_null'] else 'FAIL TO REJECT'}")
    
    lines.append("")
    lines.append("=" * 40)
    lines.append(f"PUBLISHABLE: {'YES' if results['publishable'] else 'NO'}")
    
    return '\n'.join(lines)

if __name__ == "__main__":
    # Example usage
    observed = {
        'coverage': 0.85,
        'f_words': 12
    }
    
    # Simulated null distributions
    np.random.seed(42)
    null_dists = {
        'coverage': np.random.uniform(0.5, 0.9, 10000).tolist(),
        'f_words': np.random.poisson(8, 10000).tolist()
    }
    
    results = run_null_hypothesis_test(observed, null_dists)
    
    print(format_holm_report(results))