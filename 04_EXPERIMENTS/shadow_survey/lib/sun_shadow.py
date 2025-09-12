#!/usr/bin/env python3
"""
sun_shadow.py

Solar position and shadow calculation module.
Uses simplified NOAA Solar Position Algorithm (SPA) for local solar calculations.
No external dependencies, deterministic calculations.
"""

import math
from datetime import datetime, timezone, timedelta
from typing import Dict, Tuple

# Constants
MASTER_SEED = 1337

def julian_day(dt: datetime) -> float:
    """
    Calculate Julian Day Number from datetime.
    """
    year = dt.year
    month = dt.month
    day = dt.day + dt.hour/24.0 + dt.minute/1440.0 + dt.second/86400.0
    
    if month <= 2:
        year -= 1
        month += 12
    
    a = math.floor(year / 100)
    b = 2 - a + math.floor(a / 4)
    
    jd = math.floor(365.25 * (year + 4716)) + \
         math.floor(30.6001 * (month + 1)) + day + b - 1524.5
    
    return jd

def julian_century(jd: float) -> float:
    """
    Calculate Julian Century from Julian Day.
    """
    return (jd - 2451545.0) / 36525.0

def solar_declination_hour_angle(dt_utc: datetime, lon_deg: float) -> Tuple[float, float]:
    """
    Calculate solar declination and hour angle.
    Simplified calculation for reasonable accuracy.
    """
    jd = julian_day(dt_utc)
    jc = julian_century(jd)
    
    # Mean longitude of sun
    L0 = 280.46646 + jc * (36000.76983 + jc * 0.0003032)
    L0 = L0 % 360
    
    # Mean anomaly of sun
    M = 357.52911 + jc * (35999.05029 - 0.0001537 * jc)
    M_rad = math.radians(M)
    
    # Equation of center
    C = math.sin(M_rad) * (1.914602 - jc * (0.004817 + 0.000014 * jc)) + \
        math.sin(2 * M_rad) * (0.019993 - 0.000101 * jc) + \
        math.sin(3 * M_rad) * 0.000289
    
    # True longitude of sun
    true_lon = L0 + C
    
    # Apparent longitude (simplified, ignoring nutation)
    app_lon = true_lon - 0.00569
    
    # Mean obliquity of ecliptic
    obliquity = 23.439291 - jc * 0.0130042
    obliquity_rad = math.radians(obliquity)
    app_lon_rad = math.radians(app_lon)
    
    # Solar declination
    declination = math.asin(math.sin(obliquity_rad) * math.sin(app_lon_rad))
    
    # Equation of time (in minutes)
    y = math.tan(obliquity_rad / 2) ** 2
    eq_time = 4 * math.degrees(
        y * math.sin(2 * math.radians(L0)) -
        2 * 0.0167 * math.sin(M_rad) +
        4 * 0.0167 * y * math.sin(M_rad) * math.cos(2 * math.radians(L0)) -
        0.5 * y * y * math.sin(4 * math.radians(L0)) -
        1.25 * 0.0167 * 0.0167 * math.sin(2 * M_rad)
    )
    
    # Time offset in minutes
    time_offset = eq_time - 4 * lon_deg
    
    # True solar time
    true_solar_time = dt_utc.hour * 60 + dt_utc.minute + \
                     dt_utc.second / 60 + time_offset
    
    # Hour angle
    hour_angle = (true_solar_time / 4) - 180
    if hour_angle < -180:
        hour_angle += 360
    elif hour_angle > 180:
        hour_angle -= 360
    
    return math.degrees(declination), hour_angle

def solar_alt_az(dt_local: datetime, lat_deg: float, lon_deg: float, 
                tzinfo=None) -> Tuple[float, float]:
    """
    Calculate solar altitude and azimuth for given local datetime and location.
    
    Args:
        dt_local: Local datetime (naive or aware)
        lat_deg: Latitude in degrees (positive = North)
        lon_deg: Longitude in degrees (positive = East)
        tzinfo: Timezone info if dt_local is naive
    
    Returns:
        (altitude_deg, azimuth_deg) where:
        - altitude: Degrees above horizon (negative = below)
        - azimuth: Degrees from North (0=N, 90=E, 180=S, 270=W)
    """
    # Convert to UTC
    if dt_local.tzinfo is None:
        if tzinfo is None:
            # Assume EST/EDT for Langley
            is_dst = dt_local.month in range(4, 11)  # Simplified DST check
            offset_hours = -4 if is_dst else -5
            tzinfo = timezone(timedelta(hours=offset_hours))
        dt_local = dt_local.replace(tzinfo=tzinfo)
    
    dt_utc = dt_local.astimezone(timezone.utc)
    
    # Get solar position
    declination, hour_angle = solar_declination_hour_angle(dt_utc, lon_deg)
    
    # Convert to radians
    lat_rad = math.radians(lat_deg)
    dec_rad = math.radians(declination)
    ha_rad = math.radians(hour_angle)
    
    # Solar altitude
    alt_rad = math.asin(
        math.sin(lat_rad) * math.sin(dec_rad) +
        math.cos(lat_rad) * math.cos(dec_rad) * math.cos(ha_rad)
    )
    altitude = math.degrees(alt_rad)
    
    # Solar azimuth
    az_rad = math.atan2(
        -math.sin(ha_rad),
        math.tan(dec_rad) * math.cos(lat_rad) - math.sin(lat_rad) * math.cos(ha_rad)
    )
    azimuth = (math.degrees(az_rad) + 180) % 360
    
    return altitude, azimuth

def shadow_params(dt_local: datetime, lat_deg: float = 38.95, 
                 lon_deg: float = -77.146) -> Dict:
    """
    Calculate shadow parameters for given datetime and location.
    
    Args:
        dt_local: Local datetime
        lat_deg: Latitude (default: Langley CIA)
        lon_deg: Longitude (default: Langley CIA)
    
    Returns:
        Dictionary with shadow parameters:
        - datetime: ISO format string
        - sun_alt: Sun altitude in degrees
        - sun_az: Sun azimuth in degrees
        - shadow_angle: Shadow angle in degrees
        - shadow_bearing: Direction of shadow
        - shadow_length_unit: Shadow length for unit gnomon
        - is_night: True if sun below horizon
    """
    sun_alt, sun_az = solar_alt_az(dt_local, lat_deg, lon_deg)
    
    # Shadow calculations
    is_night = sun_alt < 0
    
    if is_night:
        # Night: full shadow
        shadow_angle = 90.0
        shadow_length = float('inf')
    else:
        # Shadow angle is complement of sun altitude
        shadow_angle = max(0, 90 - sun_alt)
        # Shadow length for unit height gnomon
        if sun_alt > 0:
            shadow_length = math.tan(math.radians(shadow_angle))
        else:
            shadow_length = float('inf')
    
    # Shadow bearing is opposite to sun azimuth
    shadow_bearing = (sun_az + 180) % 360
    
    return {
        'datetime': dt_local.isoformat(),
        'sun_alt': round(sun_alt, 2),
        'sun_az': round(sun_az, 2),
        'shadow_angle': round(shadow_angle, 2),
        'shadow_bearing': round(shadow_bearing, 2),
        'shadow_length_unit': round(shadow_length, 3) if shadow_length != float('inf') else 'inf',
        'is_night': is_night
    }

def critical_datetimes() -> list:
    """
    Return list of critical datetimes for testing.
    Includes ±60 min in 15-min increments around each.
    """
    base_times = [
        # Berlin Wall opening (CET = UTC+1)
        datetime(1989, 11, 9, 18, 53, tzinfo=timezone(timedelta(hours=1))),
        # Kryptos dedication (EST = UTC-5)
        datetime(1990, 11, 3, 14, 0, tzinfo=timezone(timedelta(hours=-5))),
        # Summer solstice 1990 (noon local EDT = UTC-4)
        datetime(1990, 6, 21, 12, 0, tzinfo=timezone(timedelta(hours=-4))),
        # Winter solstice 1990 (noon local EST = UTC-5)
        datetime(1990, 12, 21, 12, 0, tzinfo=timezone(timedelta(hours=-5)))
    ]
    
    # Add time variations
    all_times = []
    for base_time in base_times:
        for delta_min in range(-60, 61, 15):
            varied_time = base_time + timedelta(minutes=delta_min)
            all_times.append(varied_time)
    
    return all_times

def langley_hourly_progression(date: datetime.date, start_hour: int = 9, 
                              end_hour: int = 15) -> list:
    """
    Generate hourly progression for a specific date at Langley.
    
    Args:
        date: Date to analyze
        start_hour: Starting hour (local time)
        end_hour: Ending hour (local time)
    
    Returns:
        List of datetime objects for each hour
    """
    times = []
    
    # Determine if DST applies
    is_dst = date.month in range(4, 11)
    offset_hours = -4 if is_dst else -5
    tz = timezone(timedelta(hours=offset_hours))
    
    for hour in range(start_hour, end_hour + 1):
        dt = datetime(date.year, date.month, date.day, hour, 0, tzinfo=tz)
        times.append(dt)
    
    return times

# Test functions
def test_solar_calculations():
    """Test solar calculation functions."""
    print("Testing Solar Calculations")
    print("-" * 50)
    
    # Test for Kryptos dedication
    dedication = datetime(1990, 11, 3, 14, 0, 
                         tzinfo=timezone(timedelta(hours=-5)))
    
    print(f"\nKryptos Dedication: {dedication}")
    params = shadow_params(dedication)
    
    for key, value in params.items():
        print(f"  {key}: {value}")
    
    # Test hourly progression
    print("\nHourly Progression for Nov 3, 1990:")
    print("-" * 30)
    
    for dt in langley_hourly_progression(datetime(1990, 11, 3).date(), 9, 15):
        params = shadow_params(dt)
        print(f"{dt.strftime('%H:%M')}: alt={params['sun_alt']:5.1f}°, "
              f"az={params['sun_az']:5.1f}°, shadow={params['shadow_angle']:5.1f}°")
    
    # Test critical times
    print("\nCritical Datetimes Sample:")
    print("-" * 30)
    
    for dt in critical_datetimes()[:5]:
        params = shadow_params(dt)
        print(f"{dt.strftime('%Y-%m-%d %H:%M %Z')}: "
              f"shadow_angle={params['shadow_angle']:5.1f}°")

if __name__ == "__main__":
    test_solar_calculations()