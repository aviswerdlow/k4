KRYPTOS MODEL DELIVERABLES
==========================
Generated: 2025-09-13 02:08
Blender Version: 4.3.1

OVERVIEW
--------
This directory contains the complete Kryptos sculpture 3D model analysis,
including 456 tick positions covering all sections (K1-K4), surrogate letter
positions for K4, and cylindrical projection scan results.

DIRECTORY STRUCTURE
-------------------

01_scene/
  Kryptos_work.blend     - Blender working file with all objects and markers
                          - Units: Metric, Scale: 1.0 (1 unit = 1 cm)
                          - Contains POND_CENTER landmark

02_exports/
  kryptos_centerline.csv - Panel centerline (45 points, 10-tick sampling)
  panel_ticks.csv        - All 456 tick positions with arc lengths
  uv_world.csv          - UV↔World mapping (109,183 vertices)
  relief_bake.png       - Grayscale relief texture (4096x1024)
  letters_surrogate_k4.csv - 97 surrogate K4 positions (tick-aligned)

03_projection_scan/
  selections_M15.json   - Top-15 letter selections per angle
  selections_M20.json   - Top-20 letter selections per angle
  selections_M24.json   - Top-24 letter selections per angle
  light_sweep_results.json - Consolidated results for LM scoring
  clpt_receipts.json    - Scan parameters and hashes
  projection_scan_summary.json - Coverage statistics
  scan_config.json      - Cylinder/slit configuration
  frames/              - Would contain 180 irradiance PNGs (not rendered)

04_full_sculpture/
  kryptos_full_sculpture_ticks.csv - All 456 ticks with section assignments
  full_sculpture_cross_section.json - Cross-section paths and keys
  k4_with_full_context.json - K4 positions with alignment data
  cross_section_analysis.json - Spatial relationships summary

05_overlays/
  overlay_uv_panel.png  - UV unwrap visualization
  overlay_uv_centroids.jpeg - Letter positions on UV
  overlay_uv_centroids_marked.jpeg - With position markers

06_receipts/
  kryptos_landmarks.json - Scene landmarks and measurements
  kryptos_geometry_receipts.json - Geometry export documentation
  letter_centroids_receipts.json - Surrogate extraction parameters

KEY SPECIFICATIONS
------------------
• Total arc length: 1267.93 cm
• Tick spacing: ~2.0 cm (456 ticks total)
• Pond center: (-27.82, 21.19, 76.70)
• K4 surrogate letters: 97 (rows: 25, 18, 21, 33)
• Projection scan: 180 angles, 2° steps, 5° slit width

SECTION BREAKDOWN
-----------------
K1: Ticks 0-88 (89 positions)
K2: Ticks 89-179 (91 positions)
K3: Ticks 180-317 (138 positions)
K4: Ticks 318-455 (138 positions)

IMPORTANT NOTES
---------------
1. SURROGATE DATA: The K4 letter positions are extracted from relief
   analysis, not individual letter objects. When vendor provides
   per-letter file, map to tick indices for ground truth.

2. COORDINATE FRAMES: Centroid world coordinates and tick world
   coordinates use different object transforms. The tick indices
   provide consistent ordering regardless of transform.

3. CROSS-SECTION ANALYSIS: 12 X-positions show alignment across
   multiple sections, suggesting K4 solution may require information
   from K1-K3.

4. PROJECTION SCAN: Results ready for 5-gram LM scoring with
   Bonferroni correction. ~44% selection diversity observed.

USAGE
-----
For K4 analysis:
1. Use letters_surrogate_k4.csv for geometric positions
2. Apply cross-section paths from full_sculpture_cross_section.json
3. Score projections with light_sweep_results.json
4. When letters arrive, map to tick indices

For full sculpture:
1. Use kryptos_full_sculpture_ticks.csv for all 456 positions
2. K1-K3 plaintext can be mapped to ticks 0-317
3. Test reading paths that span sections

VALIDATION
----------
All files include SHA-256 hashes in receipts/ for verification.
Tick indices are monotone with respect to arc length.
97 K4 positions confirmed with expected row distribution.
456 total positions cover complete sculpture.

---
End of README
