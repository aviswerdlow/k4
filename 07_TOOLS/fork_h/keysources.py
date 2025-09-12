#!/usr/bin/env python3
"""
Fork H3 - Running Key Sources
Non-periodic key generation from K1-K3 plaintexts and other sources
"""

import json
import os
from typing import Dict, List, Optional

class KeySources:
    def __init__(self):
        # K1, K2, K3 plaintexts (known solutions, normalized to A-Z)
        self.K1_PT = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
        
        self.K2_PT = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONXDOESLANGLEYKNOWABOUTTHISXTHEYSHOULDITSBURIEDOUTTHERESOMEWHEREXWHOKNOWSTHEEXACTLOCATIONONLYWWTHISWASHISLASTMESSAGEXTHIRTYEIGHTDEGREESFIFTYSEVENMINUTESSIXPOINTFIVESECONDSORTHSEVENTYSEVENDEGREESEIGHTMINUTESFORTYFOURSECONDSWESTIDBYROWSLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADEATINYBREACHINTHEUPPERLEFTHANDCORNERANDTHENWIDENINGTHEHOLEALITTLEIINSERTEDTHECANDLEANDPEEREDINTHEHOTAIRSTRIKINGMYFAIRCAUSEDTHEFLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHINEMERGEDFROMTHEMISTXCANYOUSEEANYTHINGQ"
        
        self.K3_PT = "SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADEATINYBREACHINTHEUPPERLEFTHANDCORNERANDTHENWIDENINGTHEHOLEALITTLEIINSERTEDTHECANDLEANDPEEREDINTHEHOTAIRSTRIKINGMYFAIRCAUSEDTHEFLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHINEMERGEDFROMTHEMISTXCANYOUSEEANYTHINGQ"
        
        # Misspellings
        self.IQLUSION = "IQLUSION"
        self.UNDERGRUUND = "UNDERGRUUND"
        self.DESPARATLY = "DESPARATLY"
        
        # Build all key sources
        self.sources = self._build_sources()
    
    def _build_sources(self) -> Dict[str, str]:
        """Build all key source variations"""
        sources = {}
        
        # Direct sources
        sources['K1'] = self.K1_PT
        sources['K2'] = self.K2_PT
        sources['K3'] = self.K3_PT
        sources['K1K2K3'] = self.K1_PT + self.K2_PT + self.K3_PT
        
        # Offset sources (start at specific words)
        # Find offset positions
        between_offset = 0  # K1 starts with BETWEEN
        invisible_offset = self.K2_PT.find("INVISIBLE")
        slowly_offset = self.K3_PT.find("SLOWLY")
        
        sources['K1_BETWEEN'] = self.K1_PT[between_offset:] + self.K1_PT[:between_offset]
        sources['K2_INVISIBLE'] = self.K2_PT[invisible_offset:] + self.K2_PT[:invisible_offset] if invisible_offset >= 0 else self.K2_PT
        sources['K3_SLOWLY'] = self.K3_PT[slowly_offset:] + self.K3_PT[:slowly_offset] if slowly_offset >= 0 else self.K3_PT
        
        # Selective sources
        sources['MISSPELLINGS'] = self.IQLUSION + self.UNDERGRUUND + self.DESPARATLY
        sources['MISSPELLINGS_REV'] = self.DESPARATLY + self.UNDERGRUUND + self.IQLUSION
        
        # Coordinate extraction from K2
        # "THIRTYEIGHTDEGREESFIFTYSEVENMINUTESSIXPOINTFIVESECONDSORTH"
        # "SEVENTYSEVENDEGREESEIGHTMINUTESFORTYFOURSECONDSWEST"
        # Extract numbers and convert to letters
        coords_text = self._extract_coordinates()
        sources['COORDS'] = coords_text
        
        # Composite sources
        # K1K3_MIX: Interleave K1 and K3 (1:1 ratio)
        k1k3_mix = []
        for i in range(max(len(self.K1_PT), len(self.K3_PT))):
            if i < len(self.K1_PT):
                k1k3_mix.append(self.K1_PT[i])
            if i < len(self.K3_PT):
                k1k3_mix.append(self.K3_PT[i])
        sources['K1K3_MIX'] = ''.join(k1k3_mix)
        
        # K1K3_2TO1: 2 chars from K1, 1 from K3
        k1k3_2to1 = []
        k1_idx, k3_idx = 0, 0
        while k1_idx < len(self.K1_PT) or k3_idx < len(self.K3_PT):
            # Take 2 from K1
            for _ in range(2):
                if k1_idx < len(self.K1_PT):
                    k1k3_2to1.append(self.K1_PT[k1_idx])
                    k1_idx += 1
            # Take 1 from K3
            if k3_idx < len(self.K3_PT):
                k1k3_2to1.append(self.K3_PT[k3_idx])
                k3_idx += 1
        sources['K1K3_2TO1'] = ''.join(k1k3_2to1)
        
        # Special tokens
        sources['PALIMPSEST'] = "PALIMPSEST" * 10  # Repeat to get enough length
        sources['ABSCISSA'] = "ABSCISSA" * 13
        sources['KRYPTOS'] = "KRYPTOS" * 14
        sources['BERLINCLOCK'] = "BERLINCLOCK" * 9
        
        # Tableau-based (if available)
        sources['YARD'] = self._build_yard()
        
        return sources
    
    def _extract_coordinates(self) -> str:
        """Extract coordinate numbers from K2 and convert to letters"""
        # Map digits to letters (A=1, B=2, ... I=9, J=0)
        digit_map = {'0': 'J', '1': 'A', '2': 'B', '3': 'C', '4': 'D',
                    '5': 'E', '6': 'F', '7': 'G', '8': 'H', '9': 'I'}
        
        # Extract coordinate phrases from K2
        coord_phrases = [
            "THIRTYEIGHT",  # 38
            "FIFTYSEVEN",   # 57
            "SIX",          # 6
            "FIVE",         # 5 (from "SIXPOINTFIVE")
            "SEVENTYSEVEN", # 77
            "EIGHT",        # 8
            "FORTYFOUR"     # 44
        ]
        
        # Convert to numbers then to letters
        coord_letters = []
        
        # Manual mapping of written numbers to digits
        number_map = {
            "THIRTYEIGHT": "38",
            "FIFTYSEVEN": "57",
            "SIX": "6",
            "FIVE": "5",
            "SEVENTYSEVEN": "77",
            "EIGHT": "8",
            "FORTYFOUR": "44"
        }
        
        for phrase in coord_phrases:
            if phrase in number_map:
                for digit in number_map[phrase]:
                    coord_letters.append(digit_map[digit])
        
        # Also try direct number sequence
        all_coords = "38576577844"  # All coordinates concatenated
        coord_letters2 = ''.join(digit_map[d] for d in all_coords)
        
        return coord_letters2
    
    def _build_yard(self) -> str:
        """Build YARD from tableau rows (placeholder)"""
        # If we had tableau access, we'd build from Y, A, R, D rows
        # For now, use a deterministic pattern
        yard = "YARDABCEFGHIJKLMNOPQSTUVWXZ"
        return yard * 4  # Repeat to ensure length
    
    def get_key_at(self, source_name: str, index: int, offset: int = 0) -> str:
        """Get key character at position with offset"""
        if source_name not in self.sources:
            return '?'
        
        key_stream = self.sources[source_name]
        if not key_stream:
            return '?'
        
        # Apply offset and wrap
        effective_idx = (index + offset) % len(key_stream)
        return key_stream[effective_idx]
    
    def get_source_length(self, source_name: str) -> int:
        """Get length of key source"""
        if source_name not in self.sources:
            return 0
        return len(self.sources[source_name])
    
    def list_sources(self) -> List[str]:
        """List all available key sources"""
        return list(self.sources.keys())
    
    def get_source(self, source_name: str) -> str:
        """Get full key source string"""
        return self.sources.get(source_name, '')


def main():
    """Test key sources"""
    ks = KeySources()
    
    print("=== Fork H3 - Key Sources ===\n")
    
    print("Available sources:")
    for name in ks.list_sources():
        length = ks.get_source_length(name)
        first_20 = ks.get_source(name)[:20] if length > 0 else "N/A"
        print(f"  {name:20} Length: {length:4}  First 20: {first_20}")
    
    print("\nTest key extraction:")
    print(f"K1K2K3 at index 0, offset 0: {ks.get_key_at('K1K2K3', 0, 0)}")
    print(f"K1K2K3 at index 21, offset 0: {ks.get_key_at('K1K2K3', 21, 0)}")
    print(f"K1K2K3 at index 21, offset 7: {ks.get_key_at('K1K2K3', 21, 7)}")
    
    print("\nMisspellings source:")
    print(f"Full: {ks.get_source('MISSPELLINGS')}")
    
    print("\nCoordinates source:")
    print(f"First 50: {ks.get_source('COORDS')[:50]}")


if __name__ == "__main__":
    main()