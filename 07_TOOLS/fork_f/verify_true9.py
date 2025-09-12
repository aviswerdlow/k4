#!/usr/bin/env python3
"""
Verify TRUE@9 L=11 p=0 which shows 26 gains
"""

MASTER_SEED = 1337

# Load ciphertext
with open('../../02_DATA/ciphertext_97.txt', 'r') as f:
    ciphertext = f.read().strip()

# Known anchors
anchors = {
    21: 'E', 22: 'A', 23: 'S', 24: 'T',
    25: 'N', 26: 'O', 27: 'R', 28: 'T',
    29: 'H', 30: 'E', 31: 'A', 32: 'S', 33: 'T',
    63: 'B', 64: 'E', 65: 'R', 66: 'L', 67: 'I', 68: 'N',
    69: 'C', 70: 'L', 71: 'O', 72: 'C', 73: 'K'
}

token = "TRUE"
start = 9
L = 11
phase = 0

print(f"Testing {token}@{start} L={L} p={phase}")
print(f"Ciphertext: {ciphertext[start:start+4]}")

# Check each position
def compute_class(i):
    return ((i % 2) * 3) + (i % 3)

for i, char in enumerate(token):
    pos = start + i
    ct = ciphertext[pos]
    pt = char
    cls = compute_class(pos)
    slot = (pos - phase) % L
    print(f"  Pos {pos}: CT={ct} PT={pt} Class={cls} Slot={slot}")
    
    # Check if this is an anchor
    if pos in anchors:
        if anchors[pos] == pt:
            print(f"    Matches anchor {anchors[pos]}")
        else:
            print(f"    CONFLICTS with anchor {anchors[pos]}")