class ConfirmationError(Exception):
    """Exception for when confirmation is not provided"""


class InvalidRefreshTokenError(Exception):
    """Exception for an invalid user reset token"""
