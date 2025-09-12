# Fresh-slate K4 derivation Makefile
# Derives from CT + cribs only, no AI, no hypothesis scaffolding

.PHONY: all clean fresh-baseline-four fresh-baseline-three-no-berlin \
        fresh-baseline-three-no-clock fresh-baseline-two-east-ne \
        fresh-explain fresh-all

# Default: run all baseline derivations
all: fresh-all

# Run all baseline derivations
fresh-all: fresh-baseline-four fresh-baseline-three-no-berlin \
           fresh-baseline-three-no-clock fresh-baseline-two-east-ne
	@echo "All fresh-slate derivations complete"
	@echo "Check runs/ directory for results"

# Four anchors: EAST, NORTHEAST, BERLIN, CLOCK
fresh-baseline-four:
	@echo "=== Running baseline with 4 anchors ==="
	python3 tools/fresh_slate_derive.py \
	  --ct inputs/ciphertext_97.txt \
	  --crib inputs/cribs/four_anchors.json \
	  --classing classing/baseline.json \
	  --out runs/baseline_four_anchors/

# Three anchors: EAST, NORTHEAST, CLOCK (no BERLIN)
fresh-baseline-three-no-berlin:
	@echo "=== Running baseline with 3 anchors (no BERLIN) ==="
	python3 tools/fresh_slate_derive.py \
	  --ct inputs/ciphertext_97.txt \
	  --crib inputs/cribs/three_anchors_no_berlin.json \
	  --classing classing/baseline.json \
	  --out runs/baseline_three_no_berlin/

# Three anchors: EAST, NORTHEAST, BERLIN (no CLOCK)
fresh-baseline-three-no-clock:
	@echo "=== Running baseline with 3 anchors (no CLOCK) ==="
	python3 tools/fresh_slate_derive.py \
	  --ct inputs/ciphertext_97.txt \
	  --crib inputs/cribs/three_anchors_no_clock.json \
	  --classing classing/baseline.json \
	  --out runs/baseline_three_no_clock/

# Two anchors: EAST, NORTHEAST only
fresh-baseline-two-east-ne:
	@echo "=== Running baseline with 2 anchors (EAST, NORTHEAST) ==="
	python3 tools/fresh_slate_derive.py \
	  --ct inputs/ciphertext_97.txt \
	  --crib inputs/cribs/two_anchors_east_ne.json \
	  --classing classing/baseline.json \
	  --out runs/baseline_two_east_ne/

# Explain a single index (default: 80)
fresh-explain:
	@echo "=== Explaining index 80 ==="
	python3 tools/explain_one.py \
	  --ct inputs/ciphertext_97.txt \
	  --crib inputs/cribs/four_anchors.json \
	  --classing classing/baseline.json \
	  --index 80

# Clean all runs
clean:
	rm -rf runs/*
	@echo "Cleaned all run outputs"