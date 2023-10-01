class ConfirmationError(Exception):
    """Exception for when confirmation is not provided"""


class InvalidResetTokenError(Exception):
    """Exception for an invalid user reset token"""
