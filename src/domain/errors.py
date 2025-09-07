# src/domain/errors.py

class ValidationError(Exception):
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(message)

class UsernameError(ValidationError):
    pass

class PasswordError(ValidationError):
    pass

class ContactError(ValidationError):
    pass

class PersonalError(ValidationError):
    pass

class LocationError(ValidationError):
    pass
