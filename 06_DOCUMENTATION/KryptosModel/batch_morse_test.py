#!/usr/bin/env python3
"""
Batch test multiple sun angles for Morse patterns
"""

import subprocess
import json
import numpy as np

# Test grid of sun positions
AZIMUTHS = [130, 135, 140]  # ±5° from primary
ALTITUDES = [40, 45, 50]    # ±5° from primary

# Scanline positions to test (adjust based on your render)
SCANLINES = [512, 768, 1024, 1280, 1536]  # Multiple Y positions

results = []

for az in AZIMUTHS:
    for alt in ALTITUDES:
        image_file = f"plaza_shadow_test_az{int(az)}_alt{int(alt)}.png"
        
        for y_line in SCANLINES:
            print(f"Testing {image_file} at y={y_line}")
            
            # Run analysis
            cmd = ["python", "morse_analysis.py", image_file, str(y_line)]
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                
                # Load results
                with open("morse_analysis_results.json", "r") as f:
                    result = json.load(f)
                    result['azimuth'] = az
                    result['altitude'] = alt
                    result['scanline_y'] = y_line
                    results.append(result)
            except:
                pass

# Analyze batch results
significant = [r for r in results if r.get('reject_null', False)]

print(f"\nBatch Analysis Complete")
print(f"Total tests: {len(results)}")
print(f"Significant (p<0.001): {len(significant)}")

if significant:
    print("\nSignificant findings:")
    for r in significant:
        print(f"  Az={r['azimuth']}°, Alt={r['altitude']}°, Y={r['scanline_y']}")
        print(f"    Decoded: '{r['decoded']}'")
        print(f"    P-value: {r['p_value']:.4f}")

# Save all results
with open("batch_morse_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nFull results saved to batch_morse_results.json")
