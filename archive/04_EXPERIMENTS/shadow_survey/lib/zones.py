#!/usr/bin/env python3
"""
zones.py

Zone mapping strategies to convert shadow parameters into index masks.
Three independent strategies: Anchor-aligned, Periodic bands, Depth gradient.
"""

import json
import math
from pathlib import Path
from typing import List, Tuple, Dict

class ZoneMapper:
    """Base class for zone mapping strategies."""
    
    def __init__(self, text_length: int = 97):
        self.text_length = text_length
    
    def create_mask(self, shadow_params: Dict) -> List[Tuple[int, int, int]]:
        """
        Create zone mask from shadow parameters.
        
        Returns:
            List of (start, end, state) tuples where state is:
            0 = light
            1 = shadow (or mid-shadow)
            2 = deep shadow
        """
        raise NotImplementedError
    
    def save_mask(self, mask: List[Tuple[int, int, int]], 
                 filepath: Path, metadata: Dict = None):
        """Save mask to JSON file with metadata."""
        mask_data = {
            'mask': mask,
            'strategy': self.__class__.__name__,
            'metadata': metadata or {}
        }
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(mask_data, f, indent=2)
    
    def mask_to_binary(self, mask: List[Tuple[int, int, int]]) -> List[bool]:
        """Convert mask to binary array (True = in shadow)."""
        binary = [False] * self.text_length
        for start, end, state in mask:
            if state > 0:  # Any shadow state
                for i in range(start, min(end + 1, self.text_length)):
                    binary[i] = True
        return binary
    
    def mask_to_states(self, mask: List[Tuple[int, int, int]]) -> List[int]:
        """Convert mask to per-index state array."""
        states = [0] * self.text_length
        for start, end, state in mask:
            for i in range(start, min(end + 1, self.text_length)):
                states[i] = state
        return states

class AnchorAlignedZones(ZoneMapper):
    """
    A-zones: Hard-coded segments aligned with anchor positions.
    Motivated by artwork and anchor structure.
    """
    
    # Fixed segment boundaries
    SEGMENTS = [
        (0, 20),    # Head
        (21, 33),   # EAST + NORTHEAST region
        (34, 62),   # Mid section
        (63, 73),   # BERLIN + CLOCK region
        (74, 96)    # Tail
    ]
    
    def __init__(self, text_length: int = 97, theta_threshold: float = 30.0):
        """
        Args:
            theta_threshold: Shadow angle threshold for marking as "in shadow"
        """
        super().__init__(text_length)
        self.theta_threshold = theta_threshold
    
    def create_mask(self, shadow_params: Dict) -> List[Tuple[int, int, int]]:
        """
        Create anchor-aligned zone mask.
        Segments are marked as shadow if shadow_angle >= threshold.
        """
        shadow_angle = shadow_params.get('shadow_angle', 0)
        is_night = shadow_params.get('is_night', False)
        
        mask = []
        
        for start, end in self.SEGMENTS:
            if is_night:
                # Night: everything in deep shadow
                state = 2
            elif shadow_angle >= self.theta_threshold:
                # Determine which segments are in shadow
                # Anchor regions (21-33, 63-73) more likely in shadow
                if start == 21 or start == 63:
                    state = 1  # Shadow
                else:
                    # Alternate pattern for other segments
                    state = 1 if (start // 20) % 2 == 1 else 0
            else:
                # Low shadow angle: mostly light
                state = 0
            
            mask.append((start, end, state))
        
        return mask
    
    def create_stylized_mask(self, shadow_angle: float = 35.0) -> List[Tuple[int, int, int]]:
        """
        Create stylized mask for rendering-specific test.
        Anchor bands in shadow, others in light.
        """
        mask = []
        
        for start, end in self.SEGMENTS:
            # Put anchor regions in shadow
            if start == 21 or start == 63:
                state = 1  # Shadow
            else:
                state = 0  # Light
            
            mask.append((start, end, state))
        
        return mask

class PeriodicShadowBands(ZoneMapper):
    """
    B-zones: Periodic shadow bands based on shadow bearing.
    Creates repeating patterns across the text.
    """
    
    def create_mask(self, shadow_params: Dict) -> List[Tuple[int, int, int]]:
        """
        Create periodic band mask based on shadow bearing.
        """
        shadow_bearing = shadow_params.get('shadow_bearing', 0)
        shadow_angle = shadow_params.get('shadow_angle', 0)
        
        # Convert bearing to stride (period)
        stride = max(2, min(97, int(round(shadow_bearing / 5))))
        
        # Determine shadow width based on angle
        if shadow_angle < 20:
            shadow_width = stride // 4
        elif shadow_angle < 40:
            shadow_width = stride // 3
        else:
            shadow_width = stride // 2
        
        mask = []
        current_pos = 0
        
        while current_pos < self.text_length:
            # Light band
            light_end = min(current_pos + stride - shadow_width - 1, self.text_length - 1)
            if current_pos <= light_end:
                mask.append((current_pos, light_end, 0))
            
            # Shadow band
            shadow_start = light_end + 1
            shadow_end = min(shadow_start + shadow_width - 1, self.text_length - 1)
            if shadow_start < self.text_length:
                mask.append((shadow_start, shadow_end, 1))
            
            current_pos = shadow_end + 1
        
        return mask

class ShadowDepthGradient(ZoneMapper):
    """
    C-zones: Shadow depth gradient with three levels.
    Maps shadow angle to depth levels and creates graduated zones.
    """
    
    def create_mask(self, shadow_params: Dict) -> List[Tuple[int, int, int]]:
        """
        Create gradient mask with three shadow levels.
        """
        shadow_angle = shadow_params.get('shadow_angle', 0)
        shadow_bearing = shadow_params.get('shadow_bearing', 0)
        
        # Determine depth levels based on shadow angle
        if shadow_angle < 20:
            # Shallow shadows - mostly light
            return self._create_light_dominant_mask()
        elif shadow_angle < 35:
            # Medium shadows - mixed pattern
            return self._create_mixed_gradient_mask(shadow_bearing)
        else:
            # Deep shadows - complex gradient
            return self._create_deep_gradient_mask(shadow_angle, shadow_bearing)
    
    def _create_light_dominant_mask(self) -> List[Tuple[int, int, int]]:
        """Light with occasional shadow spots."""
        mask = [(0, self.text_length - 1, 0)]  # All light
        
        # Add some shadow spots at key positions
        shadow_spots = [
            (21, 24, 1),   # EAST position
            (63, 68, 1),   # BERLIN position
        ]
        
        # Merge shadow spots into mask
        final_mask = []
        for start, end, state in mask:
            added_spots = False
            for spot_start, spot_end, spot_state in shadow_spots:
                if spot_start >= start and spot_end <= end:
                    # Add light before spot if needed
                    if start < spot_start:
                        final_mask.append((start, spot_start - 1, state))
                    # Add shadow spot
                    final_mask.append((spot_start, spot_end, spot_state))
                    # Continue with light after
                    if spot_end < end:
                        start = spot_end + 1
                    else:
                        added_spots = True
                        break
            
            if not added_spots and start <= end:
                final_mask.append((start, end, state))
        
        return final_mask
    
    def _create_mixed_gradient_mask(self, shadow_bearing: float) -> List[Tuple[int, int, int]]:
        """Mixed gradient with varying shadow depths."""
        mask = []
        
        # Create gradient pattern based on position
        period = max(5, int(shadow_bearing / 10))
        
        for i in range(0, self.text_length, period):
            end = min(i + period - 1, self.text_length - 1)
            
            # Cycle through light, mid-shadow, deep shadow
            cycle_pos = (i // period) % 3
            
            if cycle_pos == 0:
                state = 0  # Light
            elif cycle_pos == 1:
                state = 1  # Mid-shadow
            else:
                state = 2  # Deep shadow
            
            mask.append((i, end, state))
        
        return mask
    
    def _create_deep_gradient_mask(self, shadow_angle: float, 
                                  shadow_bearing: float) -> List[Tuple[int, int, int]]:
        """Deep gradient with complex patterns."""
        mask = []
        
        # Anchor regions get deep shadow
        anchor_regions = [
            (21, 33),  # EAST + NORTHEAST
            (63, 73)   # BERLIN + CLOCK
        ]
        
        current_pos = 0
        
        for anchor_start, anchor_end in anchor_regions:
            # Before anchor: gradient from light to mid
            if current_pos < anchor_start:
                mid_point = (current_pos + anchor_start) // 2
                mask.append((current_pos, mid_point, 0))  # Light
                mask.append((mid_point + 1, anchor_start - 1, 1))  # Mid-shadow
            
            # Anchor region: deep shadow
            mask.append((anchor_start, anchor_end, 2))
            
            current_pos = anchor_end + 1
        
        # After last anchor: gradient from mid to light
        if current_pos < self.text_length:
            mid_point = (current_pos + self.text_length - 1) // 2
            if mid_point > current_pos:
                mask.append((current_pos, mid_point, 1))  # Mid-shadow
                mask.append((mid_point + 1, self.text_length - 1, 0))  # Light
            else:
                mask.append((current_pos, self.text_length - 1, 0))  # Light
        
        return mask

def create_all_masks(shadow_params: Dict, output_dir: Path = None) -> Dict[str, List]:
    """
    Create all three types of masks for given shadow parameters.
    
    Returns:
        Dictionary with mask types as keys and masks as values
    """
    if output_dir is None:
        output_dir = Path("04_EXPERIMENTS/shadow_survey/masks")
    
    masks = {}
    
    # A-zones: Anchor-aligned
    a_mapper = AnchorAlignedZones()
    masks['Azones'] = a_mapper.create_mask(shadow_params)
    
    # Also test with different thresholds
    for theta in [20, 25, 35]:
        a_mapper_theta = AnchorAlignedZones(theta_threshold=theta)
        masks[f'Azones_theta{theta}'] = a_mapper_theta.create_mask(shadow_params)
    
    # B-zones: Periodic bands
    b_mapper = PeriodicShadowBands()
    masks['Bzones'] = b_mapper.create_mask(shadow_params)
    
    # C-zones: Depth gradient
    c_mapper = ShadowDepthGradient()
    masks['Czones'] = c_mapper.create_mask(shadow_params)
    
    # Save masks if output directory provided
    if shadow_params.get('datetime'):
        dt_str = shadow_params['datetime'].replace(':', '-').replace(' ', 'T')
        
        for mask_type, mask in masks.items():
            filepath = output_dir / f"{dt_str}_{mask_type}.json"
            mapper = ZoneMapper()
            mapper.save_mask(mask, filepath, metadata=shadow_params)
    
    return masks

def test_zone_mapping():
    """Test zone mapping strategies."""
    print("Testing Zone Mapping Strategies")
    print("-" * 50)
    
    # Test shadow parameters
    test_params = {
        'datetime': '1990-11-03T14:00:00',
        'sun_alt': 28.9,
        'sun_az': 210.2,
        'shadow_angle': 61.1,
        'shadow_bearing': 30.2,
        'shadow_length_unit': 1.746,
        'is_night': False
    }
    
    # Create all masks
    masks = create_all_masks(test_params)
    
    for mask_type, mask in masks.items():
        print(f"\n{mask_type}:")
        for start, end, state in mask:
            state_name = ['light', 'shadow', 'deep_shadow'][state]
            print(f"  [{start:2d}-{end:2d}]: {state_name}")
    
    # Test stylized mask
    print("\nStylized Mask (anchors in shadow):")
    a_mapper = AnchorAlignedZones()
    stylized = a_mapper.create_stylized_mask()
    for start, end, state in stylized:
        state_name = ['light', 'shadow'][state]
        print(f"  [{start:2d}-{end:2d}]: {state_name}")

if __name__ == "__main__":
    test_zone_mapping()