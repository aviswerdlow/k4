# How to Reproduce These Results

## Prerequisites

1. Python 3.8+ with pdfplumber: `pip install pdfplumber`
2. Flint PDF at: `06_DOCUMENTATION/A_System_of_Geometry_and_Trigonometry.pdf`
3. K4 ciphertext at: `02_DATA/ciphertext_97.txt`
4. Anchors JSON at: `02_DATA/anchors/four_anchors.json`

## Steps

```bash
# Run complete pipeline
cd experiments/flint_otp_traverse
python run_traverse_otp.py

# Or use Makefile
make traverse-otp-all
```

## Key Parameters

- MASTER_SEED = 1337 (ensures reproducibility)
- Anchors: EAST@21-24, NORTHEAST@25-33, BERLIN@63-68, CLOCK@69-73
- Keystream families: F1-F6 (single digit, pairs, triples, sums, interleave, paths)
- Decoders: Vigenère (P=C-K) and Beaufort (P=K-C)
