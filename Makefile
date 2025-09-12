# Makefile for K4 External Constraints Investigation (Fork D)
# MASTER_SEED = 1337

PYTHON = python3
SHELL = /bin/bash

# Directories
BERLIN_DIR = 07_TOOLS/berlin_clock
TABLEAU_DIR = 07_TOOLS/tableau_sync
PHYS_DIR = 04_EXPERIMENTS/physical_analysis
BEARING_DIR = 07_TOOLS/bearings
COMPOSITE_DIR = 04_EXPERIMENTS/composites

# Output directories
OUTPUT_BASE = fork_d_results
TIMESTAMP = $(shell date +%Y%m%d_%H%M%S)

.PHONY: all clean berlin-clock-all tableau-sync physical-analysis bearings composites fork-d-report

# Default target
all: berlin-clock-all tableau-sync physical-analysis bearings
	@echo "=== All Fork D tests complete ==="
	@echo "Results in $(OUTPUT_BASE)/"

# Task 1: Berlin Clock tests
berlin-clock-all:
	@echo "=== Running Berlin Clock tests ==="
	@mkdir -p $(OUTPUT_BASE)/berlin_clock
	cd $(BERLIN_DIR) && $(PYTHON) berlin_clock_k4.py
	@cp -r $(BERLIN_DIR)/runs/* $(OUTPUT_BASE)/berlin_clock/ 2>/dev/null || true
	@echo "Berlin Clock tests complete"

# Task 2: Tableau synchronization
tableau-sync:
	@echo "=== Running Tableau Synchronization ==="
	@mkdir -p $(OUTPUT_BASE)/tableau_sync
	cd $(TABLEAU_DIR) && $(PYTHON) tableau_synchronizer.py
	@cp -r $(TABLEAU_DIR)/output/* $(OUTPUT_BASE)/tableau_sync/ 2>/dev/null || true
	@echo "Tableau sync tests complete"

# Task 3: Physical position analysis
physical-analysis:
	@echo "=== Running Physical Position Analysis ==="
	@mkdir -p $(OUTPUT_BASE)/physical
	cd $(PHYS_DIR) && $(PYTHON) physical_position.py
	@cp -r $(PHYS_DIR)/output/* $(OUTPUT_BASE)/physical/ 2>/dev/null || true
	@echo "Physical analysis complete"

# Task 4: Bearings analysis
bearings:
	@echo "=== Running Bearings Analysis ==="
	@mkdir -p $(OUTPUT_BASE)/bearings
	cd $(BEARING_DIR) && $(PYTHON) bearing_analysis.py
	@cp -r $(BEARING_DIR)/output/* $(OUTPUT_BASE)/bearings/ 2>/dev/null || true
	@echo "Bearings analysis complete"

# Task 5: Composite mechanisms
composites:
	@echo "=== Running Composite Mechanism Tests ==="
	@mkdir -p $(OUTPUT_BASE)/composites
	cd $(COMPOSITE_DIR) && $(PYTHON) composite_mechanisms.py
	@cp -r $(COMPOSITE_DIR)/output/* $(OUTPUT_BASE)/composites/ 2>/dev/null || true
	@echo "Composite tests complete"

# Generate final report
fork-d-report: all
	@echo "=== Generating Fork D Report ==="
	$(PYTHON) generate_fork_d_report.py $(OUTPUT_BASE)
	@echo "Report generated: $(OUTPUT_BASE)/FORK_D_REPORT.md"

# Quick test targets
test-berlin:
	cd $(BERLIN_DIR) && $(PYTHON) berlin_clock_simulator.py

test-tableau:
	cd $(TABLEAU_DIR) && $(PYTHON) -c "from tableau_synchronizer import *; sync = TableauSynchronizer(); print(\"Tableau built:\", len(sync.tableau), \"rows\")"

# Validation target
validate:
	@echo "=== Validating result cards ==="
	$(PYTHON) validate_result_cards.py $(OUTPUT_BASE)

# Clean targets
clean:
	rm -rf $(OUTPUT_BASE)
	rm -rf $(BERLIN_DIR)/runs
	rm -rf $(BERLIN_DIR)/METHODS_MANIFEST.json
	rm -rf $(TABLEAU_DIR)/output
	rm -rf $(TABLEAU_DIR)/*.json
	rm -rf $(TABLEAU_DIR)/*.csv
	rm -rf $(PHYS_DIR)/output
	rm -rf $(BEARING_DIR)/output
	rm -rf $(COMPOSITE_DIR)/output
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -delete

clean-results:
	rm -rf $(OUTPUT_BASE)

# Archive results
archive:
	tar -czf fork_d_results_$(TIMESTAMP).tar.gz $(OUTPUT_BASE)/
	@echo "Results archived to fork_d_results_$(TIMESTAMP).tar.gz"

# Help target
help:
	@echo "K4 External Constraints Investigation (Fork D) - Make targets:"
	@echo ""
	@echo "  make all              - Run all tests (Berlin, Tableau, Physical, Bearings)"
	@echo "  make berlin-clock-all - Run Berlin Clock tests only"
	@echo "  make tableau-sync     - Run Tableau synchronization only"
	@echo "  make physical-analysis - Run physical position analysis only"
	@echo "  make bearings         - Run bearings analysis only"
	@echo "  make composites       - Run composite mechanism tests"
	@echo "  make fork-d-report    - Generate final report"
	@echo "  make validate         - Validate all result cards"
	@echo "  make clean            - Clean all generated files"
	@echo "  make archive          - Archive results with timestamp"
	@echo ""
	@echo "Quick tests:"
	@echo "  make test-berlin      - Test Berlin Clock simulator"
	@echo "  make test-tableau     - Test Tableau builder"
	@echo ""
	@echo "MASTER_SEED = 1337 (frozen)"
