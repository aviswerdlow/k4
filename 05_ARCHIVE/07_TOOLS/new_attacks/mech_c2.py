#!/usr/bin/env python3
"""
C2 - Sculpture Physical Properties
Test if physical features (raised/recessed/patina) are intentional constraints.
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

def run_tests(harness):
    """Run physical property tests"""
    results = {
        'tests': [],
        'summary': {
            'mechanism': 'C2_Physical_Properties',
            'total_tests': 0,
            'best_config': None,
            'best_unknown_count': 97,
            'baseline_unknown_count': 50,
            'success': False,
            'data_status': 'placeholder'
        }
    }
    
    # Load physical tags
    with open(f'{harness.doc_path}/COMMON/physical_tags.json', 'r') as f:
        physical_data = json.load(f)
    
    if physical_data.get('placeholder', False):
        print("\nNote: Physical property data not yet available")
        print("Generating synthetic test data for framework validation...")
        
        # Generate synthetic data for testing
        np.random.seed(1337)
        physical_data = generate_synthetic_tags(harness)
    
    # Test 1: Correlation scan
    print("\nTest 1: Correlation analysis with unknown positions")
    correlation_result = test_correlation(harness, physical_data)
    results['tests'].append(correlation_result)
    
    # Test 2: Constraint attempts for meaningful tags
    print("\nTest 2: Testing physical property constraints")
    for tag_name in ['raised', 'recessed', 'patina']:
        if physical_data[tag_name]:
            config = test_physical_constraint(harness, physical_data, tag_name)
            results['tests'].append(config)
            if config['unknown_count'] < results['summary']['best_unknown_count']:
                results['summary']['best_unknown_count'] = config['unknown_count']
                results['summary']['best_config'] = config['test_id']
    
    results['summary']['total_tests'] = len(results['tests'])
    results['summary']['success'] = results['summary']['best_unknown_count'] < 50
    
    if results['summary']['success']:
        results['summary']['conclusion'] = f"Physical properties reduced unknowns to {results['summary']['best_unknown_count']}"
    else:
        results['summary']['conclusion'] = "No physical property correlation found (awaiting real data)"
    
    return results

def generate_synthetic_tags(harness):
    """Generate synthetic physical tags for testing"""
    np.random.seed(1337)
    
    # Create some structure in synthetic data
    raised = sorted(np.random.choice(range(97), 30, replace=False).tolist())
    recessed = sorted(np.random.choice([i for i in range(97) if i not in raised], 25, replace=False).tolist())
    patina = sorted(np.random.choice(range(97), 20, replace=False).tolist())
    angle_marks = [21, 25, 63, 69]  # At anchor starts
    
    return {
        'raised': raised,
        'recessed': recessed,
        'patina': patina,
        'angle_marks': angle_marks,
        'synthetic': True
    }

def test_correlation(harness, physical_data):
    """Test correlation between physical properties and unknowns"""
    unknown_set = set(harness.baseline_data['unknown_indices'])
    
    correlations = {}
    chi_squares = {}
    
    for tag_name in ['raised', 'recessed', 'patina']:
        if not physical_data.get(tag_name):
            continue
            
        tag_set = set(physical_data[tag_name])
        
        # Build contingency table
        # [unknown & tagged, unknown & not tagged]
        # [known & tagged, known & not tagged]
        a = len(unknown_set & tag_set)  # Unknown and tagged
        b = len(unknown_set - tag_set)  # Unknown and not tagged
        c = len(tag_set - unknown_set)  # Known and tagged
        d = 97 - a - b - c              # Known and not tagged
        
        contingency = [[a, b], [c, d]]
        
        # Chi-square test
        if min(a+b, c+d, a+c, b+d) > 0:
            chi2, p_value, _, _ = stats.chi2_contingency(contingency)
            chi_squares[tag_name] = {
                'chi2': chi2,
                'p_value': p_value,
                'correlation': 'significant' if p_value < 0.05 else 'not significant'
            }
        else:
            chi_squares[tag_name] = {
                'chi2': 0,
                'p_value': 1.0,
                'correlation': 'insufficient data'
            }
        
        # Simple overlap percentage
        correlations[tag_name] = {
            'overlap_count': a,
            'overlap_pct': (a / len(unknown_set)) * 100 if unknown_set else 0,
            'tag_count': len(tag_set)
        }
    
    return {
        'test_id': 'correlation_scan',
        'config': 'chi-square analysis',
        'derived_count': 47,
        'unknown_count': 50,
        'anchors_preserved': True,
        'reduction': 0,
        'correlations': correlations,
        'chi_squares': chi_squares
    }

def test_physical_constraint(harness, physical_data, tag_name):
    """Test if a physical property defines a constraint"""
    tag_indices = set(physical_data[tag_name])
    
    # Try family flip for tagged positions only
    L = 17
    wheels = {}
    
    # Initialize wheels
    for c in range(6):
        wheels[c] = {
            'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
            'L': L,
            'residues': [None] * L
        }
    
    # Apply anchor + tail constraints
    all_constraints = harness.get_anchor_positions() | harness.get_tail_positions()
    
    for pos in all_constraints:
        c = harness.compute_class(pos)
        s = pos % L
        
        # Flip family if position is tagged
        family = wheels[c]['family']
        if pos in tag_indices:
            family = 'beaufort' if family == 'vigenere' else 'vigenere'
        
        c_char = harness.ciphertext[pos]
        p_char = harness.canonical_pt[pos]
        
        c_val = ord(c_char) - ord('A')
        p_val = ord(p_char) - ord('A')
        
        if family == 'vigenere':
            k_val = (c_val - p_val) % 26
        else:
            k_val = (p_val + c_val) % 26
        
        wheels[c]['residues'][s] = k_val
    
    plaintext, derived_count, unknown_indices = harness.derive_plaintext(wheels, L)
    anchors_ok = harness.validate_anchors(plaintext)
    
    return {
        'test_id': f'physical_{tag_name}_flip',
        'config': f'Family flip for {tag_name} positions',
        'derived_count': derived_count,
        'unknown_count': len(unknown_indices),
        'anchors_preserved': anchors_ok,
        'reduction': 50 - len(unknown_indices),
        'tag_count': len(tag_indices)
    }

def generate_pdf(results, output_dir):
    """Generate one-page PDF summary"""
    fig = plt.figure(figsize=(8.5, 11))
    
    # Title
    fig.text(0.5, 0.95, 'C2: Sculpture Physical Properties', 
             fontsize=16, weight='bold', ha='center')
    
    # Data status warning
    if results['summary']['data_status'] == 'placeholder':
        fig.text(0.5, 0.90, '(Using synthetic data - awaiting real physical tags)', 
                fontsize=10, style='italic', ha='center', color='red')
    
    # Correlation results
    ax1 = plt.subplot(2, 2, 1)
    ax1.set_title('Property Correlations', fontsize=12)
    
    # Extract correlation data from first test
    if results['tests'] and 'correlations' in results['tests'][0]:
        corr_data = results['tests'][0]['correlations']
        tags = list(corr_data.keys())
        overlaps = [corr_data[t]['overlap_pct'] for t in tags]
        
        ax1.bar(tags, overlaps, color=['coral', 'lightblue', 'lightgreen'])
        ax1.set_ylabel('Overlap with Unknowns (%)')
        ax1.set_ylim(0, 100)
        ax1.grid(True, alpha=0.3)
    else:
        ax1.text(0.5, 0.5, 'No correlation data', ha='center', va='center')
    
    # Chi-square results
    ax2 = plt.subplot(2, 2, 2)
    ax2.axis('off')
    
    chi_text = "Chi-Square Tests:\n\n"
    if results['tests'] and 'chi_squares' in results['tests'][0]:
        chi_data = results['tests'][0]['chi_squares']
        for tag, stats in chi_data.items():
            chi_text += f"{tag}: χ²={stats['chi2']:.2f}, p={stats['p_value']:.3f}\n"
            chi_text += f"  → {stats['correlation']}\n\n"
    else:
        chi_text += "No test data available"
    
    ax2.text(0.1, 0.5, chi_text, fontsize=9, va='center', family='monospace')
    
    # Results summary
    ax3 = plt.subplot(2, 1, 2)
    ax3.axis('off')
    
    summary_text = f"""
Summary:
--------
Tests Run: {results['summary']['total_tests']}
Best Config: {results['summary']['best_config']}
Best Unknown Count: {results['summary']['best_unknown_count']} (baseline: 50)
Success: {'YES' if results['summary']['success'] else 'NO'}

Conclusion: {results['summary']['conclusion']}

Note: Physical property analysis requires actual sculpture measurements.
      This test framework is ready for real data when available.
"""
    ax3.text(0.1, 0.5, summary_text, fontsize=10, va='center', family='monospace')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/C2_results.pdf', format='pdf', bbox_inches='tight')
    plt.close()
    
    print(f"Generated {output_dir}/C2_results.pdf")