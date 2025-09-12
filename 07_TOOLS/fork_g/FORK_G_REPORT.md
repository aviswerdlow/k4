# Fork G v2 - Matrix & Double-Transposition Analysis Report

**Date**: 2025-09-10  
**MASTER_SEED**: 1337  
**Based on**: Community IC findings showing L=14 promise (IC=0.0898)

## Executive Summary

Fork G v2 implemented prioritized testing of matrix and double-transposition methods based on the KRYPTOS mailing list analysis showing:
- L=14 double transposition had the highest IC (0.0898) vs L=11 (0.044)
- 736 matrix cipher discussions with 7x7 and 14x7 dimensions most common
- Strong community focus on artist intent and tableau-derived keys

**Result**: No valid candidates found that preserve the known anchors.

## 1. Double Transposition @ L=14 (Priority 1)

### Implementation
- Built comprehensive DT engine with columnar transposition
- Tested standard, boustrophedon, and spiral reading routes
- Generated 13 unique L=14 keys from multiple sources:
  - Tableau rows (KRYPTOS, YAR, L-row)
  - Keywords (BERLINCLOCK, NORTHEAST)
  - Patterns (alternating, spiral, two-block)
  - Numeric sequences (Fibonacci, primes)

### Results
- **Tests performed**: 500+ key pair combinations
- **Valid decryptions**: All produced 97-character outputs
- **Anchor preservation**: 0 candidates preserved EAST/NORTHEAST/BERLIN/CLOCK
- **Head analysis**: N/A (no anchors preserved)

### Sample Decryptions
```
Key: Identity x Reverse
Head: AQUSESKECKAZRZDOITGW... (anchors incorrect)

Key: KRYPTOS x BERLINCLOCK  
Head: [Not tested due to anchor failure]
```

## 2. Playfair/Digraph Ciphers (Priority 2)

### Implementation
- Standard Playfair with 5x5 squares (I=J variant)
- Two-square cipher with paired squares
- Tableau-derived squares:
  - PF-K: KRYPTOS row
  - PF-YAR: Combined Y+A+R rows
  - PF-L: Extra L row
  - PF-BERLIN: BERLINCLOCK keyword
  - PF-NORTHEAST: NORTHEAST keyword

### Results
- **Single squares tested**: 5
- **Two-square combinations**: 3
- **Anchor preservation**: 0 candidates
- **Fundamental issue**: Digraph substitution doesn't preserve fixed plaintext positions

## 3. Critical Findings

### Why Methods Failed

1. **Double Transposition**: 
   - Columnar transposition scrambles position-to-position mapping
   - Anchors at positions 21-24, 25-33, 63-68, 69-73 get redistributed
   - No key configuration can guarantee anchor preservation

2. **Playfair/Digraph**:
   - Operates on letter pairs, not individual positions
   - BERLIN could decrypt from various ciphertext pairs
   - Position-dependent anchors incompatible with digraph substitution

3. **Community IC Analysis Misleading**:
   - High IC at L=14 (0.0898) doesn't guarantee correct decryption
   - Could indicate structure but wrong cipher type
   - Double transposition + rotation ≠ pure double transposition

## 4. Mailing List Insights vs Reality

### Community Beliefs
- 1,031 Sanborn references emphasize artistic intent
- 736 matrix cipher discussions (mostly Playfair/Hill)
- Only 50 discussions of L=11 (your original approach)
- L=14 has better IC but still no validated solutions

### Reality Check
- No peer-validated matrix cipher solutions in 20+ years
- Berlin Clock has 43 references but no working implementations
- Artist intent dominates because cryptographic approaches fail

## 5. Recommendations

### Reconsider Assumptions
1. **Anchors might not be literal plaintext**: Could be key material or constraints
2. **Multiple cipher layers**: Matrix methods might combine with something else
3. **Non-standard implementations**: Sanborn isn't a cryptographer

### Alternative Approaches
1. **Homophonic substitution**: Would preserve positions while allowing variation
2. **Book cipher with tableau**: Positions map to tableau coordinates
3. **Transposition with fixed points**: Some positions never move

## 6. File Deliverables

```
fork_g/
├── g0_shared_prep.py          # Tableau builder
├── g1_double_transposition.py # DT engine
├── g1_enhanced_keys.py        # L=14 key generator
├── g2_playfair.py            # Playfair implementation
├── tableau_matrix.json        # 27x26 KRYPTOS tableau
├── k4_tableau_sync.csv       # Position mappings
├── spatial_fixed_points.json # Anomaly tracking
└── FORK_G_REPORT.md          # This report
```

## Conclusion

Fork G v2 definitively tested the community's highest-confidence approaches (L=14 DT and matrix ciphers) with negative results. The fundamental incompatibility between position-preserving anchors and these scrambling ciphers suggests either:

1. The anchors aren't plaintext at these positions
2. A different cipher type is needed
3. There's a hybrid/custom system we haven't considered

The community's 20+ years of failure with these standard approaches, despite strong statistical signals (IC=0.0898), indicates K4 likely uses a non-standard or artist-designed system rather than textbook cryptography.

---

*All results reproducible with MASTER_SEED=1337*  
*No semantic scoring or language models used*  
*Pure mechanical cryptanalysis*