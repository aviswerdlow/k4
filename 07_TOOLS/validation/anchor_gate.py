#!/usr/bin/env python3
"""
Anchor Gate - Strict validator for four immutable anchors in K4 plaintext
"""

from typing import Dict, List, Tuple, Optional


class AnchorGate:
    """Validates exact anchor text at fixed positions"""
    
    # Immutable anchors (0-based indices)
    ANCHORS = {
        'EAST': (21, 24),       # positions 21-24
        'NORTHEAST': (25, 33),  # positions 25-33  
        'BERLIN': (63, 68),     # positions 63-68
        'CLOCK': (69, 73)       # positions 69-73
    }
    
    @classmethod
    def validate(cls, plaintext: str) -> Tuple[bool, Dict[str, bool], List[str]]:
        """
        Validate all anchors in plaintext
        
        Args:
            plaintext: Decrypted text to validate
            
        Returns:
            (all_valid, anchor_results, errors)
        """
        plaintext = plaintext.upper()
        results = {}
        errors = []
        
        for anchor_name, (start, end) in cls.ANCHORS.items():
            # Extract text at anchor position (end is inclusive)
            if len(plaintext) > end:
                actual = plaintext[start:end+1]
                expected = anchor_name
                
                if actual == expected:
                    results[anchor_name] = True
                else:
                    results[anchor_name] = False
                    errors.append(f"{anchor_name}: Expected '{expected}' at {start}-{end}, got '{actual}'")
            else:
                results[anchor_name] = False
                errors.append(f"{anchor_name}: Plaintext too short (need position {end})")
        
        all_valid = all(results.values())
        return all_valid, results, errors
    
    @classmethod
    def get_anchor_indices(cls) -> List[int]:
        """Get all indices covered by anchors"""
        indices = []
        for start, end in cls.ANCHORS.values():
            indices.extend(range(start, end + 1))
        return sorted(indices)
    
    @classmethod
    def get_non_anchor_text(cls, plaintext: str) -> str:
        """
        Extract text excluding anchor positions
        
        Returns text from [0..20] + [34..62] + [74..96]
        """
        plaintext = plaintext.upper()
        anchor_indices = set(cls.get_anchor_indices())
        
        non_anchor = []
        for i, char in enumerate(plaintext):
            if i not in anchor_indices:
                non_anchor.append(char)
        
        return ''.join(non_anchor)
    
    @classmethod
    def get_non_anchor_segments(cls, plaintext: str) -> Dict[str, str]:
        """Get non-anchor text by segment"""
        return {
            'pre_EAST': plaintext[0:21] if len(plaintext) > 20 else plaintext[0:],
            'mid_gap': plaintext[34:63] if len(plaintext) > 62 else '',
            'post_CLOCK': plaintext[74:97] if len(plaintext) > 73 else ''
        }
    
    @classmethod
    def score_non_anchor_english(cls, plaintext: str) -> Dict[str, any]:
        """
        Score English quality excluding anchor positions
        """
        non_anchor = cls.get_non_anchor_text(plaintext)
        
        # Function words to check
        function_words = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL',
                         'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'ITS', 'CAN', 'HAD']
        
        # Count function words in non-anchor text
        found_words = []
        for word in function_words:
            if word in non_anchor:
                found_words.append(word)
        
        # Score based on common patterns
        score = 0
        for tri in ['THE', 'AND', 'ING', 'HER', 'HAT', 'HIS', 'THA', 'ERE', 'FOR', 'ENT']:
            score += non_anchor.count(tri) * 3
        for bi in ['TH', 'HE', 'IN', 'ER', 'AN', 'ED', 'ND', 'TO', 'EN', 'ES']:
            score += non_anchor.count(bi)
        
        return {
            'non_anchor_length': len(non_anchor),
            'function_words': found_words,
            'function_word_count': len(found_words),
            'english_score': score,
            'score_per_char': score / len(non_anchor) if len(non_anchor) > 0 else 0
        }
    
    @classmethod
    def quick_report(cls, plaintext: str) -> str:
        """Generate a quick validation report"""
        valid, results, errors = cls.validate(plaintext)
        english = cls.score_non_anchor_english(plaintext)
        
        report = []
        report.append("ANCHOR VALIDATION")
        report.append("=" * 50)
        
        for anchor, (start, end) in cls.ANCHORS.items():
            status = "✅" if results.get(anchor, False) else "❌"
            actual = plaintext[start:end+1] if len(plaintext) > end else "TOO SHORT"
            report.append(f"{status} {anchor:10} [{start:2}-{end:2}]: {actual}")
        
        report.append("")
        report.append("NON-ANCHOR ENGLISH")
        report.append("-" * 50)
        report.append(f"Function words: {', '.join(english['function_words']) if english['function_words'] else 'None'}")
        report.append(f"English score: {english['english_score']} ({english['score_per_char']:.3f}/char)")
        
        if not valid:
            report.append("")
            report.append("ERRORS")
            report.append("-" * 50)
            for error in errors:
                report.append(f"  {error}")
        
        return '\n'.join(report)


def main():
    """Test the anchor gate"""
    import sys
    
    # Test with a sample plaintext
    if len(sys.argv) > 1:
        plaintext = sys.argv[1]
    else:
        # Test with a constructed example
        plaintext = "A" * 21 + "EAST" + "NORTHEAST" + "B" * 30 + "BERLIN" + "CLOCK" + "C" * 23
    
    print(AnchorGate.quick_report(plaintext))
    
    # Also test validation
    valid, results, errors = AnchorGate.validate(plaintext)
    print(f"\nValidation result: {'PASS' if valid else 'FAIL'}")
    
    if valid:
        print("All anchors validated successfully!")
    else:
        print("Anchor validation failed:")
        for error in errors:
            print(f"  - {error}")


if __name__ == '__main__':
    main()