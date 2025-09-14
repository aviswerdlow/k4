# Phase 3 Zone Experiments

## Scope
Zone-based cryptanalysis using masks, routes, and classical ciphers to find a paper-doable solution for K4.

## Acceptance Criteria
1. **Round-trip validation**: Must re-encrypt to exact ciphertext
2. **BERLINCLOCK verification**: Positions 64-73 must decode to "BERLIN CLOCK"
3. **Null control**: Must beat random null hypotheses
4. **Single manifest**: One recipe for all 97 characters
5. **Paper-doable**: All operations must be doable by hand

## Experiment Batches

### Batch A - MID Zone Exploitation
Focus on the MID zone (34-62) with various masks and ciphers.

### Batch B - Turn Flip Wash Routes
Test different route patterns with emphasis on "turn, flip, wash" metaphor.

### Batch C - Mask Discovery
Automated mask discovery based on patterns in the ciphertext.

### Batch D - Twist Detector
Small modifications to baseline that might unlock the solution.

### Batch E - Antipodes Cross-check
Validate solutions work with Antipodes reordering.

## Running Experiments
```bash
# Run batch A
make phase3-a

# Run batch B
make phase3-b

# Verify a specific manifest
make verify-rt

# Generate notecard
make notecard
```

## Results Location
All results are stored in `04_EXPERIMENTS/phase3_zone/runs/` with timestamps.