# K4 CLI Plus - Main Makefile
# Zone-based cryptanalysis framework for K4

.PHONY: help phase3-a phase3-b phase3-c phase3-d phase3-antipodes verify-rt notecard clean

help:
	@echo "K4 CLI Plus - Available targets:"
	@echo "  phase3-a        - Run Batch A: MID zone exploitation"
	@echo "  phase3-b        - Run Batch B: Turn flip wash routes"
	@echo "  phase3-c        - Run Batch C: Mask discovery"
	@echo "  phase3-d        - Run Batch D: Twist detector"
	@echo "  phase3-antipodes - Run Antipodes cross-check"
	@echo "  verify-rt       - Verify round-trip for a manifest"
	@echo "  notecard        - Generate notecard for a solution"
	@echo "  clean           - Clean generated files"

# Phase 3 Batch A - MID zone exploitation
phase3-a:
	@echo "Running Phase 3 Batch A - MID zone exploitation..."
	@mkdir -p 04_EXPERIMENTS/phase3_zone/runs
	python3 03_SOLVERS/zone_mask_v1/scripts/zone_runner.py \
		--manifest 04_EXPERIMENTS/phase3_zone/configs/batch_a.json \
		--batch \
		--output 04_EXPERIMENTS/phase3_zone/runs

# Phase 3 Batch B - Turn flip wash routes
phase3-b:
	@echo "Running Phase 3 Batch B - Turn flip wash routes..."
	@mkdir -p 04_EXPERIMENTS/phase3_zone/runs
	python3 03_SOLVERS/zone_mask_v1/scripts/zone_runner.py \
		--manifest 04_EXPERIMENTS/phase3_zone/configs/batch_b.json \
		--batch \
		--output 04_EXPERIMENTS/phase3_zone/runs

# Phase 3 Batch C - Mask discovery
phase3-c:
	@echo "Running Phase 3 Batch C - Mask discovery..."
	@mkdir -p 04_EXPERIMENTS/mask_discovery/reports
	python3 04_EXPERIMENTS/mask_discovery/discover_masks.py \
		--ct 02_DATA/ciphertext_97.txt \
		--out 04_EXPERIMENTS/mask_discovery/reports

# Phase 3 Batch D - Twist detector
phase3-d:
	@echo "Running Phase 3 Batch D - Twist detector..."
	@if [ -f "04_EXPERIMENTS/phase3_zone/runs/best.json" ]; then \
		python3 04_EXPERIMENTS/twist_detector/sanborn_twist.py \
			--baseline 04_EXPERIMENTS/phase3_zone/runs/best.json; \
	else \
		echo "Error: No best.json found. Run other batches first."; \
		exit 1; \
	fi

# Phase 3 Antipodes cross-check
phase3-antipodes:
	@echo "Running Antipodes cross-check..."
	python3 04_EXPERIMENTS/antipodes_check/reorder_to_antipodes.py \
		--ct 02_DATA/ciphertext_97.txt \
		--layout 02_DATA/antipodes_layout.json

# Verify round-trip for a manifest
verify-rt:
	@if [ -z "$(MANIFEST)" ]; then \
		if [ -f "04_EXPERIMENTS/phase3_zone/runs/best.json" ]; then \
			MANIFEST="04_EXPERIMENTS/phase3_zone/runs/best.json"; \
		else \
			echo "Error: No manifest specified. Use MANIFEST=path/to/manifest.json"; \
			exit 1; \
		fi \
	fi; \
	python3 03_SOLVERS/zone_mask_v1/scripts/verifier.py \
		--manifest $$MANIFEST \
		--ct 02_DATA/ciphertext_97.txt \
		--verbose

# Generate notecard for a solution
notecard:
	@if [ -z "$(MANIFEST)" ]; then \
		if [ -f "04_EXPERIMENTS/phase3_zone/runs/best.json" ]; then \
			MANIFEST="04_EXPERIMENTS/phase3_zone/runs/best.json"; \
		else \
			echo "Error: No manifest specified. Use MANIFEST=path/to/manifest.json"; \
			exit 1; \
		fi \
	fi; \
	python3 03_SOLVERS/zone_mask_v1/scripts/notecard.py \
		--manifest $$MANIFEST \
		--out 04_EXPERIMENTS/phase3_zone/runs/best_notecard.md

# Additional experimental targets
discover-masks:
	@echo "Running mask discovery experiments..."
	@mkdir -p 04_EXPERIMENTS/mask_discovery
	python3 04_EXPERIMENTS/mask_discovery/discover_masks.py \
		--ct 02_DATA/ciphertext_97.txt \
		--out 04_EXPERIMENTS/mask_discovery/reports

test-routes:
	@echo "Testing route variants..."
	@mkdir -p 04_EXPERIMENTS/route_variants
	python3 04_EXPERIMENTS/route_variants/grid_routes.py \
		--ct 02_DATA/ciphertext_97.txt

error-injection:
	@echo "Running error injection tests..."
	python3 04_EXPERIMENTS/error_injection/inject_errors.py \
		--manifest 04_EXPERIMENTS/phase3_zone/runs/best.json

k5-gate:
	@echo "Running K5 gate check..."
	python3 04_EXPERIMENTS/k5_gate/post_plaintext_gate.py \
		--plaintext 04_EXPERIMENTS/phase3_zone/runs/best_plaintext.txt

# Validation and testing
validate-manifest:
	@if [ -z "$(MANIFEST)" ]; then \
		echo "Error: No manifest specified. Use MANIFEST=path/to/manifest.json"; \
		exit 1; \
	fi
	python3 07_TOOLS/validation/validate_manifest.py \
		--manifest $(MANIFEST) \
		--schema 03_SOLVERS/zone_mask_v1/recipes/recipe.schema.json

validate-roundtrip:
	@if [ -z "$(MANIFEST)" ]; then \
		echo "Error: No manifest specified. Use MANIFEST=path/to/manifest.json"; \
		exit 1; \
	fi
	python3 07_TOOLS/validation/validate_roundtrip.py \
		--manifest $(MANIFEST) \
		--ct 02_DATA/ciphertext_97.txt

# Null control tests
null-key-scramble:
	python3 07_TOOLS/nulls/key_scramble.py \
		--manifest 04_EXPERIMENTS/phase3_zone/runs/best.json \
		--iterations 1000

null-segment-shuffle:
	python3 07_TOOLS/nulls/segment_shuffle.py \
		--manifest 04_EXPERIMENTS/phase3_zone/runs/best.json \
		--iterations 1000

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	rm -rf 04_EXPERIMENTS/phase3_zone/runs/*.json
	rm -rf 04_EXPERIMENTS/phase3_zone/runs/*.txt
	rm -rf 04_EXPERIMENTS/phase3_zone/runs/*.md
	rm -rf 04_EXPERIMENTS/mask_discovery/reports/*
	@echo "Clean complete."

# Development helpers
lint:
	@echo "Running Python linting..."
	python3 -m pylint 03_SOLVERS/zone_mask_v1/scripts/*.py

format:
	@echo "Formatting Python code..."
	python3 -m black 03_SOLVERS/zone_mask_v1/scripts/

test:
	@echo "Running unit tests..."
	python3 -m pytest 03_SOLVERS/zone_mask_v1/tests/ -v

# Installation
install:
	@echo "Installing dependencies..."
	pip3 install -r requirements.txt

requirements.txt:
	@echo "numpy>=1.20.0" > requirements.txt
	@echo "pytest>=6.0.0" >> requirements.txt
	@echo "pylint>=2.0.0" >> requirements.txt
	@echo "black>=21.0" >> requirements.txt
	@echo "jsonschema>=3.2.0" >> requirements.txt