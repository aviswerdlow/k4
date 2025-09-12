#!/bin/bash

echo "=== Fresh-Slate Validation ==="
echo ""

# Check no external imports
echo "Checking for stdlib-only imports..."
IMPORTS=$(grep -h "^import\|^from" tools/*.py | grep -v "^from fresh_slate_derive" | sort -u)
STDLIB_ONLY=true

while IFS= read -r line; do
    # Check if it's a standard library import
    if [[ ! "$line" =~ ^(import|from)\ (json|os|sys|hashlib|argparse|pathlib|matplotlib) ]]; then
        echo "  ❌ Non-stdlib import found: $line"
        STDLIB_ONLY=false
    fi
done <<< "$IMPORTS"

if [ "$STDLIB_ONLY" = true ]; then
    echo "  ✅ All imports are stdlib-only (excluding matplotlib for visualization)"
fi

echo ""

# Check run outputs exist
echo "Checking baseline runs..."
for run in baseline_four_anchors baseline_three_no_berlin baseline_three_no_clock baseline_two_east_ne; do
    if [ -f "runs/$run/summary.json" ]; then
        UNDETERMINED=$(python3 -c "import json; print(json.load(open('runs/$run/summary.json'))['undetermined_count'])")
        echo "  ✅ $run: $UNDETERMINED undetermined positions"
    else
        echo "  ❌ $run: missing"
    fi
done

echo ""

# Test explain functionality
echo "Testing explain functionality..."
OUTPUT=$(cd . && python3 tools/explain_one.py \
    --ct inputs/ciphertext_97.txt \
    --crib inputs/cribs/four_anchors.json \
    --classing classing/baseline.json \
    --index 21 2>/dev/null | grep "Plaintext letter:")

if [[ "$OUTPUT" == *"E"* ]]; then
    echo "  ✅ explain_one.py correctly derives index 21 as 'E'"
else
    echo "  ❌ explain_one.py failed to derive index 21"
fi

echo ""
echo "=== Validation Complete ==="