#!/bin/bash
# Pre-merge check script to ensure repository integrity
# Run this before merging any PR

set -e

echo "Running pre-merge integrity checks..."

# Check 1: No simulated content outside quarantine
echo "1. Checking for simulated content outside quarantine..."
SIMULATED_FILES=$(find experiments -type f -name "*.py" -o -name "*.json" -o -name "*.md" | \
                  grep -v "_simulated" | \
                  xargs grep -l -i "simulated\|mock\|placeholder" 2>/dev/null | \
                  grep -v "audit/scripts" || true)

if [ ! -z "$SIMULATED_FILES" ]; then
    echo "⚠️  Warning: Files containing simulation keywords outside quarantine:"
    echo "$SIMULATED_FILES"
    echo "Please review these files for actual simulated content."
fi

# Check 2: No links to _simulated in README
echo "2. Checking for links to quarantined content..."
if grep -q "_simulated" README.md 2>/dev/null; then
    echo "❌ Error: README contains links to _simulated content"
    exit 1
else
    echo "✅ README clean"
fi

# Check 3: Conceptual content is marked
echo "3. Checking conceptual folders are properly marked..."
CONCEPTUAL_DIRS=$(find experiments -type d -name "*conceptual*" 2>/dev/null || true)
for dir in $CONCEPTUAL_DIRS; do
    if [ ! -f "$dir/README.md" ]; then
        echo "⚠️  Warning: Conceptual directory $dir missing README.md"
    elif ! grep -qi "conceptual\|no execution\|not executed" "$dir/README.md"; then
        echo "⚠️  Warning: Conceptual directory $dir/README.md doesn't clearly indicate non-execution"
    fi
done

# Check 4: Bundle validator on new bundles
echo "4. Checking for new bundle directories..."
NEW_BUNDLES=$(find experiments -type f -name "coverage_report.json" -mtime -1 2>/dev/null | xargs -I {} dirname {} || true)
if [ ! -z "$NEW_BUNDLES" ]; then
    echo "Found new bundles to validate:"
    echo "$NEW_BUNDLES"
    echo "Consider running: python3 experiments/audit/scripts/validate_bundle.py"
fi

# Check 5: Audit reports exist
echo "5. Checking for audit trail..."
if [ -f "experiments/audit/runs/*/AUDIT_REPORT.md" ]; then
    echo "✅ Audit reports found"
else
    echo "ℹ️  No audit reports found - consider running audit if making significant changes"
fi

echo ""
echo "Pre-merge checks complete!"
echo "Remember to:"
echo "  1. Review any warnings above"
echo "  2. Update audit if adding new experiments"
echo "  3. Clearly mark any conceptual content"
echo "  4. Never link to _simulated directories"

exit 0