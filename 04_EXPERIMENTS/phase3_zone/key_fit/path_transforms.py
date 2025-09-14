#!/usr/bin/env python3
"""
Path transformations for K4 - J1 approaches
Visual/sculptural paths that reorder before classical cipher
"""

from typing import List, Tuple


def helix_28_path(text: str) -> str:
    """
    Helix-28: Step +28 mod 97 for 97 steps
    Creates a helical reading pattern matching Sanborn's 28-step rhythm
    """
    n = len(text)
    result = []
    pos = 0
    
    for _ in range(n):
        result.append(text[pos])
        pos = (pos + 28) % n
    
    return ''.join(result)


def helix_28_inverse(text: str) -> str:
    """
    Inverse of Helix-28 path
    """
    n = len(text)
    result = [''] * n
    pos = 0
    
    for i in range(n):
        result[pos] = text[i]
        pos = (pos + 28) % n
    
    return ''.join(result)


def serpentine_turn(text: str, rows: int = 7, cols: int = 14) -> str:
    """
    Serpentine with quarter-turn
    Write in 7×14, rotate 90° clockwise, read serpentine
    """
    orig_len = len(text)  # Save original length
    if len(text) < rows * cols:
        text = text + 'X' * (rows * cols - len(text))  # Pad if needed
    
    # Write into grid row by row
    grid = []
    idx = 0
    for r in range(rows):
        row = []
        for c in range(cols):
            if idx < len(text):
                row.append(text[idx])
                idx += 1
            else:
                row.append('X')
        grid.append(row)
    
    # Rotate 90° clockwise: new[c][rows-1-r] = old[r][c]
    rotated = []
    for c in range(cols):
        new_row = []
        for r in range(rows - 1, -1, -1):
            new_row.append(grid[r][c])
        rotated.append(new_row)
    
    # Read serpentine from rotated grid
    result = []
    for i, row in enumerate(rotated):
        if i % 2 == 0:
            result.extend(row)  # Left to right
        else:
            result.extend(row[::-1])  # Right to left
    
    # Trim to original length
    return ''.join(result)[:orig_len]


def serpentine_turn_inverse(text: str, rows: int = 7, cols: int = 14) -> str:
    """
    Inverse of serpentine with quarter-turn
    """
    orig_len = len(text)
    if len(text) < rows * cols:
        text = text + 'X' * (rows * cols - len(text))
    
    # Reconstruct rotated grid from serpentine reading
    rotated = []
    idx = 0
    for i in range(cols):  # Rotated has cols rows
        row = []
        if i % 2 == 0:
            # Read left to right
            for j in range(rows):
                if idx < len(text):
                    row.append(text[idx])
                    idx += 1
        else:
            # Read right to left
            start_idx = idx
            for j in range(rows):
                if idx < len(text):
                    idx += 1
            # Now read backwards from idx-1 to start_idx
            for j in range(idx - 1, start_idx - 1, -1):
                if j < len(text):
                    row.append(text[j])
        rotated.append(row)
    
    # Rotate back (counter-clockwise): old[r][c] = new[c][rows-1-r]
    grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            row.append(rotated[c][rows - 1 - r])
        grid.append(row)
    
    # Read row by row
    result = []
    for row in grid:
        result.extend(row)
    
    return ''.join(result)[:orig_len]


def ring24_path(text: str) -> str:
    """
    Ring24 path: 24×4 grid, read in ring pattern
    Matches Weltzeituhr 24-hour structure
    Special handling for K4's 97 characters
    """
    n = len(text)
    rows = 4
    cols = 24
    grid_size = rows * cols  # 96
    
    # For K4's 97 chars, we'll handle the extra char specially
    padded = text
    if n < grid_size:
        padded = text + 'X' * (grid_size - n)
    elif n > grid_size:
        # Save extra char(s) for later
        extra = text[grid_size:]
        padded = text[:grid_size]
    
    # Write into 24×4 grid column by column
    grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            idx = c * rows + r
            if idx < len(padded):
                row.append(padded[idx])
            else:
                row.append('X')
        grid.append(row)
    
    # Read in ring pattern: outer ring, then inner rings
    result = []
    
    # Outer ring (clockwise)
    # Top row left to right
    for c in range(cols):
        result.append(grid[0][c])
    # Right column top to bottom (skip corner)
    for r in range(1, rows):
        result.append(grid[r][cols-1])
    # Bottom row right to left (skip corner)
    for c in range(cols-2, -1, -1):
        result.append(grid[rows-1][c])
    # Left column bottom to top (skip corners)
    for r in range(rows-2, 0, -1):
        result.append(grid[r][0])
    
    # Inner rings (if any remain)
    if rows > 2 and cols > 2:
        # Second ring
        for c in range(1, cols-1):
            result.append(grid[1][c])
        for c in range(cols-2, 0, -1):
            result.append(grid[2][c])
    
    # For K4's 97th character, append it at the end
    result_text = ''.join(result)
    if n > grid_size:
        result_text += extra
    
    return result_text[:n]


def ring24_inverse(text: str) -> str:
    """
    Inverse of Ring24 path
    Special handling for K4's 97 characters
    """
    n = len(text)
    rows = 4
    cols = 24
    grid_size = rows * cols  # 96
    
    # Handle extra character(s) if present
    extra = ""
    if n > grid_size:
        extra = text[grid_size:]
        text = text[:grid_size]
    
    # Initialize grid
    grid = [['X'] * cols for _ in range(rows)]
    
    # Place characters in ring pattern
    idx = 0
    
    # Outer ring
    for c in range(cols):
        if idx < len(text):
            grid[0][c] = text[idx]
            idx += 1
    for r in range(1, rows):
        if idx < len(text):
            grid[r][cols-1] = text[idx]
            idx += 1
    for c in range(cols-2, -1, -1):
        if idx < len(text):
            grid[rows-1][c] = text[idx]
            idx += 1
    for r in range(rows-2, 0, -1):
        if idx < len(text):
            grid[r][0] = text[idx]
            idx += 1
    
    # Inner rings
    if rows > 2 and cols > 2:
        for c in range(1, cols-1):
            if idx < len(text):
                grid[1][c] = text[idx]
                idx += 1
        for c in range(cols-2, 0, -1):
            if idx < len(text):
                grid[2][c] = text[idx]
                idx += 1
    
    # Read column by column
    result = []
    for c in range(cols):
        for r in range(rows):
            result.append(grid[r][c])
    
    # Add back the extra character(s)
    result_text = ''.join(result)
    if extra:
        result_text += extra
    
    return result_text[:n]


def test_paths():
    """Test path transformations for round-trip"""
    test_text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 4  # 104 chars, trim to 97
    test_text = test_text[:97]
    
    print("Testing path transformations...")
    print(f"Original: {test_text[:40]}...")
    
    # Test Helix-28
    h28 = helix_28_path(test_text)
    h28_inv = helix_28_inverse(h28)
    assert h28_inv == test_text, "Helix-28 round-trip failed"
    print(f"Helix-28: {h28[:40]}...")
    print("  ✓ Helix-28 round-trip passed")
    
    # Test Serpentine-turn
    st = serpentine_turn(test_text)
    st_inv = serpentine_turn_inverse(st)
    if st_inv != test_text:
        print(f"\nDEBUG Serpentine:")
        print(f"Original length: {len(test_text)}")
        print(f"After transform: {len(st)}")
        print(f"After inverse: {len(st_inv)}")
        print(f"First 20 original: {test_text[:20]}")
        print(f"First 20 after inverse: {st_inv[:20]}")
        # Find first mismatch
        for i in range(min(len(test_text), len(st_inv))):
            if test_text[i] != st_inv[i]:
                print(f"First mismatch at index {i}: '{test_text[i]}' vs '{st_inv[i]}'")
                break
    assert st_inv == test_text, "Serpentine-turn round-trip failed"
    print(f"Serpentine-turn: {st[:40]}...")
    print("  ✓ Serpentine-turn round-trip passed")
    
    # Test Ring24
    r24 = ring24_path(test_text)
    r24_inv = ring24_inverse(r24)
    if r24_inv != test_text:
        print(f"\nDEBUG Ring24:")
        print(f"Original length: {len(test_text)}")
        print(f"After transform: {len(r24)}")
        print(f"After inverse: {len(r24_inv)}")
        print(f"First 40 original: {test_text[:40]}")
        print(f"First 40 after inverse: {r24_inv[:40]}")
        # Find first mismatch
        for i in range(min(len(test_text), len(r24_inv))):
            if test_text[i] != r24_inv[i]:
                print(f"First mismatch at index {i}: '{test_text[i]}' vs '{r24_inv[i]}'")
                break
    assert r24_inv == test_text, "Ring24 round-trip failed"
    print(f"Ring24: {r24[:40]}...")
    print("  ✓ Ring24 round-trip passed")


if __name__ == '__main__':
    test_paths()