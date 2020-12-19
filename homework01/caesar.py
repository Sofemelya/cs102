import typing as tp


def encrypt_caesar(plaintext: str, shift: int = 3) -> str:
    """
    Encrypts plaintext using a Caesar cipher.

    >>> encrypt_caesar("PYTHON")
    'SBWKRQ'
    >>> encrypt_caesar("python")
    'sbwkrq'
    >>> encrypt_caesar("Python3.6")
    'Sbwkrq3.6'
    >>> encrypt_caesar("")
    ''
    """
    ciphertext = ""
    for bukva in range(len(plaintext)):
        bukva = plaintext[bukva]
        if bukva.isupper():
            ciphertext += chr((ord(bukva) + shift - ord("A")) % 26 + ord("A"))
        elif bukva.islower():
            ciphertext += chr((ord(bukva) + shift - ord("a")) % 26 + ord("a"))
        else:
            ciphertext = ciphertext + bukva
    return ciphertext


def decrypt_caesar(ciphertext: str, shift: int = 3) -> str:
    """
    Decrypts a ciphertext using a Caesar cipher.

    >>> decrypt_caesar("SBWKRQ")
    'PYTHON'
    >>> decrypt_caesar("sbwkrq")
    'python'
    >>> decrypt_caesar("Sbwkrq3.6")
    'Python3.6'
    >>> decrypt_caesar("")
    ''
    """
    plaintext = ""
    for bukva in range(len(ciphertext)):
        bukva = ciphertext[bukva]
        if bukva.isupper():
            plaintext += chr((ord(bukva) - shift - ord("A")) % 26 + ord("A"))
        elif bukva.islower():
            plaintext += chr((ord(bukva) - shift - ord("a")) % 26 + ord("a"))
        else:
            plaintext = plaintext + bukva
    return plaintext


def caesar_breaker_brute_force(ciphertext: str, dictionary: tp.Set[str]) -> int:
    d = {"python", "java", "ruby"}
    """
        >>> d = {"python", "java", "ruby"}
        >>> caesar_breaker("python", d)
        0
        >>> caesar_breaker("sbwkrq", d)
        3
        """
    best_shift = 0
    for shift in range(0, 27):
        if decrypt_caesar(ciphertext, shift):
            if decrypt_caesar(ciphertext, shift) in dictionary:
                shift = best_shift
    return best_shift
