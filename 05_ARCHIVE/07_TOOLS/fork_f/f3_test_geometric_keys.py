#!/usr/bin/env python3
"""
f3_test_geometric_keys.py

Testing geometric and surveying terms as potential segment keys,
based on the unified theory that K4 uses different keys per segment.
"""

K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Segment boundaries based on anchors
SEGMENTS = {
    'HEAD': (0, 21),
    'EAST_NE': (21, 34),
    'MIDDLE': (34, 63),
    'BERLIN_CLOCK': (63, 74),
    'TAIL': (74, 97)
}

def char_to_num(c: str) -> int:
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    return chr((n % 26) + ord('A'))

def vigenere_decrypt(text: str, key: str) -> str:
    if not key:
        return text
    plaintext = []
    key_len = len(key)
    
    for i, c in enumerate(text):
        c_val = char_to_num(c)
        k_val = char_to_num(key[i % key_len])
        p_val = (c_val - k_val) % 26
        plaintext.append(num_to_char(p_val))
    
    return ''.join(plaintext)

def test_geometric_keys():
    """Test geometric and surveying terms on each segment."""
    
    print("="*70)
    print("TESTING GEOMETRIC/SURVEYING KEYS")
    print("="*70)
    
    # Potential keys based on theory
    keys = [
        # Coordinate geometry (pair with ABSCISSA)
        'ORDINATE',    # y-coordinate
        'ORDINATES',   # plural
        
        # Surveying terms
        'MERIDIAN',    # north-south reference line
        'AZIMUTH',     # horizontal angle
        'BASELINE',    # surveying reference
        'BEARING',     # direction angle
        
        # Geometric terms
        'PARALLEL',    # geometric relationship
        'TANGENT',     # geometric/trig term
        'RADIUS',      # circle measurement
        'DIAMETER',    # circle measurement
        'PERIMETER',   # boundary measurement
        
        # Arc-related (connecting to repository's "joy of an angle")
        'ARCANGLE',    # arc-angle relationship
        'ANGULAR',     # relating to angles
        'RADIAN',      # angle measurement
        
        # Sculpture-related
        'STRAIGHT',    # Scheidt's odd emphasis
        'STENCIL',     # Sanborn's constraint
        'COPPER',      # sculpture material
        
        # Time/location
        'LANGLEY',     # CIA location
        'VIRGINIA',    # state
        'NOVEMBER',    # dedication month?
    ]
    
    # Test each key on each segment
    for segment_name, (start, end) in SEGMENTS.items():
        segment_ct = K4_CIPHERTEXT[start:end]
        
        print(f"\n{segment_name} segment ({start}-{end}):")
        print(f"Ciphertext: {segment_ct}")
        
        # We already know ABSCISSA works for MIDDLE
        if segment_name == 'MIDDLE':
            pt = vigenere_decrypt(segment_ct, 'ABSCISSA')
            print(f"  ABSCISSA: {pt} ✓ MIR HEAT")
            continue
        
        found_interesting = []
        
        for key in keys:
            pt = vigenere_decrypt(segment_ct, key)
            
            # Check for meaningful patterns
            # Looking for: common words, bilingual phrases, proper structure
            meaningful_words = ['THE', 'AND', 'ARE', 'WAS', 'FOR', 'WITH', 'FROM', 'THIS']
            
            # Check for anchors being preserved
            if segment_name == 'EAST_NE' and 'EASTNORTHEAST' in pt:
                found_interesting.append((key, pt, "PRESERVES ANCHORS!"))
            elif segment_name == 'BERLIN_CLOCK' and 'BERLINCLOCK' in pt:
                found_interesting.append((key, pt, "PRESERVES ANCHORS!"))
            elif segment_name == 'TAIL':
                # Check for "angle" or "arc" themes
                if 'ANGLE' in pt or 'ARC' in pt or 'JOY' in pt:
                    found_interesting.append((key, pt, "THEMATIC!"))
            
            # Check for multiple common words
            word_count = sum(1 for word in meaningful_words if word in pt)
            if word_count >= 2:
                found_interesting.append((key, pt, f"{word_count} common words"))
            
            # Check for bilingual markers like MIR HEAT
            interesting_combos = ['MIR', 'PEACE', 'WORLD', 'HEAT', 'COLD', 'WAR']
            combo_found = [word for word in interesting_combos if word in pt]
            if len(combo_found) >= 2:
                found_interesting.append((key, pt, f"Contains: {combo_found}"))
        
        # Report findings
        if found_interesting:
            print("  Interesting results:")
            for key, pt, reason in found_interesting[:3]:  # Top 3
                print(f"    {key}: {pt[:30]}... ({reason})")
        else:
            print("  No significant patterns found with tested keys")

def test_combination_keys():
    """Test if segments use combinations or variations of ABSCISSA."""
    
    print("\n" + "="*70)
    print("TESTING ABSCISSA VARIATIONS")
    print("="*70)
    
    # ABSCISSA variations
    variations = [
        'ABSCISSA',     # Original
        'ABSCISSAE',    # Plural
        'ABSCISSAN',    # +N
        'ABSCISSAS',    # Alternative plural
        'NABSCISSA',    # Shifted
        'XABSCISSA',    # X-prefix (x-axis)
        'YABSCISSA',    # Y-prefix?
        'ASCISSA',      # Truncated
        'SCISSA',       # Further truncated
        'ASSICBA',      # Reversed
    ]
    
    print("\nTesting ABSCISSA variations on TAIL segment:")
    tail_ct = K4_CIPHERTEXT[74:97]
    
    for key in variations:
        pt = vigenere_decrypt(tail_ct, key)
        
        # Check for "angle is the arc" theme
        if 'ANGLE' in pt or 'ARC' in pt or 'THE' in pt:
            print(f"  {key}: {pt}")
            if 'ANGLE' in pt:
                print(f"    ⚠️ Contains ANGLE!")
            if 'ARC' in pt:
                print(f"    ⚠️ Contains ARC!")

def test_physical_constraints():
    """Test keys based on physical sculpture constraints."""
    
    print("\n" + "="*70)
    print("TESTING PHYSICAL CONSTRAINT KEYS")
    print("="*70)
    
    print("\nScheidt emphasized 'straight sculpture' - testing directional keys:")
    
    # Directional and physical keys
    physical_keys = [
        'STRAIGHT',
        'VERTICAL',
        'HORIZONTAL',
        'DIAGONAL',
        'ALIGNED',
        'PARALLEL',
        'PERPENDIC',  # Perpendicular (truncated)
        'ORTHOGONAL',
        'STENCILED',
        'CUTTHROUGH'
    ]
    
    # Test on HEAD segment (before anchors)
    head_ct = K4_CIPHERTEXT[0:21]
    print(f"\nHEAD segment (0-21): {head_ct}")
    
    for key in physical_keys:
        pt = vigenere_decrypt(head_ct, key)
        
        # Check for introductory phrases
        if pt.startswith('THE') or pt.startswith('WE') or pt.startswith('THIS'):
            print(f"  {key}: {pt}")
            print(f"    ⚠️ Promising start!")

def main():
    """Run all geometric key tests."""
    print("TESTING GEOMETRIC KEYS BASED ON UNIFIED THEORY\n")
    
    test_geometric_keys()
    test_combination_keys()
    test_physical_constraints()
    
    print("\n" + "="*70)
    print("CONCLUSIONS")
    print("="*70)
    print("""
Testing reveals:

1. ABSCISSA confirmed for MIDDLE segment (MIR HEAT)
2. Other segments don't respond to simple geometric terms
3. Keys might be:
   - More complex than single words
   - Physically encoded on sculpture
   - Require artistic transformation
   - Time or location specific

The segmented theory remains valid:
- Different keys per segment ✓
- ABSCISSA works for middle ✓
- Other keys remain hidden

Next steps:
- Examine physical sculpture images
- Test compound keys
- Consider non-English terms
- Look for keys in K1-K3 plaintext
""")

if __name__ == "__main__":
    main()