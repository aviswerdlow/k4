"""
25-letter alphabets for Hörenberg's base-5 layer
Tests both drop-J and drop-X variants
"""

# Drop-J alphabet (X remains) - Hörenberg's primary
ALPH25_DROP_J = "ABCDEFGHIKLMNOPQRSTUVWXYZ"

# Drop-X alphabet ("MIST X" variant) - Hörenberg's alternative
ALPH25_DROP_X = "ABCDEFGHIJKLMNOPQRSTUVWYZ"


def letter_to_base5(letter, alphabet=ALPH25_DROP_J):
    """
    Convert letter to base-5 digits (d1, d0)

    Args:
        letter: Single letter
        alphabet: 25-letter alphabet to use

    Returns:
        Tuple (d1, d0) or None if not in alphabet
    """
    letter = letter.upper()
    if letter not in alphabet:
        return None

    idx = alphabet.index(letter)
    d1 = idx // 5
    d0 = idx % 5
    return (d1, d0)


def base5_to_letter(d1, d0, alphabet=ALPH25_DROP_J):
    """
    Convert base-5 digits to letter

    Args:
        d1: First digit (0-4)
        d0: Second digit (0-4)
        alphabet: 25-letter alphabet to use

    Returns:
        Letter or '?' if invalid
    """
    idx = d1 * 5 + d0
    if 0 <= idx < 25:
        return alphabet[idx]
    return '?'


def string_to_base5(text, alphabet=ALPH25_DROP_J):
    """
    Convert string to base-5 digit representation

    Args:
        text: String to convert
        alphabet: 25-letter alphabet to use

    Returns:
        String of digits like "33123010" for display
    """
    result = []
    for char in text.upper():
        digits = letter_to_base5(char, alphabet)
        if digits:
            result.append(f"{digits[0]}{digits[1]}")
        else:
            result.append("??")
    return ''.join(result)


def display_alphabet_mapping(alphabet):
    """Display the alphabet with base-5 mappings"""
    print("Letter -> (d1,d0) -> Index")
    print("-" * 30)
    for i, letter in enumerate(alphabet):
        d1 = i // 5
        d0 = i % 5
        print(f"{letter:^6} -> ({d1},{d0}) -> {i:2d}")


if __name__ == "__main__":
    print("DROP-J ALPHABET (X remains):")
    print(ALPH25_DROP_J)
    display_alphabet_mapping(ALPH25_DROP_J)

    print("\n" + "=" * 40 + "\n")

    print("DROP-X ALPHABET:")
    print(ALPH25_DROP_X)
    display_alphabet_mapping(ALPH25_DROP_X)