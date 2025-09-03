import csv
import json
from pathlib import Path

def assert_upper_97(pt: str):
    if len(pt) != 97:
        raise AssertionError(f"Plaintext must be 97 chars, got {len(pt)}")
    if any(c < 'A' or c > 'Z' for c in pt):
        raise AssertionError("Plaintext must be A..Z only")

def _read_anchors_csv(path: str):
    with open(path, newline="", encoding="utf-8") as f:
        return [(row["token"], int(row["start"]), int(row["end"])) for row in csv.DictReader(f)]

def assert_anchors(pt: str, anchors_csv: str):
    for token, s, e in _read_anchors_csv(anchors_csv):
        span = pt[s:e+1]
        if span != token:
            raise AssertionError(f"Anchor {token} not at [{s},{e}] (found '{span}')")

def assert_head_lock(pt: str):
    if len(pt) < 75:
        raise AssertionError("Head lock [0,74] check failed: PT too short")

def assert_seam_guard(pt: str, seam_json: str):
    guard = json.loads(Path(seam_json).read_text(encoding="utf-8"))
    h0, h1 = guard["hejoy"]
    if pt[h0:h1+1] != "HEJOY":
        raise AssertionError(f"HEJOY must be at [{h0},{h1}]")
    s0, s1 = guard["seam"]["range"]
    expected_letters = guard["seam"].get("letters", None)
    if expected_letters and pt[s0:s1+1] != expected_letters:
        raise AssertionError(f"Seam letters mismatch at [{s0},{s1}]")
    for cut in guard["seam"]["cuts"]:
        if not (s0 <= cut <= s1):
            raise AssertionError(f"Cut {cut} lies outside seam range")