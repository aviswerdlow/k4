# 04_EXPERIMENTS - Supporting Evidence

This directory contains important experiments that provide supporting evidence for the K4 solution.

## Key Experiments

### seam_free/
Evidence for tail invariance - demonstrates that letters [80-96] are consistent across multiple routes and heads.
- See: `runs/20250903/FINAL_SUMMARY.md`

### anchors_only/
Analysis showing that anchors alone don't force the tail - requires the full system of constraints.
- See: `TAIL_FORCING_REPORT.md`

### anchors_multiclass/
Multi-class (c6a/c6b) anchor analysis showing feasibility but not complete tail determination.
- See: `TAIL_FORCING_REPORT.md`

### p74_editorial/
Resolution of P[74] - all 26 letters were lawful, we chose 'T' for readability ("THE JOY").
- See: `runs/20250905/matrix_examples/`

### typo_tolerance/
Levenshtein-1 misspelling tolerance analysis - gate remains strict.
- See: `runs/20250904/`

### cadence_panel/
K1-K3 vs K4 style comparison with token windows and character windows.
- See: `runs/2025-09-05/QUICK_READ.md`

### alternates/
Survey of alternative approaches and adjacent frames.
- See: `runs/2025-09-05/`

## Usage

These experiments provide context and validation for the main solution. They demonstrate:
1. Why certain design choices were made
2. What alternatives were considered
3. How robust the solution is to variations
4. Evidence for claims made in the main documentation
