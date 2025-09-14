#!/bin/bash
# Phase 3 Execution Script - Run priority manifests

echo "=========================================="
echo "K4 PHASE 3 EXECUTION PLAN"
echo "=========================================="
echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create output directories
mkdir -p 04_EXPERIMENTS/phase3_zone/runs
mkdir -p 04_EXPERIMENTS/mask_discovery/reports
mkdir -p 04_EXPERIMENTS/antipodes_check
mkdir -p 04_EXPERIMENTS/twist_detector

# Preflight checks
echo "1. PREFLIGHT SANITY CHECKS"
echo "------------------------"

# Test framework is working (skip toy test for now)
echo -n "Testing framework imports... "
if python3 -c "from zone_mask_v1.scripts.mask_library import apply_mask; from zone_mask_v1.scripts.cipher_families import VigenereCipher" 2>/dev/null; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    # Try with path adjustment
    cd 03_SOLVERS
    if python3 -c "from zone_mask_v1.scripts.mask_library import apply_mask; from zone_mask_v1.scripts.cipher_families import VigenereCipher" 2>/dev/null; then
        echo -e "${GREEN}✓ PASS${NC}"
        cd ..
    else
        echo -e "${RED}✗ FAIL${NC}"
        echo "Framework import issues. Check Python path."
        cd ..
    fi
fi

# Test Antipodes invertibility
echo -n "Testing Antipodes reorder... "
if python3 04_EXPERIMENTS/antipodes_check/reorder_to_antipodes.py \
    --ct 02_DATA/ciphertext_97.txt \
    --layout 02_DATA/antipodes_layout.json > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${YELLOW}⚠ WARNING${NC}"
fi

echo
echo "2. RUNNING PRIORITY MANIFESTS"
echo "----------------------------"

# Function to run a single manifest
run_manifest() {
    local name=$1
    local manifest=$2
    
    echo -n "Running $name... "
    
    timestamp=$(date +%Y%m%d_%H%M%S)
    output_dir="04_EXPERIMENTS/phase3_zone/runs/ts_${timestamp}_${name}"
    mkdir -p "$output_dir"
    
    # Run the manifest
    if python3 03_SOLVERS/zone_mask_v1/scripts/zone_runner.py \
        --manifest "$manifest" \
        --output "$output_dir" > "$output_dir/stdout.log" 2>&1; then
        
        # Check if BERLINCLOCK was found
        if grep -q "BERLINCLOCK" "$output_dir/stdout.log"; then
            echo -e "${GREEN}✓ SUCCESS - BERLINCLOCK FOUND!${NC}"
            
            # Run null tests
            echo "  Running null controls..."
            python3 07_TOOLS/nulls/key_scramble.py \
                --manifest "$manifest" \
                --iterations 20 \
                --output "$output_dir/null_key.json" > /dev/null 2>&1
            
            python3 07_TOOLS/nulls/segment_shuffle.py \
                --manifest "$manifest" \
                --iterations 20 \
                --output "$output_dir/null_seg.json" > /dev/null 2>&1
            
            # Check K5 gate
            python3 04_EXPERIMENTS/k5_gate/post_plaintext_gate.py \
                --manifest "$manifest" \
                --output "$output_dir/k5_gate.json" > /dev/null 2>&1
            
            echo "  Results saved to: $output_dir"
            return 0
        else
            echo -e "${YELLOW}⚠ No BERLINCLOCK${NC}"
        fi
    else
        echo -e "${RED}✗ FAILED${NC}"
    fi
    
    return 1
}

# Run A series (MID zone focus)
echo
echo "A Series - MID Zone Exploitation:"
run_manifest "A1" "04_EXPERIMENTS/phase3_zone/configs/batch_a_A1.json"
run_manifest "A2" "04_EXPERIMENTS/phase3_zone/configs/batch_a_A2.json"
run_manifest "A3" "04_EXPERIMENTS/phase3_zone/configs/batch_a_A3.json"

# Run B series (Route variations)
echo
echo "B Series - Turn Flip Wash Routes:"
run_manifest "B1" "04_EXPERIMENTS/phase3_zone/configs/batch_b_B1.json"
run_manifest "B2" "04_EXPERIMENTS/phase3_zone/configs/batch_b_B2.json"

# Run C series (Diagonal weave)
echo
echo "C Series - Diagonal Weave:"
run_manifest "C1" "04_EXPERIMENTS/phase3_zone/configs/batch_c_C1.json"

# Run mask discovery
echo
echo "3. MASK DISCOVERY"
echo "----------------"
echo -n "Running mask discovery analysis... "
if python3 04_EXPERIMENTS/mask_discovery/discover_masks.py \
    --ct 02_DATA/ciphertext_97.txt \
    --out 04_EXPERIMENTS/mask_discovery/reports \
    --zones > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Complete${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
fi

# Find best candidate
echo
echo "4. SELECTING BEST CANDIDATE"
echo "-------------------------"

# Look for any successful runs
best_candidate=""
for run_dir in 04_EXPERIMENTS/phase3_zone/runs/ts_*; do
    if [ -f "$run_dir/manifest.json" ]; then
        # Check if this run has BERLINCLOCK
        if grep -q "berlinclock_verified.*true" "$run_dir/receipts.json" 2>/dev/null; then
            best_candidate="$run_dir/manifest.json"
            echo -e "${GREEN}✓ Found candidate: $run_dir${NC}"
            break
        fi
    fi
done

if [ -z "$best_candidate" ]; then
    echo -e "${YELLOW}No successful candidate found in initial runs.${NC}"
    echo "Proceeding to escalation..."
    
    # Run twist detector on best scoring manifest
    echo
    echo "5. TWIST DETECTION"
    echo "----------------"
    
    # Find manifest with best score even if no BERLINCLOCK
    for manifest in 04_EXPERIMENTS/phase3_zone/configs/batch_a_A1.json; do
        echo "Testing twists on $manifest..."
        python3 04_EXPERIMENTS/twist_detector/sanborn_twist.py \
            --baseline "$manifest" \
            --output 04_EXPERIMENTS/twist_detector/results.json
        
        if [ -f "04_EXPERIMENTS/twist_detector/best_twist.json" ]; then
            echo -e "${GREEN}✓ Found improving twist${NC}"
            best_candidate="04_EXPERIMENTS/twist_detector/best_twist.json"
            break
        fi
    done
else
    # Copy best to standard location
    cp "$best_candidate" "04_EXPERIMENTS/phase3_zone/runs/best.json"
    
    echo
    echo "5. ANTIPODES CROSS-CHECK"
    echo "----------------------"
    echo -n "Testing with Antipodes reordering... "
    
    if python3 04_EXPERIMENTS/antipodes_check/reorder_to_antipodes.py \
        --ct 02_DATA/ciphertext_97.txt \
        --layout 02_DATA/antipodes_layout.json \
        --manifest "$best_candidate" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
    else
        echo -e "${RED}✗ FAIL${NC}"
    fi
fi

# Final summary
echo
echo "=========================================="
echo "EXECUTION COMPLETE"
echo "=========================================="

if [ -n "$best_candidate" ]; then
    echo -e "${GREEN}Best candidate saved to: 04_EXPERIMENTS/phase3_zone/runs/best.json${NC}"
    echo
    echo "Next steps:"
    echo "1. Review the solution: make notecard"
    echo "2. Run full null test: make null-key-scramble"
    echo "3. Package if valid: Create under 01_PUBLISHED/candidates/"
else
    echo -e "${YELLOW}No valid candidate found. Review logs and escalate.${NC}"
fi

echo
echo "All run logs saved in: 04_EXPERIMENTS/phase3_zone/runs/"