from cryptography.fernet import Fernet
from app.core.config import settings, Settings


class Encryptor:
    """Handles encryption/decryption of sensitive data like Plaid tokens"""

    def __init__(self, encryption_key: str = None):
        if encryption_key:
            self.cipher = Fernet(encryption_key.encode())
        elif settings:
            self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())
        else:
            raise ValueError("Encryption key must be provided or settings must be configured")

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string"""
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a string"""
        return self.cipher.decrypt(ciphertext.encode()).decode()


# Global encryptor instance
try:
    encryptor = Encryptor()
except Exception:
    # Allow import to succeed even if encryptor can't be created (e.g., during tests)
    encryptor = None  # type: ignore


def encrypt_token(token: str) -> str:
    """
    Encrypt a token using the global encryptor

    Args:
        token: Plaintext token

    Returns:
        Encrypted token
    """
    if encryptor is None:
        raise ValueError("Encryptor not initialized")
    return encryptor.encrypt(token)


def decrypt_token(encrypted_token: str) -> str:
    """
    Decrypt a token using the global encryptor

    Args:
        encrypted_token: Encrypted token

    Returns:
        Decrypted token
    """
    if encryptor is None:
        raise ValueError("Encryptor not initialized")
    return encryptor.decrypt(encrypted_token)
