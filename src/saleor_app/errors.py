class SaleorAppError(Exception):
    """Generic Saleor App Error, all framework errros inherit from this"""


class InstallAppError(SaleorAppError):
    """Install App error"""


class ConfigurationError(SaleorAppError):
    """App is misconfigured"""
