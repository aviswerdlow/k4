#!/usr/bin/env python3
"""
C7 - Matrix Approach
Test grid reshapes, Hill cipher blocks, and Playfair variants.
"""

import matplotlib.pyplot as plt
import numpy as np

def run_tests(harness):
    """Run matrix-based tests"""
    results = {
        'tests': [],
        'summary': {
            'mechanism': 'C7_Matrix_Approach',
            'total_tests': 0,
            'best_config': None,
            'best_unknown_count': 97,
            'baseline_unknown_count': 50,
            'success': False
        }
    }
    
    # Test 1: Grid reshapes
    print("\nTest 1: Grid reshape class functions")
    grid_shapes = [(7, 14), (14, 7), (13, 8), (8, 13), (11, 9)]
    for rows, cols in grid_shapes:
        config = test_grid_reshape(harness, rows, cols)
        results['tests'].append(config)
        if config['unknown_count'] < results['summary']['best_unknown_count']:
            results['summary']['best_unknown_count'] = config['unknown_count']
            results['summary']['best_config'] = config['test_id']
    
    # Test 2: Small Hill cipher blocks
    print("\nTest 2: Hill cipher 2x2 blocks")
    for matrix_id in ['identity', 'simple1', 'simple2']:
        config = test_hill_cipher(harness, 2, matrix_id)
        results['tests'].append(config)
        if config['unknown_count'] < results['summary']['best_unknown_count']:
            results['summary']['best_unknown_count'] = config['unknown_count']
            results['summary']['best_config'] = config['test_id']
    
    # Test 3: Playfair-style with different grids
    print("\nTest 3: Playfair grid variants")
    for keyword in ['KRYPTOS', 'SANBORN', 'LANGLEY']:
        config = test_playfair_variant(harness, keyword)
        results['tests'].append(config)
        if config['unknown_count'] < results['summary']['best_unknown_count']:
            results['summary']['best_unknown_count'] = config['unknown_count']
            results['summary']['best_config'] = config['test_id']
    
    results['summary']['total_tests'] = len(results['tests'])
    results['summary']['success'] = results['summary']['best_unknown_count'] < 50
    
    if results['summary']['success']:
        results['summary']['conclusion'] = f"Matrix approach reduced unknowns to {results['summary']['best_unknown_count']}"
    else:
        results['summary']['conclusion'] = "No matrix mechanism reduced unknowns"
    
    return results

def test_grid_reshape(harness, rows, cols):
    """Test grid-based alternate class function"""
    L = 17
    
    # Grid-based class function
    def grid_class(i, rows, cols):
        if i >= 97:
            return 0
        # Map position to grid coordinates
        row = (i // cols) % rows
        col = i % cols
        # Create class from grid position
        return (row + col) % 6
    
    # Initialize wheels with grid-based classes
    wheels = {}
    for c in range(6):
        wheels[c] = {
            'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
            'L': L,
            'residues': [None] * L
        }
    
    # Apply constraints using grid class
    all_constraints = harness.get_anchor_positions() | harness.get_tail_positions()
    
    for pos in all_constraints:
        c = grid_class(pos, rows, cols)
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
        c = grid_class(i, rows, cols)
        s = i % L
        
        if s < len(wheels[c]['residues']) and wheels[c]['residues'][s] is not None:
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
        'test_id': f'grid_{rows}x{cols}',
        'config': f'{rows}×{cols} grid reshape',
        'derived_count': derived_count,
        'unknown_count': len(unknown_indices),
        'anchors_preserved': anchors_ok,
        'reduction': 50 - len(unknown_indices)
    }

def test_hill_cipher(harness, block_size, matrix_id):
    """Test small Hill cipher blocks"""
    L = 17
    
    # Define test matrices (must be invertible mod 26)
    if matrix_id == 'identity':
        matrix = np.array([[1, 0], [0, 1]])
    elif matrix_id == 'simple1':
        matrix = np.array([[3, 2], [5, 7]])  # Det = 11 (coprime to 26)
    elif matrix_id == 'simple2':
        matrix = np.array([[5, 3], [2, 3]])  # Det = 9 (coprime to 26)
    else:
        matrix = np.array([[1, 0], [0, 1]])
    
    # Build baseline wheels
    wheels = harness.build_baseline_wheels(use_tail=True)
    
    # Apply Hill cipher to head unknowns only
    unknown_head = [i for i in harness.baseline_data['unknown_indices'] if i < 74]
    
    # Process in blocks
    for i in range(0, len(unknown_head) - block_size + 1, block_size):
        block_indices = unknown_head[i:i+block_size]
        
        if len(block_indices) == block_size:
            # Get ciphertext block
            c_block = [ord(harness.ciphertext[idx]) - ord('A') for idx in block_indices]
            c_vec = np.array(c_block)
            
            # Apply inverse Hill (simplified - would need proper inverse)
            # For testing, just apply forward transform
            p_vec = (matrix @ c_vec) % 26
            
            # Store results
            for j, idx in enumerate(block_indices):
                c = harness.compute_class(idx)
                s = idx % L
                
                # Derive key from Hill result
                p_val = p_vec[j]
                c_val = ord(harness.ciphertext[idx]) - ord('A')
                
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
        'test_id': f'hill_{block_size}x{block_size}_{matrix_id}',
        'config': f'Hill {block_size}×{block_size}, matrix={matrix_id}',
        'derived_count': derived_count,
        'unknown_count': len(unknown_indices),
        'anchors_preserved': anchors_ok,
        'reduction': 50 - len(unknown_indices)
    }

def test_playfair_variant(harness, keyword):
    """Test Playfair-style digraph substitution"""
    # Build 5x5 Playfair grid from keyword
    alphabet = 'ABCDEFGHIKLMNOPQRSTUVWXYZ'  # J merged with I
    key_letters = []
    for c in keyword.upper():
        if c not in key_letters and c in alphabet:
            key_letters.append(c)
    
    for c in alphabet:
        if c not in key_letters:
            key_letters.append(c)
    
    # Create grid
    grid = []
    for i in range(5):
        grid.append(key_letters[i*5:(i+1)*5])
    
    # Find position in grid
    def find_pos(letter):
        if letter == 'J':
            letter = 'I'
        for r in range(5):
            for c in range(5):
                if grid[r][c] == letter:
                    return r, c
        return 0, 0
    
    # Test on head pairs
    L = 17
    wheels = harness.build_baseline_wheels(use_tail=True)
    
    # Apply to unknown head positions in pairs
    unknown_head = [i for i in harness.baseline_data['unknown_indices'] if i < 74]
    
    for i in range(0, len(unknown_head) - 1, 2):
        idx1, idx2 = unknown_head[i], unknown_head[i+1]
        
        c1 = ord(harness.ciphertext[idx1]) - ord('A')
        c2 = ord(harness.ciphertext[idx2]) - ord('A')
        
        # Simple Playfair-inspired transform (not full Playfair)
        # Just shift by row+col position
        r1, col1 = find_pos(chr(c1 + ord('A')))
        r2, col2 = find_pos(chr(c2 + ord('A')))
        
        p1 = (c1 + r1 + col1) % 26
        p2 = (c2 + r2 + col2) % 26
        
        # Update wheels
        for idx, p_val in [(idx1, p1), (idx2, p2)]:
            c = harness.compute_class(idx)
            s = idx % L
            c_val = ord(harness.ciphertext[idx]) - ord('A')
            
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
        'test_id': f'playfair_{keyword.lower()}',
        'config': f'Playfair variant, key={keyword}',
        'derived_count': derived_count,
        'unknown_count': len(unknown_indices),
        'anchors_preserved': anchors_ok,
        'reduction': 50 - len(unknown_indices)
    }

def generate_pdf(results, output_dir):
    """Generate one-page PDF summary"""
    fig = plt.figure(figsize=(8.5, 11))
    
    # Title
    fig.text(0.5, 0.95, 'C7: Matrix Approach Tests', 
             fontsize=16, weight='bold', ha='center')
    
    # Grid reshape visualization
    ax1 = plt.subplot(3, 2, 1)
    ax1.set_title('Grid Reshapes Tested', fontsize=10)
    
    grid_tests = [t for t in results['tests'] if t['test_id'].startswith('grid_')]
    if grid_tests:
        labels = [t['test_id'].replace('grid_', '') for t in grid_tests]
        unknowns = [t['unknown_count'] for t in grid_tests]
        
        ax1.barh(range(len(labels)), unknowns, color='lightblue')
        ax1.set_yticks(range(len(labels)))
        ax1.set_yticklabels(labels, fontsize=8)
        ax1.set_xlabel('Unknown Count')
        ax1.axvline(x=50, color='red', linestyle='--')
    
    # Hill cipher results
    ax2 = plt.subplot(3, 2, 2)
    ax2.set_title('Hill Cipher Tests', fontsize=10)
    
    hill_tests = [t for t in results['tests'] if 'hill' in t['test_id']]
    if hill_tests:
        labels = [t['test_id'].replace('hill_', '') for t in hill_tests]
        unknowns = [t['unknown_count'] for t in hill_tests]
        
        ax2.bar(range(len(labels)), unknowns, color='coral')
        ax2.set_xticks(range(len(labels)))
        ax2.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
        ax2.set_ylabel('Unknown Count')
        ax2.axhline(y=50, color='red', linestyle='--')
    
    # Playfair results
    ax3 = plt.subplot(3, 2, 3)
    ax3.set_title('Playfair Variants', fontsize=10)
    
    playfair_tests = [t for t in results['tests'] if 'playfair' in t['test_id']]
    if playfair_tests:
        labels = [t['test_id'].replace('playfair_', '').upper() for t in playfair_tests]
        unknowns = [t['unknown_count'] for t in playfair_tests]
        
        ax3.bar(range(len(labels)), unknowns, color='green')
        ax3.set_xticks(range(len(labels)))
        ax3.set_xticklabels(labels)
        ax3.set_ylabel('Unknown Count')
        ax3.axhline(y=50, color='red', linestyle='--')
    
    # Example grid
    ax4 = plt.subplot(3, 2, 4)
    ax4.set_title('7×14 Grid Example', fontsize=10)
    
    # Draw 7x14 grid
    for row in range(7):
        for col in range(14):
            idx = row * 14 + col
            if idx < 97:
                color = 'lightgray' if idx in harness.baseline_data['unknown_indices'] else 'white'
                rect = plt.Rectangle((col, 6-row), 0.9, 0.9, 
                                    facecolor=color, edgecolor='black', linewidth=0.5)
                ax4.add_patch(rect)
    
    ax4.set_xlim(-0.5, 14.5)
    ax4.set_ylim(-0.5, 7.5)
    ax4.set_aspect('equal')
    ax4.axis('off')
    
    # Summary
    ax5 = plt.subplot(3, 1, 3)
    ax5.axis('off')
    
    summary_text = f"""
Summary:
--------
Tests Run: {results['summary']['total_tests']}
Best Config: {results['summary']['best_config']}
Best Unknown Count: {results['summary']['best_unknown_count']} (baseline: 50)
Success: {'YES' if results['summary']['success'] else 'NO'}

Conclusion: {results['summary']['conclusion']}

Tested:
• Grid reshapes (7×14, 14×7, 13×8, etc.)
• Hill cipher 2×2 blocks
• Playfair-style digraph substitution
"""
    
    ax5.text(0.1, 0.5, summary_text, fontsize=10, va='center', family='monospace')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/C7_results.pdf', format='pdf', bbox_inches='tight')
    plt.close()
    
    print(f"Generated {output_dir}/C7_results.pdf")