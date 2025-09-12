#!/usr/bin/env python3
"""
Fork K - Berlin Clock (Mengenlehreuhr) State Generator
Generates 24-element vectors from Berlin Clock light states
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple

class BerlinClock:
    def __init__(self):
        """Initialize Berlin Clock processor"""
        self.name = "Mengenlehreuhr"
        
    def state(self, dt: datetime, ignore_seconds: bool = True) -> Tuple[List[int], Dict]:
        """
        Return a 24-length pattern describing clock lights at datetime dt.
        
        Rows (top to bottom):
          R1: 4 lamps (5-hour blocks)
          R2: 4 lamps (1-hour blocks)
          R3: 11 lamps (5-minute blocks; lamps 3,6,9 are red markers)
          R4: 4 lamps (1-minute blocks)
        
        Returns:
            raw_lamps: List of 24 ints (0=off, 1=yellow, 2=red)
            info: Dict with per-row counts and metadata
        """
        # Extract time components
        hours = dt.hour
        minutes = dt.minute
        seconds = dt.second
        
        # R1: 5-hour blocks (4 lamps)
        r1_count = hours // 5
        r1_lamps = [1 if i < r1_count else 0 for i in range(4)]
        
        # R2: 1-hour blocks (4 lamps)
        r2_count = hours % 5
        r2_lamps = [1 if i < r2_count else 0 for i in range(4)]
        
        # R3: 5-minute blocks (11 lamps, positions 3,6,9 are red when lit)
        r3_count = minutes // 5
        r3_lamps = []
        for i in range(11):
            if i < r3_count:
                # Positions 2, 5, 8 (0-indexed) are red markers
                if i in [2, 5, 8]:
                    r3_lamps.append(2)  # Red
                else:
                    r3_lamps.append(1)  # Yellow
            else:
                r3_lamps.append(0)  # Off
        
        # R4: 1-minute blocks (4 lamps)
        r4_count = minutes % 5
        r4_lamps = [1 if i < r4_count else 0 for i in range(4)]
        
        # Combine all lamps
        raw_lamps = r1_lamps + r2_lamps + r3_lamps + r4_lamps
        
        # Verify length
        assert len(raw_lamps) == 23, f"Expected 23 lamps, got {len(raw_lamps)}"
        
        # Pad to 24 with seconds indicator if not ignoring
        if not ignore_seconds:
            # Seconds lamp blinks on/off each second
            seconds_lamp = 1 if seconds % 2 == 0 else 0
            raw_lamps = [seconds_lamp] + raw_lamps
        else:
            # Pad with 0 to reach 24
            raw_lamps = raw_lamps + [0]
        
        # Create info dict
        info = {
            'time': dt.strftime('%H:%M:%S'),
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'r1_count': r1_count,
            'r2_count': r2_count,
            'r3_count': r3_count,
            'r4_count': r4_count,
            'row_counts': [r1_count, r2_count, r3_count, r4_count]
        }
        
        return raw_lamps, info
    
    def encode_binary(self, raw_lamps: List[int]) -> List[int]:
        """Encode lamps as binary on/off (0/1)"""
        return [1 if lamp > 0 else 0 for lamp in raw_lamps]
    
    def encode_color(self, raw_lamps: List[int]) -> List[int]:
        """Encode lamps with color values (0=off, 1=yellow, 2=red)"""
        return raw_lamps.copy()
    
    def encode_rowcount(self, info: Dict) -> List[int]:
        """Encode as per-row counts expanded to 24 elements"""
        row_counts = info['row_counts']
        
        # Expand each row count to fill its portion of 24
        # R1 (4 lamps) -> 6 positions
        # R2 (4 lamps) -> 6 positions  
        # R3 (11 lamps) -> 6 positions
        # R4 (4 lamps) -> 6 positions
        
        expanded = []
        for count in row_counts:
            # Each row gets 6 positions
            for _ in range(6):
                expanded.append(count)
        
        return expanded[:24]
    
    def get_all_encodings(self, dt: datetime) -> Dict[str, List[int]]:
        """Get all encoding variants for a datetime"""
        raw_lamps, info = self.state(dt, ignore_seconds=True)
        
        return {
            'B-bin': self.encode_binary(raw_lamps),
            'B-color': self.encode_color(raw_lamps),
            'B-rowcount': self.encode_rowcount(info),
            'raw': raw_lamps,
            'info': info
        }


def main():
    """Test Berlin Clock implementation"""
    bc = BerlinClock()
    
    # Test with sample time
    test_dt = datetime(1990, 11, 3, 14, 30, 15)  # 14:30:15
    
    print("=== Berlin Clock Test ===")
    print(f"Time: {test_dt}")
    
    raw_lamps, info = bc.state(test_dt)
    print(f"\nRaw lamps (24): {raw_lamps}")
    print(f"Info: {info}")
    
    # Test all encodings
    encodings = bc.get_all_encodings(test_dt)
    for enc_name, enc_values in encodings.items():
        if enc_name != 'info':
            print(f"\n{enc_name}: {enc_values[:12]}... (first 12 of 24)")
    
    # Verify clock reading
    print("\n=== Clock Reading Verification ===")
    print(f"Time: {info['hours']:02d}:{info['minutes']:02d}")
    print(f"R1 (5-hour blocks): {info['r1_count']} lamps lit = {info['r1_count'] * 5} hours")
    print(f"R2 (1-hour blocks): {info['r2_count']} lamps lit = {info['r2_count']} hours")
    print(f"Total hours: {info['r1_count'] * 5 + info['r2_count']}")
    print(f"R3 (5-min blocks): {info['r3_count']} lamps lit = {info['r3_count'] * 5} minutes")
    print(f"R4 (1-min blocks): {info['r4_count']} lamps lit = {info['r4_count']} minutes")
    print(f"Total minutes: {info['r3_count'] * 5 + info['r4_count']}")


if __name__ == "__main__":
    main()