#!/usr/bin/env python3
"""
Test Fork K components individually to verify implementation
"""

from datetime import datetime
from berlin_clock import BerlinClock
from urania_clock import UraniaTimeZones
from keystream_mappers import KeystreamMapper

def test_components():
    """Test each component individually"""
    
    print("=== Component Testing ===\n")
    
    # Test Berlin Clock
    bc = BerlinClock()
    test_dt = datetime(1990, 11, 3, 14, 30, 0)  # 14:30
    
    print(f"1. Berlin Clock at {test_dt}:")
    raw_lamps, info = bc.state(test_dt)
    print(f"   Raw lamps: {raw_lamps[:12]}... (first 12 of 24)")
    print(f"   Time reading: {info['hours']:02d}:{info['minutes']:02d}")
    print(f"   Row counts: {info['row_counts']}")
    
    # Test Urania Clock
    uc = UraniaTimeZones()
    print(f"\n2. Urania Clock at {test_dt}:")
    hours, info = uc.state(test_dt, dst_mode='off')
    print(f"   Hour values: {hours[:12]}... (first 12 of 24)")
    print(f"   Berlin offset: UTC+{info['berlin_offset']}")
    
    # Test Keystream Mapper
    mapper = KeystreamMapper()
    berlin_vec = bc.encode_color(raw_lamps)
    urania_vec = uc.encode_hours(hours)
    
    print(f"\n3. Keystream Generation:")
    keystream = mapper.generate_keystream(berlin_vec, urania_vec, 'direct_concat', {'jitter': 0})
    print(f"   Keystream length: {len(keystream)}")
    print(f"   First 20 values: {keystream[:20]}")
    print(f"   Value range: {min(keystream)}-{max(keystream)}")
    
    # Test decryption
    print("\n4. Test Decryption:")
    k4_sample = "OBKRUOXOGHULBSOLIFBB"  # First 20 chars
    
    # Simple Vigenere decrypt
    plaintext = []
    for i, c_char in enumerate(k4_sample):
        k_val = keystream[i]
        k_char = chr(k_val + ord('A'))
        p_char = chr((ord(c_char) - ord(k_char)) % 26 + ord('A'))
        plaintext.append(p_char)
    
    result = ''.join(plaintext)
    print(f"   K4 sample: {k4_sample}")
    print(f"   Key vals:  {keystream[:20]}")
    print(f"   Plaintext: {result}")
    
    # Check specific positions for anchors
    print("\n5. Anchor Position Check:")
    print(f"   Position 21-24 should be EAST")
    
    # Generate full 97-char keystream and check anchor positions
    k4_full = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
    
    # Try different keystream variants
    print("\n6. Testing Multiple Keystream Variants:")
    
    variants = mapper.get_all_variants(berlin_vec, urania_vec)
    
    for variant_name, keystream in list(variants.items())[:3]:  # Test first 3
        # Decrypt positions 21-24
        anchor_chars = []
        for i in range(21, 25):
            c_char = k4_full[i]
            k_val = keystream[i]
            k_char = chr(k_val + ord('A'))
            # Try Vigenere
            p_char = chr((ord(c_char) - ord(k_char)) % 26 + ord('A'))
            anchor_chars.append(p_char)
        
        anchor_text = ''.join(anchor_chars)
        print(f"   {variant_name}: pos 21-24 = {anchor_text} (should be EAST)")
        
        if anchor_text == 'EAST':
            print(f"     *** MATCH! Testing full anchors... ***")
            # Check all anchors
            anchors = {
                'EAST': (21, 24),
                'NORTHEAST': (25, 33),
                'BERLIN': (63, 68),
                'CLOCK': (69, 73)
            }
            
            all_match = True
            for anchor_name, (start, end) in anchors.items():
                test_chars = []
                for i in range(start, end + 1):
                    c_char = k4_full[i]
                    k_val = keystream[i]
                    k_char = chr(k_val + ord('A'))
                    p_char = chr((ord(c_char) - ord(k_char)) % 26 + ord('A'))
                    test_chars.append(p_char)
                test_text = ''.join(test_chars)
                match = test_text == anchor_name
                print(f"     {anchor_name}: {test_text} {'✓' if match else '✗'}")
                if not match:
                    all_match = False
            
            if all_match:
                print("     *** ALL ANCHORS MATCH! ***")


if __name__ == "__main__":
    test_components()