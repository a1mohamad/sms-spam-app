from cryptography.fernet import Fernet, InvalidToken

from core.errors import (
    MessageDecryptionError,
    MessageEncryptionError,
)

class MessageCipher:
    """Encrypt and decrypt SMS messages using Fernet."""

    def __init__(self, encryption_key: str) -> None:
        """Initialize the message cipher.

        Args:
            encryption_key: URL-safe base64-encoded Fernet key.

        Raises:
            RuntimeError: If the encryption key is invalid.
        """
        try:
            self._fernet = Fernet(encryption_key.encode("utf-8"))
        except (TypeError, ValueError) as exc:
            # An invalid key is an application configuration failure.
            raise RuntimeError(
                "MESSAGE_ENCRYPTION_KEY is invalid."
            ) from exc
        
    def encrypt(self, message: str) -> bytes:
        """Encrypt an SMS message.

        Args:
            message: Plaintext SMS message.

        Returns:
            Authenticated encrypted message bytes.

        Raises:
            MessageEncryptionError: If the message cannot be encrypted.
        """

        try:
            return self._fernet.encrypt(message.encode("utf-8"))
        except (TypeError, UnicodeEncodeError) as exc:
            # Never include the plaintext message in the exception.
            raise MessageEncryptionError(
                "SMS Message encryption failed."
            ) from exc
        
    def decrypt(self, ciphertext: bytes) -> str:
        """Decrypt an encrypted SMS message.

        Args:
            ciphertext: Authenticated encrypted message bytes.

        Returns:
            Original plaintext SMS message.

        Raises:
            MessageDecryptionError: If the ciphertext is invalid or damaged.
        """

        try:
            plaintext = self._fernet.decrypt(ciphertext)
            return plaintext.decode("utf-8")
        except (InvalidToken, TypeError, UnicodeDecodeError) as exc:
            raise MessageDecryptionError(
                "SMS Message decryption failed."
            ) from exc