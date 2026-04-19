"""Exception classes for Socrates Nexus."""

from typing import Optional, Dict, Any


class LLMError(Exception):
    """Base exception for Socrates Nexus."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        super().__init__(self.message)


# Alias for consistency with library name
NexusError = LLMError


class RateLimitError(LLMError):
    """Raised when rate limit is exceeded (HTTP 429)."""

    def __init__(self, message: str, retry_after: Optional[int] = None):
        self.message = message
        self.retry_after = retry_after
        context = {"retry_after": retry_after}
        super().__init__(
            f"{message}. Retry after {retry_after} seconds." if retry_after else message,
            error_code="RATE_LIMIT",
            context=context,
        )


class AuthenticationError(LLMError):
    """Raised when authentication fails (HTTP 401/403)."""

    def __init__(self, message: str = "Invalid API key or authentication failed"):
        super().__init__(message, error_code="AUTHENTICATION_ERROR")


class InvalidAPIKeyError(AuthenticationError):
    """Raised when API key is invalid."""

    def __init__(self, message: str = "Invalid API key"):
        super().__init__(message)


class TimeoutError(LLMError):
    """Raised when request times out."""

    def __init__(self, message: str = "Request timed out"):
        super().__init__(message, error_code="TIMEOUT")


class ContextLengthExceededError(LLMError):
    """Raised when input exceeds model's context length."""

    def __init__(self, message: str = "Input exceeds model's maximum context length"):
        super().__init__(message, error_code="CONTEXT_LENGTH_EXCEEDED")


class ModelNotFoundError(LLMError):
    """Raised when model is not found."""

    def __init__(self, message: str = "Model not found"):
        super().__init__(message, error_code="MODEL_NOT_FOUND")


class ProviderError(LLMError):
    """Raised when provider encounters an error."""

    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message, error_code=error_code or "PROVIDER_ERROR")


class StreamingError(LLMError):
    """Raised when streaming fails."""

    def __init__(self, message: str = "Streaming failed"):
        super().__init__(message, error_code="STREAMING_ERROR")


class InvalidRequestError(LLMError):
    """Raised when request is malformed."""

    def __init__(self, message: str = "Invalid request"):
        super().__init__(message, error_code="INVALID_REQUEST")


class ConfigurationError(LLMError):
    """Raised when configuration is invalid."""

    def __init__(self, message: str = "Invalid configuration"):
        super().__init__(message, error_code="CONFIGURATION_ERROR")
