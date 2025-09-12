# Boundary-Aware Tokenization v2.1 Report

**Status**: Report-only (does not affect decision gating)
**Purpose**: Tie-break analysis for function word counts

## Analysis

**Letters at positions 74-79**: `THEJOY`

**Boundary split applied**: Yes

The sequence 'THEJOY' at the head boundary (position 74) was split into:
- 'THE' (positions 74-76) - counted in head window
- 'JOY' (positions 77-79) - excluded from head window

## Function Word Counts

| Tokenization | Head Function Words | List |
|--------------|---------------------|------|
| v2 (decision) | 0 |  |
| v2.1 (report) | 1 | the |

**Delta**: +1 function word(s)

## Implications

This boundary-aware tokenization (v2.1) is used **only** for reporting and potential tie-break analysis. The decision pipeline (phrase gate, null hypothesis testing) continues to use standard v2 tokenization. **This tokenization is report-only; decision gating continues to use tokenization v2.**

The presence of 'THEJOY' at the boundary suggests editorial awareness of the head/tail division, with 'THE' belonging semantically to the head instruction and 'JOY' introducing the tail fragment.
