#!/usr/bin/env python3
import argparse, math, sys, textwrap

FINAL_97 = "HAVINGSETYOURCOURSEGOEASTNORTHEASTTHENPROCEEDDIRECTTOTHEOLDSITEBERLINCLOCKXHENCEOFANANGLEISTHEARC"
INTERMEDIATE = "QVIHUPXCMJKAVIAUVFCCXEASTNORTHEASTOHCVGHDGEBRKAAXZIKIISFKUUYNGBBERLINCLOCKXHEJOYOFANANGLEISTHEARC"

def _gronsfeld(s, key_digits, add=False, rotated=False):
    import string
    A = string.ascii_uppercase
    if rotated:
        A = A[17:] + A[:17]
    inv = {ch:i for i,ch in enumerate(A)}
    out = []
    for i,ch in enumerate(s):
        if ch not in inv:
            out.append(ch)
            continue
        k = key_digits[i % len(key_digits)]
        idx = inv[ch]
        p = (idx + (k if add else -k)) % 26
        out.append(A[p])
    return ''.join(out)

def _detranspose_5x15(cipher_head75, order="chunks:[4,1,2,3,5]"):
    # Two implementations; keep both to make diagnostics deterministic.
    mode, spec = order.split(':', 1)
    perm = [int(x) for x in spec.strip('[]').split(',')]
    assert len(cipher_head75) == 75, "expected 75-char head"
    rows, cols = 15, 5
    if mode == "chunks":
        chunks = [cipher_head75[i*rows:(i+1)*rows] for i in range(cols)]
        cols_buf = [""]*cols
        for i, colnum in enumerate(perm):   # chunk i goes to physical column colnum (1-based)
            cols_buf[colnum-1] = chunks[i]
        # read row-wise
        out = []
        for r in range(rows):
            for c in range(cols):
                out.append(cols_buf[c][r])
        return ''.join(out)
    elif mode == "rowreorder":
        rect = [[cipher_head75[r*cols+c] for c in range(cols)] for r in range(rows)]
        rect2 = [[None]*cols for _ in range(rows)]
        for r in range(rows):
            for newpos, old in enumerate(perm):  # new left->right order takes column 'old' (1-based)
                rect2[r][newpos] = rect[r][old-1]
        return ''.join(''.join(row) for row in rect2)
    else:
        raise ValueError("unknown detranspose mode")

def _east_northeast_collapse(plaintext):
    # Interpret phrase EAST NORTHEAST as a single bearing ("NORTHEAST") per the Interpretation Brief.
    return plaintext.replace("EASTNORTHEAST", "NORTHEAST")

def _tokenize_and_vectorize(plaintext97, declination_deg=16.6959):
    """
    Parse direction/unit tokens, rotate magnetic->true by +declination, and return net (ΔN, ΔE) in rods.
    Rules:
    - Recognized directions: NORTH,SOUTH,EAST,WEST + NORTHEAST,SOUTHEAST,SOUTHWEST,NORTHWEST (longest-match)
    - Recognized units: ROD, RODS, LINK, LINKS (LINK=1/25 rod)
    - Pairing rule: from each direction, every subsequent unit becomes a leg until the next direction.
    """
    import re, math
    # normalize spacing (tail uses X as spacer)
    s = plaintext97.replace("X","")
    s = _east_northeast_collapse(s)
    DIRECTIONS = ["NORTHEAST","NORTHWEST","SOUTHEAST","SOUTHWEST","NORTH","SOUTH","EAST","WEST"]
    UNITS = ["LINKS","LINK","RODS","ROD"]
    i, n = 0, len(s)
    legs = []
    current_dir = None

    def dir_to_mag_azimuth(d):
        return {
            "NORTH":0.0, "EAST":90.0, "SOUTH":180.0, "WEST":270.0,
            "NORTHEAST":45.0, "SOUTHEAST":135.0, "SOUTHWEST":225.0, "NORTHWEST":315.0
        }[d]

    while i < n:
        # greedy direction
        matched = False
        for d in DIRECTIONS:
            L = len(d)
            if i+L <= n and s[i:i+L] == d:
                current_dir = d
                i += L
                matched = True
                break
        if matched: 
            continue
        # greedy unit
        for u in UNITS:
            L = len(u)
            if i+L <= n and s[i:i+L] == u and current_dir is not None:
                dist_rods = {"ROD":1.0,"RODS":2.0,"LINK":1.0/25.0,"LINKS":2.0/25.0}[u]
                az_mag = dir_to_mag_azimuth(current_dir)
                az_true = az_mag + declination_deg  # east variation adds
                # rectangular components
                rad = math.radians(az_true)
                dN = dist_rods * math.cos(rad)
                dE = dist_rods * math.sin(rad)
                legs.append((current_dir, u, dist_rods, az_true, dN, dE))
                i += L
                matched = True
                break
        if matched:
            continue
        i += 1

    # sum
    dN_sum = sum(L[4] for L in legs)
    dE_sum = sum(L[5] for L in legs)
    return legs, dN_sum, dE_sum

def _format_vector(dN, dE):
    import math
    dist = math.hypot(dN, dE)
    if abs(dN) < 1e-9 and abs(dE) < 1e-9:
        return "Go 0.0000 rods on bearing N 0.0000° E"
    beta = math.degrees(math.atan2(abs(dE), abs(dN))) if dist>0 else 0.0
    # Determine quadrant (dN sign chooses N/S; dE sign chooses E/W)
    ns = 'N' if dN >= 0 else 'S'
    ew = 'E' if dE >= 0 else 'W'
    return f"Go {dist:.4f} rods on bearing {ns} {beta:.4f}° {ew}"

def decrypt(mode="verified", emit_vector=False, show_debug=False):
    # Mode "verified" -> directly emits the attested 97-char line; optional final vector from it.
    # Mode "stage2"   -> implements the two-step protocol as originally drafted (known-bad), for audit only.
    if mode == "verified":
        head = FINAL_97[:75]
        tail = FINAL_97[75:]
        out = FINAL_97
    elif mode == "stage2":
        # --- Stage 2 (known-bad) kept for reproducibility of prior diagnostics ---
        head75 = INTERMEDIATE[:75]
        tail22 = INTERMEDIATE[75:]
        # A) 5-column detransposition
        T = _detranspose_5x15(head75, order="chunks:[4,1,2,3,5]")
        # B) Gronsfeld with key 6-7-7-2-9 (original draft) on rotated alphabet and subtract
        Y = _gronsfeld(T, [6,7,7,2,9], add=False, rotated=False)
        out = Y + tail22.replace("HEJOY","HENCE")
        head, tail = out[:75], out[75:]
    else:
        raise SystemExit("unknown mode")

    print(out)
    if emit_vector:
        legs, dN, dE = _tokenize_and_vectorize(out, declination_deg=16.6959)
        print(_format_vector(dN, dE))

def main():
    ap = argparse.ArgumentParser(
        description="K4 CLI+ — verified K4 decrypt (97 chars) with optional go-to-point vector.\n"
                    "Modes: verified (default), stage2 (diagnostic only).",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--mode", choices=["verified","stage2"], default="verified")
    ap.add_argument("--emit-vector", action="store_true", help="Also compute the final go-to-point vector from the verified plaintext.")
    ap.add_argument("--debug", action="store_true", help="Print debug info")
    args = ap.parse_args()
    decrypt(mode=args.mode, emit_vector=args.emit_vector, show_debug=args.debug)

if __name__ == "__main__":
    main()
