# Makefile for Fork F - New Directions
# MASTER_SEED = 1337

PYTHON = python3
SHELL = /bin/bash

# Directories
F1_DIR = f1_anchor_search
F2_DIR = f2_ciphers
F3_DIR = f3_physical
F4_DIR = f4_errors
F5_DIR = f5_crosskeys

# Output
OUTPUT_BASE = fork_f_results
TIMESTAMP = $(shell date +%Y%m%d_%H%M%S)

.PHONY: all clean f1-scan f1-top f2-transposition f2-digraphs f2-nihilist f3-pack f4-errors f5-runningkey f5-tableaukey f6-confirm-new-anchors

# Default target
all: f1-scan f2-transposition
	@echo "=== Fork F tests complete ==="
	@echo "Check $(OUTPUT_BASE)/ for results"

# F1: Anchor Search (HIGHEST PRIORITY)
f1-scan:
	@echo "=== F1: Systematic Anchor Search ==="
	@mkdir -p $(OUTPUT_BASE)/f1
	cd $(F1_DIR) && $(PYTHON) f1_anchor_search.py
	@cp -r $(F1_DIR)/output/* $(OUTPUT_BASE)/f1/ 2>/dev/null || true
	@echo "F1 scan complete"

f1-top:
	@echo "=== F1: Top 10 Hits ==="
	@if [ -f $(OUTPUT_BASE)/f1/F1_top10.json ]; then \
		cat $(OUTPUT_BASE)/f1/F1_top10.json | $(PYTHON) -m json.tool; \
	else \
		echo "Run 'make f1-scan' first"; \
	fi

# F2: Non-Polyalphabetic Ciphers
f2-transposition:
	@echo "=== F2.1: Transposition Tests ==="
	@mkdir -p $(OUTPUT_BASE)/f2
	cd $(F2_DIR) && $(PYTHON) f2_transposition.py
	@cp -r $(F2_DIR)/output/* $(OUTPUT_BASE)/f2/ 2>/dev/null || true
	@echo "F2.1 transposition complete"

f2-digraphs:
	@echo "=== F2.2: Playfair/Two-Square Tests ==="
	@mkdir -p $(OUTPUT_BASE)/f2
	cd $(F2_DIR) && $(PYTHON) f2_digraphs.py
	@cp -r $(F2_DIR)/output/* $(OUTPUT_BASE)/f2/ 2>/dev/null || true
	@echo "F2.2 digraphs complete"

f2-nihilist:
	@echo "=== F2.3: Nihilist Tests ==="
	@mkdir -p $(OUTPUT_BASE)/f2
	cd $(F2_DIR) && $(PYTHON) f2_nihilist.py
	@cp -r $(F2_DIR)/output/* $(OUTPUT_BASE)/f2/ 2>/dev/null || true
	@echo "F2.3 nihilist complete"

# F3: Physical Inspection
f3-pack:
	@echo "=== F3: Physical Inspection Packet ==="
	@mkdir -p $(OUTPUT_BASE)/f3
	cd $(F3_DIR) && $(PYTHON) f3_physical_packet.py
	@cp -r $(F3_DIR)/output/* $(OUTPUT_BASE)/f3/ 2>/dev/null || true
	@echo "F3 packet generated"

# F4: Error Tolerance
f4-errors:
	@echo "=== F4: Error-Tolerant Matching ==="
	@mkdir -p $(OUTPUT_BASE)/f4
	cd $(F4_DIR) && $(PYTHON) f4_error_tolerance.py
	@cp -r $(F4_DIR)/output/* $(OUTPUT_BASE)/f4/ 2>/dev/null || true
	@echo "F4 error tolerance complete"

# F5: Cross-Section Keys
f5-runningkey:
	@echo "=== F5.1: Running Key Tests ==="
	@mkdir -p $(OUTPUT_BASE)/f5
	cd $(F5_DIR) && $(PYTHON) f5_running_key.py
	@cp -r $(F5_DIR)/output/* $(OUTPUT_BASE)/f5/ 2>/dev/null || true
	@echo "F5.1 running key complete"

f5-tableaukey:
	@echo "=== F5.2: Tableau Key Tests ==="
	@mkdir -p $(OUTPUT_BASE)/f5
	cd $(F5_DIR) && $(PYTHON) f5_tableau_key.py
	@cp -r $(F5_DIR)/output/* $(OUTPUT_BASE)/f5/ 2>/dev/null || true
	@echo "F5.2 tableau key complete"

# F6: Confirmation with new anchors
f6-confirm-new-anchors:
	@echo "=== F6: Confirming New Anchors ==="
	@if [ -f $(OUTPUT_BASE)/f1/F1_top10.json ]; then \
		cd $(F1_DIR) && $(PYTHON) f6_confirm_anchors.py; \
		cp -r $(F1_DIR)/f6_output/* $(OUTPUT_BASE)/f6/ 2>/dev/null || true; \
	else \
		echo "No new anchors to confirm. Run f1-scan first."; \
	fi

# Quick tests
test-lists:
	@echo "=== Checking candidate lists ==="
	@wc -l $(F1_DIR)/*.lst
	@if [ -f $(F1_DIR)/POLICIES.SHA256 ]; then \
		cat $(F1_DIR)/POLICIES.SHA256; \
	fi

# Validation
validate:
	@echo "=== Validating Fork F result cards ==="
	$(PYTHON) ../../validate_result_cards.py $(OUTPUT_BASE)

# Bundle for forum
bundle:
	@echo "=== Creating Forum Bundle ==="
	@mkdir -p $(OUTPUT_BASE)/bundle
	@cp -r $(OUTPUT_BASE)/f1/F1_anchor_hits.csv $(OUTPUT_BASE)/bundle/ 2>/dev/null || true
	@cp -r $(OUTPUT_BASE)/f1/F1_top10.json $(OUTPUT_BASE)/bundle/ 2>/dev/null || true
	@cp README.md $(OUTPUT_BASE)/bundle/ 2>/dev/null || true
	@zip -r FORK_F_forum_bundle_$(TIMESTAMP).zip $(OUTPUT_BASE)/bundle/
	@echo "Bundle created: FORK_F_forum_bundle_$(TIMESTAMP).zip"

# Clean
clean:
	rm -rf $(OUTPUT_BASE)
	rm -rf $(F1_DIR)/output $(F1_DIR)/POLICIES.SHA256
	rm -rf $(F2_DIR)/output
	rm -rf $(F3_DIR)/output
	rm -rf $(F4_DIR)/output
	rm -rf $(F5_DIR)/output
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -delete

clean-results:
	rm -rf $(OUTPUT_BASE)

# Help
help:
	@echo "Fork F - New Directions Toward the Missing 50"
	@echo ""
	@echo "Priority targets:"
	@echo "  make f1-scan    - Run systematic anchor search (HIGHEST PRIORITY)"
	@echo "  make f1-top     - Show top 10 anchor candidates"
	@echo ""
	@echo "Cipher tests:"
	@echo "  make f2-transposition - Test pure transposition ciphers"
	@echo "  make f2-digraphs      - Test Playfair/Two-Square"
	@echo "  make f2-nihilist      - Test Nihilist cipher"
	@echo ""
	@echo "Other tests:"
	@echo "  make f3-pack    - Generate physical inspection packet"
	@echo "  make f4-errors  - Test error tolerance"
	@echo "  make f5-runningkey - Test running keys from K1/K2/K3"
	@echo ""
	@echo "Utilities:"
	@echo "  make validate   - Validate result cards"
	@echo "  make bundle     - Create forum bundle"
	@echo "  make clean      - Clean all generated files"
	@echo ""
	@echo "MASTER_SEED = 1337 (frozen)"