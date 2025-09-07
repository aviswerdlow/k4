#!/usr/bin/env python3
"""Test that padding sentinels are rejected in strict mode."""

import tempfile
import unittest
from pathlib import Path
import sys
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from validate_bundle import check_no_padding


class TestNoPadding(unittest.TestCase):
    """Test padding sentinel detection."""
    
    def test_sentinel_bundle_fails(self):
        """Test that a bundle with sentinels fails validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bundle_path = Path(tmpdir)
            
            # Create files with sentinels
            readable_path = bundle_path / "readable_canonical.txt"
            readable_path.write_text(
                "HEAD: WE ARE IN THE GRID SEE XXXX EAST NORTHEAST AND WE ARE BY THE LINE TO SEE YYYYYYY BERLINCLOCK\n"
                "TAIL: [RESERVED]\n"
            )
            
            pt_path = bundle_path / "plaintext_97.txt"
            pt_path.write_text("WEAREINTHEGRIDSEEXXXXEASTNORTHEASTANDWEAREBYTHELINETOSEEYYYYYYYBERLINCLOCK")
            
            # Check should fail
            ok, errors = check_no_padding(bundle_path)
            self.assertFalse(ok)
            self.assertEqual(len(errors), 2)
            self.assertIn("Padding tokens found", errors[0])
            self.assertIn("Padding tokens found", errors[1])
    
    def test_filler_bundle_passes(self):
        """Test that a bundle with lexicon fillers passes validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bundle_path = Path(tmpdir)
            
            # Create files with fillers
            readable_path = bundle_path / "readable_canonical.txt"
            readable_path.write_text(
                "HEAD: WE ARE IN THE GRID SEE THEN EAST NORTHEAST AND WE ARE BY THE LINE TO SEE BETWEEN BERLINCLOCK\n"
                "TAIL: [RESERVED]\n"
            )
            
            pt_path = bundle_path / "plaintext_97.txt"
            pt_path.write_text("WEAREINTHEGRIDSEETHENEASTNORTHEASTANDWEAREBYTHELINETOSEEBETWEENBERLINCLOCK")
            
            # Check should pass
            ok, errors = check_no_padding(bundle_path)
            self.assertTrue(ok)
            self.assertEqual(len(errors), 0)
    
    def test_current_winner_passes(self):
        """Test that the current winner passes validation."""
        winner_path = Path("01_PUBLISHED/winner_HEAD_0020_v522B")
        if winner_path.exists():
            ok, errors = check_no_padding(winner_path)
            self.assertTrue(ok, f"Current winner should have no padding: {errors}")
    
    def test_archived_sentinel_fails(self):
        """Test that the archived sentinel bundle is correctly detected."""
        archive_path = Path("01_PUBLISHED/previous_winners/HEAD_0020_v522B_padding_sentinel")
        if archive_path.exists():
            ok, errors = check_no_padding(archive_path)
            self.assertFalse(ok, "Archived sentinel bundle should be detected")
            self.assertGreater(len(errors), 0, "Should have padding errors")


if __name__ == "__main__":
    # Import validation module
    sys.path.insert(0, str(Path(__file__).parent.parent / "07_TOOLS" / "validation"))
    from validate_bundle import check_no_padding
    
    unittest.main()