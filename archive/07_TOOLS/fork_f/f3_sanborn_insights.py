#!/usr/bin/env python3
"""
f3_sanborn_insights.py

Testing non-mathematical, artistic, and visual approaches to K4
based on Sanborn interview clues.
"""

K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Anchor positions
ANCHORS = {
    'EAST': (21, 25),
    'NORTHEAST': (25, 34),
    'BERLIN': (63, 69),
    'CLOCK': (69, 74)
}

def test_visual_patterns():
    """Test typography and visual cipher approaches."""
    print("="*70)
    print("VISUAL/TYPOGRAPHY PATTERNS")
    print("="*70)
    
    print("\n1. Letter shapes and stencil constraints:")
    print("   Letters with holes: A, B, D, O, P, Q, R")
    print("   Letters without holes: C, E, F, G, H, I, J, K, L, M, N, S, T, U, V, W, X, Y, Z")
    
    # Extract letters with/without holes
    holes = set('ABDOPQR')
    with_holes = []
    without_holes = []
    
    for i, c in enumerate(K4_CIPHERTEXT):
        if c in holes:
            with_holes.append((i, c))
        else:
            without_holes.append((i, c))
    
    print(f"\n   K4 has {len(with_holes)} letters with holes:")
    print(f"   Positions: {[p for p, _ in with_holes[:10]]}...")
    print(f"   Pattern: {''.join([c for _, c in with_holes[:20]])}")
    
    # Test if reading only holed/solid letters reveals anything
    holed_only = ''.join([c for _, c in with_holes])
    solid_only = ''.join([c for _, c in without_holes])
    
    print(f"\n2. Reading only 'holed' letters: {holed_only[:40]}...")
    print(f"   Reading only 'solid' letters: {solid_only[:40]}...")
    
    # Check for patterns in positions
    print("\n3. Position patterns of holed letters:")
    hole_distances = []
    for i in range(1, len(with_holes)):
        dist = with_holes[i][0] - with_holes[i-1][0]
        hole_distances.append(dist)
    
    print(f"   Distances: {hole_distances[:20]}...")
    
    # Typography-based grouping (similar shapes)
    print("\n4. Typography groupings (similar letterforms):")
    groups = {
        'verticals': 'IJTL',
        'curves': 'OQGC',
        'angles': 'AVWMN',
        'mixed': 'BDEPRSFHKUXYZ'
    }
    
    for name, letters in groups.items():
        count = sum(1 for c in K4_CIPHERTEXT if c in letters)
        print(f"   {name}: {count} occurrences")

def test_spatial_arrangements():
    """Test physical/spatial transformations."""
    print("\n" + "="*70)
    print("SPATIAL ARRANGEMENTS")
    print("="*70)
    
    # Arrange in grids of different sizes
    grids = [7, 8, 9, 10, 11]  # 97 is prime, but try near factors
    
    for width in grids:
        print(f"\n{width}x{97//width + 1} grid:")
        for row in range(0, 97, width):
            print(f"  {K4_CIPHERTEXT[row:row+width]}")
        
        # Read vertically
        vertical = []
        for col in range(width):
            for row in range(0, 97, width):
                if row + col < 97:
                    vertical.append(K4_CIPHERTEXT[row + col])
        
        vert_str = ''.join(vertical)
        print(f"  Vertical: {vert_str[:30]}...")
        
        # Check anchors in vertical reading
        if 'EAST' in vert_str or 'BERLIN' in vert_str:
            print(f"  ⚠️ Found anchor in vertical reading!")

def test_hidden_revealed_duality():
    """Test the hidden/revealed duality theme."""
    print("\n" + "="*70)
    print("HIDDEN/REVEALED DUALITY")
    print("="*70)
    
    print("\n1. Alternating letters (hidden/revealed):")
    hidden = ''.join([K4_CIPHERTEXT[i] for i in range(0, 97, 2)])
    revealed = ''.join([K4_CIPHERTEXT[i] for i in range(1, 97, 2)])
    
    print(f"   'Hidden' (even): {hidden[:30]}...")
    print(f"   'Revealed' (odd): {revealed[:30]}...")
    
    print("\n2. Mirror/reflection patterns:")
    # Test palindromes and mirrors
    reversed_k4 = K4_CIPHERTEXT[::-1]
    print(f"   Reversed: {reversed_k4[:30]}...")
    
    # XOR forward and backward
    xor_result = []
    for i in range(97):
        f_val = ord(K4_CIPHERTEXT[i]) - ord('A')
        b_val = ord(reversed_k4[i]) - ord('A')
        xor_val = f_val ^ b_val
        xor_result.append(chr((xor_val % 26) + ord('A')))
    
    print(f"   XOR fwd/bwd: {''.join(xor_result[:30])}...")
    
    print("\n3. Archaeological layers (stratigraphic reading):")
    # Divide into "strata" based on anchors
    strata = [
        (0, 21, "Surface"),
        (21, 34, "EAST-NORTHEAST layer"),
        (34, 63, "Middle stratum"),
        (63, 74, "BERLIN-CLOCK layer"),
        (74, 97, "Deep layer")
    ]
    
    for start, end, name in strata:
        segment = K4_CIPHERTEXT[start:end]
        print(f"   {name}: {segment}")

def test_time_dependent():
    """Test time-dependent interpretations."""
    print("\n" + "="*70)
    print("TIME-DEPENDENT PATTERNS")
    print("="*70)
    
    print("\n1. 10-year cycle hypothesis:")
    print("   Created: 1990")
    print("   10 years: 2000 (K1-K3 solved)")
    print("   20 years: 2010 (K4 anchor hints)")
    print("   30 years: 2020 (planned revelation?)")
    print("   35 years: 2025 (current)")
    
    # Test year-based keys
    years = [1990, 2000, 2010, 2020, 2025, 2030]
    for year in years:
        # Convert year to letters (various methods)
        year_str = str(year)
        
        # Method 1: digits as positions
        key1 = ''.join([chr(int(d) + ord('A')) for d in year_str])
        
        # Method 2: year mod 26
        key2 = chr((year % 26) + ord('A')) * 8
        
        print(f"\n   Year {year}:")
        print(f"     Digit key: {key1}")
        print(f"     Mod key: {key2}")

def test_incomplete_information():
    """Test if K4 is informationally incomplete by design."""
    print("\n" + "="*70)
    print("INCOMPLETE INFORMATION HYPOTHESIS")
    print("="*70)
    
    print("\nWhat if K4 requires external information?")
    
    print("\n1. Missing key hypothesis:")
    print("   - Anchors tell us WHERE plaintext goes")
    print("   - But not HOW to decrypt the rest")
    print("   - Key might be elsewhere in Kryptos sculpture")
    
    print("\n2. Two-part message:")
    print("   - K4 might be only half the message")
    print("   - Other half in physical sculpture features")
    print("   - Or in Sanborn's other artworks")
    
    print("\n3. Verification mechanism:")
    print("   - 'Provisions in place for acknowledging'")
    print("   - Solution might trigger something observable")
    print("   - Or match future revealed information")
    
    # Test if MIR HEAT could be a verification phrase
    print("\n4. MIR HEAT as verification?")
    print("   - MIR = Russian for 'peace' or 'world'")
    print("   - HEAT = temperature/energy")
    print("   - Cold War context (1990)")
    print("   - 'World Heat' or 'Peace Heat'?")
    print("   - Statistical improbability suggests significance")

def test_artistic_transformations():
    """Test non-mathematical, artistic transformations."""
    print("\n" + "="*70)
    print("ARTISTIC TRANSFORMATIONS")
    print("="*70)
    
    print("\n1. Geological strata shift:")
    # Shift each "layer" by different amounts
    strata_shifted = ""
    shifts = [0, 4, 9, 6, 3]  # Based on anchor positions?
    
    boundaries = [0, 21, 34, 63, 74, 97]
    for i in range(5):
        start, end = boundaries[i], boundaries[i+1]
        segment = K4_CIPHERTEXT[start:end]
        shift = shifts[i]
        
        shifted_segment = ""
        for c in segment:
            c_val = ord(c) - ord('A')
            shifted_segment += chr(((c_val + shift) % 26) + ord('A'))
        
        strata_shifted += shifted_segment
        print(f"   Layer {i} (shift {shift}): {shifted_segment[:20]}...")
    
    print("\n2. Spiral reading (like archaeological dig):")
    # Create spiral pattern
    # This is complex - simplified version
    print("   [Would require physical sculpture dimensions]")
    
    print("\n3. Shadow/light pattern:")
    # Alternate transformation based on position
    shadow_light = ""
    for i, c in enumerate(K4_CIPHERTEXT):
        c_val = ord(c) - ord('A')
        if i % 3 == 0:  # "Shadow"
            c_val = (c_val + 3) % 26
        elif i % 3 == 1:  # "Penumbra"
            c_val = (c_val - 1) % 26
        # else "Light" - no change
        shadow_light += chr(c_val + ord('A'))
    
    print(f"   Shadow/light: {shadow_light[:40]}...")

def main():
    """Run all Sanborn-inspired tests."""
    print("TESTING SANBORN INTERVIEW INSIGHTS")
    print("Non-mathematical, artistic, and conceptual approaches\n")
    
    test_visual_patterns()
    test_spatial_arrangements()
    test_hidden_revealed_duality()
    test_time_dependent()
    test_incomplete_information()
    test_artistic_transformations()
    
    print("\n" + "="*70)
    print("KEY INSIGHTS")
    print("="*70)
    print("""
Based on Sanborn's interview:

1. K4 likely uses a NON-MATHEMATICAL transformation
   - Sanborn emphasized his mathematical inability
   - Requested systems "that didn't necessarily depend on mathematics"
   
2. Physical/visual properties matter
   - Typography expertise (Herman Zapf connection)
   - Stencil constraints (letters with holes)
   - Spatial arrangements on sculpture
   
3. The solution involves LAYERS of meaning
   - "Plain text itself is cryptic"
   - Hidden/revealed duality
   - Archaeological/stratigraphic themes
   
4. Time might be a factor
   - 10-year artistic cycles
   - "Provisions for acknowledgment" after death
   - Deliberate long-term secrecy
   
5. K4 might be INCOMPLETE by design
   - No one knows full solution (compartmentalized)
   - External verification mechanism
   - Requires information beyond the ciphertext

The MIR HEAT finding remains intriguing in this context:
- Non-mathematical (simple Vigenère)
- Statistically significant
- Bilingual (hidden/revealed duality?)
- But incomplete (by design?)

K4 may require thinking like an ARTIST, not a cryptanalyst.
""")

if __name__ == "__main__":
    main()