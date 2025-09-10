#!/usr/bin/env python3
"""Merge the 4 ALGEBRA_CORE pages into a single PDF"""

from PyPDF2 import PdfMerger
import os

def merge_algebra_pdfs():
    """Merge the 4 pages into ALGEBRA_CORE.pdf"""
    
    merger = PdfMerger()
    
    # Add pages in order
    pdf_files = [
        'ALGB_P1_24_of_97.pdf',
        'ALGB_P2_TAIL_P74.pdf', 
        'ALGB_P3_K3_HINTS.pdf',
        'ALGB_P4_NEXT_TESTS.pdf'
    ]
    
    for pdf in pdf_files:
        if os.path.exists(pdf):
            merger.append(pdf)
            print(f"Added {pdf}")
        else:
            print(f"Warning: {pdf} not found")
    
    # Write merged PDF
    merger.write('ALGEBRA_CORE.pdf')
    merger.close()
    
    print("\n✅ Created ALGEBRA_CORE.pdf (4 pages)")

if __name__ == "__main__":
    merge_algebra_pdfs()