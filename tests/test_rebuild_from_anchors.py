#!/usr/bin/env python3
"""Smoke test for rebuild_from_anchors tool"""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

class TestRebuildFromAnchors(unittest.TestCase):
    """Test that rebuild_from_anchors produces expected results"""
    
    def test_rebuild_from_anchors_smoke(self):
        """Test that the tool runs and produces expected undetermined count"""
        
        # Run the tool in a temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Run rebuild_from_anchors
            cmd = [
                'python3', '07_TOOLS/rebuild_from_anchors.py',
                '--ct', '02_DATA/ciphertext_97.txt',
                '--anchors', '02_DATA/anchors/four_anchors.json',
                '--out', tmpdir
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Check that it succeeded
            self.assertEqual(result.returncode, 0, 
                           f"Tool failed with stderr: {result.stderr}")
            
            # Check that summary.json was created
            summary_path = Path(tmpdir) / 'summary.json'
            self.assertTrue(summary_path.exists(), 
                          "summary.json not created")
            
            # Check the undetermined count
            with open(summary_path) as f:
                summary = json.load(f)
            
            # With anchors-only, expect 26 undetermined positions
            self.assertEqual(summary['undetermined_count'], 26,
                           f"Expected 26 undetermined positions, got {summary['undetermined_count']}")
            
            # Check that wheels.json was created
            wheels_path = Path(tmpdir) / 'wheels.json'
            self.assertTrue(wheels_path.exists(), 
                          "wheels.json not created")
            
            # Check that derived_plaintext.txt was created
            pt_path = Path(tmpdir) / 'derived_plaintext.txt'
            self.assertTrue(pt_path.exists(), 
                          "derived_plaintext.txt not created")
            
            # Verify the plaintext has the expected anchors
            with open(pt_path) as f:
                plaintext = f.read()
            
            # Check for anchor presence
            self.assertIn('EAST', plaintext[21:25])
            self.assertIn('NORTHEAST', plaintext[25:34])
            self.assertIn('BERLIN', plaintext[63:69])
            self.assertIn('CLOCK', plaintext[69:74])

if __name__ == '__main__':
    unittest.main()