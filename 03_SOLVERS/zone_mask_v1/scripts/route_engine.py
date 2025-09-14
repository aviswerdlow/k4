"""
Route Engine v2 - Small routes for "turn, flip, wash" operations
Now includes Path transformations (Helix-28, Serpentine-turn, Ring24)
"""

import math
from typing import List, Dict, Any, Tuple
import sys
import os

# Add path to import path_transforms module
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..', '04_EXPERIMENTS/phase3_zone/key_fit'))
from path_transforms import (
    helix_28_path, helix_28_inverse,
    serpentine_turn, serpentine_turn_inverse,
    ring24_path, ring24_inverse
)


class RouteBase:
    """Base class for all route operations"""
    
    def apply(self, text: str, params: Dict[str, Any]) -> str:
        """Apply route to text"""
        raise NotImplementedError
    
    def invert(self, text: str, params: Dict[str, Any]) -> str:
        """Invert route operation"""
        raise NotImplementedError


class ColumnarRoute(RouteBase):
    """Columnar transposition with m×n grid"""
    
    def apply(self, text: str, params: Dict[str, Any]) -> str:
        rows = params.get('rows', 7)
        cols = params.get('cols', 14)
        key_order = params.get('key_order', list(range(cols)))
        passes = params.get('passes', 1)
        row_flip_between_passes = params.get('row_flip_between_passes', False)
        
        result = text
        
        for pass_num in range(passes):
            # Create grid
            grid = self._create_grid(result, rows, cols)
            
            # Flip rows if needed between passes
            if pass_num > 0 and row_flip_between_passes:
                grid = grid[::-1]
            
            # Read columns in key order
            output = []
            for col_idx in key_order:
                for row in grid:
                    if col_idx < len(row) and row[col_idx]:
                        output.append(row[col_idx])
            
            result = ''.join(output)
        
        return result
    
    def invert(self, text: str, params: Dict[str, Any]) -> str:
        rows = params.get('rows', 7)
        cols = params.get('cols', 14)
        key_order = params.get('key_order', list(range(cols)))
        passes = params.get('passes', 1)
        row_flip_between_passes = params.get('row_flip_between_passes', False)
        
        result = text
        
        # Apply inverse passes in reverse order
        for pass_num in range(passes - 1, -1, -1):
            # Calculate column lengths
            total_chars = len(result)
            base_col_len = total_chars // cols
            extra_chars = total_chars % cols
            
            # Build columns in key order
            columns = [[] for _ in range(cols)]
            idx = 0
            
            for col_idx in key_order:
                col_len = base_col_len + (1 if col_idx < extra_chars else 0)
                for _ in range(col_len):
                    if idx < len(result):
                        columns[col_idx].append(result[idx])
                        idx += 1
            
            # Reconstruct grid from columns
            grid = []
            for r in range(rows):
                row = []
                for c in range(cols):
                    if r < len(columns[c]):
                        row.append(columns[c][r])
                    else:
                        row.append('')
                grid.append(row)
            
            # Flip rows if needed
            if pass_num > 0 and row_flip_between_passes:
                grid = grid[::-1]
            
            # Read row-wise
            result = ''.join(''.join(row) for row in grid)
        
        return result.rstrip()
    
    def _create_grid(self, text: str, rows: int, cols: int) -> List[List[str]]:
        """Create grid from text"""
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
        return grid


class SerpentineRoute(RouteBase):
    """Serpentine S-read across rows"""
    
    def apply(self, text: str, params: Dict[str, Any]) -> str:
        rows = params.get('rows', 7)
        cols = params.get('cols', 14)
        
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
        
        # Read in serpentine pattern
        result = []
        for r in range(rows):
            if r % 2 == 0:
                # Left to right
                result.extend(grid[r])
            else:
                # Right to left
                result.extend(reversed(grid[r]))
        
        return ''.join(c for c in result if c)
    
    def invert(self, text: str, params: Dict[str, Any]) -> str:
        rows = params.get('rows', 7)
        cols = params.get('cols', 14)
        
        # Fill grid in serpentine pattern
        grid = [['' for _ in range(cols)] for _ in range(rows)]
        idx = 0
        
        for r in range(rows):
            if r % 2 == 0:
                # Left to right
                for c in range(cols):
                    if idx < len(text):
                        grid[r][c] = text[idx]
                        idx += 1
            else:
                # Right to left
                for c in range(cols - 1, -1, -1):
                    if idx < len(text):
                        grid[r][c] = text[idx]
                        idx += 1
        
        # Read row-wise
        result = []
        for row in grid:
            for char in row:
                if char:
                    result.append(char)
        
        return ''.join(result)


class AlternatingRowRoute(RouteBase):
    """Alternating row direction: left-to-right then right-to-left"""
    
    def apply(self, text: str, params: Dict[str, Any]) -> str:
        # This is essentially the same as serpentine
        # but can have different parameters
        return SerpentineRoute().apply(text, params)
    
    def invert(self, text: str, params: Dict[str, Any]) -> str:
        return SerpentineRoute().invert(text, params)


class SpiralRoute(RouteBase):
    """Spiral in or spiral out on near-square grid"""
    
    def apply(self, text: str, params: Dict[str, Any]) -> str:
        rows = params.get('rows', 10)
        cols = params.get('cols', 10)
        direction = params.get('direction', 'in')  # 'in' or 'out'
        
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
        
        # Read in spiral pattern
        result = []
        top, bottom = 0, rows - 1
        left, right = 0, cols - 1
        
        while top <= bottom and left <= right:
            # Right
            for c in range(left, right + 1):
                if grid[top][c]:
                    result.append(grid[top][c])
            top += 1
            
            # Down
            for r in range(top, bottom + 1):
                if grid[r][right]:
                    result.append(grid[r][right])
            right -= 1
            
            # Left
            if top <= bottom:
                for c in range(right, left - 1, -1):
                    if grid[bottom][c]:
                        result.append(grid[bottom][c])
                bottom -= 1
            
            # Up
            if left <= right:
                for r in range(bottom, top - 1, -1):
                    if grid[r][left]:
                        result.append(grid[r][left])
                left += 1
        
        if direction == 'out':
            result = result[::-1]
        
        return ''.join(result)
    
    def invert(self, text: str, params: Dict[str, Any]) -> str:
        rows = params.get('rows', 10)
        cols = params.get('cols', 10)
        direction = params.get('direction', 'in')
        
        # Create empty grid
        grid = [['' for _ in range(cols)] for _ in range(rows)]
        
        # Fill in spiral pattern
        chars = list(text)
        if direction == 'out':
            chars = chars[::-1]
        
        idx = 0
        top, bottom = 0, rows - 1
        left, right = 0, cols - 1
        
        while top <= bottom and left <= right and idx < len(chars):
            # Right
            for c in range(left, right + 1):
                if idx < len(chars):
                    grid[top][c] = chars[idx]
                    idx += 1
            top += 1
            
            # Down
            for r in range(top, bottom + 1):
                if idx < len(chars):
                    grid[r][right] = chars[idx]
                    idx += 1
            right -= 1
            
            # Left
            if top <= bottom:
                for c in range(right, left - 1, -1):
                    if idx < len(chars):
                        grid[bottom][c] = chars[idx]
                        idx += 1
                bottom -= 1
            
            # Up
            if left <= right:
                for r in range(bottom, top - 1, -1):
                    if idx < len(chars):
                        grid[r][left] = chars[idx]
                        idx += 1
                left += 1
        
        # Read row-wise
        result = []
        for row in grid:
            for char in row:
                if char:
                    result.append(char)
        
        return ''.join(result)


class TumbleRoute(RouteBase):
    """Washing machine tumble: write grid, rotate 90 degrees, read"""
    
    def apply(self, text: str, params: Dict[str, Any]) -> str:
        rows = params.get('rows', 7)
        cols = params.get('cols', 14)
        rotations = params.get('rotations', 1)  # Number of 90-degree rotations
        second_pass_flip = params.get('second_pass_flip', False)
        
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
        
        # Apply rotations
        for _ in range(rotations % 4):
            grid = self._rotate_90(grid)
        
        # Optional second pass with flip
        if second_pass_flip:
            grid = [row[::-1] for row in grid]  # Flip horizontally
        
        # Read result
        result = []
        for row in grid:
            for char in row:
                if char:
                    result.append(char)
        
        return ''.join(result)
    
    def invert(self, text: str, params: Dict[str, Any]) -> str:
        rows = params.get('rows', 7)
        cols = params.get('cols', 14)
        rotations = params.get('rotations', 1)
        second_pass_flip = params.get('second_pass_flip', False)
        
        # Calculate dimensions after rotation
        for _ in range(rotations % 4):
            rows, cols = cols, rows
        
        # Create grid from rotated text
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
        
        # Undo second pass flip
        if second_pass_flip:
            grid = [row[::-1] for row in grid]
        
        # Undo rotations (rotate opposite direction)
        for _ in range((4 - rotations % 4) % 4):
            grid = self._rotate_90(grid)
        
        # Read result
        result = []
        for row in grid:
            for char in row:
                if char:
                    result.append(char)
        
        return ''.join(result)
    
    def _rotate_90(self, grid: List[List[str]]) -> List[List[str]]:
        """Rotate grid 90 degrees clockwise"""
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0
        
        rotated = []
        for c in range(cols):
            new_row = []
            for r in range(rows - 1, -1, -1):
                if c < len(grid[r]):
                    new_row.append(grid[r][c])
                else:
                    new_row.append('')
            rotated.append(new_row)
        
        return rotated


# Route factory
class Helix28Path(RouteBase):
    """Helix-28 path: Step +28 mod 97 for helical reading pattern"""
    
    def apply(self, text: str, params: Dict[str, Any]) -> str:
        """Apply Helix-28 path transformation"""
        return helix_28_path(text)
    
    def invert(self, text: str, params: Dict[str, Any]) -> str:
        """Invert Helix-28 path transformation"""
        return helix_28_inverse(text)


class SerpentineTurnPath(RouteBase):
    """Serpentine with quarter-turn: 7×14 grid, rotate 90° clockwise, read serpentine"""
    
    def apply(self, text: str, params: Dict[str, Any]) -> str:
        """Apply Serpentine-turn path transformation"""
        rows = params.get('rows', 7)
        cols = params.get('cols', 14)
        return serpentine_turn(text, rows, cols)
    
    def invert(self, text: str, params: Dict[str, Any]) -> str:
        """Invert Serpentine-turn path transformation"""
        rows = params.get('rows', 7)
        cols = params.get('cols', 14)
        return serpentine_turn_inverse(text, rows, cols)


class Ring24Path(RouteBase):
    """Ring24 path: 24×4 grid, read in ring pattern (Weltzeituhr-inspired)"""
    
    def apply(self, text: str, params: Dict[str, Any]) -> str:
        """Apply Ring24 path transformation"""
        return ring24_path(text)
    
    def invert(self, text: str, params: Dict[str, Any]) -> str:
        """Invert Ring24 path transformation"""
        return ring24_inverse(text)


def create_route(route_type: str) -> RouteBase:
    """Factory function to create route instances"""
    routes = {
        'columnar': ColumnarRoute,
        'serpentine': SerpentineRoute,
        'alt_rows': AlternatingRowRoute,
        'spiral': SpiralRoute,
        'tumble': TumbleRoute,
        # Path transformations
        'helix28': Helix28Path,
        'serpentine_turn': SerpentineTurnPath,
        'ring24': Ring24Path
    }
    
    if route_type not in routes:
        raise ValueError(f"Unknown route type: {route_type}")
    
    return routes[route_type]()


def apply_route(text: str, route_config: Dict[str, Any]) -> str:
    """Apply a route based on configuration"""
    route_type = route_config.get('type')
    params = route_config.get('params', {})
    
    route = create_route(route_type)
    return route.apply(text, params)


def invert_route(text: str, route_config: Dict[str, Any]) -> str:
    """Invert a route based on configuration"""
    route_type = route_config.get('type')
    params = route_config.get('params', {})
    
    route = create_route(route_type)
    return route.invert(text, params)