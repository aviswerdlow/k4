#!/usr/bin/env python3
"""Validate JSON bundle files against schemas."""

import argparse
import json
from pathlib import Path

from jsonschema import ValidationError, validate

REQUIRED_FILES = [
    "coverage_report.json",
    "phrase_gate_report.json",
    "holm_report_canonical.json",
    "hashes.txt",
]


def load_schemas(schema_dir: Path):
    schemas = {}
    for path in schema_dir.glob("*.json"):
        with open(path, "r", encoding="utf-8") as f:
            schemas[path.stem] = json.load(f)
    return schemas


def match_schema(file_name: str, schemas):
    for name in schemas:
        if file_name.startswith(name):
            return schemas[name]
    return None


def check_no_padding(bundle: Path) -> tuple[bool, list[str]]:
    """Check that published bundles don't contain padding sentinels."""
    errors = []
    
    # Check readable_canonical.txt for padding sentinels
    readable_path = bundle / "readable_canonical.txt"
    if readable_path.exists():
        with open(readable_path, 'r') as f:
            content = f.read()
            if "XXXX" in content or "YYYYYYY" in content:
                errors.append(f"Padding tokens found in {readable_path}. Published bundles must use lexicon fillers.")
    
    # Check plaintext_97.txt
    pt_path = bundle / "plaintext_97.txt"
    if pt_path.exists():
        with open(pt_path, 'r') as f:
            content = f.read()
            if "XXXX" in content or "YYYYYYY" in content:
                errors.append(f"Padding tokens found in {pt_path}. Published bundles must use lexicon fillers.")
    
    return len(errors) == 0, errors

def validate_bundle(
    bundle: Path,
    schema_dir: Path,
    mode: str = "strict",
) -> bool:
    schemas = load_schemas(schema_dir)
    ok = True
    errors = []
    
    # Check for padding sentinels in strict mode for published bundles
    if mode == "strict" and "01_PUBLISHED" in str(bundle):
        no_padding, padding_errors = check_no_padding(bundle)
        if not no_padding:
            ok = False
            errors.extend(padding_errors)
    
    for json_path in bundle.rglob("*.json"):
        schema = match_schema(json_path.name, schemas)
        if schema is None:
            print(f"{json_path}: no matching schema; skipped")
            continue
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            validate(instance=data, schema=schema)
            print(f"{json_path}: ok")
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"{json_path}: {e}")
            if mode == "strict":
                ok = False
                errors.append(f"{json_path}: {e}")
    if mode == "strict":
        cand_dirs = list(bundle.glob("cand_*"))
        if cand_dirs:
            summary = list(bundle.glob("uniqueness_confirm_summary*.json"))
            if not summary:
                ok = False
                errors.append("missing uniqueness summary")
            for cand_dir in cand_dirs:
                for name in REQUIRED_FILES:
                    if not (cand_dir / name).exists():
                        ok = False
                        errors.append(f"missing {cand_dir / name}")
    if errors:
        print("Validation errors:")
        for e in errors:
            print(f" - {e}")
    return ok


def main():
    parser = argparse.ArgumentParser(description="Validate bundle JSON files")
    parser.add_argument("bundle", type=Path, help="Path to bundle directory")
    parser.add_argument("--schema", type=Path, default=Path("scripts/schema"))
    parser.add_argument(
        "--mode",
        choices=["strict", "lenient"],
        default="strict",
    )
    args = parser.parse_args()
    success = validate_bundle(
        bundle=args.bundle,
        schema_dir=args.schema,
        mode=args.mode,
    )
    raise SystemExit(0 if success else 1)


if __name__ == "__main__":
    main()
