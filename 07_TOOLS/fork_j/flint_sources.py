#!/usr/bin/env python3
"""
Fork J - Abel Flint Text Sources
Normalized surveying text from "A System of Geometry and Trigonometry with a Treatise on Surveying" (1835)
"""

class FlintSources:
    def __init__(self):
        # Flint field-book opening - "Beginning at a mere-stone..."
        # This appears in Flint's Appendix as a canonical field-book example
        self.field_book_raw = "Beginning at a mere-stone in the east line of the tract, thence north forty-five degrees west two hundred and thirty poles to a white oak"
        
        # Normalize to A-Z only
        self.field_book = self._normalize(self.field_book_raw)
        
        # Flint's definition of angle measurement
        # From the trigonometry section on angle/arc relationships
        self.def_28_raw = "The measure of an angle is the arc of a circle contained between the two lines which form the angle, the arc being described from the vertex as a center"
        
        self.def_28 = self._normalize(self.def_28_raw)
        
        # Additional surveying phrases from Flint
        self.north_south_raw = "by north and south and east and west"
        self.north_south = self._normalize(self.north_south_raw)
        
        # Surveying instructions block (composite from multiple sections)
        self.surveying_block_raw = """
        The surveyor begins at a known point and measures the bearing and distance to the next station.
        Each line is recorded with its bearing in degrees and its length in poles or chains.
        The field book contains a complete record of all measurements taken in the field.
        """
        
        self.surveying_block = self._normalize(self.surveying_block_raw)
        
        # Build PT scaffolds for J.1
        self.pt_scaffolds = self._build_pt_scaffolds()
        
        # Build key sources for J.2
        self.key_sources = self._build_key_sources()
    
    def _normalize(self, text: str) -> str:
        """Normalize text to A-Z only"""
        result = []
        for char in text.upper():
            if 'A' <= char <= 'Z':
                result.append(char)
        return ''.join(result)
    
    def _build_pt_scaffolds(self) -> dict:
        """Build plaintext scaffolds for J.1 testing"""
        scaffolds = {}
        
        # Head from field-book opening
        head = "BEGINNINGATAMERESTONE"  # 21 chars
        
        # Middle section with directional phrasing
        middle = "BYNORTHANDSOUTHANDEASTANDWEST"  # 29 chars
        
        # Two tail variants
        tail_a = "THEMEASUREOFANANGLEISTHEARC"  # 27 chars - Flint's definition
        tail_b = "THEJOYOFANANGLEISTHEARC"  # 23 chars - Prior variant
        
        # Build full scaffolds with anchors
        # Positions: 0-20: head, 21-24: EAST, 25-33: NORTHEAST, 34-62: middle,
        #           63-68: BERLIN, 69-73: CLOCK, 74-96: tail
        
        # Scaffold A (Flint tail)
        scaffold_a = head[:21]  # 0-20
        scaffold_a += "EAST"  # 21-24
        scaffold_a += "NORTHEAST"  # 25-33
        scaffold_a += middle[:29]  # 34-62
        scaffold_a += "BERLIN"  # 63-68
        scaffold_a += "CLOCK"  # 69-73
        scaffold_a += tail_a[:23]  # 74-96 (truncate to fit)
        
        # Scaffold B (Joy variant tail)
        scaffold_b = head[:21]  # 0-20
        scaffold_b += "EAST"  # 21-24
        scaffold_b += "NORTHEAST"  # 25-33
        scaffold_b += middle[:29]  # 34-62
        scaffold_b += "BERLIN"  # 63-68
        scaffold_b += "CLOCK"  # 69-73
        scaffold_b += tail_b  # 74-96
        
        scaffolds['A'] = scaffold_a
        scaffolds['B'] = scaffold_b
        
        # Verify lengths
        assert len(scaffold_a) == 97, f"Scaffold A length: {len(scaffold_a)}"
        assert len(scaffold_b) == 97, f"Scaffold B length: {len(scaffold_b)}"
        
        return scaffolds
    
    def _build_key_sources(self) -> dict:
        """Build key sources for J.2 testing"""
        sources = {}
        
        # Def-28 region (angle/arc definition)
        sources['Flint_Def28'] = self.def_28
        
        # Field-book block (beginning at mere-stone + following)
        sources['Flint_Fieldbook'] = self.field_book + self.surveying_block
        
        # Composite sources
        sources['Flint_Composite'] = self.def_28 + self.field_book + self.surveying_block
        
        # Directional phrase
        sources['Flint_Directional'] = self.north_south * 10  # Repeat to ensure length
        
        return sources
    
    def get_scaffold(self, variant: str) -> str:
        """Get PT scaffold A or B"""
        return self.pt_scaffolds.get(variant, '')
    
    def get_key_source(self, name: str) -> str:
        """Get key source by name"""
        return self.key_sources.get(name, '')
    
    def get_ledger(self) -> str:
        """Generate source ledger for documentation"""
        ledger = []
        ledger.append("=== Fork J - Flint Source Ledger ===\n")
        ledger.append("Abel Flint (1835): A System of Geometry and Trigonometry with a Treatise on Surveying\n")
        ledger.append("\n--- Field-book Opening ---")
        ledger.append(f"Raw: {self.field_book_raw}")
        ledger.append(f"Normalized: {self.field_book[:50]}...")
        ledger.append("Source: Flint's Appendix, field-book example")
        ledger.append("\n--- Definition 28 (Angle/Arc) ---")
        ledger.append(f"Raw: {self.def_28_raw[:100]}...")
        ledger.append(f"Normalized: {self.def_28[:50]}...")
        ledger.append("Source: Trigonometry section, angle measurement")
        ledger.append("\n--- PT Scaffolds ---")
        ledger.append("Scaffold A (Flint tail):")
        ledger.append(f"  0-20: {self.pt_scaffolds['A'][:21]}")
        ledger.append(f"  74-96: {self.pt_scaffolds['A'][74:]}")
        ledger.append("Scaffold B (Joy variant):")
        ledger.append(f"  0-20: {self.pt_scaffolds['B'][:21]}")
        ledger.append(f"  74-96: {self.pt_scaffolds['B'][74:]}")
        
        return '\n'.join(ledger)


def main():
    """Test Flint sources"""
    flint = FlintSources()
    
    print("=== Fork J - Flint Sources ===\n")
    
    # Test scaffolds
    for variant in ['A', 'B']:
        scaffold = flint.get_scaffold(variant)
        print(f"Scaffold {variant} (length={len(scaffold)}):")
        print(f"  Head (0-20): {scaffold[:21]}")
        print(f"  EAST (21-24): {scaffold[21:25]}")
        print(f"  NORTHEAST (25-33): {scaffold[25:34]}")
        print(f"  Middle (34-62): {scaffold[34:63]}")
        print(f"  BERLIN (63-68): {scaffold[63:69]}")
        print(f"  CLOCK (69-73): {scaffold[69:74]}")
        print(f"  Tail (74-96): {scaffold[74:]}")
        print()
    
    # Test key sources
    print("Key sources:")
    for name in ['Flint_Def28', 'Flint_Fieldbook', 'Flint_Composite']:
        source = flint.get_key_source(name)
        print(f"  {name}: length={len(source)}, first 30: {source[:30]}")
    
    print("\n" + flint.get_ledger())


if __name__ == "__main__":
    main()