# business/encryption.py
import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

def encrypt_url(url: str) -> str:
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        raise ValueError("ENCRYPTION_KEY environment variable is not set.")
    
    key_bytes = key.encode("utf-8")
    if len(key_bytes) < 16:
        raise ValueError("ENCRYPTION_KEY must be at least 16 bytes long.")
    key_bytes = key_bytes[:16]

    iv = key_bytes

    backend = default_backend()
    cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv), backend=backend)

    # Pad the URL so its length is a multiple of 16 bytes.
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(url.encode("utf-8")) + padder.finalize()

    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    encrypted = iv + ciphertext
    return base64.urlsafe_b64encode(encrypted).decode("utf-8")