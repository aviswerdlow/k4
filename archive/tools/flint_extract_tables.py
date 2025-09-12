#!/usr/bin/env python3
"""
Extract traverse tables from Flint PDF
Focus on numeric tables near the end of the book
Preserve verbatim structure and page references
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTTextBox


def extract_page_text(pdf_path: str, page_num: int) -> str:
    """Extract text from a specific page"""
    for i, page in enumerate(extract_pages(pdf_path), 1):
        if i == page_num:
            text = ""
            for element in page:
                if isinstance(element, LTTextContainer):
                    text += element.get_text()
            return text
    return ""


def detect_table_structure(text: str) -> bool:
    """Detect if text contains tabular numeric data"""
    lines = text.split('\n')
    
    # Look for patterns suggesting tables
    numeric_lines = 0
    for line in lines:
        # Count lines with multiple numeric values
        numbers = re.findall(r'\d+', line)
        if len(numbers) >= 3:  # At least 3 numbers per line suggests table
            numeric_lines += 1
    
    # If >30% of lines are numeric, likely a table
    return numeric_lines > len(lines) * 0.3


def parse_table_page(text: str, page_num: int) -> Optional[Dict]:
    """Parse a page containing traverse tables"""
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    # Try to identify table structure
    table_data = {
        "page": page_num,
        "table_id": f"TRAVERSE_{page_num}",
        "headers": {},
        "row_labels": [],
        "col_labels": [],
        "cells": [],
        "verbatim_block": text[:2000]  # First 2000 chars for reference
    }
    
    # Look for header patterns (degrees, minutes, etc.)
    header_found = False
    data_start = 0
    
    for i, line in enumerate(lines):
        # Check for degree/minute headers
        if re.search(r'(degrees?|minutes?|lat|dep|bearing)', line, re.I):
            header_found = True
            # Try to extract column headers
            numbers = re.findall(r'\d+', line)
            if numbers:
                table_data["col_labels"] = numbers[:10]  # Max 10 columns
            data_start = i + 1
            break
    
    if not header_found:
        # Try to detect numeric table without explicit headers
        for i, line in enumerate(lines):
            numbers = re.findall(r'\d+', line)
            if len(numbers) >= 5:  # Row with many numbers
                data_start = i
                # Use position indices as column labels
                table_data["col_labels"] = [str(j) for j in range(len(numbers))]
                break
    
    # Parse data rows
    for line in lines[data_start:]:
        # Extract all numbers from the line
        numbers = re.findall(r'\d+', line)
        
        if len(numbers) >= 2:  # Valid data row
            # First number might be row label (degree value)
            if len(numbers) > len(table_data["col_labels"]):
                table_data["row_labels"].append(numbers[0])
                table_data["cells"].append(numbers[1:])
            else:
                table_data["cells"].append(numbers)
    
    # Only return if we found substantial data
    if len(table_data["cells"]) >= 5:
        return table_data
    
    return None


def digits_only(s: str) -> str:
    """Keep only digits 0-9"""
    return ''.join(c for c in s if c.isdigit())


def flatten_row_major(table_json: Dict) -> str:
    """Flatten table cells row-major into digit stream"""
    result = []
    for row in table_json["cells"]:
        for cell in row:
            result.append(digits_only(str(cell)))
    return ''.join(result)


def flatten_col_major(table_json: Dict) -> str:
    """Flatten table cells column-major into digit stream"""
    if not table_json["cells"]:
        return ""
    
    result = []
    num_cols = max(len(row) for row in table_json["cells"])
    
    for col_idx in range(num_cols):
        for row in table_json["cells"]:
            if col_idx < len(row):
                result.append(digits_only(str(row[col_idx])))
    
    return ''.join(result)


def walk_diagonal(table_json: Dict, kind: str = "main", wrap: bool = True) -> str:
    """Walk table diagonally to extract digit stream"""
    if not table_json["cells"]:
        return ""
    
    result = []
    rows = table_json["cells"]
    num_rows = len(rows)
    num_cols = max(len(row) for row in rows)
    
    if kind == "main":
        # Main diagonal (top-left to bottom-right)
        for start_col in range(num_cols):
            r, c = 0, start_col
            while r < num_rows and (c < num_cols or wrap):
                if wrap:
                    c = c % num_cols
                if c < len(rows[r]):
                    result.append(digits_only(str(rows[r][c])))
                r += 1
                c += 1
                if not wrap and c >= num_cols:
                    break
                    
        # Continue with diagonals starting from left edge
        for start_row in range(1, num_rows):
            r, c = start_row, 0
            while r < num_rows and (c < num_cols or wrap):
                if wrap:
                    c = c % num_cols
                if c < len(rows[r]):
                    result.append(digits_only(str(rows[r][c])))
                r += 1
                c += 1
                if not wrap and c >= num_cols:
                    break
    
    else:  # anti-diagonal
        # Anti-diagonal (top-right to bottom-left)
        for start_col in range(num_cols - 1, -1, -1):
            r, c = 0, start_col
            while r < num_rows and c >= 0:
                if c < len(rows[r]):
                    result.append(digits_only(str(rows[r][c])))
                r += 1
                c -= 1
                
        # Continue with diagonals starting from left edge
        for start_row in range(1, num_rows):
            r, c = start_row, num_cols - 1
            while r < num_rows and c >= 0:
                if c < len(rows[r]):
                    result.append(digits_only(str(rows[r][c])))
                r += 1
                c -= 1
    
    return ''.join(result)


def extract_traverse_tables():
    """Main extraction function"""
    base_path = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus")
    pdf_path = base_path / "06_DOCUMENTATION/A_System_of_Geometry_and_Trigonometry.pdf"
    
    # Create output directories
    tables_dir = base_path / "tables"
    parsed_dir = tables_dir / "parsed"
    parsed_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Extracting traverse tables from Flint PDF...")
    print(f"Scanning last 50 pages for numeric tables...")
    
    # Target pages - focus on the last portion of the book
    # Flint's book has ~183 pages, traverse tables typically near end
    target_pages = list(range(134, 184))  # Last 50 pages
    
    extracted_tables = []
    
    for page_num in target_pages:
        if page_num % 10 == 0:
            print(f"  Scanning page {page_num}...")
        
        text = extract_page_text(str(pdf_path), page_num)
        
        # Check if this page has table-like structure
        if detect_table_structure(text):
            print(f"  Found potential table on page {page_num}")
            
            table_data = parse_table_page(text, page_num)
            if table_data:
                # Save parsed table
                output_file = parsed_dir / f"TRAVERSE_{page_num}.json"
                with open(output_file, 'w') as f:
                    json.dump(table_data, f, indent=2)
                
                # Generate flattened versions
                row_major = flatten_row_major(table_data)
                col_major = flatten_col_major(table_data)
                diag_main = walk_diagonal(table_data, "main", wrap=True)
                
                # Add metadata
                table_data["digit_streams"] = {
                    "row_major": row_major[:100] + "..." if len(row_major) > 100 else row_major,
                    "col_major": col_major[:100] + "..." if len(col_major) > 100 else col_major,
                    "diagonal_main": diag_main[:100] + "..." if len(diag_main) > 100 else diag_main,
                    "total_digits": len(row_major)
                }
                
                extracted_tables.append({
                    "page": page_num,
                    "table_id": table_data["table_id"],
                    "rows": len(table_data["cells"]),
                    "cols": len(table_data["col_labels"]),
                    "total_cells": sum(len(row) for row in table_data["cells"]),
                    "digit_count": len(row_major)
                })
                
                print(f"    Extracted: {len(table_data['cells'])} rows, "
                      f"{len(row_major)} digits")
    
    # Create page index
    page_index = {
        "source": "A_System_of_Geometry_and_Trigonometry.pdf",
        "tables_found": len(extracted_tables),
        "pages_scanned": len(target_pages),
        "tables": extracted_tables
    }
    
    with open(tables_dir / "page_index.json", 'w') as f:
        json.dump(page_index, f, indent=2)
    
    # Create summary markdown
    with open(parsed_dir / "INDEX.md", 'w') as f:
        f.write("# Extracted Traverse Tables\n\n")
        f.write(f"Source: Flint's A System of Geometry and Trigonometry\n")
        f.write(f"Pages scanned: {target_pages[0]}-{target_pages[-1]}\n")
        f.write(f"Tables found: {len(extracted_tables)}\n\n")
        
        f.write("## Table Summary\n\n")
        f.write("| Page | Table ID | Rows | Cols | Total Cells | Digits |\n")
        f.write("|------|----------|------|------|-------------|--------|\n")
        
        for table in extracted_tables:
            f.write(f"| {table['page']} | {table['table_id']} | ")
            f.write(f"{table['rows']} | {table['cols']} | ")
            f.write(f"{table['total_cells']} | {table['digit_count']} |\n")
        
        if extracted_tables:
            f.write("\n## Sample Digit Streams\n\n")
            # Show first table's streams as example
            first_table_file = parsed_dir / f"TRAVERSE_{extracted_tables[0]['page']}.json"
            with open(first_table_file) as tf:
                first_table = json.load(tf)
                row_major = flatten_row_major(first_table)
                f.write(f"### Table {first_table['table_id']} (Page {first_table['page']})\n\n")
                f.write(f"**Row-major (first 100 digits):**\n")
                f.write(f"`{row_major[:100]}`\n\n")
    
    print(f"\nExtraction complete!")
    print(f"  Tables found: {len(extracted_tables)}")
    print(f"  Output: tables/parsed/")
    print(f"  Index: tables/page_index.json")
    print(f"  Summary: tables/parsed/INDEX.md")


if __name__ == "__main__":
    extract_traverse_tables()