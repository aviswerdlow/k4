# Makefile for Fork RK - Running Key Cipher

.PHONY: all clean test quick full status help

# Configuration
PYTHON = python3
BASE_DIR = /Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus
RK_DIR = $(BASE_DIR)/04_EXPERIMENTS/fork_rk
RESULTS_DIR = $(RK_DIR)/results

# Default target
all: quick

# Clean generated files
clean:
	rm -rf $(RESULTS_DIR)/*.json
	rm -f $(RK_DIR)/RUN_SUMMARY.csv
	rm -f $(RK_DIR)/RANKED_SUMMARY.md
	@echo "Cleaned all generated files"

# Quick test (subset of keys)
quick: rk-quick

rk-quick:
	@echo "=========================================="
	@echo "FORK RK - QUICK TEST"
	@echo "=========================================="
	cd $(BASE_DIR) && $(PYTHON) -c "import sys; sys.path.insert(0, '$(RK_DIR)'); \
		from run_rk_tests import RunningKeyTester; \
		tester = RunningKeyTester(); \
		from running_key_cipher import K1_PLAINTEXT, K2_PLAINTEXT; \
		for offset in [0, 10, 20]: \
			for family in ['vigenere', 'beaufort']: \
				tester.test_configuration('RK1', {'key_text': K1_PLAINTEXT, 'offset': offset}, family); \
				tester.test_configuration('RK2', {'key_text': K2_PLAINTEXT, 'offset': offset}, family); \
		print(f'Quick test complete: {tester.test_count} tests, {len(tester.passing_results)} candidates')"

# Full test
full: rk-all

rk-all:
	@echo "=========================================="
	@echo "FORK RK - FULL TEST"
	@echo "=========================================="
	cd $(BASE_DIR) && $(PYTHON) $(RK_DIR)/run_rk_tests.py

# Status check
status:
	@echo "Fork RK Status:"
	@echo -n "Result files: "; ls $(RESULTS_DIR)/*.json 2>/dev/null | wc -l
	@if [ -f "$(RK_DIR)/RUN_SUMMARY.csv" ]; then \
		echo -n "Tests in CSV: "; tail -n +2 $(RK_DIR)/RUN_SUMMARY.csv | wc -l; \
		echo -n "Anchors preserved: "; cut -d',' -f5 $(RK_DIR)/RUN_SUMMARY.csv | grep -c "True"; \
	fi

# Help
help:
	@echo "Fork RK - Running Key Cipher"
	@echo ""
	@echo "Targets:"
	@echo "  make quick   - Quick test with subset of keys"
	@echo "  make full    - Full test with all key variants"
	@echo "  make status  - Show current status"
	@echo "  make clean   - Remove generated files"
	@echo ""
	@echo "Quick start: make quick"