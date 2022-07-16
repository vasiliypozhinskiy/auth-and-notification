class FieldValidationError(Exception):
    default_message = "Wrong field value"

    def __init__(self, message=default_message):
        self.message = message


class AlreadyExistsError(Exception):
    default_message = "Resource already exists"

    def __init__(self, message=default_message):
        self.message = message


class NotFoundError(Exception):
    default_message = "Resource not found"

    def __init__(self, message=default_message):
        self.message = message


class BadPasswordError(Exception):
    default_message = """
    Password must contain minimum eight characters, 
    at least one uppercase letter, 
    one lowercase letter, one number and one special character
    """

    def __init__(self, message=default_message):
        self.message = message


class BadEmailError(Exception):
    default_message = "Wrong email"

    def __init__(self, message=default_message):
        self.message = message


class BadLengthError(Exception):
    default_message = "Wrong length of field"

    def __init__(self, message=default_message):
        self.message = message


class BadIdFormat(Exception):
    default_message = "Wrong id format"

    def __init__(self, message=default_message):
        self.message = message


class AccessDenied(Exception):
    default_message = "Wrong email or password"

    def __init__(self, message=default_message):
        self.message = message


class InvalidToken(Exception):
    default_message = "Invalid access token"

    def __init__(self, message=default_message):
        self.message = message


class UnExistingLogin(Exception):
    default_message = "See this login first time bro"

    def __init__(self, message=default_message):
        self.message = message


class ServiceUnavailable(Exception):
    default_message = "Service temporary unavailable"

    def __init__(self, message=default_message):
        self.message = message


class RequestLimitReached(Exception):
    default_message = "Too much request"

    def __init__(self, message=default_message):
        self.message = message
