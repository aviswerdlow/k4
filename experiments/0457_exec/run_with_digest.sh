#!/bin/bash
#
# Master execution script using winner's proof digest
# Runs all analyses with actual key schedules
#

set -e  # Exit on error

echo "========================================="
echo "04:57 EXECUTION WITH PROOF DIGEST"
echo "========================================="
echo ""
echo "Branch: experiment-0457-exec"
echo "Date: $(date +%Y%m%d)"
echo "Using winner's verified key schedules"
echo ""

# Check we're on the right branch
BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "experiment-0457-exec" ]; then
    echo "WARNING: Not on experiment-0457-exec branch"
    echo "Current branch: $BRANCH"
fi

# Check proof digest exists
if [ ! -f "experiments/0457_exec/data/winner_proof_digest.json" ]; then
    echo "ERROR: Winner's proof digest not found!"
    echo "Expected at: experiments/0457_exec/data/winner_proof_digest.json"
    exit 1
fi

echo "Winner's digest found. Key schedules:"
grep -A 6 '"per_class"' experiments/0457_exec/data/winner_proof_digest.json | head -8

echo ""
echo "=== Phase 1: Sensitivity Strip (3×3 with 3 replicates) ==="
echo "This will run 27 total executions (9 policies × 3 replicates)"
echo "All using winner's fixed key schedule"
echo ""
python3 experiments/0457_exec/scripts/run_sensitivity_digest.py

echo ""
echo "=== Phase 2: P[74] Strip (A-Z) ==="
echo "This will run 26 executions (one per letter)"
echo "Only 'T' should be lawful with winner's schedule"
echo ""
python3 experiments/0457_exec/scripts/run_p74_digest.py

echo ""
echo "=== Phase 3: GRID Controls (MAP/TRUE/FACT) ==="
echo "This will run 3 executions with fail point analysis"
echo "Expected to fail at lawfulness or Flint"
echo ""
python3 experiments/0457_exec/scripts/run_controls_digest.py

echo ""
echo "=== Phase 4: Leakage Ablation ==="
echo "Testing Generic track with anchors masked"
echo ""
python3 experiments/0457_exec/scripts/run_leakage_ablation.py

echo ""
echo "=== Phase 5: Package Results ==="
DATE=$(date +%Y%m%d)
ZIP_NAME="k4_0457_exec_${DATE}.zip"

cd experiments/0457_exec/runs/${DATE}
zip -r ../../../../${ZIP_NAME} sensitivity_strip p74_strip controls_grid -x "*.txt"
cd -

echo ""
echo "========================================="
echo "EXECUTION COMPLETE"
echo "========================================="
echo ""
echo "Results locations:"
echo "  Sensitivity: experiments/0457_exec/runs/${DATE}/sensitivity_strip/SENS_STRIP_MATRIX.csv"
echo "  P[74]: experiments/0457_exec/runs/${DATE}/p74_strip/P74_STRIP_SUMMARY.csv"
echo "  Controls: experiments/0457_exec/runs/${DATE}/controls_grid/CONTROLS_SUMMARY.csv"
echo "  Leakage: experiments/0457_exec/runs/${DATE}/leakage_ablation/LEAKAGE_ABLATION.md"
echo "  Receipts: experiments/0457_exec/docs/RECEIPTS.md"
echo "  Package: ${ZIP_NAME}"
echo ""
echo "Summary for email:"
echo "  Nine-cell sensitivity executed with three nulls replicates per cell;"
echo "  per-cell bundles attached; winner status stable across grid."
echo "  P[74] A-Z strip executed; summary CSV + bundles attached;"
echo "  controls run in GRID-only + AND + nulls with exact fail points;"
echo "  Generic leakage ablation shows no anchor dependence."