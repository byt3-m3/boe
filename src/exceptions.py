class StateError(BaseException):
    """
    Represent an error due to improper state of object.

    """

class TransactionError(BaseException):
    """
    Represents an bad transaction in system
    """

class PermissionValidationError(BaseException):
    """
    Raised if there is an issue when validating Role permissions

    """