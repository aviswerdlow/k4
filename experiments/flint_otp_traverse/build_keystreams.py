#!/usr/bin/env python3
"""
Build keystream families from traverse table numeric data
Convert digit streams to 97-character A-Z keystreams using multiple mapping families
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple


MASTER_SEED = 1337  # For determinism


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


def walk_diagonal(table_json: Dict, kind: str = "main") -> str:
    """Walk table diagonally to extract digit stream"""
    if not table_json["cells"]:
        return ""
    
    result = []
    rows = table_json["cells"]
    num_rows = len(rows)
    num_cols = max(len(row) for row in rows) if rows else 0
    
    if kind == "main":
        # Main diagonal walk
        for d in range(num_rows + num_cols - 1):
            for i in range(max(0, d - num_cols + 1), min(d + 1, num_rows)):
                j = d - i
                if j < len(rows[i]):
                    result.append(digits_only(str(rows[i][j])))
    else:
        # Anti-diagonal walk
        for d in range(num_rows + num_cols - 1):
            for i in range(max(0, d - num_cols + 1), min(d + 1, num_rows)):
                j = num_cols - 1 - (d - i)
                if 0 <= j < len(rows[i]):
                    result.append(digits_only(str(rows[i][j])))
    
    return ''.join(result)


class KeystreamFamily:
    """Base class for keystream generation families"""
    
    def __init__(self, family_id: str):
        self.family_id = family_id
    
    def generate(self, digit_stream: str, params: Dict) -> List[int]:
        """Generate keystream from digit stream"""
        raise NotImplementedError
    
    def get_recipe_id(self, params: Dict) -> str:
        """Generate unique recipe ID"""
        param_str = json.dumps(params, sort_keys=True)
        return f"{self.family_id}_{hashlib.md5(param_str.encode()).hexdigest()[:8]}"


class F1_SingleDigitMod(KeystreamFamily):
    """Family F1: Single-digit modulo mapping"""
    
    def __init__(self):
        super().__init__("F1")
    
    def generate(self, digit_stream: str, params: Dict) -> List[int]:
        """Map each digit with optional offset"""
        offset = params.get("offset", 0)
        keystream = []
        
        for i in range(97):
            if i < len(digit_stream):
                d = int(digit_stream[i])
                k = (d + offset) % 26
            else:
                # Cycle from beginning if stream too short
                idx = i % len(digit_stream) if digit_stream else 0
                d = int(digit_stream[idx]) if digit_stream else 0
                k = (d + offset) % 26
            keystream.append(k)
        
        return keystream


class F2_DigitPairs(KeystreamFamily):
    """Family F2: 2-digit pair mapping"""
    
    def __init__(self):
        super().__init__("F2")
    
    def generate(self, digit_stream: str, params: Dict) -> List[int]:
        """Map digit pairs to keystream"""
        sliding = params.get("sliding", False)
        offset = params.get("offset", 0)
        keystream = []
        
        if sliding:
            # Overlapping pairs: (d0,d1), (d1,d2), ...
            for i in range(97):
                if i + 1 < len(digit_stream):
                    pair_val = int(digit_stream[i:i+2])
                else:
                    # Wrap around
                    idx1 = i % len(digit_stream) if digit_stream else 0
                    idx2 = (i + 1) % len(digit_stream) if digit_stream else 0
                    pair_val = int(digit_stream[idx1] + digit_stream[idx2]) if digit_stream else 0
                
                k = (pair_val + offset) % 26
                keystream.append(k)
        else:
            # Non-overlapping pairs: (d0,d1), (d2,d3), ...
            pos = 0
            for i in range(97):
                if pos + 1 < len(digit_stream):
                    pair_val = int(digit_stream[pos:pos+2])
                    pos += 2
                else:
                    # Wrap around
                    pos = pos % len(digit_stream) if digit_stream else 0
                    if pos + 1 < len(digit_stream):
                        pair_val = int(digit_stream[pos:pos+2])
                        pos += 2
                    else:
                        pair_val = int(digit_stream[pos] + digit_stream[0]) if digit_stream else 0
                        pos = 1
                
                k = (pair_val + offset) % 26
                keystream.append(k)
        
        return keystream


class F3_DigitTriples(KeystreamFamily):
    """Family F3: 3-digit triple mapping"""
    
    def __init__(self):
        super().__init__("F3")
    
    def generate(self, digit_stream: str, params: Dict) -> List[int]:
        """Map digit triples to keystream"""
        sliding = params.get("sliding", False)
        weight = params.get("weight", 1)
        keystream = []
        
        if sliding:
            # Overlapping triples
            for i in range(97):
                if i + 2 < len(digit_stream):
                    triple_val = int(digit_stream[i:i+3])
                else:
                    # Wrap around
                    chars = []
                    for j in range(3):
                        idx = (i + j) % len(digit_stream) if digit_stream else 0
                        chars.append(digit_stream[idx] if digit_stream else '0')
                    triple_val = int(''.join(chars))
                
                k = (triple_val * weight) % 26
                keystream.append(k)
        else:
            # Non-overlapping triples
            pos = 0
            for i in range(97):
                if pos + 2 < len(digit_stream):
                    triple_val = int(digit_stream[pos:pos+3])
                    pos += 3
                else:
                    # Wrap around
                    chars = []
                    for j in range(3):
                        idx = (pos + j) % len(digit_stream) if digit_stream else 0
                        chars.append(digit_stream[idx] if digit_stream else '0')
                    triple_val = int(''.join(chars))
                    pos = (pos + 3) % len(digit_stream) if digit_stream else 0
                
                k = (triple_val * weight) % 26
                keystream.append(k)
        
        return keystream


class F4_RowColSum(KeystreamFamily):
    """Family F4: Row/column sum-difference operations"""
    
    def __init__(self):
        super().__init__("F4")
    
    def generate(self, digit_stream: str, params: Dict) -> List[int]:
        """Use digit sums with position context"""
        operation = params.get("operation", "sum")  # sum, diff, product
        keystream = []
        
        for i in range(97):
            if i < len(digit_stream):
                # Sum digits in a window
                window_size = min(3, len(digit_stream) - i)
                window = digit_stream[i:i+window_size]
                
                if operation == "sum":
                    val = sum(int(d) for d in window)
                elif operation == "diff":
                    val = int(window[0]) - sum(int(d) for d in window[1:]) if len(window) > 1 else int(window[0])
                elif operation == "product":
                    val = 1
                    for d in window:
                        val = (val * int(d)) % 100  # Keep bounded
                else:
                    val = int(window[0])
                
                k = (val + i) % 26  # Add position for variation
            else:
                # Cycle
                idx = i % len(digit_stream) if digit_stream else 0
                k = (int(digit_stream[idx]) + i) % 26 if digit_stream else i % 26
            
            keystream.append(k)
        
        return keystream


class F5_HybridInterleave(KeystreamFamily):
    """Family F5: Hybrid interleave/alternate streams"""
    
    def __init__(self):
        super().__init__("F5")
    
    def generate(self, digit_stream: str, params: Dict) -> List[int]:
        """Interleave multiple extraction patterns"""
        # For this, we need the original table
        # We'll simulate by alternating processing
        pattern = params.get("pattern", "even_odd")
        keystream = []
        
        if pattern == "even_odd":
            # Even positions from one pattern, odd from another
            for i in range(97):
                if i % 2 == 0:
                    # Use digit directly
                    idx = (i // 2) % len(digit_stream) if digit_stream else 0
                    k = int(digit_stream[idx]) % 26 if digit_stream else 0
                else:
                    # Use digit pair mod
                    idx = (i // 2) % len(digit_stream) if digit_stream else 0
                    if idx + 1 < len(digit_stream):
                        k = int(digit_stream[idx:idx+2]) % 26
                    else:
                        k = int(digit_stream[idx]) % 26 if digit_stream else 0
                keystream.append(k)
        else:
            # Alternate chunks
            chunk_size = params.get("chunk_size", 10)
            for i in range(97):
                chunk_num = i // chunk_size
                if chunk_num % 2 == 0:
                    idx = i % len(digit_stream) if digit_stream else 0
                    k = int(digit_stream[idx]) % 26 if digit_stream else 0
                else:
                    idx = i % len(digit_stream) if digit_stream else 0
                    k = (int(digit_stream[idx]) * 2) % 26 if digit_stream else 0
                keystream.append(k)
        
        return keystream


class F6_PathBased(KeystreamFamily):
    """Family F6: Path-based extraction with diagonal walks"""
    
    def __init__(self):
        super().__init__("F6")
    
    def generate(self, digit_stream: str, params: Dict) -> List[int]:
        """Use special paths through the data"""
        path_type = params.get("path", "spiral")
        keystream = []
        
        if path_type == "spiral":
            # Simulate spiral reading
            for i in range(97):
                # Spiral pattern: skip every 3rd digit
                src_idx = i + (i // 3)
                idx = src_idx % len(digit_stream) if digit_stream else 0
                k = int(digit_stream[idx]) % 26 if digit_stream else 0
                keystream.append(k)
        elif path_type == "zigzag":
            # Zigzag pattern
            for i in range(97):
                if (i // 10) % 2 == 0:
                    idx = i % len(digit_stream) if digit_stream else 0
                else:
                    idx = (len(digit_stream) - 1 - i) % len(digit_stream) if digit_stream else 0
                k = int(digit_stream[idx]) % 26 if digit_stream else 0
                keystream.append(k)
        else:
            # Default linear
            for i in range(97):
                idx = i % len(digit_stream) if digit_stream else 0
                k = int(digit_stream[idx]) % 26 if digit_stream else 0
                keystream.append(k)
        
        return keystream


def generate_all_keystreams():
    """Generate keystreams from all tables using all families"""
    base_path = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus")
    tables_dir = base_path / "tables/parsed"
    keystreams_dir = base_path / "experiments/flint_otp_traverse/keystreams"
    keystreams_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize families
    families = [
        F1_SingleDigitMod(),
        F2_DigitPairs(),
        F3_DigitTriples(),
        F4_RowColSum(),
        F5_HybridInterleave(),
        F6_PathBased()
    ]
    
    print("Generating keystreams from traverse tables...")
    print("=" * 60)
    
    # Load all tables
    table_files = list(tables_dir.glob("TRAVERSE_*.json"))
    
    if not table_files:
        print("No traverse tables found! Run extraction first.")
        return
    
    total_keystreams = 0
    
    for table_file in table_files:
        with open(table_file) as f:
            table = json.load(f)
        
        table_id = table["table_id"]
        print(f"\nProcessing {table_id} (Page {table['page']})")
        
        # Create table-specific directory
        table_dir = keystreams_dir / table_id
        table_dir.mkdir(exist_ok=True)
        
        # Generate digit streams
        streams = {
            "row_major": flatten_row_major(table),
            "col_major": flatten_col_major(table),
            "diagonal_main": walk_diagonal(table, "main"),
            "diagonal_anti": walk_diagonal(table, "anti")
        }
        
        for stream_name, digit_stream in streams.items():
            if not digit_stream:
                continue
                
            print(f"  Stream: {stream_name} ({len(digit_stream)} digits)")
            
            # Apply each family
            for family in families:
                # Generate parameter variations
                param_sets = []
                
                if family.family_id == "F1":
                    # Single digit with different offsets
                    for offset in [0, 5, 10, 13, 17]:
                        param_sets.append({"offset": offset})
                        
                elif family.family_id == "F2":
                    # Digit pairs, sliding and non-sliding
                    for sliding in [False, True]:
                        for offset in [0, 7, 13]:
                            param_sets.append({"sliding": sliding, "offset": offset})
                            
                elif family.family_id == "F3":
                    # Digit triples with weights
                    for sliding in [False, True]:
                        for weight in [1, 2, 3]:
                            param_sets.append({"sliding": sliding, "weight": weight})
                            
                elif family.family_id == "F4":
                    # Row/col operations
                    for op in ["sum", "diff", "product"]:
                        param_sets.append({"operation": op})
                        
                elif family.family_id == "F5":
                    # Hybrid patterns
                    param_sets.append({"pattern": "even_odd"})
                    param_sets.append({"pattern": "chunks", "chunk_size": 10})
                    
                elif family.family_id == "F6":
                    # Path-based
                    for path in ["spiral", "zigzag", "linear"]:
                        param_sets.append({"path": path})
                
                # Generate keystreams with each parameter set
                for params in param_sets:
                    keystream = family.generate(digit_stream, params)
                    recipe_id = family.get_recipe_id(params)
                    
                    # Create keystream record
                    keystream_data = {
                        "recipe_id": f"{table_id}_{stream_name}_{recipe_id}",
                        "kstream": keystream,
                        "provenance": {
                            "table_id": table_id,
                            "page": table["page"],
                            "path": stream_name,
                            "family": family.family_id,
                            "params": params
                        },
                        "sample_first_20": {
                            "integers": keystream[:20],
                            "letters": ''.join(chr(k + ord('A')) for k in keystream[:20])
                        }
                    }
                    
                    # Save keystream
                    output_file = table_dir / f"{stream_name}_{recipe_id}.json"
                    with open(output_file, 'w') as f:
                        json.dump(keystream_data, f, indent=2)
                    
                    total_keystreams += 1
    
    print(f"\n" + "=" * 60)
    print(f"Keystream generation complete!")
    print(f"  Total keystreams: {total_keystreams}")
    print(f"  Output: experiments/flint_otp_traverse/keystreams/")
    
    # Create summary
    summary = {
        "tables_processed": len(table_files),
        "total_keystreams": total_keystreams,
        "families_used": [f.family_id for f in families],
        "streams_per_table": list(streams.keys())
    }
    
    with open(keystreams_dir / "summary.json", 'w') as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    generate_all_keystreams()