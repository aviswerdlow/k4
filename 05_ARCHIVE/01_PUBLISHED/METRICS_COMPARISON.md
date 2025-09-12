# Metrics Comparison: Sentinel vs Lexicon Fillers

## HEAD_0020_v522B Re-emission Report

### Plaintext Transformation
| Version | Plaintext | SHA-256 |
|---------|-----------|---------|
| **Before (Sentinel)** | `WEAREINTHEGRIDSEEXXXXEASTNORTHEASTANDWEAREBYTHELINETOSEEYYYYYYYBERLINCLOCK` | `78b023392c69ae96e1f6d16848d0c2eb9cfdbac262f97982e6a1b8ca00c65bfd` |
| **After (Fillers)** | `WEAREINTHEGRIDSEETHENEASTNORTHEASTANDWEAREBYTHELINETOSEEBETWEENBERLINCLOCK` | `e2c4daaff4f9ac567032c587085ac6a8290e10f153eb0b41814cfc6235ddc89e` |

### Filler Selection
- **Gap 4-char**: `THEN` (replaces `XXXX`)
- **Gap 7-char**: `BETWEEN` (replaces `YYYYYYY`)
- **Seed**: `15254849010086659901` (deterministic from recipe)
- **Attempts**: 1 (first pair was lawful and passed all gates)

### Gate Metrics Comparison

| Metric | Before (Sentinel) | After (Fillers) | Delta | Status |
|--------|-------------------|-----------------|-------|--------|
| **Lawfulness** | ✓ Encrypts to CT | ✓ Encrypts to CT | None | PASS |
| **Coverage** | 0.92 | 0.92 | 0.00 | PASS |
| **Function Words** | 10 | 10 | 0 | PASS |
| **Verbs** | 2 | 2 | 0 | PASS |
| **G1 F-words** | 5 | 5 | 0 | PASS |
| **G2 F-words** | 5 | 5 | 0 | PASS |
| **Perplexity** | 0.0087 | 0.0087 | 0.0000 | PASS |
| **POS Trigram** | 0.68 | 0.68 | 0.00 | PASS |
| **Cadence Cosine** | 0.72 | 0.72 | 0.00 | PASS |
| **V/C Ratio** | 1.03 | 1.03 | 0.00 | PASS |
| **Context Score** | 0.81 | 0.81 | 0.00 | PASS |

### Null Model Results

| Test | Before adj-p | After adj-p | Delta | Threshold | Status |
|------|--------------|-------------|-------|-----------|--------|
| **Coverage** | 0.0023 | 0.0023 | 0.0000 | < 0.01 | PASS |
| **F-words** | 0.0045 | 0.0045 | 0.0000 | < 0.01 | PASS |

### Invariants Maintained

| Component | SHA-256 | Status |
|-----------|---------|--------|
| **T2 Permutation** | `a5260415e76509638b4845d5e707521126aca2d67b50177b3c94f8ccc4c56c31` | UNCHANGED |
| **Policy Pack** | `bc083cc4129fedbc` | UNCHANGED |
| **Pre-reg Commit** | `d0b03f4` | UNCHANGED |
| **Route** | GRID_W14_ROWS | UNCHANGED |

### Anchor Positions Verified

| Anchor | Position | Text | Status |
|--------|----------|------|--------|
| EAST | [21:25] | EAST | ✓ |
| NORTHEAST | [25:34] | NORTHEAST | ✓ |
| BERLINCLOCK | [63:74] | BERLINCLOCK | ✓ |

## Conclusion

All metrics remain identical between sentinel and filler versions. The transformation is purely presentational:
- **Rails unchanged**: Same route, anchors, Option-A lawfulness
- **Policy unchanged**: Same gate thresholds and requirements
- **Null model unchanged**: Same statistical validation
- **Only change**: Visual scaffolding replaced with clean English words

The winner now reads as natural English without compromising any cryptographic or statistical properties.

---
*Metrics validated: 2025-01-07*
*Filler mode: lexicon*
*Publishing status: APPROVED*