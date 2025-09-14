"""
Programmatic builder for KRYPTOS tableau rows
Eliminates hard-coded strings and typos
"""

# Standard keyed tableau top row
TOP = "KRYPTOSABCDEFGHIJLMNQUVWXZ"  # 26 chars


def tableau_row(shift: int) -> str:
    """
    Generate a tableau row by rotating TOP left by shift positions

    Args:
        shift: Row index (0-25)

    Returns:
        26-char rotated alphabet
    """
    s = shift % 26
    return TOP[s:] + TOP[:s]


def row_window(start_letter: str, shift: int, width: int = 31) -> str:
    """
    Extract a window from a tableau row starting at a specific column

    Args:
        start_letter: Letter that defines the starting column in TOP
        shift: Row shift (determines which tableau row to use)
        width: Number of characters to extract (default 31)

    Returns:
        Window of specified width from the tableau
    """
    row = tableau_row(shift)
    # Start column = index of start_letter in TOP (not in row)
    start = TOP.index(start_letter)
    # Take a wraparound window of row beginning at that column
    out = []
    for i in range(width):
        out.append(row[(start + i) % 26])
    return ''.join(out)


def build_xor_keystream(row_x_shift=None, row_v_shift=None, row_t_shift=None,
                        reverse_v=True, phase=0):
    """
    Build the complete 93-char XOR keystream from tableau rows

    Args:
        row_x_shift: Shift for X row (default: position of X in TOP)
        row_v_shift: Shift for V row (default: position of V in TOP)
        row_t_shift: Shift for T row (default: position of T in TOP)
        reverse_v: Whether to reverse the V row (default: True)
        phase: Phase offset for the entire keystream (0-92)

    Returns:
        93-character keystream
    """
    # Default shifts based on letter positions in TOP
    if row_x_shift is None:
        row_x_shift = TOP.index('X')  # 23
    if row_v_shift is None:
        row_v_shift = TOP.index('V')  # 21
    if row_t_shift is None:
        row_t_shift = TOP.index('T')  # 19

    # Build the three 31-char segments
    row_x = row_window('X', row_x_shift, 31)  # Forward
    row_v = row_window('V', row_v_shift, 31)
    row_t = row_window('T', row_t_shift, 31)  # Forward

    # Apply V reversal if specified
    if reverse_v:
        row_v = row_v[::-1]

    # Combine into 93-char keystream
    keystream = row_x + row_v + row_t
    assert len(keystream) == 93, f"Keystream length {len(keystream)}, expected 93"

    # Apply phase shift if specified
    if phase > 0:
        phase = phase % 93
        keystream = keystream[phase:] + keystream[:phase]

    return keystream


def display_rows():
    """Display the default tableau rows for verification"""
    sx = TOP.index('X')
    sv = TOP.index('V')
    st = TOP.index('T')

    print("Default Tableau Rows (31 chars each):")
    print("=" * 60)
    print(f"Row X (shift {sx}): {row_window('X', sx, 31)}")
    print(f"Row V (shift {sv}): {row_window('V', sv, 31)}")
    print(f"Row T (shift {st}): {row_window('T', st, 31)}")
    print(f"\nRow V reversed: {row_window('V', sv, 31)[::-1]}")
    print("=" * 60)


if __name__ == "__main__":
    display_rows()

    # Test keystream building
    ks = build_xor_keystream()
    print(f"\nDefault keystream (V reversed, phase 0):")
    print(f"Length: {len(ks)}")
    print(f"First 31: {ks[:31]}")
    print(f"Next 31:  {ks[31:62]}")
    print(f"Last 31:  {ks[62:]}")