# Analysis Plan: Explore v4.1 - Language-First Generation
**Pre-registered**: 2025-01-06  
**Commit Hash**: 4d5ce800e9425812f8ebf2c7a9041191616189a1  
**Master Seed**: 1338  
**CT SHA-256**: eea813570c7f1fd3b34674e47b5c3da8948026f5cefee612a0b38ffaa515ceab

## Objective
Generate head-window strings that:
1. Already satisfy linguistic gates BEFORE anchor insertion
2. Survive blinding and maintain quality after anchor placement
3. Pass near-gate: coverage ≥0.85, f-words ≥8, has-verb = true

## Generation Strategy

### A. Grammar-First Generation (WFSA/PCFG)
- **Templates**: Imperative S/V/O patterns without narrative tokens
  - `SET THE <COURSE|LINE> TRUE; <READ|SEE> <THEN> <SEE|NOTE>`
  - `APPLY <CORRECTION|DECLINATION>; <READ|SEE>`
- **Constraints**: POS tags, function-word rhythm
- **Placeholders**: [DIR1], [DIR2], [NOUN1], [NOUN2] for anchors

### B. Multi-Objective MCMC
**Objective terms**:
- λ_fw = 0.3: function-word count
- λ_verb = 0.2: verb presence
- λ_cov = 0.25: dictionary coverage [0,74]
- λ_ng = 0.25: blinded trigram score

**No anchor strings during generation** (EAST/NORTHEAST/BERLIN/CLOCK excluded)

### C. Anchor Placement Strategy
1. **Pareto optimization** with saliency maps
2. **Drop model** to predict post-anchor damage
3. **Local repair** with neutral moves (±2 chars of insertions)
4. **Target**: Retain ≥80% blinded score around insertions

## Acceptance Criteria

### Explore Entry Requirements
- Head [0,74] passes near-gate in UNANCHORED form
- Predicted post-anchor: f-words ≥8, has-verb = true
- Coverage retention ≥80% after placement

### Delta Margins
- δ_fixed: baseline comparison
- δ_windowed ≥ 0.05: windowed must beat fixed
- δ_shuffled ≥ 0.10: must exceed shuffled control

### Anchor Modes
Run all three for each head:
1. **Fixed**: Exact indices [21-24], [25-33], [63-73]
2. **Windowed**: r∈{2,3,4}, typo_budget∈{0,1}
3. **Shuffled**: Control for leakage

## Orbit Mapping
**ε-isolation threshold**: 0.05
- Single/double neutral edits in low-saliency positions
- Anchor-equivalent placements within window
- GRID conjugates preserving anchors
- Downgrade if >5% of neighbors tie within δ=0.01

## Null Hypothesis Testing
**Explore**: 1k mirrored nulls, Holm m=2 on {coverage, f-words}
**Confirm**: Idle unless head is:
- Delta-passing (fixed + windowed)
- Orbit-isolated (ε < 0.05)
- Null-surviving (p_adj < 0.01)

## Batch Configuration
- **Track A-L**: Language-first generation
- **K**: 200 heads per batch
- **Stages**: 4-stage MCMC (T: 3.0→2.0→1.0→0.5)
- **Chains**: 10 independent

## Kill Criteria
- 0 survivors after 200 heads → SATURATED
- Leakage detected (δ_shuffled diff > 0.02)
- Duplicate rate > 10%

## Outputs
1. `EXPLORE_MATRIX.csv`: All metrics + pre/post head quality
2. `SALIENCY.json`: Position importance maps
3. `ORBIT_SUMMARY.csv`: Isolation analysis for survivors
4. `promotion_queue.json`: Confirm-ready candidates
5. `DASHBOARD.md`: Summary statistics
6. `REPRO_STEPS.md`: Reproduction instructions
7. `MANIFEST.sha256`: File integrity

## Seed Recipe
```
EXPLORE_V4.1|{master_seed}|chain:{chain_id}|stage:{stage_id}|ct:{ct_sha256}
```

## Success Metrics
- ≥1 survivor passing all gates → proceed to Confirm
- Pre-anchor near-gate pass rate > 50%
- Post-anchor quality retention > 80%
- Orbit isolation rate > 10% of delta-passers

---
*End of Pre-registration*