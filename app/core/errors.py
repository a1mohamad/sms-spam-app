class PredictionError(Exception):
    """Raised when the inference engine cannot produce a prediction."""


class MessageEncryptionError(Exception):
    """Raised when an SMS message cannot be encrypted."""


class MessageDecryptionError(Exception):
    """Raised when an encrypted SMS message cannot be decrypted."""


class DatabaseUnavailableError(Exception):
    """Raised when the application cannot reach its database."""


class PersistenceError(Exception):
    """Raised when application data cannot be persisted or retrieved."""
