#!/bin/bash
# Run expanded manifests A4-A7, B3, C2

echo "======================================"
echo "EXPANDED BATCH EXECUTION"
echo "======================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to run and analyze a manifest
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
        
        # Extract MID zone plaintext for analysis
        if [ -f "$output_dir/plaintext_${timestamp}.txt" ]; then
            mid_text=$(python3 -c "
text = open('$output_dir/plaintext_${timestamp}.txt').read()
print(text[34:63] if len(text) > 62 else text)
")
            echo -e "${GREEN}✓${NC} MID: ${mid_text:0:20}..."
        else
            echo -e "${YELLOW}✓${NC} (no plaintext)"
        fi
        
        # Quick English check on MID zone
        english_score=$(python3 -c "
text = '$mid_text'.upper()
common = ['THE', 'AND', 'ING', 'ION', 'ENT', 'FOR', 'HER', 'THA', 'NTH', 'INT', 'ERE', 'TIO', 'TER', 'EST', 'ERS']
score = sum(1 for w in common if w in text)
print(score)
" 2>/dev/null || echo "0")
        
        if [ "$english_score" -gt "2" ]; then
            echo -e "  ${GREEN}⚡ English patterns detected! Score: $english_score${NC}"
            
            # Run quick null test
            python3 07_TOOLS/nulls/key_scramble.py \
                --manifest "$manifest" \
                --iterations 20 \
                --output "$output_dir/null_key.json" > /dev/null 2>&1 &
        fi
        
        # Check for BERLINCLOCK
        if grep -q "BERLINCLOCK" "$output_dir/stdout.log" 2>/dev/null; then
            echo -e "  ${GREEN}🎯 BERLINCLOCK FOUND!${NC}"
        fi
        
        # Save manifest to standard location
        cp "$manifest" "$output_dir/manifest.json"
        
        return 0
    else
        echo -e "${RED}✗ Failed${NC}"
        return 1
    fi
}

# Run expanded manifests
echo
echo "Running A4-A7 (period-5/7 with expanded keys):"
run_manifest "A4" "04_EXPERIMENTS/phase3_zone/configs/batch_a_A4.json"
run_manifest "A5" "04_EXPERIMENTS/phase3_zone/configs/batch_a_A5.json"
run_manifest "A6" "04_EXPERIMENTS/phase3_zone/configs/batch_a_A6.json"
run_manifest "A7" "04_EXPERIMENTS/phase3_zone/configs/batch_a_A7.json"

echo
echo "Running B3 (tumble with SHADOW/LIGHT):"
run_manifest "B3" "04_EXPERIMENTS/phase3_zone/configs/batch_b_B3.json"

echo
echo "Running C2 (diagonal weave control mode):"
run_manifest "C2" "04_EXPERIMENTS/phase3_zone/configs/batch_c_C2.json"

# Wait for background null tests
wait

echo
echo "======================================"
echo "LEADERBOARD UPDATE"
echo "======================================"
python3 scripts/leaderboard.py --top 5

echo
echo "Top MID zone results saved in: 04_EXPERIMENTS/phase3_zone/runs/"