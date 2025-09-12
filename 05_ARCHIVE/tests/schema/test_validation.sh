#!/usr/bin/env bash
set -e
python scripts/tools/validate_bundle.py tests/fixtures/schema/valid --schema scripts/schema
if python scripts/tools/validate_bundle.py tests/fixtures/schema/invalid --schema scripts/schema; then
  echo "Invalid fixtures unexpectedly passed" >&2
  exit 1
fi
echo "Fixture tests complete"
