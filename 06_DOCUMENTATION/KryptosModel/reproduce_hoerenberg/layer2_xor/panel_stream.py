"""
Panel stream generation for Hörenberg's K4 reproduction
Creates the linear scan of tableau rows with optional extra-L injection
"""

from tableau import tableau_row, TOP


def panel_stream(extra_L=False, min_len=10000):
    """
    Generate Hörenberg's panel stream (linear concatenation of tableau rows)

    Args:
        extra_L: If True, inject 'L' after each 26-char row (Hörenberg's variant)
        min_len: Minimum length of stream to generate

    Returns:
        Panel stream string of at least min_len characters
    """
    out = []

    # Concatenate tableau rows in order (0..25, 0..25, ...)
    for r in range(min_len // 26 + 2):
        row_idx = r % 26
        row = tableau_row(row_idx)
        out.append(row)

        if extra_L:
            # Hörenberg's "with L" variant - inject L after each row
            out.append('L')

    s = ''.join(out)
    return s[:min_len]


def get_m_alignment_index(extra_L=False):
    """
    Find the index in panel stream where the 'M' row alignment starts

    According to Hörenberg, the best IoC occurs when aligning to the M row.
    This finds where in the linear panel stream the M row begins.

    Returns:
        Starting index for M row in the panel stream
    """
    # The M row is tableau row 12 (MNQUVWXZKRYPTOSABCDEFGHIJL)
    # In the linear stream, we need to find where this appears

    # With extra_L, each "cycle" is 27 chars (26 + L)
    # Without extra_L, each cycle is 26 chars

    if extra_L:
        # Row 0: chars 0-26 (26 chars + L at 26)
        # Row 1: chars 27-53 (26 chars + L at 53)
        # ...
        # Row 12: starts at 12 * 27
        return 12 * 27
    else:
        # Row 12 starts at position 12 * 26
        return 12 * 26


def extract_key_window(stream, start_idx, length):
    """
    Extract a window from the panel stream

    Args:
        stream: The full panel stream
        start_idx: Starting index
        length: Number of characters to extract

    Returns:
        Key window string
    """
    return stream[start_idx:start_idx + length]


def display_stream_sample(extra_L=False):
    """Display a sample of the panel stream for verification"""
    stream = panel_stream(extra_L=extra_L, min_len=500)
    m_idx = get_m_alignment_index(extra_L=extra_L)

    print(f"Panel Stream Sample (extra_L={extra_L}):")
    print("=" * 60)
    print(f"First 100 chars: {stream[:100]}")
    print(f"\nM-row starts at index {m_idx}")
    print(f"M-row region: {stream[m_idx:m_idx+50]}")

    # Show what Hörenberg displays as the K line
    ct_len = 93  # Without OBKR
    key_window = extract_key_window(stream, m_idx, ct_len)
    print(f"\nKey window for CT (93 chars from M):")
    print(key_window)


if __name__ == "__main__":
    print("Testing panel stream generation...")
    display_stream_sample(extra_L=True)
    print("\n" + "=" * 60 + "\n")
    display_stream_sample(extra_L=False)