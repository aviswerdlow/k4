#!/usr/bin/env python3
"""
shadow_zones.py

Shadow geometry to zone mapping for Fork S-ShadowΔ.
Creates position masks with states: 0=light, 1=mid, 2=deep.
"""

import json
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Tuple, Dict

# Constants
CIA_LAT = 38.95
CIA_LON = -77.146
MASTER_SEED = 1337

def solar_alt_az(dt_local: datetime, lat_deg: float = CIA_LAT, lon_deg: float = CIA_LON) -> Tuple[float, float]:
    """
    Calculate solar altitude and azimuth.
    Simplified NOAA Solar Position Algorithm.
    
    Returns:
        (altitude_deg, azimuth_deg) where azimuth: 0=N, 90=E, 180=S, 270=W
    """
    # Convert to UTC
    dt_utc = dt_local.astimezone(timezone.utc)
    
    # Julian day calculation
    a = (14 - dt_utc.month) // 12
    y = dt_utc.year + 4800 - a
    m = dt_utc.month + 12 * a - 3
    jdn = dt_utc.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    jd = jdn + (dt_utc.hour - 12) / 24 + dt_utc.minute / 1440 + dt_utc.second / 86400
    
    # Solar calculations
    n = jd - 2451545.0
    L = (280.460 + 0.9856474 * n) % 360
    g = math.radians((357.528 + 0.9856003 * n) % 360)
    lambda_sun = math.radians(L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g))
    
    # Declination
    epsilon = math.radians(23.439 - 0.0000004 * n)
    dec = math.asin(math.sin(epsilon) * math.sin(lambda_sun))
    
    # Hour angle
    t = n / 36525
    gmst = 280.46061837 + 360.98564736629 * n + 0.000387933 * t * t
    lmst = (gmst + lon_deg) % 360
    ha = math.radians(lmst - math.degrees(lambda_sun) / 15 * 15)
    
    # Altitude and azimuth
    lat_rad = math.radians(lat_deg)
    alt = math.asin(math.sin(dec) * math.sin(lat_rad) + 
                    math.cos(dec) * math.cos(lat_rad) * math.cos(ha))
    
    az = math.atan2(-math.sin(ha), 
                    math.tan(dec) * math.cos(lat_rad) - math.sin(lat_rad) * math.cos(ha))
    
    # Convert to degrees
    alt_deg = math.degrees(alt)
    az_deg = (math.degrees(az) + 180) % 360  # 0=N, 90=E
    
    return alt_deg, az_deg

def shadow_params(dt_local: datetime) -> Dict:
    """
    Calculate shadow parameters from datetime.
    
    Returns:
        Dictionary with sun_alt, sun_az, shadow_angle, shadow_bearing
    """
    alt, az = solar_alt_az(dt_local)
    
    return {
        'datetime': dt_local.isoformat(),
        'sun_alt': round(alt, 1),
        'sun_az': round(az, 1),
        'shadow_angle': round(max(0, 90 - alt), 1),
        'shadow_bearing': round((az + 180) % 360, 1),
        'is_night': alt < 0
    }

class ZoneBuilder:
    """Base class for zone building strategies."""
    
    def __init__(self, text_length: int = 97):
        self.text_length = text_length
    
    def build_mask(self, shadow_params: Dict) -> List[Tuple[int, int, int]]:
        """
        Build zone mask from shadow parameters.
        
        Returns:
            List of (start, end, state) tuples where state ∈ {0, 1, 2}
        """
        raise NotImplementedError
    
    def save_mask(self, mask: List[Tuple[int, int, int]], 
                  filepath: Path, metadata: Dict = None):
        """Save mask to JSON file."""
        mask_data = {
            'mask': mask,
            'strategy': self.__class__.__name__,
            'metadata': metadata or {}
        }
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(mask_data, f, indent=2)

class AZones(ZoneBuilder):
    """
    A-zones: Anchor-aligned segments.
    Segments: [0,20], [21,33], [34,62], [63,73], [74,96]
    """
    
    SEGMENTS = [
        (0, 20),    # Head
        (21, 33),   # EAST + NORTHEAST
        (34, 62),   # Mid section  
        (63, 73),   # BERLIN + CLOCK
        (74, 96)    # Tail
    ]
    
    def __init__(self, text_length: int = 97, theta_0: float = 30.0):
        super().__init__(text_length)
        self.theta_0 = theta_0
    
    def build_mask(self, shadow_params: Dict) -> List[Tuple[int, int, int]]:
        """Build anchor-aligned zone mask."""
        shadow_angle = shadow_params['shadow_angle']
        is_night = shadow_params.get('is_night', False)
        
        mask = []
        
        for i, (start, end) in enumerate(self.SEGMENTS):
            if is_night:
                state = 2  # Deep shadow everywhere at night
            elif shadow_angle >= self.theta_0:
                # Anchor segments (indices 1, 3) get deep shadow
                if i in [1, 3]:  # EAST+NORTHEAST, BERLIN+CLOCK
                    state = 2  # Deep
                else:
                    state = 0  # Light
            else:
                state = 0  # All light when shadow angle low
            
            mask.append((start, end, state))
        
        return mask

class BBands(ZoneBuilder):
    """
    B-bands: Periodic shadow bands based on shadow bearing.
    """
    
    def build_mask(self, shadow_params: Dict) -> List[Tuple[int, int, int]]:
        """Build periodic band mask."""
        shadow_bearing = shadow_params['shadow_bearing']
        shadow_angle = shadow_params['shadow_angle']
        
        # Convert bearing to stride
        stride = max(2, min(97, int(round(shadow_bearing / 5))))
        
        mask = []
        
        for i in range(0, self.text_length, stride):
            end = min(i + stride - 1, self.text_length - 1)
            
            # First half of stride is mid, second half is light
            mid_end = min(i + stride // 2 - 1, self.text_length - 1)
            
            if i <= mid_end:
                mask.append((i, mid_end, 1))  # Mid
            if mid_end + 1 <= end:
                mask.append((mid_end + 1, end, 0))  # Light
        
        return mask

class CGradient(ZoneBuilder):
    """
    C-gradient: Depth gradient based on shadow angle.
    """
    
    def build_mask(self, shadow_params: Dict) -> List[Tuple[int, int, int]]:
        """Build depth gradient mask."""
        shadow_angle = shadow_params['shadow_angle']
        
        mask = []
        
        if shadow_angle < 20:
            # Level 1: Every 3rd index as mid
            for i in range(0, self.text_length, 3):
                if i + 2 < self.text_length:
                    mask.append((i, i + 1, 0))      # Light
                    mask.append((i + 2, i + 2, 1))  # Mid
                else:
                    mask.append((i, self.text_length - 1, 0))
                    
        elif shadow_angle < 35:
            # Level 2: Every 2nd index as mid
            for i in range(0, self.text_length, 2):
                if i + 1 < self.text_length:
                    mask.append((i, i, 0))          # Light
                    mask.append((i + 1, i + 1, 1))  # Mid
                else:
                    mask.append((i, i, 0))
                    
        else:
            # Level 3: Anchor segments deep, rest mid
            anchor_segments = [(21, 33), (63, 73)]
            
            current = 0
            for anchor_start, anchor_end in anchor_segments:
                if current < anchor_start:
                    mask.append((current, anchor_start - 1, 1))  # Mid
                mask.append((anchor_start, anchor_end, 2))       # Deep
                current = anchor_end + 1
            
            if current < self.text_length:
                mask.append((current, self.text_length - 1, 1))  # Mid
        
        return self._consolidate_mask(mask)
    
    def _consolidate_mask(self, mask: List[Tuple[int, int, int]]) -> List[Tuple[int, int, int]]:
        """Consolidate adjacent segments with same state."""
        if not mask:
            return mask
        
        consolidated = []
        current_start, current_end, current_state = mask[0]
        
        for start, end, state in mask[1:]:
            if state == current_state and start == current_end + 1:
                current_end = end
            else:
                consolidated.append((current_start, current_end, current_state))
                current_start, current_end, current_state = start, end, state
        
        consolidated.append((current_start, current_end, current_state))
        return consolidated

def generate_all_masks(dt_local: datetime, output_dir: Path = None) -> Dict[str, List]:
    """
    Generate all mask types for given datetime.
    
    Returns:
        Dictionary with mask type names as keys
    """
    if output_dir is None:
        output_dir = Path("04_EXPERIMENTS/shadow_delta/masks")
    
    shadow_p = shadow_params(dt_local)
    masks = {}
    
    # A-zones with different thresholds
    for theta in [20, 25, 30, 35]:
        builder = AZones(theta_0=theta)
        mask_name = f"Azones_theta{theta}"
        masks[mask_name] = builder.build_mask(shadow_p)
        
        # Save to file
        dt_str = dt_local.strftime("%Y-%m-%dT%H-%M")
        filepath = output_dir / f"{dt_str}_{mask_name}.json"
        builder.save_mask(masks[mask_name], filepath, shadow_p)
    
    # B-bands
    builder = BBands()
    masks['Bbands'] = builder.build_mask(shadow_p)
    dt_str = dt_local.strftime("%Y-%m-%dT%H-%M")
    filepath = output_dir / f"{dt_str}_Bbands.json"
    builder.save_mask(masks['Bbands'], filepath, shadow_p)
    
    # C-gradient
    builder = CGradient()
    masks['Cgradient'] = builder.build_mask(shadow_p)
    filepath = output_dir / f"{dt_str}_Cgradient.json"
    builder.save_mask(masks['Cgradient'], filepath, shadow_p)
    
    return masks

def test_shadow_zones():
    """Test shadow zone generation."""
    print("Testing Shadow Zone Generation")
    print("-" * 50)
    
    # Test datetime
    dt = datetime(1990, 11, 3, 14, 0, tzinfo=timezone(timedelta(hours=-5)))
    
    # Calculate shadow parameters
    shadow_p = shadow_params(dt)
    print(f"Datetime: {shadow_p['datetime']}")
    print(f"Sun altitude: {shadow_p['sun_alt']}°")
    print(f"Sun azimuth: {shadow_p['sun_az']}°")
    print(f"Shadow angle: {shadow_p['shadow_angle']}°")
    print(f"Shadow bearing: {shadow_p['shadow_bearing']}°")
    
    # Generate all masks
    masks = generate_all_masks(dt)
    
    print("\nGenerated masks:")
    for mask_name, mask in masks.items():
        print(f"\n{mask_name}:")
        for start, end, state in mask[:5]:  # Show first 5 segments
            state_name = ['light', 'mid', 'deep'][state]
            print(f"  [{start:2d}-{end:2d}]: {state_name}")

if __name__ == "__main__":
    test_shadow_zones()