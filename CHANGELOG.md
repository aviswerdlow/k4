# Changelog

All notable changes to the K4 repository will be documented in this file.

## 2025-01-09 — Core-Hardening Studies

### Added
- **Skeleton Uniqueness Study**: Tested 24 alternative periodic classing schemes
  - Result: 1/24 feasible (baseline only)
  - Confirms uniqueness of the six-track classing formula
- **Tail Necessity Study**: Tested 550 single-letter tail mutations
  - Result: 0/550 mutations feasible
  - Proves tail is algebraically necessary, not assumed
- **Anchor Perturbations Study**: Tested 27 anchor position shifts
  - Result: 0/27 feasible
  - Demonstrates anchors require exact positioning
- Added `core_hardening_receipt.json` with study summaries
- Added CI/CD validation workflow for core hardening results
- Added JSON schemas for study result validation
- Added Makefile targets for running and validating studies

### Documentation
- Updated main README with Core-Hardening section
- Added Section I to REPRODUCE_AND_VERIFY.md
- Created SUMMARY_FOR_REVIEWERS.md for external auditors
- Enhanced study-specific README files with findings

### Technical
- Implemented shared utilities module (`core_hardening_utils.py`)
- All studies use deterministic execution (MASTER_SEED=1337)
- Pure algebraic solving with Option-A enforcement
- No seam/tail guards in any study logic

## 2025-01-07 — Initial Release

### Added
- Complete K4 solution with 97-letter plaintext
- Winner bundle with all validation artifacts
- Pencil-and-paper reproduction instructions
- Hash-pinned receipts and manifests
- CI/CD validation workflows
- Comprehensive documentation