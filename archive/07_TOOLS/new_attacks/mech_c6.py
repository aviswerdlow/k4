#!/usr/bin/env python3
"""
C6 - Clock Arithmetic
Test mod-12/mod-60 structures around CLOCK anchor.
"""

import matplotlib.pyplot as plt
import numpy as np

def run_tests(harness):
    """Run clock arithmetic tests"""
    results = {
        'tests': [],
        'summary': {
            'mechanism': 'C6_Clock_Arithmetic',
            'total_tests': 0,
            'best_config': None,
            'best_unknown_count': 97,
            'baseline_unknown_count': 50,
            'success': False
        }
    }
    
    # Test 1: Mod-12 overlay on tail
    print("\nTest 1: Mod-12 overlay on tail indices")
    for offset in [0, 1, 6]:
        config = test_mod_overlay(harness, 12, 'tail', offset)
        results['tests'].append(config)
        if config['unknown_count'] < results['summary']['best_unknown_count']:
            results['summary']['best_unknown_count'] = config['unknown_count']
            results['summary']['best_config'] = config['test_id']
    
    # Test 2: Mod-60 on head unknowns
    print("\nTest 2: Mod-60 overlay on head unknowns")
    for offset in [0, 15, 30, 45]:
        config = test_mod_overlay(harness, 60, 'head_unknowns', offset)
        results['tests'].append(config)
        if config['unknown_count'] < results['summary']['best_unknown_count']:
            results['summary']['best_unknown_count'] = config['unknown_count']
            results['summary']['best_config'] = config['test_id']
    
    # Test 3: Clock-face transposition on tail
    print("\nTest 3: Clock-face transposition patterns")
    for pattern in ['rotate_3', 'rotate_6', 'mirror_12', 'spiral']:
        config = test_clock_transposition(harness, pattern)
        results['tests'].append(config)
        if config['unknown_count'] < results['summary']['best_unknown_count']:
            results['summary']['best_unknown_count'] = config['unknown_count']
            results['summary']['best_config'] = config['test_id']
    
    # Test 4: Mod-12 on regions around CLOCK
    print("\nTest 4: Mod-12 around CLOCK anchor")
    for radius in [5, 10, 15]:
        config = test_clock_region(harness, radius)
        results['tests'].append(config)
        if config['unknown_count'] < results['summary']['best_unknown_count']:
            results['summary']['best_unknown_count'] = config['unknown_count']
            results['summary']['best_config'] = config['test_id']
    
    results['summary']['total_tests'] = len(results['tests'])
    results['summary']['success'] = results['summary']['best_unknown_count'] < 50
    
    if results['summary']['success']:
        results['summary']['conclusion'] = f"Clock arithmetic reduced unknowns to {results['summary']['best_unknown_count']}"
    else:
        results['summary']['conclusion'] = "No clock-based mechanism reduced unknowns"
    
    return results

def test_mod_overlay(harness, modulus, target, offset):
    """Test modular overlay on specific region"""
    L = 17
    wheels = harness.build_baseline_wheels(use_tail=True)
    
    # Determine target indices
    if target == 'tail':
        target_indices = set(range(74, 97))
    elif target == 'head_unknowns':
        target_indices = set(harness.baseline_data['unknown_indices']) & set(range(74))
    else:
        target_indices = set()
    
    # Apply modular overlay
    for idx in target_indices:
        c = harness.compute_class(idx)
        s = idx % L
        
        # Calculate modular shift
        shift = ((idx - offset) % modulus)
        
        if wheels[c]['residues'][s] is not None:
            # Apply shift
            wheels[c]['residues'][s] = (wheels[c]['residues'][s] + shift) % 26
    
    # Derive plaintext
    plaintext, derived_count, unknown_indices = harness.derive_plaintext(wheels, L)
    
    # Validate
    anchors_ok = harness.validate_anchors(plaintext)
    
    return {
        'test_id': f'mod{modulus}_{target}_off{offset}',
        'config': f'mod-{modulus} on {target}, offset={offset}',
        'derived_count': derived_count,
        'unknown_count': len(unknown_indices),
        'anchors_preserved': anchors_ok,
        'reduction': 50 - len(unknown_indices)
    }

def test_clock_transposition(harness, pattern):
    """Test clock-face transposition patterns"""
    L = 17
    
    # Build baseline wheels
    wheels = harness.build_baseline_wheels(use_tail=False)
    
    # Apply tail constraints with transposition
    tail_positions = list(range(74, 97))
    tail_plaintext = list(harness.canonical_pt[74:97])
    
    # Apply transposition pattern
    if pattern == 'rotate_3':
        # Rotate by 3 positions (quarter turn on 12-hour clock)
        transposed = tail_plaintext[3:] + tail_plaintext[:3]
    elif pattern == 'rotate_6':
        # Rotate by 6 (half turn)
        transposed = tail_plaintext[6:] + tail_plaintext[:6]
    elif pattern == 'mirror_12':
        # Mirror around 12 o'clock position
        transposed = tail_plaintext[::-1]
    elif pattern == 'spiral':
        # Spiral pattern (take every 3rd)
        indices = [(i * 3) % 23 for i in range(23)]
        transposed = [tail_plaintext[i] for i in indices]
    else:
        transposed = tail_plaintext
    
    # Apply transposed tail
    for i, pos in enumerate(tail_positions):
        c = harness.compute_class(pos)
        s = pos % L
        
        c_char = harness.ciphertext[pos]
        p_char = transposed[i]
        
        c_val = ord(c_char) - ord('A')
        p_val = ord(p_char) - ord('A')
        
        if wheels[c]['family'] == 'vigenere':
            k_val = (c_val - p_val) % 26
        else:
            k_val = (p_val + c_val) % 26
        
        wheels[c]['residues'][s] = k_val
    
    # Derive plaintext
    plaintext, derived_count, unknown_indices = harness.derive_plaintext(wheels, L)
    
    # Validate
    anchors_ok = harness.validate_anchors(plaintext)
    
    return {
        'test_id': f'clock_trans_{pattern}',
        'config': f'clock transposition: {pattern}',
        'derived_count': derived_count,
        'unknown_count': len(unknown_indices),
        'anchors_preserved': anchors_ok,
        'reduction': 50 - len(unknown_indices)
    }

def test_clock_region(harness, radius):
    """Test mod-12 effects in region around CLOCK"""
    L = 17
    wheels = harness.build_baseline_wheels(use_tail=True)
    
    # CLOCK is at 69-73, center at 71
    center = 71
    target_indices = set()
    
    for idx in range(97):
        if abs(idx - center) <= radius:
            target_indices.add(idx)
    
    # Apply mod-12 shift based on distance from center
    for idx in target_indices:
        c = harness.compute_class(idx)
        s = idx % L
        
        # Clock-based shift
        distance = abs(idx - center)
        shift = distance % 12
        
        if wheels[c]['residues'][s] is not None:
            wheels[c]['residues'][s] = (wheels[c]['residues'][s] + shift) % 26
    
    # Derive plaintext
    plaintext, derived_count, unknown_indices = harness.derive_plaintext(wheels, L)
    
    # Validate
    anchors_ok = harness.validate_anchors(plaintext)
    
    return {
        'test_id': f'clock_region_r{radius}',
        'config': f'mod-12 region, radius={radius} around CLOCK',
        'derived_count': derived_count,
        'unknown_count': len(unknown_indices),
        'anchors_preserved': anchors_ok,
        'reduction': 50 - len(unknown_indices),
        'region_size': len(target_indices)
    }

def generate_pdf(results, output_dir):
    """Generate one-page PDF summary"""
    fig = plt.figure(figsize=(8.5, 11))
    
    # Title
    fig.text(0.5, 0.95, 'C6: Clock Arithmetic Tests', 
             fontsize=16, weight='bold', ha='center')
    
    # Clock face visualization
    ax1 = plt.subplot(2, 2, 1)
    ax1.set_title('Clock Face Mapping', fontsize=10)
    ax1.set_aspect('equal')
    
    # Draw clock face
    theta = np.linspace(0, 2*np.pi, 13)
    x = np.cos(theta - np.pi/2)
    y = np.sin(theta - np.pi/2)
    
    ax1.plot(x, y, 'ko-', markersize=8)
    for i in range(12):
        hour = (i + 11) % 12 + 1
        ax1.text(x[i]*1.15, y[i]*1.15, str(hour), ha='center', va='center')
    
    ax1.set_xlim(-1.5, 1.5)
    ax1.set_ylim(-1.5, 1.5)
    ax1.axis('off')
    
    # Mod patterns tested
    ax2 = plt.subplot(2, 2, 2)
    ax2.set_title('Modular Overlay Results', fontsize=10)
    
    mod_tests = [t for t in results['tests'] if t['test_id'].startswith('mod')]
    if mod_tests:
        labels = [t['test_id'].split('_')[0] for t in mod_tests]
        unknowns = [t['unknown_count'] for t in mod_tests]
        
        ax2.barh(range(len(labels)), unknowns, color='lightblue')
        ax2.set_yticks(range(len(labels)))
        ax2.set_yticklabels(labels, fontsize=8)
        ax2.set_xlabel('Unknown Count')
        ax2.axvline(x=50, color='red', linestyle='--', label='Baseline')
        ax2.legend()
    
    # Transposition results
    ax3 = plt.subplot(2, 2, 3)
    ax3.set_title('Transposition Patterns', fontsize=10)
    
    trans_tests = [t for t in results['tests'] if 'trans' in t['test_id']]
    if trans_tests:
        patterns = [t['test_id'].split('_')[-1] for t in trans_tests]
        unknowns = [t['unknown_count'] for t in trans_tests]
        
        ax3.bar(range(len(patterns)), unknowns, color='coral')
        ax3.set_xticks(range(len(patterns)))
        ax3.set_xticklabels(patterns, rotation=45, ha='right')
        ax3.set_ylabel('Unknown Count')
        ax3.axhline(y=50, color='red', linestyle='--')
    
    # Summary
    ax4 = plt.subplot(2, 2, 4)
    ax4.axis('off')
    
    summary_text = f"""
Summary:
--------
Tests: {results['summary']['total_tests']}
Best: {results['summary']['best_config']}
Unknowns: {results['summary']['best_unknown_count']}
Success: {'YES' if results['summary']['success'] else 'NO'}

{results['summary']['conclusion']}

Tested:
• Mod-12/60 overlays
• Clock transpositions
• Regional mod effects
"""
    
    ax4.text(0.1, 0.5, summary_text, fontsize=9, va='center', family='monospace')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/C6_results.pdf', format='pdf', bbox_inches='tight')
    plt.close()
    
    print(f"Generated {output_dir}/C6_results.pdf")