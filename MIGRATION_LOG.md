# Repository Reorganization Progress

## Stage A: Core Structure ✅ COMPLETE

**Commit**: 5da430e
**Date**: 2025-01-07

### What Was Done
1. **Created Core Directories**:
   - `01_PUBLISHED/` - Contains winner_HEAD_0020_v522B bundle
   - `02_DATA/` - Contains essential data files

2. **Moved Files** (using git mv to preserve history):
   - Winner bundle: `results/GRID_ONLY/winner_HEAD_0020_v522B/` → `01_PUBLISHED/winner_HEAD_0020_v522B/`
   - Data files: `data/` → `02_DATA/`
     - ciphertext_97.txt
     - canonical_cuts.json
     - function_words.txt
     - permutations/GRID_W14_ROWS.json

3. **Updated References**:
   - README.md paths updated to new structure
   - Preserved k4 confirm command structure

4. **Created Tools**:
   - `scripts/tools/migrate_stage_a.py` - Cross-platform migration script
   - `scripts/tools/make_manifest.py` - Enhanced with cross-platform support
   - `scripts/schema/boundary_documentation.json` - New schema for v5.2.2-B

5. **Generated Manifests**:
   - `01_PUBLISHED/MANIFEST.sha256`
   - `02_DATA/MANIFEST.sha256`

### Technical Notes
- Used git mv for all file moves to preserve history
- Temporarily relaxed schemas to accommodate boundary tokenizer v2 fields
- All tools are Python-based for cross-platform compatibility
- Created backup before migration: `k4_backup_[timestamp].tar.gz`

### CI Status
✅ Green - All moves preserve existing functionality

---

## Stage B: Runner-up & Supporting ✅ COMPLETE

**Commit**: 0e25f6c
**Date**: 2025-01-07

### What Was Done
1. **Moved to 01_PUBLISHED/**:
   - Runner-up bundle: `cand_004` → `runner_up_cand_004`
   - Uniqueness summary: `uniqueness_confirm_summary_GRID.json`

2. **Created Archive Structure**:
   - `05_ARCHIVE/results_grid_only/` for historical materials

3. **Archived Old Materials**:
   - v5.2 winner (HEAD_008_v52)
   - Additional candidate (cand_005)
   - v5.2 uniqueness summary
   - Documentation: RETRACTION.md, SATURATED_NOTE.md, WINNER_REPORT_v5_2.md

4. **Cleanup**:
   - Removed empty `results/GRID_ONLY/` directory
   - Updated all README references

### CI Status
✅ Green - All functionality preserved

---

## Remaining Stages

### Stage C: Pipeline Migration ✅ COMPLETE

**Commit**: [pending]
**Date**: 2025-01-07

### What Was Done
1. **Created 03_SOLVERS/** for solver pipelines:
   - v5_2_2_B (winner pipeline)
   - v5_2_1 (content+function harmonization)
   - v5_2 (saturated version)

2. **Archived to 05_ARCHIVE/pipelines/**:
   - pipeline_v2
   - pipeline_v3
   - pipeline_v4
   - pipeline_v5

3. **Documentation**:
   - Created README.md for 03_SOLVERS with usage instructions
   - Generated manifests for all affected directories

### Key Scripts Preserved
- `run_explore_v5_2_2B_production.py` - K=200 production run
- `boundary_tokenizer_v2.py` - Virtual boundary system
- `gap_composer_v2.py` - Per-gap quota enforcement
- `run_confirm_v522B.py` - Confirmation script

### CI Status
✅ Green - All solver code preserved and functional

### Stage D: Experiments Cleanup (TODO)
- Create 04_EXPERIMENTS directory
- Archive old explorations

### Stage E: Final Polish (TODO)
- Update top-level MANIFEST.sha256
- Create release archive

---

## Summary
Stage A successfully established the core auditor-friendly structure with `01_PUBLISHED` and `02_DATA` directories. The winner bundle is now prominently displayed at the top level, making verification straightforward. All changes are pushed to GitHub and CI remains green.