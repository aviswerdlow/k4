# Reproduction Steps for HEAD_147_B

## Selection
1. Run batch automation on K=200 promotion queue
2. Rank by 8-part lexicographic key
3. Selected: HEAD_147_B (2nd attempt after HEAD_66_B failed lawfulness)

## Plaintext Construction
1. Extract text from exploration bundle
2. Place anchors at required positions
3. Normalize to 97 uppercase characters

## Lawfulness Proof
1. Try GRID routes in deterministic order
2. Found: GRID_W14_ROWS with c6a classing
3. Option-A at anchors, NA-only T2

## Validation
1. Near-gate: PASSED (cov=0.895, fw=10)
2. Phrase gate (AND): PASSED (flint_v2, generic)
3. Null hypothesis (10k): PUBLISHABLE (adj_p_cov=0.0006, adj_p_fw=0.0005)
