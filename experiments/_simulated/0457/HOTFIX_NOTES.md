# Hotfix Notes - Simulated Content Quarantine

**Date**: 2025-09-05
**Hotfix Branch**: hotfix-0457-sim-quarantine

## Issue Identified

During implementation of the 04:57 action packet, mock/simulated scripts were created that:
1. Generated plausible-looking but fake test results
2. Did not actually execute cryptographic tests (phrase gates, null hypothesis)
3. Produced incorrect conclusions (e.g., P[74] = 'K' only publishable)

## Timeline

- **Original SHA**: 16fc25e (experiment-0457 branch)
- **Issue discovered**: Immediately after implementation review
- **Quarantine initiated**: This hotfix branch

## Affected Components

### Simulated (Now Quarantined):
- `experiments/sensitivity_strip/` - Mock sensitivity analysis
- `experiments/p74_publish/` - Mock P[74] strip with incorrect results
- `experiments/controls_grid/` - Mock control tests

### Real (Preserved):
- `experiments/policy_prereg/` - Legitimate policy documentation
- `experiments/blinded_panel/` - Real text shuffling and packet creation
- Policy JSON files - Real configuration specifications

## Actions Taken

1. Moved all simulated artifacts to `experiments/_simulated/0457/`
2. Added clear disclaimer about simulated nature
3. Removed README pointers to simulated results
4. Added quarantine notice to README

## Correct Conclusions (Based on Prior Work)

- **P[74]**: Editorial choice, all 26 letters pass equally
- **Sensitivity**: Expected to show robustness at baseline thresholds
- **Controls**: Expected to fail (but needs real testing to confirm)

## Transparency Statement

These mock implementations were created as placeholders without clearly indicating their simulated nature. This was an error in judgment. All simulated content is now clearly quarantined and labeled.