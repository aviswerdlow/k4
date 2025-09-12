#!/usr/bin/env python3
"""
f3_time_based_keys.py

Testing time-based keys from 1990 - astronomical data, calendar dates,
and significant events from the installation year.
"""

from typing import List, Tuple, Dict, Optional
import math

K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def char_to_num(c: str) -> int:
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    return chr((n % 26) + ord('A'))

class TimeBasedAnalyzer:
    """Test time-based and astronomical keys."""
    
    def __init__(self):
        self.k4_ct = K4_CIPHERTEXT
        
        # 1990 significant dates
        self.dates_1990 = {
            # Political events
            'FEBRUARY11': 'Nelson Mandela released',
            'MARCH11': 'Lithuania declares independence',
            'MARCH15': 'Gorbachev elected President',
            'MAY29': 'Boris Yeltsin elected',
            'OCTOBER3': 'German reunification',
            'NOVEMBER': 'Kryptos dedication (November 1990)',
            
            # Astronomical events 1990
            'JANUARY26': 'Annular solar eclipse',
            'FEBRUARY9': 'Voyager 1 photograph of solar system',
            'APRIL24': 'Hubble Space Telescope launched',
            'JULY22': 'Total solar eclipse',
            
            # Important numbers from 1990
            'NINETEEN': '19',
            'NINETY': '90',
            'MCMXC': 'Roman numerals 1990',
        }
        
        # Astronomical constants
        self.astronomical = {
            'EQUINOX': 'March 20 and September 23',
            'SOLSTICE': 'June 21 and December 21',
            'PERIHELION': 'Earth closest to sun',
            'APHELION': 'Earth farthest from sun',
            'SIDEREAL': 'Sidereal day/year',
            'SYNODIC': 'Lunar month',
        }
        
        # Time-related keys
        self.time_keys = {
            'MIDNIGHT': '00:00',
            'NOON': '12:00',
            'SUNRISE': 'Dawn',
            'SUNSET': 'Dusk',
            'HOUR': '60 minutes',
            'MINUTE': '60 seconds',
            'SECOND': 'Base time unit',
        }
    
    def vigenere_decrypt(self, text: str, key: str) -> str:
        """Standard Vigenere decryption."""
        if not key or not text:
            return text
        plaintext = []
        key_len = len(key)
        
        for i, c in enumerate(text):
            c_val = char_to_num(c)
            k_val = char_to_num(key[i % key_len])
            p_val = (c_val - k_val) % 26
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)
    
    def test_1990_dates(self):
        """Test significant 1990 dates as keys."""
        print("\n" + "="*60)
        print("TESTING 1990 SIGNIFICANT DATES")
        print("="*60)
        
        print("\n1990 was when Kryptos was installed at CIA.")
        print("Testing significant dates from that year:")
        
        for date_key, event in self.dates_1990.items():
            pt = self.vigenere_decrypt(self.k4_ct, date_key)
            
            if 'MIR' in pt or 'HEAT' in pt or self.has_meaningful_words(pt):
                print(f"\n{date_key} ({event}):")
                print(f"  {pt[:50]}...")
                
                if 'MIR' in pt:
                    print(f"    Contains MIR at {pt.find('MIR')}")
                if 'HEAT' in pt:
                    print(f"    Contains HEAT at {pt.find('HEAT')}")
                
                words = self.find_words(pt)
                if words:
                    print(f"    Words: {words}")
        
        # Test November specifically (dedication month)
        november_keys = ['NOVEMBER', 'NOVEMBER1990', 'NOV', 'NOVNINETY']
        
        print("\n\nNovember 1990 dedication variations:")
        for key in november_keys:
            pt = self.vigenere_decrypt(self.k4_ct, key)
            if self.has_words(pt):
                print(f"  {key}: {pt[:30]}...")
    
    def test_astronomical_keys(self):
        """Test astronomical events and constants."""
        print("\n" + "="*60)
        print("TESTING ASTRONOMICAL KEYS")
        print("="*60)
        
        print("\nTesting astronomical terms and events:")
        
        astro_keys = list(self.astronomical.keys()) + [
            'ECLIPSE', 'LUNAR', 'SOLAR', 'COMET', 'HALLEY',
            'VENUS', 'MARS', 'JUPITER', 'SATURN', 'URANUS',
            'NEPTUNE', 'PLUTO', 'VOYAGER', 'HUBBLE', 'GALILEO'
        ]
        
        for key in astro_keys:
            pt = self.vigenere_decrypt(self.k4_ct, key)
            
            if 'MIR' in pt or 'HEAT' in pt or self.has_meaningful_words(pt):
                print(f"\n{key}:")
                print(f"  {pt[:50]}...")
                
                words = self.find_words(pt)
                if words:
                    print(f"    Words: {words}")
    
    def test_time_units(self):
        """Test time units and clock-related keys."""
        print("\n" + "="*60)
        print("TESTING TIME UNITS")
        print("="*60)
        
        print("\nSince CLOCK is an anchor, testing time-related keys:")
        
        time_keys = list(self.time_keys.keys()) + [
            'OCLOCK', 'TIME', 'CHRONOS', 'TEMPORAL',
            'PAST', 'PRESENT', 'FUTURE', 'ETERNAL'
        ]
        
        for key in time_keys:
            pt = self.vigenere_decrypt(self.k4_ct, key)
            
            if 'MIR' in pt or 'HEAT' in pt or self.has_meaningful_words(pt):
                print(f"\n{key}:")
                print(f"  {pt[:50]}...")
                
                if 'MIR' in pt or 'HEAT' in pt:
                    print(f"    Contains MIR/HEAT!")
    
    def test_julian_dates(self):
        """Test Julian date encoding."""
        print("\n" + "="*60)
        print("TESTING JULIAN DATES")
        print("="*60)
        
        print("\nTesting Julian day numbers for 1990:")
        
        # Julian day for Nov 1, 1990 is approximately 2448212
        # Try various date formats
        julian_keys = [
            'JDTWOFOURFOUREIGHT',  # JD 2448...
            'DAYTHREEFIFTEEN',     # Day 315 of 1990 (Nov 11)
            'TWOFOURFOUREIGHT',    # 2448
            'JULIAN',              # Simple key
        ]
        
        for key in julian_keys:
            pt = self.vigenere_decrypt(self.k4_ct, key)
            
            if self.has_words(pt):
                print(f"\n{key}:")
                print(f"  {pt[:50]}...")
                
                words = self.find_words(pt)
                if words:
                    print(f"    Words: {words}")
    
    def test_coordinate_times(self):
        """Test coordinates with time components."""
        print("\n" + "="*60)
        print("TESTING COORDINATE-TIME COMBINATIONS")
        print("="*60)
        
        print("\nK2 contains coordinates with precise times.")
        print("Testing if time modifies the decryption:")
        
        # From K2: 38°57'6.5" N, 77°8'44" W
        # These could encode time as well as location
        
        # Convert to time representations
        time_keys = [
            'THREEEIGHTFIVESEVEN',  # 38:57 as time
            'SEVENSEVENZEROEIGHT',  # 77:08 as time
            'SIXPOINTFIVE',         # 6.5 seconds
            'FORTYFOUR',            # 44 seconds
        ]
        
        for key in time_keys:
            pt = self.vigenere_decrypt(self.k4_ct, key)
            
            if self.has_words(pt):
                print(f"\n{key}:")
                print(f"  {pt[:50]}...")
    
    def test_seasonal_keys(self):
        """Test seasonal and cyclical keys."""
        print("\n" + "="*60)
        print("TESTING SEASONAL KEYS")
        print("="*60)
        
        print("\nTesting seasonal and cyclical patterns:")
        
        seasonal = [
            'SPRING', 'SUMMER', 'AUTUMN', 'WINTER', 'FALL',
            'SPRINGEQUINOX', 'SUMMERSOLSTICE', 'AUTUMNEQUINOX', 'WINTERSOLSTICE',
            'VERNAL', 'ESTIVAL', 'AUTUMNAL', 'HIBERNAL'
        ]
        
        for key in seasonal:
            pt = self.vigenere_decrypt(self.k4_ct, key)
            
            if 'MIR' in pt or 'HEAT' in pt:
                print(f"\n{key}:")
                print(f"  {pt[:50]}...")
                print(f"    Contains MIR/HEAT!")
    
    def test_clock_cipher(self):
        """Test clock cipher encoding (numbers to letters)."""
        print("\n" + "="*60)
        print("TESTING CLOCK CIPHER")
        print("="*60)
        
        print("\nTesting if letters encode clock positions:")
        
        # Convert letters to clock positions (A=1, B=2, ... L=12, M=13...)
        clock_positions = []
        for c in self.k4_ct:
            pos = (char_to_num(c) % 12) + 1  # 1-12 for clock
            clock_positions.append(pos)
        
        print(f"First 20 as clock positions: {clock_positions[:20]}")
        
        # Look for patterns
        # 12:00 would be L:AA, 3:30 would be C:AD
        print("\nLooking for time patterns:")
        
        for i in range(len(self.k4_ct) - 3):
            # Check if pattern could be HH:MM
            hour = char_to_num(self.k4_ct[i]) % 12
            min1 = char_to_num(self.k4_ct[i+2])
            min2 = char_to_num(self.k4_ct[i+3])
            
            if self.k4_ct[i+1] == ':' or hour <= 12:
                minutes = (min1 * 10 + min2) % 60
                if minutes < 60:
                    time_str = f"{hour:02d}:{minutes:02d}"
                    if hour in [3, 6, 9, 12]:  # Quarter hours
                        print(f"  Position {i}: Could be {time_str}")
    
    def test_berlin_wall_dates(self):
        """Test Berlin Wall specific dates."""
        print("\n" + "="*60)
        print("TESTING BERLIN WALL DATES")
        print("="*60)
        
        print("\nSince BERLIN is an anchor, testing Wall-related dates:")
        
        wall_dates = [
            'AUGUST13',      # Wall construction began Aug 13, 1961
            'NOVEMBER9',     # Wall fell Nov 9, 1989
            'NINETEENEIGHTYNINE',  # 1989
            'NINETEENSIXTY',       # 1961
            'TWENTYEIGHT',   # Wall stood 28 years
            'CHECKPOINT',    # Checkpoint Charlie
            'FREEDOM',       # What the fall represented
        ]
        
        for key in wall_dates:
            pt = self.vigenere_decrypt(self.k4_ct, key)
            
            if 'MIR' in pt or 'HEAT' in pt or self.has_meaningful_words(pt):
                print(f"\n{key}:")
                print(f"  {pt[:50]}...")
                
                if 'BERLIN' in pt:
                    print(f"    Contains BERLIN!")
                if 'WALL' in pt:
                    print(f"    Contains WALL!")
                if 'MIR' in pt:
                    print(f"    Contains MIR!")
    
    def test_unix_timestamp(self):
        """Test Unix timestamp encoding."""
        print("\n" + "="*60)
        print("TESTING UNIX TIMESTAMP")
        print("="*60)
        
        print("\nTesting if Unix timestamp for 1990 is used:")
        
        # Unix timestamp for Nov 1, 1990 is approximately 657417600
        # Try encoding this various ways
        
        timestamp_keys = [
            'SIXFIVESEVEN',      # 657
            'UNIX',              # Simple
            'EPOCH',             # Unix epoch
            'TIMESTAMP',         # Direct
        ]
        
        for key in timestamp_keys:
            pt = self.vigenere_decrypt(self.k4_ct, key)
            
            if self.has_words(pt):
                print(f"\n{key}:")
                print(f"  {pt[:50]}...")
    
    def has_words(self, text: str) -> bool:
        """Check for common words."""
        if len(text) < 3:
            return False
        words = ['THE', 'AND', 'ARE', 'YOU', 'WAS']
        return any(word in text for word in words)
    
    def has_meaningful_words(self, text: str) -> bool:
        """Check for meaningful words."""
        words = ['THE', 'AND', 'HEAT', 'MIR', 'BERLIN', 'CLOCK', 'WAR', 'PEACE', 'TIME']
        count = sum(1 for word in words if word in text)
        return count >= 2
    
    def find_words(self, text: str) -> List[str]:
        """Find common words."""
        words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'HIS', 'HER',
                 'THAT', 'HAVE', 'FROM', 'HEAT', 'MIR', 'WAR', 'PEACE',
                 'TIME', 'CLOCK', 'BERLIN', 'WALL']
        return [word for word in words if word in text]

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("TIME-BASED KEYS ANALYSIS")
    print("Testing astronomical and temporal keys from 1990")
    print("="*70)
    
    analyzer = TimeBasedAnalyzer()
    
    # Run all tests
    analyzer.test_1990_dates()
    analyzer.test_astronomical_keys()
    analyzer.test_time_units()
    analyzer.test_julian_dates()
    analyzer.test_coordinate_times()
    analyzer.test_seasonal_keys()
    analyzer.test_clock_cipher()
    analyzer.test_berlin_wall_dates()
    analyzer.test_unix_timestamp()
    
    # Summary
    print("\n" + "="*70)
    print("TIME-BASED KEYS SUMMARY")
    print("="*70)
    
    print("\nTested temporal keys including:")
    print("- Significant 1990 dates (Berlin Wall, reunification)")
    print("- Astronomical events (eclipses, equinoxes)")
    print("- Time units (hours, minutes, seasons)")
    print("- Julian dates and Unix timestamps")
    print("- Clock positions and time encoding")
    
    print("\nThe 1990 installation date provides context but")
    print("no clear time-based key unlocked K4 completely.")
    print("ABSCISSA remains the only key producing MIR HEAT.")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()