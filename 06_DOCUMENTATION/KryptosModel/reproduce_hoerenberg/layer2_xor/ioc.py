"""
Index of Coincidence (IoC) calculation matching Hörenberg's method
"""

from collections import Counter


def calculate_ioc(text):
    """
    Calculate Index of Coincidence for a text string

    IoC = Σ(ni * (ni - 1)) / (N * (N - 1))

    where ni is the count of letter i and N is total length

    Args:
        text: String to analyze (only A-Z counted)

    Returns:
        IoC value (float)
    """
    # Filter to only letters
    clean_text = ''.join(c for c in text.upper() if c.isalpha())

    if len(clean_text) < 2:
        return 0.0

    # Count letter frequencies
    counts = Counter(clean_text)

    # Calculate IoC
    n = len(clean_text)
    numerator = sum(count * (count - 1) for count in counts.values())
    denominator = n * (n - 1)

    if denominator == 0:
        return 0.0

    return numerator / denominator


def ioc_with_details(text):
    """
    Calculate IoC and return additional details

    Returns:
        Tuple of (ioc, clean_length, letter_counts)
    """
    # Filter to only letters
    clean_text = ''.join(c for c in text.upper() if c.isalpha())

    if len(clean_text) < 2:
        return 0.0, 0, {}

    counts = Counter(clean_text)
    n = len(clean_text)
    numerator = sum(count * (count - 1) for count in counts.values())
    denominator = n * (n - 1)

    ioc = numerator / denominator if denominator > 0 else 0.0

    return ioc, n, dict(counts)


def test_ioc():
    """Test IoC calculation with known values"""
    print("Testing IoC calculation:")
    print("=" * 40)

    # Random text should have IoC ≈ 0.0385 (1/26)
    random_text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 4
    ioc_random = calculate_ioc(random_text)
    print(f"Random text IoC: {ioc_random:.6f} (expect ≈0.0385)")

    # English text should have IoC ≈ 0.065
    english_text = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"
    ioc_english = calculate_ioc(english_text)
    print(f"English IoC: {ioc_english:.6f}")

    # K4 ciphertext
    k4_ct = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
    ioc_k4 = calculate_ioc(k4_ct)
    print(f"K4 ciphertext IoC: {ioc_k4:.6f} (Hörenberg reports ≈0.036)")


if __name__ == "__main__":
    test_ioc()