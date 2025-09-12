#!/usr/bin/env python3
"""
C1 - K3 Connection Hypothesis (4×7 DNA)
Test if K3's 4×7 transposition structure matters for K4.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def run_tests(harness):
    """Run K3 connection tests"""
    results = {
        'tests': [],
        'summary': {
            'mechanism': 'C1_K3_Connection',
            'total_tests': 0,
            'best_config': None,
            'best_unknown_count': 97,
            'baseline_unknown_count': 50,
            'success': False
        }
    }
    
    # Test 1: Period 28 (4×7)
    print("\nTest 1: Period L=28 instead of L=17")
    config = test_period_28(harness)
    results['tests'].append(config)
    if config['unknown_count'] < results['summary']['best_unknown_count']:
        results['summary']['best_unknown_count'] = config['unknown_count']
        results['summary']['best_config'] = config['test_id']
    
    # Test 2: Period 7 with 4-fold overlay
    print("\nTest 2: Period L=7 with 4-phase overlay")
    for segment_config in generate_segment_configs():
        config = test_period_7_overlay(harness, segment_config)
        results['tests'].append(config)
        if config['unknown_count'] < results['summary']['best_unknown_count']:
            results['summary']['best_unknown_count'] = config['unknown_count']
            results['summary']['best_config'] = config['test_id']
    
    # Test 3: 4×7 grid patterns
    print("\nTest 3: 4×7 grid class functions")
    for grid_config in generate_grid_configs():
        config = test_grid_pattern(harness, grid_config)
        results['tests'].append(config)
        if config['unknown_count'] < results['summary']['best_unknown_count']:
            results['summary']['best_unknown_count'] = config['unknown_count']
            results['summary']['best_config'] = config['test_id']
    
    results['summary']['total_tests'] = len(results['tests'])
    results['summary']['success'] = results['summary']['best_unknown_count'] < 50
    
    if results['summary']['success']:
        results['summary']['conclusion'] = f"4×7 structure reduced unknowns to {results['summary']['best_unknown_count']}"
    else:
        results['summary']['conclusion'] = "No 4×7 overlay helped under anchor constraints"
    
    return results

def test_period_28(harness):
    """Test L=28 instead of L=17"""
    L = 28
    wheels = {}
    
    # Initialize L=28 wheels
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
        
        c_char = harness.ciphertext[pos]
        p_char = harness.canonical_pt[pos]
        
        c_val = ord(c_char) - ord('A')
        p_val = ord(p_char) - ord('A')
        
        if wheels[c]['family'] == 'vigenere':
            k_val = (c_val - p_val) % 26
        else:
            k_val = (p_val + c_val) % 26
        
        wheels[c]['residues'][s] = k_val
    
    plaintext, derived_count, unknown_indices = harness.derive_plaintext(wheels, L)
    anchors_ok = harness.validate_anchors(plaintext)
    
    return {
        'test_id': 'period_28',
        'config': f'L={L}',
        'derived_count': derived_count,
        'unknown_count': len(unknown_indices),
        'anchors_preserved': anchors_ok,
        'reduction': 50 - len(unknown_indices)
    }

def generate_segment_configs():
    """Generate 4-phase overlay configurations"""
    segments = [
        (0, 20),    # Segment 1
        (21, 33),   # Segment 2 (includes anchors)
        (34, 62),   # Segment 3
        (63, 73)    # Segment 4 (includes anchors)
    ]
    
    # Try a few family toggle patterns
    patterns = [
        [False, False, False, False],  # No toggles
        [True, False, True, False],    # Alternate segments
        [False, True, False, True],    # Other alternate
        [True, True, False, False],    # First half toggled
    ]
    
    configs = []
    for pattern in patterns:
        configs.append({
            'segments': segments,
            'toggles': pattern,
            'name': ''.join(['T' if t else 'F' for t in pattern])
        })
    
    return configs

def test_period_7_overlay(harness, segment_config):
    """Test L=7 with 4-phase overlay"""
    L = 7
    wheels = {}
    
    # Initialize L=7 wheels
    for c in range(6):
        wheels[c] = {
            'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
            'L': L,
            'residues': [None] * L
        }
    
    # Apply constraints with segment-based family toggles
    all_constraints = harness.get_anchor_positions() | harness.get_tail_positions()
    
    for pos in all_constraints:
        c = harness.compute_class(pos)
        s = pos % L
        
        # Determine segment
        segment_idx = 0
        for i, (start, end) in enumerate(segment_config['segments']):
            if start <= pos <= end:
                segment_idx = i
                break
        
        # Apply toggle if needed
        family = wheels[c]['family']
        if segment_config['toggles'][segment_idx]:
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
        'test_id': f'L7_overlay_{segment_config["name"]}',
        'config': f'L=7, toggles={segment_config["name"]}',
        'derived_count': derived_count,
        'unknown_count': len(unknown_indices),
        'anchors_preserved': anchors_ok,
        'reduction': 50 - len(unknown_indices)
    }

def generate_grid_configs():
    """Generate 4×7 grid-based class functions"""
    configs = []
    
    # Different family vectors for 4 rows
    family_vectors = [
        ['V', 'V', 'B', 'V'],
        ['B', 'V', 'B', 'V'],
        ['V', 'B', 'V', 'B'],
        ['B', 'B', 'V', 'V']
    ]
    
    for fv in family_vectors:
        configs.append({
            'rows': 4,
            'cols': 7,
            'families': fv,
            'name': ''.join(fv)
        })
    
    return configs

def test_grid_pattern(harness, grid_config):
    """Test 4×7 grid-based class function"""
    L = 17  # Keep base period
    wheels = {}
    
    # Grid-based class function
    def grid_class(i):
        if i >= 97:
            return 0
        row = (i // grid_config['cols']) % grid_config['rows']
        return row
    
    # Initialize wheels with grid families
    for r in range(grid_config['rows']):
        wheels[r] = {
            'family': 'vigenere' if grid_config['families'][r] == 'V' else 'beaufort',
            'L': L,
            'residues': [None] * L
        }
    
    # Apply constraints
    all_constraints = harness.get_anchor_positions() | harness.get_tail_positions()
    
    for pos in all_constraints:
        c = grid_class(pos)
        s = pos % L
        
        c_char = harness.ciphertext[pos]
        p_char = harness.canonical_pt[pos]
        
        c_val = ord(c_char) - ord('A')
        p_val = ord(p_char) - ord('A')
        
        if wheels[c]['family'] == 'vigenere':
            k_val = (c_val - p_val) % 26
        else:
            k_val = (p_val + c_val) % 26
        
        if wheels[c]['residues'][s] is None:
            wheels[c]['residues'][s] = k_val
    
    # Derive with grid class
    derived = []
    derived_count = 0
    unknown_indices = []
    
    for i in range(97):
        c = grid_class(i)
        s = i % L
        
        if wheels[c]['residues'][s] is not None:
            c_char = harness.ciphertext[i]
            c_val = ord(c_char) - ord('A')
            k_val = wheels[c]['residues'][s]
            
            if wheels[c]['family'] == 'vigenere':
                p_val = (c_val - k_val) % 26
            else:
                p_val = (k_val - c_val) % 26
            
            derived.append(chr(p_val + ord('A')))
            derived_count += 1
        else:
            derived.append('?')
            unknown_indices.append(i)
    
    plaintext = ''.join(derived)
    anchors_ok = harness.validate_anchors(plaintext)
    
    return {
        'test_id': f'grid_4x7_{grid_config["name"]}',
        'config': f'4×7 grid, families={grid_config["name"]}',
        'derived_count': derived_count,
        'unknown_count': len(unknown_indices),
        'anchors_preserved': anchors_ok,
        'reduction': 50 - len(unknown_indices)
    }

def generate_pdf(results, output_dir):
    """Generate one-page PDF summary"""
    fig = plt.figure(figsize=(8.5, 11))
    
    # Title
    fig.text(0.5, 0.95, 'C1: K3 Connection Hypothesis (4×7 DNA)', 
             fontsize=16, weight='bold', ha='center')
    
    # Summary stats
    ax1 = plt.subplot(3, 1, 1)
    ax1.axis('off')
    
    summary_text = f"""
Tests Run: {results['summary']['total_tests']}
Best Config: {results['summary']['best_config']}
Best Unknown Count: {results['summary']['best_unknown_count']} (baseline: 50)
Success: {'YES' if results['summary']['success'] else 'NO'}

Conclusion: {results['summary']['conclusion']}
"""
    ax1.text(0.1, 0.5, summary_text, fontsize=11, va='center', family='monospace')
    
    # Results table
    ax2 = plt.subplot(3, 1, 2)
    ax2.axis('off')
    
    # Find top 5 results
    sorted_tests = sorted(results['tests'], key=lambda x: x['unknown_count'])[:5]
    
    table_data = []
    headers = ['Test ID', 'Config', 'Unknowns', 'Reduction', 'Anchors OK']
    
    for test in sorted_tests:
        table_data.append([
            test['test_id'][:20],
            test['config'][:25],
            str(test['unknown_count']),
            str(test['reduction']),
            '✓' if test['anchors_preserved'] else '✗'
        ])
    
    table = ax2.table(cellText=table_data, colLabels=headers,
                     cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.5)
    
    # Visual diagram
    ax3 = plt.subplot(3, 1, 3)
    ax3.set_title('4×7 Grid Structure', fontsize=12)
    
    # Draw 4×7 grid
    for row in range(4):
        for col in range(7):
            idx = row * 7 + col
            if idx < 28:
                x = col
                y = 3 - row
                
                # Color based on whether it's in first 97 positions
                if idx < 97:
                    color = 'lightblue' if idx in results['tests'][0].get('unknown_indices', []) else 'lightgreen'
                else:
                    color = 'gray'
                
                rect = mpatches.Rectangle((x, y), 0.9, 0.9, 
                                         facecolor=color, edgecolor='black')
                ax3.add_patch(rect)
                ax3.text(x + 0.45, y + 0.45, str(idx), 
                        ha='center', va='center', fontsize=8)
    
    ax3.set_xlim(-0.5, 7.5)
    ax3.set_ylim(-0.5, 4.5)
    ax3.set_aspect('equal')
    ax3.axis('off')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/C1_results.pdf', format='pdf', bbox_inches='tight')
    plt.close()
    
    print(f"Generated {output_dir}/C1_results.pdf")