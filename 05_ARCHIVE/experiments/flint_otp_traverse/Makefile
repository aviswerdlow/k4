# Makefile for Flint Traverse Table OTP Testing
# Comprehensive, reproducible pipeline for testing traverse tables as K4 OTP source

.PHONY: all clean extract-traverse build-keys test-keys anchor-target combinations traverse-otp-all package-results

# Configuration
PYTHON = python3
BASE_DIR = /Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus
TOOLS_DIR = $(BASE_DIR)/tools
EXPERIMENTS_DIR = $(BASE_DIR)/experiments/flint_otp_traverse
TABLES_DIR = $(BASE_DIR)/tables/parsed
KEYSTREAMS_DIR = $(EXPERIMENTS_DIR)/keystreams
RESULTS_DIR = $(EXPERIMENTS_DIR)/results

# Default target
all: traverse-otp-all

# Clean all generated files
clean:
	rm -rf $(TABLES_DIR)
	rm -rf $(KEYSTREAMS_DIR)
	rm -rf $(EXPERIMENTS_DIR)/combinations
	rm -rf $(RESULTS_DIR)
	@echo "Cleaned all generated files"

# Step 1: Extract traverse tables from PDF
extract-traverse:
	@echo "=========================================="
	@echo "STEP 1: EXTRACTING TRAVERSE TABLES"
	@echo "=========================================="
	cd $(BASE_DIR) && $(PYTHON) $(TOOLS_DIR)/flint_extract_tables.py
	@echo "Tables extracted to: $(TABLES_DIR)"
	@echo ""

# Step 2: Build keystreams from tables
build-keys: extract-traverse
	@echo "=========================================="
	@echo "STEP 2: BUILDING KEYSTREAMS (F1-F6)"
	@echo "=========================================="
	cd $(BASE_DIR) && $(PYTHON) $(EXPERIMENTS_DIR)/build_keystreams.py
	@echo "Keystreams generated in: $(KEYSTREAMS_DIR)"
	@echo ""

# Step 3: Test keystreams against K4
test-keys: build-keys
	@echo "=========================================="
	@echo "STEP 3: TESTING KEYSTREAMS WITH ANCHORS"
	@echo "=========================================="
	cd $(BASE_DIR) && $(PYTHON) $(EXPERIMENTS_DIR)/test_keystreams.py
	@echo "Results saved to: $(RESULTS_DIR)"
	@echo ""

# Step 4: Anchor-first targeting
anchor-target: build-keys
	@echo "=========================================="
	@echo "STEP 4: ANCHOR-FIRST TARGETING"
	@echo "=========================================="
	cd $(BASE_DIR) && $(PYTHON) $(EXPERIMENTS_DIR)/anchor_targeting.py
	@echo "Targeting results saved to: $(RESULTS_DIR)"
	@echo ""

# Step 5: Generate and test combinations
combinations: build-keys
	@echo "=========================================="
	@echo "STEP 5: GENERATING COMBINATIONS"
	@echo "=========================================="
	cd $(BASE_DIR) && $(PYTHON) $(EXPERIMENTS_DIR)/combinators.py
	@echo ""
	@echo "Testing combinations..."
	cd $(BASE_DIR) && $(PYTHON) $(EXPERIMENTS_DIR)/combinators.py test
	@echo "Combination results saved to: $(RESULTS_DIR)"
	@echo ""

# Full pipeline
traverse-otp-all: extract-traverse build-keys test-keys anchor-target combinations package-results
	@echo "=========================================="
	@echo "COMPLETE TRAVERSE OTP PIPELINE FINISHED"
	@echo "=========================================="
	@cat $(RESULTS_DIR)/TOPLINE.md
	@echo ""
	@echo "Results packaged in: $(RESULTS_DIR)/FORUM_PACKET.zip"

# Package results for forum
package-results:
	@echo "=========================================="
	@echo "PACKAGING RESULTS"
	@echo "=========================================="
	@mkdir -p $(RESULTS_DIR)/forum_packet
	@cp $(RESULTS_DIR)/TOPLINE.md $(RESULTS_DIR)/forum_packet/
	@cp $(RESULTS_DIR)/TARGETING_REPORT.md $(RESULTS_DIR)/forum_packet/ 2>/dev/null || true
	@cp $(RESULTS_DIR)/COMBO_REPORT.md $(RESULTS_DIR)/forum_packet/ 2>/dev/null || true
	@cp $(RESULTS_DIR)/RUN_MATRIX.csv $(RESULTS_DIR)/forum_packet/ 2>/dev/null || true
	@cp $(RESULTS_DIR)/*passing*.json $(RESULTS_DIR)/forum_packet/ 2>/dev/null || true
	@echo "# HOW TO REPRODUCE" > $(RESULTS_DIR)/forum_packet/REPRODUCE.md
	@echo "" >> $(RESULTS_DIR)/forum_packet/REPRODUCE.md
	@echo "1. Clone repository" >> $(RESULTS_DIR)/forum_packet/REPRODUCE.md
	@echo "2. Ensure PDF at: 06_DOCUMENTATION/A_System_of_Geometry_and_Trigonometry.pdf" >> $(RESULTS_DIR)/forum_packet/REPRODUCE.md
	@echo "3. Run: make traverse-otp-all" >> $(RESULTS_DIR)/forum_packet/REPRODUCE.md
	@echo "4. Check results in: experiments/flint_otp_traverse/results/" >> $(RESULTS_DIR)/forum_packet/REPRODUCE.md
	@echo "" >> $(RESULTS_DIR)/forum_packet/REPRODUCE.md
	@echo "MASTER_SEED = 1337 (for reproducibility)" >> $(RESULTS_DIR)/forum_packet/REPRODUCE.md
	cd $(RESULTS_DIR) && zip -r FORUM_PACKET.zip forum_packet/
	@echo "Packet created: $(RESULTS_DIR)/FORUM_PACKET.zip"

# Validation tests
validate:
	@echo "Running validation tests..."
	@echo "1. Checking anchor positions..."
	@$(PYTHON) -c "import json; a=json.load(open('$(BASE_DIR)/02_DATA/anchors/four_anchors.json')); print('Anchors OK:', all(a[k]['end']-a[k]['start']+1==len(a[k]['plaintext']) for k in a))"
	@echo "2. Checking ciphertext length..."
	@wc -c < $(BASE_DIR)/02_DATA/ciphertext_97.txt | xargs -I {} test {} -eq 98 && echo "Ciphertext length OK (97 + newline)"
	@echo "3. Checking PDF exists..."
	@test -f "$(BASE_DIR)/06_DOCUMENTATION/A_System_of_Geometry_and_Trigonometry.pdf" && echo "PDF found" || echo "WARNING: PDF not found"

# Quick status check
status:
	@echo "Current status:"
	@echo -n "Tables extracted: "; ls $(TABLES_DIR)/*.json 2>/dev/null | wc -l
	@echo -n "Keystreams generated: "; find $(KEYSTREAMS_DIR) -name "*.json" 2>/dev/null | wc -l
	@echo -n "Results available: "; ls $(RESULTS_DIR)/*.md 2>/dev/null | wc -l
	@if [ -f "$(RESULTS_DIR)/TOPLINE.md" ]; then \
		echo ""; \
		echo "Latest results:"; \
		grep -A2 "Summary" $(RESULTS_DIR)/TOPLINE.md; \
	fi

# Help
help:
	@echo "Flint Traverse Table OTP Testing Pipeline"
	@echo ""
	@echo "Targets:"
	@echo "  make extract-traverse  - Extract tables from PDF"
	@echo "  make build-keys       - Generate keystreams (F1-F6 families)"
	@echo "  make test-keys        - Test keystreams with anchor validation"
	@echo "  make anchor-target    - Run anchor-first targeting"
	@echo "  make combinations     - Generate and test combinations"
	@echo "  make traverse-otp-all - Run complete pipeline"
	@echo "  make package-results  - Create forum packet"
	@echo "  make validate        - Run validation checks"
	@echo "  make status          - Show current progress"
	@echo "  make clean           - Remove all generated files"
	@echo ""
	@echo "Quick start: make traverse-otp-all"