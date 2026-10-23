"""
Sagarvani Reconstructed — Gateway Exceptions
Categorized errors for timeouts, HTTP issues, malformed schemas, and provider unavailability.
"""

from typing import Optional


class GatewayError(Exception):
    """Base exception for all external data gateway failures."""
    def __init__(self, message: str, provider: str, error_code: str = "GATEWAY_ERROR"):
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.error_code = error_code


class GatewayTimeoutError(GatewayError):
    """Raised when connection or read deadline expires."""
    def __init__(self, message: str, provider: str):
        super().__init__(message, provider, error_code="GATEWAY_TIMEOUT")


class GatewayNetworkError(GatewayError):
    """Raised when network connect failure or socket error occurs."""
    def __init__(self, message: str, provider: str):
        super().__init__(message, provider, error_code="GATEWAY_NETWORK_ERROR")


class GatewayHTTPStatusError(GatewayError):
    """Raised when provider returns HTTP 4xx or 5xx."""
    def __init__(self, message: str, provider: str, status_code: int):
        super().__init__(f"HTTP {status_code}: {message}", provider, error_code="GATEWAY_HTTP_ERROR")
        self.status_code = status_code


class GatewaySchemaValidationError(GatewayError):
    """Raised when provider response violates expected structure or array lengths."""
    def __init__(self, message: str, provider: str):
        super().__init__(message, provider, error_code="GATEWAY_INVALID_SCHEMA")
