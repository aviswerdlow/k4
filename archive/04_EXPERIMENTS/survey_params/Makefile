# Makefile for Fork S - Surveying Cipher Parameters
# Position-preserving crypto driven by plaza/survey geometry

.PHONY: all clean test survey-bearings survey-dms survey-transpose survey-matrix survey-arc survey-hybrid survey-params-all validate package

# Configuration
PYTHON = python3
BASE_DIR = /Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus
EXPERIMENTS_DIR = $(BASE_DIR)/04_EXPERIMENTS/survey_params
RESULTS_DIR = $(EXPERIMENTS_DIR)/results
LIB_DIR = $(EXPERIMENTS_DIR)/lib

# Default target
all: survey-params-all

# Clean generated files
clean:
	rm -rf $(RESULTS_DIR)/*.json
	rm -f $(EXPERIMENTS_DIR)/RUN_SUMMARY.csv
	rm -f $(EXPERIMENTS_DIR)/METHODS_MANIFEST.json
	rm -f $(EXPERIMENTS_DIR)/FINAL_REPORT.md
	@echo "Cleaned all generated files"

# Test parameter extraction
test-params:
	@echo "Testing parameter extraction utilities..."
	cd $(BASE_DIR) && $(PYTHON) $(LIB_DIR)/survey_params.py
	@echo ""

# Test Battery A: Pure bearings
survey-bearings:
	@echo "=========================================="
	@echo "TEST BATTERY A: Pure Bearings"
	@echo "=========================================="
	cd $(BASE_DIR) && $(PYTHON) -c "import sys; sys.path.insert(0, '$(LIB_DIR)'); \
		from run_survey_tests import SurveyingCipherTester; \
		tester = SurveyingCipherTester(); \
		tester.run_test_battery_A(); \
		print(f'Battery A complete: {len(tester.passing_results)} matches')"

# Test Battery B: DMS configurations
survey-dms:
	@echo "=========================================="
	@echo "TEST BATTERY B: DMS & Quadrants"
	@echo "=========================================="
	cd $(BASE_DIR) && $(PYTHON) -c "import sys; sys.path.insert(0, '$(LIB_DIR)'); \
		from run_survey_tests import SurveyingCipherTester; \
		tester = SurveyingCipherTester(); \
		tester.run_test_battery_B(); \
		print(f'Battery B complete: {len(tester.passing_results)} matches')"

# Test Battery C: Magnetic corrections
survey-magnetic:
	@echo "=========================================="
	@echo "TEST BATTERY C: Magnetic Corrections"
	@echo "=========================================="
	cd $(BASE_DIR) && $(PYTHON) -c "import sys; sys.path.insert(0, '$(LIB_DIR)'); \
		from run_survey_tests import SurveyingCipherTester; \
		tester = SurveyingCipherTester(); \
		tester.run_test_battery_C(); \
		print(f'Battery C complete: {len(tester.passing_results)} matches')"

# Test Battery D: Transposition with inversion
survey-transpose:
	@echo "=========================================="
	@echo "TEST BATTERY D: Distance/Transposition"
	@echo "=========================================="
	cd $(BASE_DIR) && $(PYTHON) -c "import sys; sys.path.insert(0, '$(LIB_DIR)'); \
		from run_survey_tests import SurveyingCipherTester; \
		tester = SurveyingCipherTester(); \
		tester.run_test_battery_D(); \
		print(f'Battery D complete: {len(tester.passing_results)} matches')"

# Test Battery E: Arc transforms
survey-arc:
	@echo "=========================================="
	@echo "TEST BATTERY E: Arc/Chord/Sector"
	@echo "=========================================="
	cd $(BASE_DIR) && $(PYTHON) -c "import sys; sys.path.insert(0, '$(LIB_DIR)'); \
		from run_survey_tests import SurveyingCipherTester; \
		tester = SurveyingCipherTester(); \
		tester.run_test_battery_E(); \
		print(f'Battery E complete: {len(tester.passing_results)} matches')"

# Hybrid pipeline tests
survey-hybrid:
	@echo "=========================================="
	@echo "HYBRID PIPELINE TESTS"
	@echo "=========================================="
	cd $(BASE_DIR) && $(PYTHON) -c "import sys; sys.path.insert(0, '$(LIB_DIR)'); \
		from run_survey_tests import SurveyingCipherTester; \
		tester = SurveyingCipherTester(); \
		tester.run_hybrid_tests(); \
		print(f'Hybrid tests complete: {len(tester.passing_results)} matches')"

# Run all survey parameter tests
survey-params-all:
	@echo "=========================================="
	@echo "FORK S - COMPLETE TEST SUITE"
	@echo "=========================================="
	cd $(BASE_DIR) && $(PYTHON) $(EXPERIMENTS_DIR)/run_survey_tests.py
	@echo ""
	@echo "Results saved to: $(RESULTS_DIR)"

# Validate anchors and data files
validate:
	@echo "Validating prerequisites..."
	@test -f "$(BASE_DIR)/02_DATA/ciphertext_97.txt" && echo "✓ Ciphertext found" || echo "✗ Ciphertext missing"
	@test -f "$(BASE_DIR)/02_DATA/anchors/four_anchors.json" && echo "✓ Anchors found" || echo "✗ Anchors missing"
	@$(PYTHON) -c "import json; \
		with open('$(BASE_DIR)/02_DATA/anchors/four_anchors.json') as f: \
			anchors = json.load(f); \
			print(f'✓ Anchors loaded: {list(anchors.keys())}'); \
			for name, data in anchors.items(): \
				assert data['end'] - data['start'] + 1 == len(data['plaintext']), f'{name} length mismatch'; \
			print('✓ Anchor positions validated')"

# Status check
status:
	@echo "Fork S Status:"
	@echo -n "Result files: "; ls $(RESULTS_DIR)/*.json 2>/dev/null | wc -l
	@if [ -f "$(EXPERIMENTS_DIR)/RUN_SUMMARY.csv" ]; then \
		echo -n "Tests in CSV: "; tail -n +2 $(EXPERIMENTS_DIR)/RUN_SUMMARY.csv | wc -l; \
		echo -n "Anchors preserved: "; cut -d',' -f2 $(EXPERIMENTS_DIR)/RUN_SUMMARY.csv | grep -c "True"; \
	fi
	@if [ -f "$(EXPERIMENTS_DIR)/FINAL_REPORT.md" ]; then \
		echo ""; \
		grep "^- " $(EXPERIMENTS_DIR)/FINAL_REPORT.md | head -5; \
	fi

# Package results for forum
package:
	@echo "Packaging Fork S results..."
	@mkdir -p $(EXPERIMENTS_DIR)/FORK_S_forum_bundle
	@cp $(RESULTS_DIR)/*.json $(EXPERIMENTS_DIR)/FORK_S_forum_bundle/ 2>/dev/null || true
	@cp $(EXPERIMENTS_DIR)/RUN_SUMMARY.csv $(EXPERIMENTS_DIR)/FORK_S_forum_bundle/ 2>/dev/null || true
	@cp $(EXPERIMENTS_DIR)/METHODS_MANIFEST.json $(EXPERIMENTS_DIR)/FORK_S_forum_bundle/ 2>/dev/null || true
	@cp $(EXPERIMENTS_DIR)/FINAL_REPORT.md $(EXPERIMENTS_DIR)/FORK_S_forum_bundle/ 2>/dev/null || true
	@cp $(EXPERIMENTS_DIR)/README.md $(EXPERIMENTS_DIR)/FORK_S_forum_bundle/ 2>/dev/null || true
	@cd $(EXPERIMENTS_DIR) && zip -r FORK_S_forum_bundle.zip FORK_S_forum_bundle/
	@echo "Forum bundle created: $(EXPERIMENTS_DIR)/FORK_S_forum_bundle.zip"

# Help
help:
	@echo "Fork S - Surveying Cipher Parameters"
	@echo ""
	@echo "Test Batteries:"
	@echo "  make survey-bearings   - Test pure bearing parameters"
	@echo "  make survey-dms       - Test DMS and quadrant parameters"
	@echo "  make survey-magnetic  - Test magnetic corrections"
	@echo "  make survey-transpose - Test transposition with distances"
	@echo "  make survey-arc       - Test arc/chord/sector transforms"
	@echo "  make survey-hybrid    - Test hybrid pipelines"
	@echo ""
	@echo "Complete Suite:"
	@echo "  make survey-params-all - Run all test batteries"
	@echo ""
	@echo "Utilities:"
	@echo "  make test-params      - Test parameter extraction"
	@echo "  make validate        - Validate data files"
	@echo "  make status          - Show current status"
	@echo "  make package         - Create forum bundle"
	@echo "  make clean           - Remove generated files"
	@echo ""
	@echo "Quick start: make survey-params-all"