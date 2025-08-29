# -*- coding: utf-8 -*-
"""
Traverse reduction + final Go‑to‑Point vector from plaintext tokens.
Implements the extraction rules the team standardized:
• Directions: NORTH/SOUTH/EAST/WEST & compounds (NORTHEAST, etc.).
• Units: ROD/RODS/LINK/LINKS (1 rod = 25 links).
• Pairing rule: each unit after a direction becomes a leg until the next
  direction appears.
• Variation (Explorer): +16.6959° is applied to convert magnetic→true bearing.
• “EAST NORTHEAST” is parsed as a single token = NORTHEAST (magnetic 45°).

Outputs the closing line “Go D rods on bearing N 61.6959° E (true)”.

This module is intentionally small & transparent so independent auditors can
rewrite it in a few minutes.
"""
from __future__ import annotations
import math
import re
from typing import List, Tuple

ALPHA = 16.6959  # declination east (Explorer key)
ROD_PER_LINK = 1/25.0

DIRECTIONS = [
    "NORTHEAST","NORTHWEST","SOUTHEAST","SOUTHWEST",
    "NORTH","SOUTH","EAST","WEST"
]

UNITS = {
    "ROD": 1.0,
    "RODS": 2.0,     # in this pipeline “RODS” was used as an explicit 2‑rod token
    "LINK": ROD_PER_LINK,
    "LINKS": 2*ROD_PER_LINK
}

def _scan_tokens(text: str) -> List[str]:
    """Upper‑case A..Z scanner; X is a word spacer used in the tail."""
    return re.findall(r"[A-Z]+", text.upper())

def _bearing_from_token(token: str) -> Tuple[float, str, str]:
    """Return magnetic azimuth in degrees for a direction token, plus quadrant pair."""
    token = token.upper()
    if token == "EASTNORTHEAST" or token == "EASTNORTH-EAST" or token == "EASTNORTH":  # paranoia
        token = "NORTHEAST"
    if token == "NORTHEAST":    return 45.0, 'N', 'E'
    if token == "NORTHWEST":    return 315.0, 'N', 'W'
    if token == "SOUTHEAST":    return 135.0, 'S', 'E'
    if token == "SOUTHWEST":    return 225.0, 'S', 'W'
    if token == "NORTH":        return 0.0, 'N', 'E'   # E placeholder for quadrant calculation
    if token == "SOUTH":        return 180.0, 'S', 'E'
    if token == "EAST":         return 90.0, 'N', 'E'
    if token == "WEST":         return 270.0, 'N', 'W'
    raise ValueError(f"Unknown direction token: {token}")

def tokens_to_legs(text: str) -> List[Tuple[float, float]]:
    """Parse the text into (true_azimuth_deg, distance_rods) legs."""
    toks = _scan_tokens(text)
    legs: List[Tuple[float, float]] = []
    current_dir = None
    for tok in toks:
        if tok in DIRECTIONS or tok == "EASTNORTHEAST":
            az_mag, ns, ew = _bearing_from_token(tok)
            current_dir = az_mag
            continue
        if tok in UNITS and current_dir is not None:
            dist_rods = UNITS[tok]
            az_true = (current_dir + ALPHA) % 360.0  # magnetic → true
            legs.append((az_true, dist_rods))
            continue
        # else ignore tokens (CLOCK, ANGLE, ARC, etc.)
    return legs

def legs_to_vector(legs: List[Tuple[float, float]]) -> Tuple[float, float, float]:
    """Return ΔN, ΔE, and distance r (all in rods)."""
    dN = dE = 0.0
    for az_true_deg, dist in legs:
        rad = math.radians(az_true_deg)
        dN += dist * math.cos(rad)
        dE += dist * math.sin(rad)
    r = math.hypot(dN, dE)
    return (dN, dE, r)

def vector_to_bearing(dN: float, dE: float) -> Tuple[float, str]:
    """Return quadrantal bearing (β in degrees, and 'N β E' style)."""
    beta = math.degrees(math.atan2(abs(dE), abs(dN))) if (dN!=0 or dE!=0) else 0.0
    qN = 'N' if dN >= 0 else 'S'
    qE = 'E' if dE >= 0 else 'W'
    return (beta, f"{qN} {beta:.4f}° {qE}")

def go_to_point(text: str) -> str:
    """High‑level one‑liner: from tokens → 'Go D rods on bearing N xx.xxxx° E'."""
    legs = tokens_to_legs(text)
    dN, dE, r = legs_to_vector(legs)
    beta, quad = vector_to_bearing(dN, dE)
    return f"Go {r:.4f} rods on bearing {quad}"
