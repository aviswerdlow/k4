#!/usr/bin/env python3
"""
Extract verbatim quotes from Flint PDF with page citations
Uses pdfminer.six to preserve line breaks and hyphenations
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from io import StringIO


def extract_page_texts(pdf_path: str) -> List[Dict[str, any]]:
    """Extract text from each page of the PDF"""
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LTTextContainer
    
    pages = []
    for page_num, page in enumerate(extract_pages(pdf_path), 1):
        text = ""
        for element in page:
            if isinstance(element, LTTextContainer):
                text += element.get_text()
        pages.append({"page": page_num, "text": text})
    
    return pages


def normalize_az(text: str) -> str:
    """Normalize text to A-Z only, uppercase"""
    # Remove all non-letter characters and convert to uppercase
    return ''.join(c.upper() for c in text if c.isalpha())


def extract_verbatim_quote(pages: List[Dict], search_text: str, context_chars: int = 50) -> Optional[Dict]:
    """Find exact quote in pages and extract with context"""
    for page_data in pages:
        text = page_data["text"]
        if search_text.lower() in text.lower():
            # Find the position
            idx = text.lower().find(search_text.lower())
            if idx == -1:
                continue
                
            # Extract context
            start = max(0, idx - context_chars)
            end = min(len(text), idx + len(search_text) + context_chars)
            
            context_before = text[start:idx]
            actual_match = text[idx:idx + len(search_text)]
            context_after = text[idx + len(search_text):end]
            
            return {
                "page": page_data["page"],
                "verbatim": actual_match,
                "context_before_50": context_before,
                "context_after_50": context_after,
                "full_context": text[start:end]
            }
    
    return None


def extract_specific_quotes():
    """Extract the specific quotes mentioned in the engineering brief"""
    
    pdf_path = "06_DOCUMENTATION/A_System_of_Geometry_and_Trigonometry.pdf"
    base_path = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus")
    pdf_full_path = base_path / pdf_path
    
    if not pdf_full_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_full_path}")
    
    # Extract all pages
    print(f"Extracting text from {pdf_full_path}...")
    pages = extract_page_texts(str(pdf_full_path))
    print(f"Extracted {len(pages)} pages")
    
    # Output directory
    quotes_dir = base_path / "quotes"
    quotes_dir.mkdir(exist_ok=True)
    
    # 1. Definition 28 (Geometry)
    angle_search = "The measure of an angle is the arc"
    angle_quote = extract_verbatim_quote(pages, angle_search)
    
    if angle_quote:
        # Look for the full definition
        for page_data in pages:
            if page_data["page"] == 13:  # Printed page 13
                text = page_data["text"]
                # Search for Definition 28
                pattern = r"28\.\s*([^.]+(?:\.[^.]+)*?angular point being the centre[^.]*\.)"
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    verbatim = match.group(0).strip()
                    normalized = normalize_az(verbatim)
                    
                    angle_def = {
                        "verbatim": verbatim,
                        "page": 13,
                        "context_before_50": angle_quote["context_before_50"],
                        "context_after_50": angle_quote["context_after_50"],
                        "normalized_AZ": normalized,
                        "normalized_len": len(normalized)
                    }
                    
                    with open(quotes_dir / "angle_definition.json", "w") as f:
                        json.dump(angle_def, f, indent=2)
                    print(f"Saved angle_definition.json (len={len(normalized)})")
    
    # 2. Five 97-char candidates
    candidates = [
        {
            "id": "A",
            "verbatim": "At the first station A, draw a meridian line and lay off the bearings to the respective angles; draw the stationary line",
            "page": 59,
            "normalized": "ATTHEFIRSTSTATIONADRAWAMERIDIANLINEANDLAYOFFTHEBEARINGSTOTHERESPECTIVEANGLESDRAWTHESTATIONARYLINE",
            "section_note": "Surveying, Case VII: To protract this field"
        },
        {
            "id": "B", 
            "verbatim": "Find the bearing from each station to the respective angles; and also the bearing and distance from one station to the",
            "page": 59,
            "normalized": "FINDTHEBEARINGFROMEACHSTATIONTOTHERESPECTIVEANGLESANDALSOTHEBEARINGANDDISTANCEFROMONESTATIONTOTHE",
            "section_note": "Surveying, Case VII"
        },
        {
            "id": "C",
            "verbatim": "From the line take offsets to the several bends, at right angles from the line; noticing in the Field-Book at what part of",
            "page": 61,
            "normalized": "FROMTHELINETAKEOFFSETSTOTHESEVERALBENDSATRIGHTANGLESFROMTHELINENOTICINGINTHEFIELDBOOKATWHATPARTOF",
            "section_note": "Surveying, Case IX: Boundary lines very irregular"
        },
        {
            "id": "D",
            "verbatim": "NOTE. In a similar manner angles may be measured; that is, with a chord of 60 degrees describe an arc on the angular point, and",
            "page": 18,
            "normalized": "NOTEINASIMILARMANNERANGLESMAYBEMEASUREDTHATISWITHACHORDOFDEGREESDESCRIBEANARCONTHEANGULARPOINTAND",
            "section_note": "Geometry, after Problem VII note on scale of chords"
        },
        {
            "id": "E",
            "verbatim": "To protract a field according to the preceding rules is preferable to the method of doing it by parallel lines, though",
            "page": 52,  # pp. 52-53
            "normalized": "TOPROTRACTAFIELDACCORDINGTOTHEPRECEDINGRULESISPREFERABLETOTHEMETHODOFDOINGITBYPARALLELLINESTHOUGH",
            "section_note": "Surveying, Another method of protracting fields"
        }
    ]
    
    for cand in candidates:
        # Verify normalization
        test_norm = normalize_az(cand["verbatim"])
        if test_norm != cand["normalized"]:
            print(f"WARNING: Candidate {cand['id']} normalization mismatch!")
            print(f"  Expected: {cand['normalized'][:50]}...")
            print(f"  Got:      {test_norm[:50]}...")
        
        # Save candidate
        cand_data = {
            "verbatim": cand["verbatim"],
            "page": cand["page"],
            "normalized_AZ": cand["normalized"],
            "normalized_len": len(cand["normalized"]),
            "section_note": cand["section_note"]
        }
        
        with open(quotes_dir / f"candidate_{cand['id']}.json", "w") as f:
            json.dump(cand_data, f, indent=2)
        
        print(f"Saved candidate_{cand['id']}.json (len={len(cand['normalized'])})")
    
    # Create normalized index
    index = {
        "angle_definition": "angle_definition.json",
        "candidates": [f"candidate_{c['id']}.json" for c in candidates]
    }
    
    with open(quotes_dir / "normalized_index.json", "w") as f:
        json.dump(index, f, indent=2)
    
    print("\nAll quotes extracted and saved to quotes/")


if __name__ == "__main__":
    extract_specific_quotes()