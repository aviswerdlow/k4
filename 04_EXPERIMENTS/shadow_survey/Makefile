# Makefile for Fork H-Shadow
# Shadow-Surveying-Modified Cipher Integration

.PHONY: all clean test shadow-all shadow-quick validate status help

# Configuration
PYTHON = python3
BASE_DIR = /Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus
EXPERIMENTS_DIR = $(BASE_DIR)/04_EXPERIMENTS/shadow_survey
RESULTS_DIR = $(EXPERIMENTS_DIR)/results
MASKS_DIR = $(EXPERIMENTS_DIR)/masks
LIB_DIR = $(EXPERIMENTS_DIR)/lib

# Default target
all: shadow-all

# Clean generated files
clean:
	rm -rf $(RESULTS_DIR)/*.json
	rm -rf $(MASKS_DIR)/*.json
	rm -f $(EXPERIMENTS_DIR)/RUN_SUMMARY.csv
	rm -f $(EXPERIMENTS_DIR)/FINAL_REPORT.md
	@echo "Cleaned all generated files"

# Test solar calculations
test-solar:
	@echo "Testing solar position calculations..."
	cd $(BASE_DIR) && $(PYTHON) $(LIB_DIR)/sun_shadow.py
	@echo ""

# Test zone mapping
test-zones:
	@echo "Testing zone mapping strategies..."
	cd $(BASE_DIR) && $(PYTHON) $(LIB_DIR)/zones.py
	@echo ""

# Test shadow cipher
test-cipher:
	@echo "Testing shadow-modified cipher..."
	cd $(BASE_DIR) && $(PYTHON) $(LIB_DIR)/shadow_polyalpha.py
	@echo ""

# Run complete shadow test suite
shadow-all:
	@echo "=========================================="
	@echo "FORK H-SHADOW - COMPLETE TEST SUITE"
	@echo "=========================================="
	cd $(BASE_DIR) && $(PYTHON) $(EXPERIMENTS_DIR)/run_shadow_tests.py
	@echo ""
	@echo "Results saved to: $(RESULTS_DIR)"

# Quick test with dedication datetime only
shadow-quick:
	@echo "=========================================="
	@echo "QUICK SHADOW TEST (Dedication only)"
	@echo "=========================================="
	cd $(BASE_DIR) && $(PYTHON) -c "import sys; sys.path.insert(0, '$(LIB_DIR)'); \
		from run_shadow_tests import ShadowSurveyTester; \
		tester = ShadowSurveyTester(); \
		tester.run_phase3_rendering_test(); \
		print(f'Quick test complete: {len(tester.passing_results)} matches')"

# Validate prerequisites
validate:
	@echo "Validating prerequisites..."
	@test -f "$(BASE_DIR)/02_DATA/ciphertext_97.txt" && echo "✓ Ciphertext found" || echo "✗ Ciphertext missing"
	@test -f "$(BASE_DIR)/02_DATA/anchors/four_anchors.json" && echo "✓ Anchors found" || echo "✗ Anchors missing"
	@$(PYTHON) -c "import math, json, datetime; print('✓ Required modules available')"
	@echo "✓ Master seed: 1337"

# Status check
status:
	@echo "Fork H-Shadow Status:"
	@echo -n "Result files: "; ls $(RESULTS_DIR)/*.json 2>/dev/null | wc -l
	@echo -n "Mask files: "; ls $(MASKS_DIR)/*.json 2>/dev/null | wc -l
	@if [ -f "$(EXPERIMENTS_DIR)/RUN_SUMMARY.csv" ]; then \
		echo -n "Tests in CSV: "; tail -n +2 $(EXPERIMENTS_DIR)/RUN_SUMMARY.csv | wc -l; \
		echo -n "Anchors preserved: "; cut -d',' -f5 $(EXPERIMENTS_DIR)/RUN_SUMMARY.csv | grep -c "True"; \
	fi
	@if [ -f "$(EXPERIMENTS_DIR)/FINAL_REPORT.md" ]; then \
		echo ""; \
		grep "^- " $(EXPERIMENTS_DIR)/FINAL_REPORT.md | head -5; \
	fi

# Help
help:
	@echo "Fork H-Shadow - Shadow-Surveying-Modified Cipher Integration"
	@echo ""
	@echo "Targets:"
	@echo "  make shadow-all    - Run complete test suite"
	@echo "  make shadow-quick  - Quick test with dedication datetime"
	@echo "  make test-solar    - Test solar calculations"
	@echo "  make test-zones    - Test zone mapping"
	@echo "  make test-cipher   - Test shadow cipher"
	@echo "  make validate      - Validate prerequisites"
	@echo "  make status        - Show current status"
	@echo "  make clean         - Remove generated files"
	@echo ""
	@echo "Critical datetimes tested:"
	@echo "  - 1989-11-09 18:53 (Berlin Wall)"
	@echo "  - 1990-11-03 14:00 (Kryptos dedication)"
	@echo "  - 1990-06-21 12:00 (Summer solstice)"
	@echo "  - 1990-12-21 12:00 (Winter solstice)"
	@echo ""
	@echo "Quick start: make shadow-all"