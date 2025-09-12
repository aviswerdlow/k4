#!/usr/bin/env python3
"""
C5 - YAR/RIP Markers
Test if YAR/RIP correspond to mechanism boundaries.
"""

import matplotlib.pyplot as plt

def run_tests(harness):
    """Run YAR/RIP boundary tests"""
    results = {
        'tests': [],
        'summary': {
            'mechanism': 'C5_YAR_RIP_Markers',
            'total_tests': 0,
            'best_config': None,
            'best_unknown_count': 97,
            'baseline_unknown_count': 50,
            'success': False
        }
    }
    
    # Get partial plaintext (47 known positions)
    baseline_wheels = harness.build_baseline_wheels(use_tail=True)
    partial_pt, _, _ = harness.derive_plaintext(baseline_wheels)
    
    # Identify potential boundary positions
    print("\nScanning for potential mechanism boundaries...")
    boundaries = find_potential_boundaries(partial_pt)
    
    # Test each boundary
    for boundary in boundaries:
        # Test family flip at boundary
        config = test_boundary_mechanism(harness, boundary, 'family_flip')
        results['tests'].append(config)
        if config['unknown_count'] < results['summary']['best_unknown_count']:
            results['summary']['best_unknown_count'] = config['unknown_count']
            results['summary']['best_config'] = config['test_id']
        
        # Test short keyword at boundary
        for kw_len in [3, 4, 5]:
            config = test_boundary_mechanism(harness, boundary, f'keyword_{kw_len}')
            results['tests'].append(config)
            if config['unknown_count'] < results['summary']['best_unknown_count']:
                results['summary']['best_unknown_count'] = config['unknown_count']
                results['summary']['best_config'] = config['test_id']
    
    results['summary']['total_tests'] = len(results['tests'])
    results['summary']['boundaries_tested'] = len(boundaries)
    results['summary']['success'] = results['summary']['best_unknown_count'] < 50
    
    if results['summary']['success']:
        results['summary']['conclusion'] = f"Boundary mechanism reduced unknowns to {results['summary']['best_unknown_count']}"
    else:
        results['summary']['conclusion'] = "No boundary mechanism reduced unknowns"
    
    return results

def find_potential_boundaries(partial_pt):
    """Find positions where mechanism changes could occur"""
    boundaries = []
    
    # Known anchor boundaries
    boundaries.extend([21, 25, 34, 63, 69, 74])
    
    # Look for patterns in known regions
    # Check for repeated characters or patterns that might indicate boundaries
    for i in range(1, len(partial_pt) - 1):
        if partial_pt[i] != '?':
            # Check for character repetition
            if i > 0 and partial_pt[i] == partial_pt[i-1] and partial_pt[i] != '?':
                boundaries.append(i)
            
            # Check for specific positions that align with structural breaks
            if i in [10, 20, 30, 40, 50, 60, 70, 80, 90]:
                boundaries.append(i)
    
    # Remove duplicates and sort
    boundaries = sorted(list(set(boundaries)))
    
    # Filter to reasonable boundaries (not too close)
    filtered = []
    last = -10
    for b in boundaries:
        if b - last >= 5:  # At least 5 positions apart
            filtered.append(b)
            last = b
    
    return filtered[:10]  # Limit to 10 boundaries

def test_boundary_mechanism(harness, boundary, mechanism_type):
    """Test a mechanism change at a specific boundary"""
    L = 17
    wheels = {}
    
    # Initialize wheels
    for c in range(6):
        wheels[c] = {
            'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
            'L': L,
            'residues': [None] * L
        }
    
    # Apply constraints with mechanism change at boundary
    all_constraints = harness.get_anchor_positions() | harness.get_tail_positions()
    
    for pos in all_constraints:
        c = harness.compute_class(pos)
        s = pos % L
        
        # Determine family based on boundary and mechanism
        family = wheels[c]['family']
        
        if mechanism_type == 'family_flip':
            # Flip family after boundary
            if pos >= boundary:
                family = 'beaufort' if family == 'vigenere' else 'vigenere'
        elif mechanism_type.startswith('keyword_'):
            # Apply dummy keyword after boundary
            kw_len = int(mechanism_type.split('_')[1])
            if pos >= boundary:
                # Simple keyword effect (add position mod kw_len)
                k_shift = (pos - boundary) % kw_len
            else:
                k_shift = 0
        else:
            k_shift = 0
        
        c_char = harness.ciphertext[pos]
        p_char = harness.canonical_pt[pos]
        
        c_val = ord(c_char) - ord('A')
        p_val = ord(p_char) - ord('A')
        
        if mechanism_type.startswith('keyword_') and pos >= boundary:
            # Apply keyword shift
            c_val = (c_val + k_shift) % 26
        
        if family == 'vigenere':
            k_val = (c_val - p_val) % 26
        else:
            k_val = (p_val + c_val) % 26
        
        wheels[c]['residues'][s] = k_val
    
    # Derive plaintext
    plaintext, derived_count, unknown_indices = harness.derive_plaintext(wheels, L)
    
    # Validate
    anchors_ok = harness.validate_anchors(plaintext)
    
    return {
        'test_id': f'boundary_{boundary}_{mechanism_type}',
        'config': f'boundary={boundary}, mech={mechanism_type}',
        'derived_count': derived_count,
        'unknown_count': len(unknown_indices),
        'anchors_preserved': anchors_ok,
        'reduction': 50 - len(unknown_indices),
        'boundary': boundary,
        'mechanism': mechanism_type
    }

def generate_pdf(results, output_dir):
    """Generate one-page PDF summary"""
    fig = plt.figure(figsize=(8.5, 11))
    
    # Title
    fig.text(0.5, 0.95, 'C5: YAR/RIP Boundary Markers', 
             fontsize=16, weight='bold', ha='center')
    
    # Boundary map
    ax1 = plt.subplot(3, 1, 1)
    ax1.set_title('Tested Boundaries', fontsize=12)
    
    # Extract boundaries from tests
    boundaries = list(set(t['boundary'] for t in results['tests'] if 'boundary' in t))
    boundaries.sort()
    
    # Plot boundaries on a line
    ax1.plot([0, 96], [0, 0], 'k-', linewidth=2)
    for b in boundaries:
        ax1.plot([b, b], [-0.5, 0.5], 'r-', linewidth=1)
        ax1.text(b, 0.7, str(b), ha='center', fontsize=8)
    
    # Mark anchors
    anchor_ranges = [(21, 24), (25, 33), (63, 68), (69, 73)]
    for start, end in anchor_ranges:
        ax1.fill_between([start, end], -0.3, 0.3, alpha=0.3, color='green')
    
    ax1.set_xlim(-2, 98)
    ax1.set_ylim(-1, 1)
    ax1.set_xlabel('Position')
    ax1.axis('off')
    
    # Results by mechanism type
    ax2 = plt.subplot(3, 1, 2)
    ax2.set_title('Unknown Count by Mechanism Type', fontsize=12)
    
    # Group by mechanism
    mechs = {}
    for test in results['tests']:
        mech = test.get('mechanism', 'unknown')
        if mech not in mechs:
            mechs[mech] = []
        mechs[mech].append(test['unknown_count'])
    
    if mechs:
        mech_names = list(mechs.keys())
        mech_means = [min(counts) for counts in mechs.values()]  # Best per type
        
        ax2.bar(range(len(mech_names)), mech_means, color='coral')
        ax2.set_xticks(range(len(mech_names)))
        ax2.set_xticklabels(mech_names, rotation=45, ha='right')
        ax2.set_ylabel('Best Unknown Count')
        ax2.axhline(y=50, color='red', linestyle='--', label='Baseline')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    # Summary
    ax3 = plt.subplot(3, 1, 3)
    ax3.axis('off')
    
    summary_text = f"""
Summary:
--------
Tests Run: {results['summary']['total_tests']}
Boundaries Tested: {results['summary']['boundaries_tested']}
Best Config: {results['summary']['best_config']}
Best Unknown Count: {results['summary']['best_unknown_count']} (baseline: 50)
Success: {'YES' if results['summary']['success'] else 'NO'}

Conclusion: {results['summary']['conclusion']}

Note: Tested family flips and keyword overlays at structural boundaries.
      No semantic interpretation of YAR/RIP - purely mechanical tests.
"""
    
    ax3.text(0.1, 0.5, summary_text, fontsize=10, va='center', family='monospace')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/C5_results.pdf', format='pdf', bbox_inches='tight')
    plt.close()
    
    print(f"Generated {output_dir}/C5_results.pdf")