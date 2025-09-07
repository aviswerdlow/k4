#!/usr/bin/env python3
"""
Test that no padding sentinels appear in published bundles.
Ensures XXXX and YYYYYYY tokens are not present in published files.
"""

import unittest
from pathlib import Path


class TestNoPaddingInPublished(unittest.TestCase):
    """Test that published bundles contain no padding sentinels."""
    
    PADDING_TOKENS = ["XXXX", "YYYYYYY"]
    
    def test_no_padding_in_readable_canonical(self):
        """Test that readable_canonical.txt has no padding tokens."""
        file_path = Path("01_PUBLISHED/latest/readable_canonical.txt")
        
        if not file_path.exists():
            # Try the direct winner path
            file_path = Path("01_PUBLISHED/winner_HEAD_0020_v522B/readable_canonical.txt")
        
        if file_path.exists():
            content = file_path.read_text()
            
            for token in self.PADDING_TOKENS:
                self.assertNotIn(
                    token, 
                    content,
                    f"Padding token {token} found in published readable_canonical.txt. "
                    f"Published bundles must use lexicon fillers, not padding sentinels."
                )
    
    def test_no_padding_in_plaintext(self):
        """Test that plaintext_97.txt has no padding tokens."""
        file_path = Path("01_PUBLISHED/latest/plaintext_97.txt")
        
        if not file_path.exists():
            # Try the direct winner path
            file_path = Path("01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt")
        
        if file_path.exists():
            content = file_path.read_text()
            
            for token in self.PADDING_TOKENS:
                self.assertNotIn(
                    token,
                    content,
                    f"Padding token {token} found in published plaintext_97.txt. "
                    f"Published bundles must use lexicon fillers, not padding sentinels."
                )
    
    def test_lexicon_fillers_present(self):
        """Test that lexicon fillers are present in the published bundle."""
        file_path = Path("01_PUBLISHED/latest/plaintext_97.txt")
        
        if not file_path.exists():
            # Try the direct winner path  
            file_path = Path("01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt")
        
        if file_path.exists():
            content = file_path.read_text()
            
            # Check for the expected fillers
            self.assertIn("THEN", content, "Lexicon filler 'THEN' not found in plaintext")
            self.assertIn("BETWEEN", content, "Lexicon filler 'BETWEEN' not found in plaintext")
            
            # Verify the full expected plaintext
            expected = "WEAREINTHEGRIDSEETHENEASTNORTHEASTANDWEAREBYTHELINETOSEEBETWEENBERLINCLOCK"
            self.assertEqual(
                content.strip(),
                expected,
                "Published plaintext does not match expected filler version"
            )
    
    def test_archived_sentinel_bundle_exists(self):
        """Test that the archived sentinel bundle is preserved for history."""
        archive_path = Path("01_PUBLISHED/previous_winners/HEAD_0020_v522B_padding_sentinel")
        
        self.assertTrue(
            archive_path.exists(),
            "Archived sentinel bundle should be preserved in previous_winners/"
        )
        
        if archive_path.exists():
            # Verify the archived version has sentinels
            pt_path = archive_path / "plaintext_97.txt"
            if pt_path.exists():
                content = pt_path.read_text()
                self.assertIn("XXXX", content, "Archived bundle should contain XXXX sentinel")
                self.assertIn("YYYYYYY", content, "Archived bundle should contain YYYYYYY sentinel")


if __name__ == "__main__":
    unittest.main()