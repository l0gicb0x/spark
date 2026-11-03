"""Typed errors used at SPARK boundaries."""


class ConfigError(Exception):
    """Settings could not be loaded or saved."""


class SecretError(Exception):
    """Credential Manager operation failed."""


class ProviderError(Exception):
    """A provider connection test failed with a user-actionable category."""


class PathError(Exception):
    """Application data locations are unavailable."""
