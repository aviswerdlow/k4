# Saturation Notice - Policy v5.1

**Date**: 2025-01-07  
**Policy Version**: 5.1.0  
**Status**: ARCHIVED - SATURATED

## Summary

Context Gate evaluation on v4.1.1 K=200 candidates revealed complete saturation:
- **0/200 candidates passed Context Gate**
- Universal failure on semantic_specificity (all scored 1/5)
- All heads identified as function-word salads

## Root Cause

The v4.1.1 generator optimized for syntactic validity without semantic content:
- Excessive function words (the, and, then, that)
- No content-bearing nouns or concrete terms
- Word sequences that are grammatically legal but semantically empty

## Resolution

This saturation led to development of v5.2 Content-Aware Generation:
- Enforces semantic content during generation
- Uses surveying vocabulary lexicon
- Requires minimum content ratios and noun phrases
- **Result**: 100% Context Gate pass rate in v5.2 pilot

## Archived Files

- `runs/context_gate_v5_1/CONTEXT_JUDGMENTS.csv`: All 200 evaluations
- `runs/context_gate_v5_1/CONTEXT_SUMMARY.md`: Statistical analysis  
- `runs/context_gate_v5_1/context/*.json`: Individual judgments
- `SATURATION_REPORT_v5_1.md`: Comprehensive analysis

## Lessons Learned

1. **Post-hoc filtering insufficient**: Must enforce semantic content during generation
2. **Context Gate effective**: Successfully identified word-salad problem
3. **Lexicon-based generation works**: v5.2 pilot shows 100% success with content constraints

---
**Status**: This v5.1 exploration is permanently archived. See v5.2 for production implementation.