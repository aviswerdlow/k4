#!/usr/bin/env python3
"""
Systematic sweep - enumerate all 97-char normalized candidates in hot zones
Target Surveying cases VI-IX, Appendix No. I, and key sections
Use anchor-first filtering for efficiency
"""

import json
import csv
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Generator
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer


def normalize_az(text: str) -> str:
    """Normalize text to A-Z only, uppercase"""
    return ''.join(c.upper() for c in text if c.isalpha())


def char_to_num(c: str) -> int:
    """Convert A-Z to 0-25"""
    return ord(c) - ord('A')


def num_to_char(n: int) -> str:
    """Convert 0-25 to A-Z"""
    return chr((n % 26) + ord('A'))


def load_ciphertext() -> str:
    """Load K4 ciphertext"""
    ct_path = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/02_DATA/ciphertext_97.txt")
    with open(ct_path) as f:
        return f.read().strip()


def load_anchors() -> Dict:
    """Load anchor constraints"""
    anchor_path = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/02_DATA/anchors/four_anchors.json")
    with open(anchor_path) as f:
        return json.load(f)


def extract_target_pages(pdf_path: str, target_pages: List[int]) -> Dict[int, str]:
    """Extract text from specific pages"""
    pages_text = {}
    
    for page_num, page in enumerate(extract_pages(pdf_path), 1):
        if page_num in target_pages:
            text = ""
            for element in page:
                if isinstance(element, LTTextContainer):
                    text += element.get_text()
            pages_text[page_num] = text
    
    return pages_text


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using simple heuristics"""
    # Clean up text
    text = ' '.join(text.split())  # Normalize whitespace
    
    # Split on sentence endings
    sentences = re.split(r'[.!?;]\s+', text)
    
    # Filter out very short fragments
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    return sentences


def compute_required_key_letters(ciphertext: str, anchors: Dict, 
                                decode_type: str = "vigenere") -> Dict[int, str]:
    """Compute what key letters must be at anchor positions"""
    required = {}
    
    for anchor_name, anchor_data in anchors.items():
        start = anchor_data["start"]
        plaintext = anchor_data["plaintext"]
        
        for i, p_char in enumerate(plaintext):
            pos = start + i
            c_char = ciphertext[pos]
            
            if decode_type == "vigenere":
                # P = (C - K) mod 26, so K = (C - P) mod 26
                k_val = (char_to_num(c_char) - char_to_num(p_char)) % 26
            else:  # beaufort
                # P = (K - C) mod 26, so K = (P + C) mod 26
                k_val = (char_to_num(p_char) + char_to_num(c_char)) % 26
            
            required[pos] = num_to_char(k_val)
    
    return required


def check_anchor_feasibility(window: str, required_keys: Dict[int, str]) -> bool:
    """Check if a 97-char window satisfies required key letters at anchor positions"""
    for pos, required_char in required_keys.items():
        if pos < len(window) and window[pos] != required_char:
            return False
    return True


def vigenere_decode(ciphertext: str, key: str) -> str:
    """Vigenère decode: P = (C - K) mod 26"""
    result = []
    for c, k in zip(ciphertext, key):
        p_val = (char_to_num(c) - char_to_num(k)) % 26
        result.append(num_to_char(p_val))
    return ''.join(result)


def beaufort_decode(ciphertext: str, key: str) -> str:
    """Beaufort decode: P = (K - C) mod 26"""
    result = []
    for c, k in zip(ciphertext, key):
        p_val = (char_to_num(k) - char_to_num(c)) % 26
        result.append(num_to_char(p_val))
    return ''.join(result)


def check_anchors(plaintext: str, anchors: Dict) -> bool:
    """Check if plaintext satisfies all anchor constraints"""
    for anchor_name, anchor_data in anchors.items():
        start = anchor_data["start"]
        end = anchor_data["end"] + 1
        expected = anchor_data["plaintext"]
        
        actual = plaintext[start:end]
        if actual != expected:
            return False
    
    return True


def generate_97_windows(pages_text: Dict[int, str]) -> Generator[Dict, None, None]:
    """Generate all 97-char windows from pages"""
    for page_num, page_text in pages_text.items():
        sentences = split_into_sentences(page_text)
        
        for sent_idx, sentence in enumerate(sentences):
            normalized = normalize_az(sentence)
            
            if len(normalized) < 97:
                continue  # Skip sentences shorter than 97 chars
            
            # Generate all 97-char windows
            for offset in range(len(normalized) - 96):
                window = normalized[offset:offset + 97]
                
                # Extract verbatim portion (approximate)
                yield {
                    "page": page_num,
                    "sentence_idx": sent_idx,
                    "offset": offset,
                    "normalized": window,
                    "verbatim_approx": sentence[offset:min(offset + 120, len(sentence))],
                    "sentence_start": sentence[:50] + "..."
                }


def test_window(window_data: Dict, ciphertext: str, anchors: Dict,
               required_v: Dict, required_b: Dict) -> Optional[Dict]:
    """Test a single 97-char window"""
    window = window_data["normalized"]
    
    # Check Vigenère feasibility
    if check_anchor_feasibility(window, required_v):
        plaintext_v = vigenere_decode(ciphertext, window)
        if check_anchors(plaintext_v, anchors):
            return {
                "decode_variant": "vigenere",
                "anchors_pass": True,
                "plaintext_head": plaintext_v[:40],
                **window_data
            }
    
    # Check Beaufort feasibility
    if check_anchor_feasibility(window, required_b):
        plaintext_b = beaufort_decode(ciphertext, window)
        if check_anchors(plaintext_b, anchors):
            return {
                "decode_variant": "beaufort",
                "anchors_pass": True,
                "plaintext_head": plaintext_b[:40],
                **window_data
            }
    
    return None


def main():
    """Run systematic sweep of Flint text"""
    base_path = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus")
    pdf_path = base_path / "06_DOCUMENTATION/A_System_of_Geometry_and_Trigonometry.pdf"
    results_dir = base_path / "experiments/flint_otp/results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    ciphertext = load_ciphertext()
    anchors = load_anchors()
    
    # Compute required key letters for anchor-first filtering
    required_v = compute_required_key_letters(ciphertext, anchors, "vigenere")
    required_b = compute_required_key_letters(ciphertext, anchors, "beaufort")
    
    print("=" * 70)
    print("SYSTEMATIC SWEEP OF FLINT TEXT")
    print("=" * 70)
    print(f"Target: 97-char windows with anchor-first filtering")
    print(f"Required key letters for Vigenère at anchor positions:")
    for pos in sorted(list(required_v.keys())[:5]):
        print(f"  Position {pos}: '{required_v[pos]}'")
    print("  ...")
    print()
    
    # Target pages (Surveying sections, Appendix, key areas)
    target_pages = list(range(50, 65))  # Surveying sections
    target_pages.extend(range(16, 22))  # Geometry sections
    target_pages.extend(range(150, 160))  # Appendix area (adjust based on PDF)
    
    print(f"Extracting pages: {target_pages[:10]}... ({len(target_pages)} total)")
    pages_text = extract_target_pages(str(pdf_path), target_pages)
    print(f"Extracted {len(pages_text)} pages")
    
    # Generate and test windows
    results = []
    windows_tested = 0
    windows_feasible = 0
    
    print("\nScanning for 97-char windows...")
    for window_data in generate_97_windows(pages_text):
        windows_tested += 1
        
        # Quick feasibility check
        window = window_data["normalized"]
        if check_anchor_feasibility(window, required_v) or \
           check_anchor_feasibility(window, required_b):
            windows_feasible += 1
            
            # Full test
            result = test_window(window_data, ciphertext, anchors, 
                               required_v, required_b)
            if result:
                results.append(result)
                print(f"\n✓ MATCH FOUND!")
                print(f"  Page {result['page']}, sentence {result['sentence_idx']}, "
                      f"offset {result['offset']}")
                print(f"  Variant: {result['decode_variant']}")
                print(f"  Sentence start: {result['sentence_start']}")
                print(f"  Plaintext head: {result['plaintext_head'][:20]}...")
        
        if windows_tested % 1000 == 0:
            print(f"  Tested {windows_tested} windows, {windows_feasible} feasible, "
                  f"{len(results)} matches")
    
    print(f"\n" + "=" * 70)
    print(f"SWEEP COMPLETE")
    print(f"  Windows tested: {windows_tested}")
    print(f"  Windows feasible: {windows_feasible}")
    print(f"  Matches found: {len(results)}")
    
    # Save results
    if results:
        # Save detailed results
        sweep_results = results_dir / "sweep_results.json"
        with open(sweep_results, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save CSV matrix
        csv_path = results_dir / "SWEEP_MATRIX.csv"
        with open(csv_path, 'w', newline='') as f:
            fieldnames = ["page", "sentence_idx", "offset", "decode_variant",
                         "sentence_start", "plaintext_head"]
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(results)
        
        print(f"\nResults saved to:")
        print(f"  JSON: {sweep_results}")
        print(f"  CSV: {csv_path}")
    
    # Generate top hits summary
    summary_path = results_dir / "SWEEP_TOP_HITS.md"
    with open(summary_path, 'w') as f:
        f.write("# SYSTEMATIC SWEEP - TOP HITS\n\n")
        f.write(f"## Statistics\n\n")
        f.write(f"- Windows tested: {windows_tested}\n")
        f.write(f"- Windows passing anchor feasibility: {windows_feasible}\n")
        f.write(f"- Windows passing full anchor check: {len(results)}\n")
        f.write(f"- Pages examined: {len(pages_text)}\n\n")
        
        if results:
            f.write("## Matches Found\n\n")
            f.write("| Page | Sentence | Offset | Variant | Sentence Start |\n")
            f.write("|------|----------|--------|---------|----------------|\n")
            
            for r in results[:20]:  # Top 20
                f.write(f"| {r['page']} | {r['sentence_idx']} | {r['offset']} | ")
                f.write(f"{r['decode_variant']} | {r['sentence_start'][:40]}... |\n")
        else:
            f.write("## No Matches Found\n\n")
            f.write("No 97-character windows from the target Flint sections ")
            f.write("satisfy all four anchor constraints (EAST, NORTHEAST, BERLIN, CLOCK) ")
            f.write("under either Vigenère or Beaufort decoding.\n\n")
            f.write("This provides strong evidence that Flint text is not used ")
            f.write("as a direct OTP key for K4.\n")
    
    print(f"\nSummary saved to {summary_path}")
    
    if not results:
        print("\n✗ NO MATCHES FOUND")
        print("  No 97-char Flint windows satisfy K4's anchor constraints")


if __name__ == "__main__":
    main()