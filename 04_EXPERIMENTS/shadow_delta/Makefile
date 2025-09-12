# Makefile for Fork S-ShadowΔ
# Zone-Driven Shadow/Survey Integration

.PHONY: all clean test quick full status help

# Configuration
PYTHON = python3
BASE_DIR = /Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus
SHADOW_DELTA_DIR = $(BASE_DIR)/04_EXPERIMENTS/shadow_delta
RESULTS_DIR = $(SHADOW_DELTA_DIR)/results
MASKS_DIR = $(SHADOW_DELTA_DIR)/masks

# Default target
all: quick

# Clean generated files
clean:
	rm -rf $(RESULTS_DIR)/*.json
	rm -rf $(RESULTS_DIR)/applied/*.json
	rm -rf $(MASKS_DIR)/*.json
	rm -f $(SHADOW_DELTA_DIR)/RUN_SUMMARY.csv
	rm -f $(SHADOW_DELTA_DIR)/DELTA_vs_ForkS.md
	@echo "Cleaned all generated files"

# Test shadow zones
test-zones:
	@echo "Testing shadow zone generation..."
	cd $(BASE_DIR) && $(PYTHON) $(SHADOW_DELTA_DIR)/shadow_zones.py
	@echo ""

# Test zone cipher
test-cipher:
	@echo "Testing zone-driven cipher..."
	cd $(BASE_DIR) && $(PYTHON) $(SHADOW_DELTA_DIR)/zone_polyalpha.py
	@echo ""

# Quick test (dedication + A-zones + 2 bearings + P-Light)
quick: sshadow-quick

sshadow-quick:
	@echo "=========================================="
	@echo "FORK S-SHADOWΔ - QUICK TEST"
	@echo "=========================================="
	cd $(BASE_DIR) && $(PYTHON) $(SHADOW_DELTA_DIR)/run_shadow_delta_tests.py
	@echo ""
	@echo "Results saved to: $(RESULTS_DIR)"

# Full test matrix
full: sshadow-all

sshadow-all:
	@echo "=========================================="
	@echo "FORK S-SHADOWΔ - FULL TEST MATRIX"
	@echo "=========================================="
	cd $(BASE_DIR) && $(PYTHON) -c "import sys; sys.path.insert(0, '$(SHADOW_DELTA_DIR)'); \
		from run_shadow_delta_tests import ShadowDeltaTester, main; \
		tester = ShadowDeltaTester(); \
		tester.run_full_test(); \
		tester.generate_summary(); \
		print(f'Full test complete: {len(tester.all_results)} tests')"

# Status check
status:
	@echo "Fork S-ShadowΔ Status:"
	@echo -n "Result files: "; ls $(RESULTS_DIR)/*.json 2>/dev/null | wc -l
	@echo -n "Mask files: "; ls $(MASKS_DIR)/*.json 2>/dev/null | wc -l
	@echo -n "Applied logs: "; ls $(RESULTS_DIR)/applied/*.json 2>/dev/null | wc -l
	@if [ -f "$(SHADOW_DELTA_DIR)/RUN_SUMMARY.csv" ]; then \
		echo -n "Tests in CSV: "; tail -n +2 $(SHADOW_DELTA_DIR)/RUN_SUMMARY.csv | wc -l; \
		echo -n "Anchors preserved: "; cut -d',' -f5 $(SHADOW_DELTA_DIR)/RUN_SUMMARY.csv | grep -c "True"; \
	fi
	@if [ -f "$(SHADOW_DELTA_DIR)/DELTA_vs_ForkS.md" ]; then \
		echo ""; \
		grep "^- " $(SHADOW_DELTA_DIR)/DELTA_vs_ForkS.md | head -5; \
	fi

# Help
help:
	@echo "Fork S-ShadowΔ - Zone-Driven Shadow/Survey Integration"
	@echo ""
	@echo "Targets:"
	@echo "  make quick         - Quick test (dedication, A-zones, 2 bearings, P-Light)"
	@echo "  make full          - Full test matrix (all datetimes, masks, profiles)"
	@echo "  make test-zones    - Test shadow zone generation"
	@echo "  make test-cipher   - Test zone-driven cipher"
	@echo "  make status        - Show current status"
	@echo "  make clean         - Remove generated files"
	@echo ""
	@echo "Quick start: make quick"