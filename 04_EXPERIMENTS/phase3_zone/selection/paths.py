#!/usr/bin/env python3
"""
Plan R: Selection overlay paths
Read second message from K4 along specific paths
"""

from typing import List, Tuple, Set, Dict

# K4 length
K4_LENGTH = 97

# Anchor positions to exclude
ANCHOR_POSITIONS = {
    "EAST": (21, 24),
    "NORTHEAST": (25, 33),
    "BERLIN": (63, 68),
    "CLOCK": (69, 73)
}

def get_anchor_indices() -> Set[int]:
    """Get all anchor position indices"""
    locked = set()
    for start, end in ANCHOR_POSITIONS.values():
        for i in range(start, end + 1):
            locked.add(i)
    return locked

def mod_k_path(text: str, k: int, r: int) -> Tuple[str, List[int]]:
    """
    Select indices where i mod k = r, excluding anchors
    
    Args:
        text: Input text
        k: Modulus (5-11)
        r: Residue (0 to k-1)
    
    Returns:
        (selected_text, selected_indices)
    """
    anchors = get_anchor_indices()
    selected = []
    indices = []
    
    for i in range(len(text)):
        if i not in anchors and i % k == r:
            selected.append(text[i])
            indices.append(i)
    
    return ''.join(selected), indices

def grid_diagonal_path(text: str, step: Tuple[int, int], 
                       start_row: int = 0, start_col: int = 0) -> Tuple[str, List[int]]:
    """
    Read diagonal through 7×14 grid (97 chars = 7×14 - 1)
    
    Args:
        text: Input text
        step: (row_step, col_step) like (1,2) or (2,1)
        start_row: Starting row (0-6)
        start_col: Starting column (0-13)
    
    Returns:
        (selected_text, selected_indices)
    """
    anchors = get_anchor_indices()
    selected = []
    indices = []
    
    # K4 as 7×14 grid (last cell empty)
    rows = 7
    cols = 14
    
    row = start_row
    col = start_col
    row_step, col_step = step
    
    while 0 <= row < rows and 0 <= col < cols:
        index = row * cols + col
        if index < len(text) and index not in anchors:
            selected.append(text[index])
            indices.append(index)
        
        row += row_step
        col += col_step
    
    return ''.join(selected), indices

def ring24_path(text: str, offset: int = 0, skip: int = 4) -> Tuple[str, List[int]]:
    """
    Select every skip-th position along a 24-cycle ring
    
    Args:
        text: Input text
        offset: Starting position in cycle
        skip: Positions to skip (default 4 for every 4th)
    
    Returns:
        (selected_text, selected_indices)
    """
    anchors = get_anchor_indices()
    selected = []
    indices = []
    
    # Create 24-position cycles
    cycle_length = 24
    num_cycles = len(text) // cycle_length + 1
    
    for cycle in range(num_cycles):
        base = cycle * cycle_length
        pos = offset
        
        for _ in range(cycle_length // skip):
            index = base + (pos % cycle_length)
            if index < len(text) and index not in anchors:
                selected.append(text[index])
                indices.append(index)
            pos += skip
    
    return ''.join(selected), indices

def fibonacci_path(text: str, start: int = 0) -> Tuple[str, List[int]]:
    """
    Select indices at Fibonacci positions
    
    Args:
        text: Input text
        start: Starting offset
    
    Returns:
        (selected_text, selected_indices)
    """
    anchors = get_anchor_indices()
    selected = []
    indices = []
    
    # Generate Fibonacci sequence
    fib = [0, 1]
    while fib[-1] < len(text):
        fib.append(fib[-1] + fib[-2])
    
    for f in fib:
        index = (start + f) % len(text)
        if index not in anchors:
            selected.append(text[index])
            indices.append(index)
    
    return ''.join(selected), indices

def prime_path(text: str) -> Tuple[str, List[int]]:
    """
    Select indices at prime number positions
    
    Returns:
        (selected_text, selected_indices)
    """
    anchors = get_anchor_indices()
    
    # Generate primes up to text length
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True
    
    primes = [i for i in range(len(text)) if is_prime(i)]
    
    selected = []
    indices = []
    
    for p in primes:
        if p not in anchors:
            selected.append(text[p])
            indices.append(p)
    
    return ''.join(selected), indices

def every_nth_path(text: str, n: int, start: int = 0) -> Tuple[str, List[int]]:
    """
    Simple every n-th character selection
    
    Args:
        text: Input text
        n: Step size
        start: Starting position
    
    Returns:
        (selected_text, selected_indices)
    """
    anchors = get_anchor_indices()
    selected = []
    indices = []
    
    pos = start
    while pos < len(text):
        if pos not in anchors:
            selected.append(text[pos])
            indices.append(pos)
        pos += n
    
    return ''.join(selected), indices

def get_all_paths(text: str) -> List[Dict]:
    """
    Generate all selection paths for testing
    
    Returns:
        List of path results with metadata
    """
    paths = []
    
    # Mod-k paths
    for k in range(5, 12):
        for r in range(min(3, k)):  # Test first 3 residues
            selected, indices = mod_k_path(text, k, r)
            if len(selected) >= 10:  # Minimum length
                paths.append({
                    'type': 'mod_k',
                    'params': f'k={k}, r={r}',
                    'selected': selected,
                    'indices': indices,
                    'length': len(selected)
                })
    
    # Grid diagonals
    for step in [(1, 2), (2, 1), (1, 1)]:
        for start_row in range(3):
            selected, indices = grid_diagonal_path(text, step, start_row, 0)
            if len(selected) >= 10:
                paths.append({
                    'type': 'grid_diagonal',
                    'params': f'step={step}, start_row={start_row}',
                    'selected': selected,
                    'indices': indices,
                    'length': len(selected)
                })
    
    # Ring24
    for offset in range(0, 24, 6):
        for skip in [4, 6, 8]:
            selected, indices = ring24_path(text, offset, skip)
            if len(selected) >= 10:
                paths.append({
                    'type': 'ring24',
                    'params': f'offset={offset}, skip={skip}',
                    'selected': selected,
                    'indices': indices,
                    'length': len(selected)
                })
    
    # Every n-th
    for n in range(3, 9):
        for start in range(min(3, n)):
            selected, indices = every_nth_path(text, n, start)
            if len(selected) >= 10:
                paths.append({
                    'type': 'every_nth',
                    'params': f'n={n}, start={start}',
                    'selected': selected,
                    'indices': indices,
                    'length': len(selected)
                })
    
    # Special paths
    selected, indices = fibonacci_path(text)
    if len(selected) >= 10:
        paths.append({
            'type': 'fibonacci',
            'params': 'standard',
            'selected': selected,
            'indices': indices,
            'length': len(selected)
        })
    
    selected, indices = prime_path(text)
    if len(selected) >= 10:
        paths.append({
            'type': 'prime',
            'params': 'standard',
            'selected': selected,
            'indices': indices,
            'length': len(selected)
        })
    
    return paths

if __name__ == "__main__":
    # Test paths
    test_text = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
    
    print("Testing selection paths...")
    print("=" * 60)
    
    # Test mod-k
    selected, indices = mod_k_path(test_text, k=5, r=0)
    print(f"\nMod-5 (r=0): {selected[:30]}...")
    print(f"Indices: {indices[:10]}...")
    
    # Test diagonal
    selected, indices = grid_diagonal_path(test_text, (1, 2))
    print(f"\nDiagonal (1,2): {selected[:30]}...")
    
    # Test ring24
    selected, indices = ring24_path(test_text, offset=0, skip=4)
    print(f"\nRing24 (skip=4): {selected[:30]}...")
    
    # Count all paths
    all_paths = get_all_paths(test_text)
    print(f"\nTotal paths generated: {len(all_paths)}")