from cryptography.fernet import Fernet
import pytest

from app.core.errors import (
    MessageDecryptionError,
    MessageEncryptionError,
)
from app.security.message_cipher import MessageCipher


@pytest.fixture
def message_cipher() -> MessageCipher:
    return MessageCipher(Fernet.generate_key().decode("utf-8"))


def test_message_cipher_round_trip_preserves_unicode(
    message_cipher: MessageCipher,
) -> None:
    message = "Free prize – پاسخ دهید"

    ciphertext = message_cipher.encrypt(message)

    assert ciphertext != message.encode("utf-8")
    assert message.encode("utf-8") not in ciphertext
    assert message_cipher.decrypt(ciphertext) == message


def test_message_cipher_randomizes_repeated_plaintext(
    message_cipher: MessageCipher,
) -> None:
    message = "same message"

    assert message_cipher.encrypt(message) != message_cipher.encrypt(message)


def test_message_cipher_rejects_tampered_ciphertext(
    message_cipher: MessageCipher,
) -> None:
    ciphertext = message_cipher.encrypt("protected message")
    tampered = ciphertext[:-1] + bytes([ciphertext[-1] ^ 1])

    with pytest.raises(MessageDecryptionError):
        message_cipher.decrypt(tampered)


def test_message_cipher_rejects_invalid_key() -> None:
    with pytest.raises(RuntimeError, match="MESSAGE_ENCRYPTION_KEY"):
        MessageCipher("not-a-valid-fernet-key")


def test_message_cipher_translates_encryption_failure(
    message_cipher: MessageCipher,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_encryption(_: bytes) -> bytes:
        raise TypeError("cryptography implementation detail")

    monkeypatch.setattr(message_cipher._fernet, "encrypt", fail_encryption)

    with pytest.raises(MessageEncryptionError) as exc_info:
        message_cipher.encrypt("private message")

    assert "private message" not in str(exc_info.value)
