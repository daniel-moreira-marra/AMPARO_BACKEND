class DomainException(Exception):
    """Base class for all domain-related exceptions."""
    def __init__(self, message: str, code: str = "domain_error", details=None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(message)


class ValidationError(DomainException):
    """Exception raised when a business rule validation fails."""
    def __init__(self, message: str, code: str = "validation_error", details=None):
        super().__init__(message, code, details)


class PermissionDenied(DomainException):
    """Exception raised when an actor is not allowed to perform an action."""
    def __init__(self, message: str, code: str = "permission_denied", details=None):
        super().__init__(message, code, details)


class NotFound(DomainException):
    """Exception raised when a domain entity is not found."""
    def __init__(self, message: str, code: str = "not_found", details=None):
        super().__init__(message, code, details)
