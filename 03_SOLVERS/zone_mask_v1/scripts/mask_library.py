"""
Mask Library v2 - Invertible, paper-doable masks for K4 cryptanalysis
"""

import numpy as np
from typing import List, Dict, Any, Tuple


class MaskBase:
    """Base class for all mask operations"""
    
    def apply(self, text: str, params: Dict[str, Any]) -> str:
        """Apply mask to text"""
        raise NotImplementedError
    
    def invert(self, text: str, params: Dict[str, Any]) -> str:
        """Invert mask operation"""
        raise NotImplementedError


class PeriodicInterleave(MaskBase):
    """Periodic interleave masks (period-2, period-3)"""
    
    def apply(self, text: str, params: Dict[str, Any]) -> str:
        period = params.get('period', 2)
        result = [''] * len(text)
        
        # Split into period groups
        groups = [[] for _ in range(period)]
        for i, char in enumerate(text):
            groups[i % period].append(char)
        
        # Interleave groups
        idx = 0
        for j in range(max(len(g) for g in groups)):
            for group in groups:
                if j < len(group):
                    result[idx] = group[j]
                    idx += 1
        
        return ''.join(result)
    
    def invert(self, text: str, params: Dict[str, Any]) -> str:
        # Periodic interleave is self-inverse for period 2
        # For other periods, we reverse the process
        period = params.get('period', 2)
        n = len(text)
        result = [''] * n
        
        # Calculate group sizes
        base_size = n // period
        remainder = n % period
        group_sizes = [base_size + (1 if i < remainder else 0) for i in range(period)]
        
        # Extract groups
        groups = []
        idx = 0
        for size in group_sizes:
            group = []
            for i in range(size):
                if idx + i * period < n:
                    group.append(text[idx + i * period])
            groups.append(group)
            idx += 1
        
        # Reconstruct original
        result_idx = 0
        for i in range(max(len(g) for g in groups)):
            for j, group in enumerate(groups):
                if i < len(group):
                    result[result_idx] = group[i]
                    result_idx += 1
        
        return ''.join(result)


class FixedCycle(MaskBase):
    """Fixed cycle shuffles (3-cycle, 5-cycle)"""
    
    def apply(self, text: str, params: Dict[str, Any]) -> str:
        cycle_length = params.get('cycle', 3)
        result = list(text)
        n = len(text)
        
        # Apply cycles
        for start in range(0, n - cycle_length + 1, cycle_length):
            # Rotate positions within cycle
            temp = result[start]
            for i in range(cycle_length - 1):
                result[start + i] = result[start + i + 1]
            result[start + cycle_length - 1] = temp
        
        return ''.join(result)
    
    def invert(self, text: str, params: Dict[str, Any]) -> str:
        cycle_length = params.get('cycle', 3)
        result = list(text)
        n = len(text)
        
        # Apply inverse cycles (rotate opposite direction)
        for start in range(0, n - cycle_length + 1, cycle_length):
            temp = result[start + cycle_length - 1]
            for i in range(cycle_length - 1, 0, -1):
                result[start + i] = result[start + i - 1]
            result[start] = temp
        
        return ''.join(result)


class DiagonalWeave(MaskBase):
    """Diagonal weave masks (twill-style)"""
    
    def apply(self, text: str, params: Dict[str, Any]) -> str:
        rows = params.get('rows', 7)
        cols = params.get('cols', 14)
        step = params.get('step', [1, 1])  # [row_step, col_step]
        
        # Create grid
        grid = []
        idx = 0
        for r in range(rows):
            row = []
            for c in range(cols):
                if idx < len(text):
                    row.append(text[idx])
                    idx += 1
                else:
                    row.append('')
            grid.append(row)
        
        # Read diagonally
        result = []
        visited = set()
        
        # Start from each position on first row and first column
        starts = [(0, c) for c in range(cols)] + [(r, 0) for r in range(1, rows)]
        
        for start_r, start_c in starts:
            r, c = start_r, start_c
            while 0 <= r < rows and 0 <= c < cols:
                if (r, c) not in visited and grid[r][c]:
                    result.append(grid[r][c])
                    visited.add((r, c))
                r += step[0]
                c += step[1]
        
        return ''.join(result)
    
    def invert(self, text: str, params: Dict[str, Any]) -> str:
        rows = params.get('rows', 7)
        cols = params.get('cols', 14)
        step = params.get('step', [1, 1])
        
        # Create empty grid
        grid = [['' for _ in range(cols)] for _ in range(rows)]
        
        # Calculate diagonal order
        order = []
        visited = set()
        starts = [(0, c) for c in range(cols)] + [(r, 0) for r in range(1, rows)]
        
        for start_r, start_c in starts:
            r, c = start_r, start_c
            while 0 <= r < rows and 0 <= c < cols:
                if (r, c) not in visited:
                    order.append((r, c))
                    visited.add((r, c))
                r += step[0]
                c += step[1]
        
        # Fill grid in diagonal order
        for i, (r, c) in enumerate(order):
            if i < len(text):
                grid[r][c] = text[i]
        
        # Read row-wise
        result = []
        for row in grid:
            for char in row:
                if char:
                    result.append(char)
        
        return ''.join(result)


class AlternatingSheet(MaskBase):
    """Alternating sheet mask - take every Nth char with alternating offset"""
    
    def apply(self, text: str, params: Dict[str, Any]) -> str:
        n = params.get('n', 3)
        block_size = params.get('block_size', 10)
        
        result = []
        for block_idx in range(0, len(text), block_size):
            block = text[block_idx:block_idx + block_size]
            offset = (block_idx // block_size) % n
            
            for i in range(offset, len(block), n):
                result.append(block[i])
            for i in range(len(block)):
                if i % n != offset:
                    result.append(block[i])
        
        return ''.join(result)
    
    def invert(self, text: str, params: Dict[str, Any]) -> str:
        # Complex inversion - requires tracking original positions
        n = params.get('n', 3)
        block_size = params.get('block_size', 10)
        original_len = len(text)
        
        # Reconstruct by reversing the selection process
        result = [''] * original_len
        text_idx = 0
        
        for block_idx in range(0, original_len, block_size):
            block_end = min(block_idx + block_size, original_len)
            block_len = block_end - block_idx
            offset = (block_idx // block_size) % n
            
            # First pass: positions with offset
            for i in range(offset, block_len, n):
                if text_idx < len(text):
                    result[block_idx + i] = text[text_idx]
                    text_idx += 1
            
            # Second pass: other positions
            for i in range(block_len):
                if i % n != offset:
                    if text_idx < len(text):
                        result[block_idx + i] = text[text_idx]
                        text_idx += 1
        
        return ''.join(result)


class FibonacciSkip(MaskBase):
    """Fibonacci skip mask - select indices using Fk modulo length"""
    
    def _fibonacci(self, n: int) -> List[int]:
        """Generate first n Fibonacci numbers"""
        if n <= 0:
            return []
        elif n == 1:
            return [1]
        
        fib = [1, 1]
        for i in range(2, n):
            fib.append(fib[-1] + fib[-2])
        return fib
    
    def apply(self, text: str, params: Dict[str, Any]) -> str:
        skip_count = params.get('skip_count', 15)
        
        # Generate Fibonacci indices
        fib_nums = self._fibonacci(skip_count)
        indices = [f % len(text) for f in fib_nums]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_indices = []
        for idx in indices:
            if idx not in seen:
                unique_indices.append(idx)
                seen.add(idx)
        
        # Select characters at Fibonacci indices first
        result = [text[i] for i in unique_indices]
        
        # Add remaining characters
        for i, char in enumerate(text):
            if i not in seen:
                result.append(char)
        
        return ''.join(result)
    
    def invert(self, text: str, params: Dict[str, Any]) -> str:
        skip_count = params.get('skip_count', 15)
        original_len = len(text)
        
        # Generate Fibonacci indices
        fib_nums = self._fibonacci(skip_count)
        indices = [f % original_len for f in fib_nums]
        
        # Remove duplicates
        seen = set()
        unique_indices = []
        for idx in indices:
            if idx not in seen:
                unique_indices.append(idx)
                seen.add(idx)
        
        # Reconstruct original order
        result = [''] * original_len
        text_idx = 0
        
        # Place Fibonacci-indexed characters
        for orig_idx in unique_indices:
            if text_idx < len(text):
                result[orig_idx] = text[text_idx]
                text_idx += 1
        
        # Place remaining characters
        for i in range(original_len):
            if i not in seen:
                if text_idx < len(text):
                    result[i] = text[text_idx]
                    text_idx += 1
        
        return ''.join(result)


class LowFrequencySmoother(MaskBase):
    """Low-frequency smoother - duplicate low-freq letters at fixed residues"""
    
    def apply(self, text: str, params: Dict[str, Any]) -> str:
        residue = params.get('residue', 3)
        target_chars = params.get('target_chars', ['Q', 'Z', 'X'])
        
        result = []
        for i, char in enumerate(text):
            result.append(char)
            if i % residue == 0 and char.upper() in target_chars:
                result.append(char)  # Duplicate
        
        return ''.join(result)
    
    def invert(self, text: str, params: Dict[str, Any]) -> str:
        residue = params.get('residue', 3)
        target_chars = params.get('target_chars', ['Q', 'Z', 'X'])
        
        result = []
        skip_next = False
        
        for i in range(len(text)):
            if skip_next:
                skip_next = False
                continue
            
            char = text[i]
            result.append(char)
            
            # Check if this was a duplicated position
            orig_pos = len(result) - 1
            if orig_pos % residue == 0 and char.upper() in target_chars:
                # Check if next char is duplicate
                if i + 1 < len(text) and text[i + 1] == char:
                    skip_next = True
        
        return ''.join(result)


# Mask factory
class SparseNull(MaskBase):
    """Sparse null mask - reindex by extracting residue class"""
    
    def apply(self, text: str, params: Dict[str, Any]) -> str:
        """
        At decrypt: split into two streams based on residue, concatenate, process
        """
        k = params.get('k', 6)
        r = params.get('r', 2)
        
        # Split into A (non-residue) and B (residue) streams
        stream_a = []  # indices where i mod k != r
        stream_b = []  # indices where i mod k == r
        
        for i, char in enumerate(text):
            if i % k == r:
                stream_b.append(char)
            else:
                stream_a.append(char)
        
        # Concatenate A + B
        return ''.join(stream_a) + ''.join(stream_b)
    
    def invert(self, text: str, params: Dict[str, Any]) -> str:
        """
        Inverse: reconstruct original positions from concatenated streams
        """
        k = params.get('k', 6)
        r = params.get('r', 2)
        n = len(text)
        
        # Calculate sizes of A and B streams
        b_count = sum(1 for i in range(n) if i % k == r)
        a_count = n - b_count
        
        # Split back into streams
        stream_a = text[:a_count]
        stream_b = text[a_count:]
        
        # Reconstruct original positions
        result = []
        a_idx = 0
        b_idx = 0
        
        for i in range(n):
            if i % k == r:
                if b_idx < len(stream_b):
                    result.append(stream_b[b_idx])
                    b_idx += 1
            else:
                if a_idx < len(stream_a):
                    result.append(stream_a[a_idx])
                    a_idx += 1
        
        return ''.join(result)


class SparseDouble(MaskBase):
    """Sparse double mask - swap adjacent pairs in residue class"""
    
    def apply(self, text: str, params: Dict[str, Any]) -> str:
        """
        Swap adjacent characters at residue positions for micro-scramble
        """
        k = params.get('k', 6)
        r = params.get('r', 2)
        result = list(text)
        
        # Find all positions in residue class
        residue_positions = [i for i in range(len(text)) if i % k == r]
        
        # Swap adjacent pairs within residue class
        for j in range(0, len(residue_positions) - 1, 2):
            pos1 = residue_positions[j]
            pos2 = residue_positions[j + 1]
            # Swap characters at these positions
            result[pos1], result[pos2] = result[pos2], result[pos1]
        
        return ''.join(result)
    
    def invert(self, text: str, params: Dict[str, Any]) -> str:
        """
        Sparse double is self-inverse (swapping twice returns original)
        """
        return self.apply(text, params)


def create_mask(mask_type: str) -> MaskBase:
    """Factory function to create mask instances"""
    masks = {
        'period2': PeriodicInterleave,
        'period3': PeriodicInterleave,
        'period5': PeriodicInterleave,
        'period7': PeriodicInterleave,
        'cycle3': FixedCycle,
        'cycle5': FixedCycle,
        'diag_weave': DiagonalWeave,
        'alt_sheet': AlternatingSheet,
        'fib_skip': FibonacciSkip,
        'lowfreq_smoother': LowFrequencySmoother,
        'sparse_null': SparseNull,
        'sparse_double': SparseDouble
    }
    
    if mask_type not in masks:
        raise ValueError(f"Unknown mask type: {mask_type}")
    
    return masks[mask_type]()


def apply_mask(text: str, mask_config: Dict[str, Any]) -> str:
    """Apply a mask based on configuration"""
    mask_type = mask_config.get('type')
    params = mask_config.get('params', {})
    
    # Set default parameters based on type
    if mask_type == 'period2':
        params.setdefault('period', 2)
    elif mask_type == 'period3':
        params.setdefault('period', 3)
    elif mask_type == 'period5':
        params.setdefault('period', 5)
    elif mask_type == 'period7':
        params.setdefault('period', 7)
    elif mask_type == 'cycle3':
        params.setdefault('cycle', 3)
    elif mask_type == 'cycle5':
        params.setdefault('cycle', 5)
    
    mask = create_mask(mask_type)
    return mask.apply(text, params)


def invert_mask(text: str, mask_config: Dict[str, Any]) -> str:
    """Invert a mask based on configuration"""
    mask_type = mask_config.get('type')
    params = mask_config.get('params', {})
    
    # Set default parameters based on type
    if mask_type == 'period2':
        params.setdefault('period', 2)
    elif mask_type == 'period3':
        params.setdefault('period', 3)
    elif mask_type == 'period5':
        params.setdefault('period', 5)
    elif mask_type == 'period7':
        params.setdefault('period', 7)
    elif mask_type == 'cycle3':
        params.setdefault('cycle', 3)
    elif mask_type == 'cycle5':
        params.setdefault('cycle', 5)
    
    mask = create_mask(mask_type)
    return mask.invert(text, params)