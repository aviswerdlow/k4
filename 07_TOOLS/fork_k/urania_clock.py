#!/usr/bin/env python3
"""
Fork K - Urania World Time Clock State Generator
Generates 24-element vectors from Urania Weltzeituhr time zones
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple

class UraniaTimeZones:
    def __init__(self):
        """Initialize Urania World Time Clock processor"""
        self.name = "Weltzeituhr"
        
        # 24 representative cities/zones in ring order
        # Based on actual Urania clock cities
        self.cities = [
            ('Reykjavik', 0),      # UTC+0
            ('London', 0),          # UTC+0 (GMT)
            ('Paris', 1),           # UTC+1 (CET)
            ('Berlin', 1),          # UTC+1 (CET)
            ('Cairo', 2),           # UTC+2
            ('Moscow', 3),          # UTC+3
            ('Dubai', 4),           # UTC+4
            ('Karachi', 5),         # UTC+5
            ('Delhi', 5.5),         # UTC+5:30
            ('Dhaka', 6),           # UTC+6
            ('Bangkok', 7),         # UTC+7
            ('Beijing', 8),         # UTC+8
            ('Tokyo', 9),           # UTC+9
            ('Sydney', 10),         # UTC+10
            ('Noumea', 11),         # UTC+11
            ('Auckland', 12),       # UTC+12
            ('Samoa', -11),         # UTC-11
            ('Honolulu', -10),      # UTC-10
            ('Anchorage', -9),      # UTC-9
            ('Los_Angeles', -8),    # UTC-8 (PST)
            ('Denver', -7),         # UTC-7 (MST)
            ('Chicago', -6),        # UTC-6 (CST)
            ('New_York', -5),       # UTC-5 (EST)
            ('Caracas', -4),        # UTC-4
        ]
        
        assert len(self.cities) == 24, f"Expected 24 cities, got {len(self.cities)}"
    
    def state(self, dt: datetime, dst_mode: str = 'off') -> Tuple[List[int], Dict]:
        """
        Return a length-24 vector describing 24 time zone hours at dt.
        
        Args:
            dt: Source datetime (assumed Europe/Berlin local time)
            dst_mode: 'off', 'on', or 'auto' for DST handling
        
        Returns:
            hours: List of 24 hour values (0-23)
            info: Dict with metadata
        """
        # Convert dt to UTC for calculations
        berlin_offset_hours = 1  # Base CET offset
        
        # Apply DST if needed
        if dst_mode == 'on':
            berlin_offset_hours = 2  # CEST
        elif dst_mode == 'auto':
            # Simplified DST check for 1990 (last Sunday March to last Sunday October)
            if 3 <= dt.month <= 10:
                if dt.month > 3 and dt.month < 10:
                    berlin_offset_hours = 2
                # More complex logic would be needed for edge months
        
        # Convert Berlin time to UTC
        utc_dt = dt - timedelta(hours=berlin_offset_hours)
        
        # Calculate local hour for each city
        hours = []
        city_times = []
        
        for city_name, base_offset in self.cities:
            # Apply DST adjustments if mode is 'on' or 'auto'
            offset = base_offset
            if dst_mode == 'on' and base_offset != 0:
                # Simplified: add 1 hour DST to non-UTC zones
                # Real implementation would need per-zone DST rules
                if -8 <= base_offset <= -5 or 1 <= base_offset <= 2:
                    offset += 1
            
            # Calculate local time
            local_dt = utc_dt + timedelta(hours=offset)
            local_hour = local_dt.hour
            hours.append(local_hour)
            city_times.append({
                'city': city_name,
                'offset': offset,
                'hour': local_hour,
                'time': local_dt.strftime('%H:%M')
            })
        
        # Create info dict
        info = {
            'source_time': dt.strftime('%Y-%m-%d %H:%M:%S'),
            'utc_time': utc_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'berlin_offset': berlin_offset_hours,
            'dst_mode': dst_mode,
            'city_times': city_times
        }
        
        return hours, info
    
    def encode_hours(self, hours: List[int]) -> List[int]:
        """Encode as raw hours (0-23)"""
        return hours.copy()
    
    def encode_scaled(self, hours: List[int]) -> List[int]:
        """Scale hours 0-23 to 0-25 range"""
        scaled = []
        for h in hours:
            # Map 0-23 to 0-25
            # Simple linear scaling with injection points
            if h <= 11:
                scaled.append(h)
            elif h == 12:
                scaled.append(13)  # Skip 12, inject gap
            elif h <= 22:
                scaled.append(h + 1)
            else:  # h == 23
                scaled.append(25)
        return scaled
    
    def encode_minutes(self, hours: List[int]) -> List[int]:
        """Encode as minutes past midnight (0-1439) mod 26"""
        minutes = []
        for h in hours:
            mins_past_midnight = h * 60
            # Map to 0-25 range
            minutes.append(mins_past_midnight % 26)
        return minutes
    
    def get_all_encodings(self, dt: datetime, dst_mode: str = 'off') -> Dict:
        """Get all encoding variants for a datetime"""
        hours, info = self.state(dt, dst_mode)
        
        return {
            'U-hour': self.encode_hours(hours),
            'U-scaled': self.encode_scaled(hours),
            'U-minutes': self.encode_minutes(hours),
            'raw': hours,
            'info': info
        }


def main():
    """Test Urania Clock implementation"""
    uc = UraniaTimeZones()
    
    # Test with sample time
    test_dt = datetime(1990, 11, 3, 14, 30, 15)  # Nov 3, 1990, 14:30:15
    
    print("=== Urania World Time Clock Test ===")
    print(f"Berlin Time: {test_dt}")
    
    # Test with DST off
    hours, info = uc.state(test_dt, dst_mode='off')
    print(f"\nRaw hours (24 cities): {hours}")
    print(f"UTC time: {info['utc_time']}")
    print(f"Berlin offset: UTC+{info['berlin_offset']}")
    
    # Show first few cities
    print("\nFirst 6 cities:")
    for ct in info['city_times'][:6]:
        print(f"  {ct['city']:12} UTC{ct['offset']:+.1f} -> {ct['time']}")
    
    # Test encodings
    encodings = uc.get_all_encodings(test_dt, dst_mode='off')
    for enc_name, enc_values in encodings.items():
        if enc_name not in ['raw', 'info']:
            print(f"\n{enc_name}: {enc_values[:12]}... (first 12 of 24)")


if __name__ == "__main__":
    main()