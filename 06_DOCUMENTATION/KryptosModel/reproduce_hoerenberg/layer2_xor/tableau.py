"""
Tableau generation for Hörenberg's K4 reproduction
Uses the standard KRYPTOS keyed alphabet
"""

# Standard keyed tableau top row from the sculpture
TOP = "KRYPTOSABCDEFGHIJLMNQUVWXZ"


def tableau_row(shift):
    """
    Generate a tableau row by rotating TOP left by shift positions

    Args:
        shift: Row index (0-25)

    Returns:
        26-char rotated alphabet
    """
    s = shift % 26
    return TOP[s:] + TOP[:s]


def get_row_for_letter(letter):
    """
    Get the tableau row that starts with the given letter

    Args:
        letter: Starting letter (A-Z)

    Returns:
        The tableau row starting with that letter
    """
    # Find which shift produces a row starting with this letter
    for shift in range(26):
        row = tableau_row(shift)
        if row[0] == letter.upper():
            return row
    return None


def get_row_index_for_letter(letter):
    """
    Get the row index for a given starting letter

    Args:
        letter: Starting letter (A-Z)

    Returns:
        Row index (0-25) or -1 if not found
    """
    # The row that starts with 'letter' is at index where TOP[index] = letter
    letter = letter.upper()

    # Special handling for the M row that Hörenberg uses
    # The M row starts at shift 12 (where TOP rotated left 12 times starts with M)
    for shift in range(26):
        row = tableau_row(shift)
        if row[0] == letter:
            return shift

    return -1


def display_tableau():
    """Display the full 26x26 tableau for verification"""
    print("KRYPTOS Tableau (First 10 rows):")
    print("=" * 60)
    for i in range(10):
        row = tableau_row(i)
        label = row[0]
        print(f"Row {i:2d} ({label}): {row}")
    print("...")
    print(f"Row 12 (M): {tableau_row(12)}")