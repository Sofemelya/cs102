def encrypt_vigenere(plaintext: str, keyword: str) -> str:
    """
    Encrypts plaintext using a Vigenere cipher.

    >>> encrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> encrypt_vigenere("python", "a")
    'python'
    >>> encrypt_vigenere("ATTACKATDAWN", "LEMON")
    'LXFOPVEFRNHR'
    """
    ciphertext = ""
    for element in range(len(plaintext)):
        bukva = plaintext[element]
        keyword = keyword.upper()
        shift = ord(keyword[element % len(keyword)]) - 65
        element = 0
        if bukva.islower():
            ciphertext += chr(97 + ((ord(bukva) - 97 + shift) % 26))
        elif bukva.isupper():
            ciphertext += chr(65 + ((ord(bukva) - 65 + shift) % 26))
        else:
            ciphertext += bukva
        element += 1
    return ciphertext


def decrypt_vigenere(ciphertext: str, keyword: str) -> str:
    """
    Decrypts a ciphertext using a Vigenere cipher.

    >>> decrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> decrypt_vigenere("python", "a")
    'python'
    >>> decrypt_vigenere("LXFOPVEFRNHR", "LEMON")
    'ATTACKATDAWN'
    """
    plaintext = ""
    for element in range(len(ciphertext)):
        bukva = ciphertext[element]
        keyword = keyword.upper()
        shift = ord(keyword[element % len(keyword)]) - 65
        element = 0
        if bukva.islower():
            plaintext += chr(97 + ((ord(bukva) - 97 - shift) % 26))
        elif bukva.isupper():
            plaintext += chr(65 + ((ord(bukva) - 65 - shift) % 26))
        else:
            plaintext += bukva
        element += 1
    return plaintext

