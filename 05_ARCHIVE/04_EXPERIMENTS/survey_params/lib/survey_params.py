#!/usr/bin/env python3
"""
survey_params.py

Core utilities for extracting cipher parameters from surveying quantities.
Bearings, DMS, rectangular components, distances, and arc transforms.
"""

import math
from typing import Dict, List, Tuple, Optional

# Master seed for reproducibility
MASTER_SEED = 1337

# Reference bearings (degrees from TRUE unless noted)
TRUE_NE_PLUS = 61.6959
TRUE_ENE_MINUS = 50.8041
MAG_NE_PLUS_1989_B = 59.5959
MAG_ENE_MINUS_1989_B = 48.7041
OFFSET_ONLY = 16.6959

# DMS exemplars
DMS_EXEMPLARS = [
    (16, 41, 45),
    (61, 41, 45),
    (50, 48, 15)
]

# Declinations
LANGLEY_1990_DECLINATION = 9.5  # degrees West
BERLIN_1989_DECLINATION = -2.0  # degrees East (negative for East)

# Rectangular reductions (ΔN, ΔE in meters)
RECTANGULAR_COORDS = {
    '5_rods_ne': (11.923, 22.140),
    '5_rods_ene': (15.892, 19.488),
    'mag_5_rods_ne': (12.726, 21.688),
    'mag_5_rods_ene': (16.595, 18.892),
}

# Unit conversions
ROD_TO_METERS = 5.0292
ROD_TO_FEET = 16.5
METERS_TO_FEET = 3.28084

def clamp(value: float, min_val: int, max_val: int) -> int:
    """Clamp value to range [min_val, max_val]."""
    return max(min_val, min(max_val, int(value)))

def bearing_to_params(bearing: float) -> Dict[str, int]:
    """
    Convert bearing to cipher parameters.
    
    Returns:
        L_int: Integer part of bearing
        L_round: Rounded bearing
        offset_alpha: Fractional part mapped to 0-25
        offset_alpha_r: Rounded fractional part mapped to 0-25
    """
    L_int = int(bearing)
    L_round = round(bearing)
    
    # Fractional part to alphabet offset
    frac = bearing - int(bearing)
    offset_alpha = int(frac * 26) % 26
    offset_alpha_r = int(round(frac * 26)) % 26
    
    # Clamp L values to valid range [2, 97]
    L_int = clamp(L_int, 2, 97)
    L_round = clamp(L_round, 2, 97)
    
    return {
        'L_int': L_int,
        'L_round': L_round,
        'offset_alpha': offset_alpha,
        'offset_alpha_r': offset_alpha_r,
        'source_bearing': bearing
    }

def dms_to_configs(D: int, M: int, S: int) -> List[Dict]:
    """
    Convert DMS (Degrees, Minutes, Seconds) to cipher configurations.
    
    Returns list of plausible configurations with different interpretations.
    """
    configs = []
    
    # Config 1: L=D, phase=M, offset=S%26
    configs.append({
        'L': clamp(D, 2, 97),
        'phase': M,
        'offset': S % 26,
        'interpretation': 'D_as_L_M_as_phase_S_as_offset'
    })
    
    # Config 2: L=D+M, phase=S, offset=D%26
    configs.append({
        'L': clamp(D + M, 2, 97),
        'phase': S,
        'offset': D % 26,
        'interpretation': 'DM_sum_as_L'
    })
    
    # Config 3: L=S, phase=M, offset=D%26
    if S >= 2:  # Only if S is valid as L
        configs.append({
            'L': clamp(S, 2, 97),
            'phase': M,
            'offset': D % 26,
            'interpretation': 'S_as_L'
        })
    
    # Config 4: Multi-wheel with wheel_count from minutes
    wheel_count = M // 10
    if wheel_count > 0:
        configs.append({
            'L': clamp(D, 2, 97),
            'phase': M % 10,
            'offset': S % 26,
            'wheel_count': wheel_count,
            'interpretation': 'multi_wheel_from_minutes'
        })
    
    # Config 5: Combined total seconds as parameter
    total_seconds = D * 3600 + M * 60 + S
    L_from_seconds = clamp(total_seconds % 97 + 2, 2, 97)
    configs.append({
        'L': L_from_seconds,
        'phase': M,
        'offset': S % 26,
        'interpretation': 'total_seconds_mod'
    })
    
    return configs

def coords_to_params(dN: float, dE: float) -> Dict:
    """
    Convert rectangular coordinates (ΔN, ΔE) to cipher parameters.
    
    Returns various distance and ratio-based parameters.
    """
    # Calculate distance
    distance_m = math.sqrt(dN**2 + dE**2)
    distance_ft = distance_m * METERS_TO_FEET
    distance_rods = distance_m / ROD_TO_METERS
    
    # Integer versions for L
    L_m_int = clamp(int(distance_m), 2, 97)
    L_feet = clamp(int(distance_ft), 2, 97)
    L_rods = clamp(int(distance_rods), 2, 97)
    
    # Ratio-based parameters
    if abs(dN) > 0.001:
        ratio_e_n = dE / dN
        L_ratio = clamp(int(abs(ratio_e_n) * 10), 2, 97)
    else:
        ratio_e_n = 0
        L_ratio = 2
    
    # Angle from coordinates
    angle_rad = math.atan2(dE, dN)
    angle_deg = math.degrees(angle_rad)
    if angle_deg < 0:
        angle_deg += 360
    
    # Column suggestions for transposition
    columns_suggestions = []
    for val in [5, int(math.sqrt(distance_m)), L_rods, 16, 17, 25]:
        if 2 <= val <= 97:
            columns_suggestions.append(val)
    
    return {
        'distance_m': distance_m,
        'distance_ft': distance_ft,
        'distance_rods': distance_rods,
        'L_m_int': L_m_int,
        'L_feet': L_feet,
        'L_rods': L_rods,
        'ratio_e_n': ratio_e_n,
        'L_ratio': L_ratio,
        'angle_deg': angle_deg,
        'columns': list(set(columns_suggestions)),
        'offset_from_angle': int(angle_deg) % 26,
        'dN': dN,
        'dE': dE
    }

def arc_family_params(angle_deg: float) -> Dict:
    """
    Convert angle to arc/chord/sector parameters (Flint-style transforms).
    
    Returns parameters derived from circular geometry.
    """
    # Convert to radians
    angle_rad = math.radians(angle_deg)
    
    # Arc length on unit circle
    arc_length = angle_rad  # For unit circle, arc = angle in radians
    
    # Chord length = 2 * sin(angle/2)
    chord = 2 * math.sin(angle_rad / 2)
    
    # Sector ratio (fraction of full circle)
    sector = angle_deg / 360.0
    
    # Map to integer parameters
    L_arc = clamp(int(arc_length * 26), 2, 97)
    off_chr = int(chord * 100) % 26
    fam_idx = int(sector * 100) % 26
    
    # Additional derived parameters
    L_deg = clamp(int(angle_deg), 2, 97)
    complement = 90 - angle_deg if angle_deg <= 90 else 360 - angle_deg
    supplement = 180 - angle_deg if angle_deg <= 180 else 540 - angle_deg
    
    return {
        'angle_deg': angle_deg,
        'angle_rad': angle_rad,
        'arc_length': arc_length,
        'chord': chord,
        'sector': sector,
        'L_arc': L_arc,
        'L_deg': L_deg,
        'off_chr': off_chr,
        'fam_idx': fam_idx,
        'complement_deg': complement,
        'supplement_deg': supplement,
        'L_complement': clamp(int(abs(complement)), 2, 97),
        'L_supplement': clamp(int(abs(supplement)), 2, 97)
    }

def quadrant_params(angle_deg: float) -> Dict:
    """
    Extract quadrant-based parameters from angle.
    """
    # Normalize to 0-360
    normalized = angle_deg % 360
    
    # Determine quadrant (1-4)
    if 0 <= normalized < 90:
        quadrant = 1
        ref_angle = normalized
    elif 90 <= normalized < 180:
        quadrant = 2
        ref_angle = 180 - normalized
    elif 180 <= normalized < 270:
        quadrant = 3
        ref_angle = normalized - 180
    else:
        quadrant = 4
        ref_angle = 360 - normalized
    
    return {
        'quadrant': quadrant,
        'reference_angle': ref_angle,
        'L_quad': quadrant,  # Use quadrant as short L
        'L_ref': clamp(int(ref_angle), 2, 97),
        'offset_quad': (quadrant * 6) % 26  # Spread quadrants across alphabet
    }

def declination_adjustments(true_bearing: float, declination: float) -> Dict:
    """
    Calculate magnetic bearing adjustments based on declination.
    
    Args:
        true_bearing: True bearing in degrees
        declination: Magnetic declination (positive = West, negative = East)
    
    Returns:
        Dictionary with true and magnetic bearings and adjustments
    """
    # Magnetic bearing = True bearing - Declination
    # (For West declination, magnetic is less than true)
    magnetic_bearing = true_bearing - declination
    
    # Normalize to 0-360
    if magnetic_bearing < 0:
        magnetic_bearing += 360
    elif magnetic_bearing >= 360:
        magnetic_bearing -= 360
    
    # Caesar shift values
    caesar_pre = int(round(declination)) % 26
    caesar_post = (-int(round(declination))) % 26
    
    return {
        'true_bearing': true_bearing,
        'magnetic_bearing': magnetic_bearing,
        'declination': declination,
        'caesar_pre': caesar_pre,
        'caesar_post': caesar_post,
        'L_true': clamp(int(true_bearing), 2, 97),
        'L_magnetic': clamp(int(magnetic_bearing), 2, 97)
    }

def generate_all_params() -> Dict:
    """
    Generate comprehensive parameter sets from all surveying quantities.
    """
    all_params = {
        'bearings': {},
        'dms': [],
        'coordinates': {},
        'arc_transforms': {},
        'quadrants': {},
        'declinations': {}
    }
    
    # Process reference bearings
    bearings = {
        'true_ne_plus': TRUE_NE_PLUS,
        'true_ene_minus': TRUE_ENE_MINUS,
        'mag_ne_plus_1989': MAG_NE_PLUS_1989_B,
        'mag_ene_minus_1989': MAG_ENE_MINUS_1989_B,
        'offset_only': OFFSET_ONLY
    }
    
    for name, bearing in bearings.items():
        all_params['bearings'][name] = bearing_to_params(bearing)
        all_params['arc_transforms'][name] = arc_family_params(bearing)
        all_params['quadrants'][name] = quadrant_params(bearing)
    
    # Process DMS exemplars
    for dms in DMS_EXEMPLARS:
        all_params['dms'].append({
            'dms': dms,
            'configs': dms_to_configs(*dms)
        })
    
    # Process rectangular coordinates
    for name, coords in RECTANGULAR_COORDS.items():
        all_params['coordinates'][name] = coords_to_params(*coords)
    
    # Process declination adjustments
    for bearing_name, bearing_val in bearings.items():
        if 'true' in bearing_name:
            # Langley adjustment
            all_params['declinations'][f'{bearing_name}_langley'] = \
                declination_adjustments(bearing_val, LANGLEY_1990_DECLINATION)
            # Berlin adjustment
            all_params['declinations'][f'{bearing_name}_berlin'] = \
                declination_adjustments(bearing_val, BERLIN_1989_DECLINATION)
    
    return all_params

if __name__ == "__main__":
    # Test parameter generation
    params = generate_all_params()
    
    print("Sample Parameter Extraction:")
    print("\nBearing 61.6959°:")
    print(bearing_to_params(61.6959))
    
    print("\nDMS (61, 41, 45):")
    for config in dms_to_configs(61, 41, 45)[:2]:
        print(f"  {config}")
    
    print("\nCoordinates (11.923, 22.140):")
    coord_params = coords_to_params(11.923, 22.140)
    print(f"  Distance: {coord_params['distance_m']:.2f}m")
    print(f"  L values: {coord_params['L_m_int']}, {coord_params['L_feet']}, {coord_params['L_rods']}")
    
    print("\nArc transform for 61.6959°:")
    arc = arc_family_params(61.6959)
    print(f"  L_arc: {arc['L_arc']}, off_chr: {arc['off_chr']}, fam_idx: {arc['fam_idx']}")