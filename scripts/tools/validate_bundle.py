#!/usr/bin/env python3
"""Validate JSON bundle files against schemas."""

import argparse
import json
from pathlib import Path

from jsonschema import ValidationError, validate


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


def validate_bundle(bundle_dir: Path, schema_dir: Path) -> bool:
    schemas = load_schemas(schema_dir)
    ok = True
    for json_path in bundle_dir.rglob("*.json"):
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
            ok = False
    return ok


def main():
    parser = argparse.ArgumentParser(description="Validate bundle JSON files")
    parser.add_argument("bundle", type=Path, help="Path to bundle directory")
    parser.add_argument("--schema", type=Path, default=Path("scripts/schema"))
    args = parser.parse_args()

    success = validate_bundle(args.bundle, args.schema)
    raise SystemExit(0 if success else 1)


if __name__ == "__main__":
    main()
