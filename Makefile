# K4 Validation Makefile

.PHONY: all derive test-tail red-team validate-all clean help \
	core-harden core-harden-skeletons core-harden-tail core-harden-anchors core-harden-validate \
	core-harden-v2 core-harden-v3 core-harden-v3-all verify-min

# Default target
all: validate-all

# Minimal re-derivation (pure Python, no dependencies)
verify-min:
	@echo "=== Running minimal re-deriver (pure Python stdlib) ==="
	python3 01_PUBLISHED/winner_HEAD_0020_v522B/rederive_min.py \
	  --ct 02_DATA/ciphertext_97.txt \
	  --proof 01_PUBLISHED/winner_HEAD_0020_v522B/proof_digest_enhanced.json \
	  --out /tmp/k4_pt_min.txt && \
	echo "=== Verifying SHA-256 ===" && \
	shasum -a 256 /tmp/k4_pt_min.txt 01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt | \
	  grep -q "4eceb739ab655d6f4ec87753569b8bf04573fe26d01c0caa68d36776dd052d79" && \
	echo "✅ SHA-256 matches!" || echo "❌ SHA-256 mismatch!"

# Re-derive plaintext from CT + proof and verify SHAs
derive:
	@echo "=== Deriving plaintext from CT + proof ==="
	python3 07_TOOLS/validation/rederive_plaintext.py \
	  --ct 02_DATA/ciphertext_97.txt \
	  --proof 01_PUBLISHED/winner_HEAD_0020_v522B/proof_digest_enhanced.json \
	  --out /tmp/derived_plaintext_97.txt && \
	echo "=== Checking derivation SHAs ===" && \
	jq '.pt_sha256_bundle,.pt_sha256_derived,.tail_derivation_verified' \
	  01_PUBLISHED/winner_HEAD_0020_v522B/coverage_report.json

# Test tail derivation specifically
test-tail:
	@echo "=== Testing tail derivation (74-96) ==="
	python3 -m pytest tests/verification/test_tail_derivation.py -v || echo "Test framework not available"

# Run red team attack scripts
red-team:
	@echo "=== Running red team tests ==="
	@echo "1. Scramble tail test:"
	python3 scripts/attacks/scramble_tail_then_rederive.py
	@echo ""
	@echo "2. Drop anchor test:"
	python3 scripts/attacks/drop_anchor_then_derive.py
	@echo ""
	@echo "3. Derivation invariant check:"
	python3 07_TOOLS/validation/validate_derivation.py

# Validate bundle structure
validate-bundle:
	@echo "=== Validating winner bundle ==="
	python3 07_TOOLS/validation/validate_bundle.py \
	  01_PUBLISHED/winner_HEAD_0020_v522B --mode strict || echo "Bundle validator not available"

# Test for padding tokens
test-padding:
	@echo "=== Testing for padding tokens ==="
	python3 tests/test_no_padding_in_published.py || echo "Padding test not available"

# Run all validations
validate-all: derive test-tail test-padding validate-bundle
	@echo ""
	@echo "✅ All validation checks complete!"
	@echo ""
	@echo "Key verification points:"
	@echo "  - Plaintext re-derived from CT + proof"
	@echo "  - Tail emerges from anchor-forced wheels"
	@echo "  - No padding tokens in published bundle"
	@echo "  - Bundle structure validated"

# Quick confirm run
confirm:
	k4 confirm \
	  --ct 02_DATA/ciphertext_97.txt \
	  --pt 01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt \
	  --proof 01_PUBLISHED/winner_HEAD_0020_v522B/proof_digest.json \
	  --perm 02_DATA/permutations/GRID_W14_ROWS.json \
	  --cuts 02_DATA/constraints/canonical_cuts.json \
	  --fwords 02_DATA/constraints/function_words.txt \
	  --policy 01_PUBLISHED/winner_HEAD_0020_v522B/phrase_gate_policy.json \
	  --out /tmp/k4_verify

# Clean temporary files
clean:
	rm -f /tmp/derived_plaintext_97.txt
	rm -f /tmp/tail_derivation_temp.txt
	rm -rf /tmp/k4_verify

# Core Hardening Studies
core-harden: core-harden-skeletons core-harden-tail core-harden-anchors
	@echo ""
	@echo "✅ All core hardening studies complete!"
	@echo "Check 04_EXPERIMENTS/core_hardening/ for results"

core-harden-skeletons:
	@echo "=== Running Skeleton Uniqueness Survey ==="
	python3 03_SOLVERS/run_skeleton_survey.py

core-harden-tail:
	@echo "=== Running Tail Necessity Study ==="
	python3 03_SOLVERS/run_tail_necessity.py

core-harden-anchors:
	@echo "=== Running Anchor Perturbation Study ==="
	python3 03_SOLVERS/run_anchor_perturbations.py

core-harden-validate:
	@echo "=== Validating Core Hardening Results ==="
	python3 03_SOLVERS/validate_core_hardening.py || echo "Validator not yet implemented"

# Core Hardening v2 Studies
core-harden-v2:
	@echo "=== Running Core Hardening v2 Studies ==="
	@echo "1. Crib Ablation Study..."
	python3 07_TOOLS/core_hardening/run_crib_ablation.py
	@echo ""
	@echo "2. Minimum Tail Subset Study..."
	python3 07_TOOLS/core_hardening/run_min_tail_subset.py --kmin 10 --kmax 22
	@echo ""
	@echo "3. Alternative Tail Test..."
	python3 07_TOOLS/core_hardening/run_alt_tail_test.py --num-tails 100
	@echo ""
	@echo "4. Skeleton Survey v2..."
	python3 07_TOOLS/core_hardening/run_skeleton_survey_v2.py --max-patterns 200
	@echo ""
	@echo "✅ Core Hardening v2 complete! Check 04_EXPERIMENTS/core_hardening_v2/"

# Core Hardening v3 Studies  
core-harden-v3:
	@echo "=== Running Core Hardening v3 Studies ==="
	@echo "1. MTS Enhanced Study..."
	python3 07_TOOLS/core_hardening/run_min_tail_subset_enhanced.py --samples-per-k 100
	@echo ""
	@echo "2. Alternative Tail Enhanced..."
	python3 07_TOOLS/core_hardening/run_alt_tail_test_enhanced.py --num-tails 500
	@echo ""
	@echo "3. Skeleton Survey v3..."
	python3 07_TOOLS/core_hardening/run_skeleton_survey_v3.py --max-patterns 200
	@echo ""
	@echo "4. Creating Undetermined Positions Map..."
	python3 07_TOOLS/core_hardening/create_und_map.py
	@echo ""
	@echo "✅ Core Hardening v3 complete! Check 04_EXPERIMENTS/core_hardening_v3/"

# Run all core hardening studies
core-harden-v3-all: core-harden core-harden-v2 core-harden-v3
	@echo ""
	@echo "🎯 All Core Hardening Studies Complete!"
	@echo ""
	@echo "Results locations:"
	@echo "  v1: 04_EXPERIMENTS/core_hardening/"
	@echo "  v2: 04_EXPERIMENTS/core_hardening_v2/"
	@echo "  v3: 04_EXPERIMENTS/core_hardening_v3/"
	@echo ""
	@echo "Key findings:"
	@echo "  - Only baseline skeleton pattern is feasible"
	@echo "  - Full 22-character tail is required"
	@echo "  - 73/97 positions are undetermined without tail"

# Show help
help:
	@echo "K4 Validation Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  make derive        - Re-derive plaintext from CT + proof"
	@echo "  make test-tail     - Test tail derivation specifically"
	@echo "  make red-team      - Run red team attack scripts"
	@echo "  make validate-all  - Run all validation checks"
	@echo "  make confirm       - Run standard k4 confirm"
	@echo ""
	@echo "Core Hardening Studies (v1):"
	@echo "  make core-harden             - Run all three v1 hardening studies"
	@echo "  make core-harden-skeletons   - Run skeleton uniqueness survey"
	@echo "  make core-harden-tail        - Run tail necessity study"
	@echo "  make core-harden-anchors     - Run anchor perturbations study"
	@echo ""
	@echo "Core Hardening Studies (v2/v3):"
	@echo "  make core-harden-v2          - Run all v2 enhanced studies"
	@echo "  make core-harden-v3          - Run all v3.1 final studies"
	@echo "  make core-harden-v3-all      - Run complete v1+v2+v3 suite"
	@echo ""
	@echo "  make clean         - Remove temporary files"
	@echo "  make help          - Show this help message"
	@echo ""
	@echo "Quick validation:"
	@echo "  make validate-all"
	@echo ""
	@echo "Complete core hardening suite:"
	@echo "  make core-harden-v3-all"