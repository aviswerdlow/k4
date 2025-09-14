# K4 CLI Plus - Zone-Based Cryptanalysis Framework

A comprehensive framework for solving the K4 cipher using zone-based analysis with masks, routes, and classical ciphers.

## Quick Start

```bash
# Test the framework
python3 test_framework.py

# Run experiments
make phase3-a  # MID zone exploitation
make phase3-b  # Turn flip wash routes
make phase3-c  # Mask discovery

# Verify a solution
make verify-rt MANIFEST=path/to/manifest.json

# Generate human-readable notecard
make notecard MANIFEST=path/to/manifest.json
```

## Architecture

### Core Components

1. **Zone System**: HEAD (0-20), MID (34-62), TAIL (74-96)
2. **Control Points**: BERLINCLOCK at positions 64-73
3. **Mask Library**: Period interleaves, cycles, diagonal weaves, etc.
4. **Route Engine**: Columnar, serpentine, spiral, tumble transformations
5. **Cipher Families**: Vigenere and Beaufort with key scheduling

### Directory Structure

```
02_DATA/           - Ciphertext and control data
03_SOLVERS/        - Main solver implementation
  zone_mask_v1/    - Zone-based solver
    scripts/       - Core algorithms
    recipes/       - Manifest schema
04_EXPERIMENTS/    - Experiment configurations and results
  phase3_zone/     - Main experimental batches
07_TOOLS/          - Validation and null controls
```

## Solution Requirements

1. **Deterministic**: Must round-trip exactly to original ciphertext
2. **Paper-doable**: All operations possible by hand
3. **Single recipe**: One manifest for all 97 characters
4. **BERLINCLOCK**: Must appear at control positions
5. **Null controls**: Must beat random baseline

## Manifest Format

```json
{
  "zones": {
    "head": {"start": 0, "end": 20},
    "mid": {"start": 34, "end": 62},
    "tail": {"start": 74, "end": 96}
  },
  "control": {
    "mode": "content",
    "indices": [64, 65, 66, 67, 68, 69, 70, 71, 72, 73]
  },
  "mask": {
    "type": "period2",
    "params": {"period": 2}
  },
  "route": {
    "type": "columnar",
    "params": {"rows": 7, "cols": 14}
  },
  "cipher": {
    "family": "vigenere",
    "keys": {
      "head": "ORDINATE",
      "mid": "ABSCISSA",
      "tail": "AZIMUTH"
    }
  }
}
```

## Available Masks

- **period2/period3**: Periodic interleaving
- **cycle3/cycle5**: Fixed cycle rotations
- **diag_weave**: Diagonal reading patterns
- **alt_sheet**: Alternating selection
- **fib_skip**: Fibonacci position selection
- **lowfreq_smoother**: Low-frequency letter handling

## Available Routes

- **columnar**: Column transposition with optional passes
- **serpentine**: S-pattern reading
- **spiral**: Inward/outward spiral
- **tumble**: 90-degree rotations

## Key Sets

- **Surveying**: LATITUDE, LONGITUDE, AZIMUTH, BEARING
- **Geometry**: ABSCISSA, ORDINATE, TANGENT, SECANT
- **Artistic**: SHADOW, LIGHT, LODESTONE, GIRASOL

## Running Experiments

### Batch A - MID Zone Focus
```bash
make phase3-a
```

### Batch B - Route Variations
```bash
make phase3-b
```

### Batch C - Mask Discovery
```bash
make phase3-c
```

## Validation

Every candidate solution is validated against:
1. Exact round-trip to ciphertext
2. BERLINCLOCK at control positions
3. Null hypothesis testing
4. Antipodes layout compatibility
5. Single-page notecard generation

## Next Steps

1. Run initial experiments with `make phase3-a`
2. Review results in `04_EXPERIMENTS/phase3_zone/runs/`
3. Refine promising candidates
4. Test with Antipodes ordering
5. Generate notecard for final solution

## Contributing

Add new masks in `mask_library.py`, routes in `route_engine.py`, or experiment configs in `04_EXPERIMENTS/phase3_zone/configs/`.