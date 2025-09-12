#!/usr/bin/env python3
"""
Runner script for rebuild_from_anchors tool.
Imports and calls 07_TOOLS/rebuild_from_anchors.py with repo's default inputs.
"""

import sys
import os

# Add parent directories to path to import the tool
sys.path.insert(0, os.path.abspath('../../..'))

from pathlib import Path

# Import the main tool
import importlib.util
spec = importlib.util.spec_from_file_location(
    "rebuild_from_anchors", 
    "../../../07_TOOLS/rebuild_from_anchors.py"
)
rebuild_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rebuild_module)

def main():
    """Run rebuild_from_anchors with default repo inputs"""
    
    # Default inputs
    ct_path = "../../../02_DATA/ciphertext_97.txt"
    anchors_path = "../../../02_DATA/anchors/four_anchors.json"
    output_dir = "."  # Current folder
    
    print(f"Running rebuild_from_anchors with default inputs:")
    print(f"  CT: {ct_path}")
    print(f"  Anchors: {anchors_path}")
    print(f"  Output: {output_dir}")
    print()
    
    # Call the main function from the imported module
    sys.argv = [
        "rebuild_from_anchors.py",
        "--ct", ct_path,
        "--anchors", anchors_path,
        "--out", output_dir
    ]
    
    rebuild_module.main()

if __name__ == "__main__":
    main()