#!/usr/bin/env python3
"""
C4 - KRYPTOS Keyword
Test if the sculpture's name keys the cipher.
"""

import matplotlib.pyplot as plt

def run_tests(harness):
    """Run KRYPTOS keyword tests"""
    results = {
        'tests': [],
        'summary': {
            'mechanism': 'C4_KRYPTOS_Keyword',
            'total_tests': 0,
            'best_config': None,
            'best_unknown_count': 97,
            'baseline_unknown_count': 50,
            'success': False
        }
    }
    
    keyword = "KRYPTOS"
    
    # Test different overlay modes
    print("\nTesting KRYPTOS keyword overlays...")
    
    # Mode 1: Additive overlay
    for position in ['unknowns_only', 'segment_0_20', 'segment_34_62', 'all_head']:
        config = test_keyword_overlay(harness, keyword, 'additive', position)
        results['tests'].append(config)
        if config['unknown_count'] < results['summary']['best_unknown_count']:
            results['summary']['best_unknown_count'] = config['unknown_count']
            results['summary']['best_config'] = config['test_id']
    
    # Mode 2: Beaufort-style subtraction
    for position in ['unknowns_only', 'segment_0_20', 'segment_34_62']:
        config = test_keyword_overlay(harness, keyword, 'beaufort', position)
        results['tests'].append(config)
        if config['unknown_count'] < results['summary']['best_unknown_count']:
            results['summary']['best_unknown_count'] = config['unknown_count']
            results['summary']['best_config'] = config['test_id']
    
    # Mode 3: XOR-like mod 26 flip
    for position in ['unknowns_only', 'per_class']:
        config = test_keyword_overlay(harness, keyword, 'xor', position)
        results['tests'].append(config)
        if config['unknown_count'] < results['summary']['best_unknown_count']:
            results['summary']['best_unknown_count'] = config['unknown_count']
            results['summary']['best_config'] = config['test_id']
    
    # Test other related keywords
    for kw in ['SANBORN', 'LANGLEY', 'SCHEIDT']:
        config = test_keyword_overlay(harness, kw, 'additive', 'unknowns_only')
        results['tests'].append(config)
        if config['unknown_count'] < results['summary']['best_unknown_count']:
            results['summary']['best_unknown_count'] = config['unknown_count']
            results['summary']['best_config'] = config['test_id']
    
    results['summary']['total_tests'] = len(results['tests'])
    results['summary']['success'] = results['summary']['best_unknown_count'] < 50
    
    if results['summary']['success']:
        results['summary']['conclusion'] = f"Keyword overlay reduced unknowns to {results['summary']['best_unknown_count']}"
    else:
        results['summary']['conclusion'] = "KRYPTOS keyword didn't reduce unknowns under constraints"
    
    return results

def test_keyword_overlay(harness, keyword, mode, position):
    """Test a specific keyword overlay configuration"""
    L = 17
    wheels = harness.build_baseline_wheels(use_tail=True)
    
    # Determine target indices based on position
    if position == 'unknowns_only':
        target_indices = set(harness.baseline_data['unknown_indices'])
        pos_desc = "unknowns"
    elif position == 'segment_0_20':
        target_indices = set(range(21))
        pos_desc = "0-20"
    elif position == 'segment_34_62':
        target_indices = set(range(34, 63))
        pos_desc = "34-62"
    elif position == 'all_head':
        target_indices = set(range(74))
        pos_desc = "head"
    elif position == 'per_class':
        # Apply per class segment
        target_indices = set(range(97))
        pos_desc = "per_class"
    else:
        target_indices = set()
        pos_desc = "none"
    
    # Apply keyword overlay
    keyword_vals = [ord(c) - ord('A') for c in keyword]
    keyword_len = len(keyword_vals)
    
    for idx in target_indices:
        c = harness.compute_class(idx)
        s = idx % L
        
        # Get keyword value for this position
        if position == 'per_class':
            # Use class as offset into keyword
            k_offset = keyword_vals[c % keyword_len]
        else:
            # Use position as offset
            k_offset = keyword_vals[idx % keyword_len]
        
        # Apply based on mode
        if wheels[c]['residues'][s] is not None:
            if mode == 'additive':
                wheels[c]['residues'][s] = (wheels[c]['residues'][s] + k_offset) % 26
            elif mode == 'beaufort':
                wheels[c]['residues'][s] = (wheels[c]['residues'][s] - k_offset) % 26
            elif mode == 'xor':
                wheels[c]['residues'][s] = wheels[c]['residues'][s] ^ k_offset
    
    # Derive plaintext
    plaintext, derived_count, unknown_indices = harness.derive_plaintext(wheels, L)
    
    # Validate
    anchors_ok = harness.validate_anchors(plaintext)
    known_ok = harness.validate_known(plaintext, harness.baseline_data['unknown_indices'])
    
    return {
        'test_id': f'{keyword}_{mode}_{pos_desc}',
        'config': f'keyword={keyword}, mode={mode}, pos={pos_desc}',
        'derived_count': derived_count,
        'unknown_count': len(unknown_indices),
        'anchors_preserved': anchors_ok,
        'known_preserved': known_ok,
        'reduction': 50 - len(unknown_indices)
    }

def generate_pdf(results, output_dir):
    """Generate one-page PDF summary"""
    fig = plt.figure(figsize=(8.5, 11))
    
    # Title
    fig.text(0.5, 0.95, 'C4: KRYPTOS Keyword Tests', 
             fontsize=16, weight='bold', ha='center')
    
    # Results by mode
    ax1 = plt.subplot(2, 1, 1)
    ax1.set_title('Unknown Count by Configuration', fontsize=12)
    
    # Group results by mode
    modes = {}
    for test in results['tests']:
        parts = test['test_id'].split('_')
        if len(parts) >= 2:
            mode = parts[1]
            if mode not in modes:
                modes[mode] = []
            modes[mode].append(test['unknown_count'])
    
    # Plot grouped bar chart
    if modes:
        x_pos = 0
        colors = ['coral', 'lightblue', 'lightgreen', 'plum']
        for i, (mode, counts) in enumerate(modes.items()):
            positions = [x_pos + j*0.2 for j in range(len(counts))]
            ax1.bar(positions, counts, width=0.15, 
                   label=mode, color=colors[i % len(colors)])
            x_pos += len(counts) * 0.2 + 0.5
        
        ax1.axhline(y=50, color='red', linestyle='--', label='Baseline (50)')
        ax1.set_ylabel('Unknown Count')
        ax1.set_xlabel('Test Configurations')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
    
    # Best results table
    ax2 = plt.subplot(2, 1, 2)
    ax2.axis('off')
    
    # Sort and show top 5
    sorted_tests = sorted(results['tests'], key=lambda x: x['unknown_count'])[:5]
    
    table_data = []
    headers = ['Configuration', 'Unknowns', 'Reduction', 'Valid']
    
    for test in sorted_tests:
        valid = '✓' if test['anchors_preserved'] and test.get('known_preserved', True) else '✗'
        table_data.append([
            test['config'][:40],
            str(test['unknown_count']),
            str(test['reduction']),
            valid
        ])
    
    if table_data:
        table = ax2.table(cellText=table_data, colLabels=headers,
                         cellLoc='center', loc='upper center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.5)
    
    # Summary
    summary_text = f"""
Summary:
--------
Tests Run: {results['summary']['total_tests']}
Best Config: {results['summary']['best_config']}
Best Unknown Count: {results['summary']['best_unknown_count']} (baseline: 50)
Success: {'YES' if results['summary']['success'] else 'NO'}

Conclusion: {results['summary']['conclusion']}

Note: Tested KRYPTOS, SANBORN, LANGLEY, SCHEIDT as keywords with
      additive, Beaufort, and XOR modes on various position sets.
"""
    
    fig.text(0.5, 0.15, summary_text, fontsize=10, ha='center', 
            va='center', family='monospace')
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.25)
    plt.savefig(f'{output_dir}/C4_results.pdf', format='pdf', bbox_inches='tight')
    plt.close()
    
    print(f"Generated {output_dir}/C4_results.pdf")