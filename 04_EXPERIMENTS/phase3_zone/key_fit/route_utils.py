#!/usr/bin/env python3
"""
Route permutation utilities for joint route+key fitting
"""

import numpy as np
from typing import List, Tuple, Dict


def apply_route(text: str, route_type: str, params: Dict = None) -> str:
    """
    Apply a route transformation to text (for decryption, this is CT → S)
    
    Args:
        text: Input text (ciphertext in decrypt context)
        route_type: Type of route ('identity', 'columnar', 'serpentine', 'diag_weave', 'ring24')
        params: Route parameters
    
    Returns:
        Transformed text S where S[p] aligns with PT index p
    """
    if route_type == 'identity':
        return text
    
    elif route_type == 'columnar':
        # Columnar 7×14: row-wise write, column-wise read
        rows = params.get('rows', 7)
        cols = params.get('cols', 14)
        return columnar_route(text, rows, cols)
    
    elif route_type == 'serpentine':
        # Serpentine 7×14: row-wise write, alternating LR/RL read
        rows = params.get('rows', 7)
        cols = params.get('cols', 14)
        return serpentine_route(text, rows, cols)
    
    elif route_type == 'diag_weave':
        # Diagonal weave with step pattern
        rows = params.get('rows', 7)
        cols = params.get('cols', 14)
        step = params.get('step', [1, 2])
        return diagonal_weave_route(text, rows, cols, step)
    
    elif route_type == 'ring24':
        # Ring24: 24 columns, 4 rows, serpentine read
        return ring24_route(text)
    
    else:
        raise ValueError(f"Unknown route type: {route_type}")


def columnar_route(text: str, rows: int, cols: int) -> str:
    """
    Columnar transposition: write row-wise, read column-wise
    For decryption: CT is written column-wise, read row-wise to get S
    """
    if len(text) < rows * cols:
        text = text + 'X' * (rows * cols - len(text))  # Pad if needed
    
    # For decryption: CT was read column-wise, so we write it column-wise
    # Then read row-wise to get S
    matrix = np.zeros((rows, cols), dtype=str)
    idx = 0
    
    # Write column-wise (how CT was read during encryption)
    for c in range(cols):
        for r in range(rows):
            if idx < len(text):
                matrix[r, c] = text[idx]
                idx += 1
    
    # Read row-wise (original PT order)
    result = []
    for r in range(rows):
        for c in range(cols):
            result.append(matrix[r, c])
    
    return ''.join(result[:97])  # K4 is 97 chars


def serpentine_route(text: str, rows: int, cols: int) -> str:
    """
    Serpentine: write row-wise, read alternating LR/RL
    For decryption: reverse the process
    """
    if len(text) < rows * cols:
        text = text + 'X' * (rows * cols - len(text))
    
    # For decryption: CT was read serpentine, so write it serpentine
    # Then read row-wise to get S
    matrix = np.zeros((rows, cols), dtype=str)
    idx = 0
    
    # Write serpentine (how CT was read during encryption)
    for r in range(rows):
        if r % 2 == 0:  # Even rows: left to right
            for c in range(cols):
                if idx < len(text):
                    matrix[r, c] = text[idx]
                    idx += 1
        else:  # Odd rows: right to left
            for c in range(cols - 1, -1, -1):
                if idx < len(text):
                    matrix[r, c] = text[idx]
                    idx += 1
    
    # Read row-wise (original PT order)
    result = []
    for r in range(rows):
        for c in range(cols):
            result.append(matrix[r, c])
    
    return ''.join(result[:97])


def diagonal_weave_route(text: str, rows: int, cols: int, step: List[int]) -> str:
    """
    Diagonal weave with step pattern
    For decryption: reverse the diagonal reading pattern
    """
    if len(text) < rows * cols:
        text = text + 'X' * (rows * cols - len(text))
    
    matrix = np.zeros((rows, cols), dtype=str)
    
    # Simplified diagonal weave for 7x14
    # Read diagonals in a pattern
    read_order = []
    
    # Simple diagonal pattern: start at each column, go diagonally
    for start_col in range(cols):
        r, c = 0, start_col
        while r < rows and c < cols:
            if 0 <= r < rows and 0 <= c < cols:
                read_order.append((r, c))
            r += 1
            c += step[0] if len(read_order) % 2 == 0 else step[1]
    
    # Also start from each row on the left side
    for start_row in range(1, rows):
        r, c = start_row, 0
        while r < rows and c < cols:
            if 0 <= r < rows and 0 <= c < cols and (r, c) not in read_order:
                read_order.append((r, c))
            r += 1
            c += step[0] if len(read_order) % 2 == 0 else step[1]
    
    # Ensure we have exactly rows*cols positions
    read_order = read_order[:rows * cols]
    
    # Now write CT according to read order
    for idx, (r, c) in enumerate(read_order[:len(text)]):
        matrix[r, c] = text[idx]
    
    # Read row-wise to get S
    result = []
    for r in range(rows):
        for c in range(cols):
            result.append(matrix[r, c])
    
    return ''.join(result[:97])


def ring24_route(text: str) -> str:
    """
    Ring24: 24 columns, 4 rows, serpentine read
    Based on Berlin Clock (Weltzeituhr) with 24 hour positions
    """
    rows = 4
    cols = 24
    
    if len(text) < rows * cols:
        text = text + 'X' * (rows * cols - len(text))
    
    # Similar to serpentine but with 24×4 dimensions
    matrix = np.zeros((rows, cols), dtype=str)
    idx = 0
    
    # Write in ring pattern (serpentine through 24×4)
    for r in range(rows):
        if r % 2 == 0:
            for c in range(cols):
                if idx < len(text):
                    matrix[r, c] = text[idx]
                    idx += 1
        else:
            for c in range(cols - 1, -1, -1):
                if idx < len(text):
                    matrix[r, c] = text[idx]
                    idx += 1
    
    # Read row-wise
    result = []
    for r in range(rows):
        for c in range(cols):
            result.append(matrix[r, c])
    
    return ''.join(result[:97])


def get_permutation_vector(route_type: str, params: Dict = None) -> List[int]:
    """
    Get the permutation vector for a route
    Returns list where result[i] = j means PT position i comes from CT position j
    """
    # Create a test string with position markers
    test = ''.join(chr(ord('A') + (i % 26)) for i in range(97))
    
    # Apply route
    transformed = apply_route(test, route_type, params)
    
    # Build permutation vector
    perm = []
    for i in range(97):
        # Find where character at position i came from
        target_char = chr(ord('A') + (i % 26))
        # Need to handle multiple occurrences
        count = i // 26
        found = 0
        for j in range(97):
            if test[j] == target_char:
                if found == count:
                    perm.append(j)
                    break
                found += 1
    
    return perm


def test_routes():
    """Test route transformations"""
    text = 'OBKRUOXOGHULBSOLIFBBFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUHUAUEKCAR'
    text += 'NYPVTTMZFPKWGDKZXTJCDIGKUHUAUEK'
    
    print("Testing routes on K4 ciphertext:")
    print(f"Original: {text[:40]}...")
    
    for route_type in ['identity', 'columnar', 'serpentine', 'diag_weave', 'ring24']:
        if route_type == 'identity':
            params = {}
        elif route_type in ['columnar', 'serpentine', 'diag_weave']:
            params = {'rows': 7, 'cols': 14}
            if route_type == 'diag_weave':
                params['step'] = [1, 2]
        else:
            params = {}
        
        transformed = apply_route(text, route_type, params)
        print(f"\n{route_type}:")
        print(f"  First 40: {transformed[:40]}")
        print(f"  At 21-24: {transformed[21:25]}")
        print(f"  At 63-68: {transformed[63:69]}")


if __name__ == '__main__':
    test_routes()