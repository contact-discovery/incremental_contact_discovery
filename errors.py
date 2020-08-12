import enum

from Messages_pb2 import Result

class ICDError(Exception):
    """ A generic error.

    Attributes
    ----------
    result : Messages_pb2.Result
        The specific casue of the error.
    """

    def __init__(self, result):
        self.result = result

class AuthenticationError(ICDError):
    """ An error caused by invalid authentication. """

    def __init__(self):
        ICDError.__init__(self, Result.AUTHENTICATION_INVALID)

class RateLimitError(ICDError):
    """ An error caused by exceeding the allowed rate limits. """

    def __init__(self):
        ICDError.__init__(self, Result.RATE_LIMIT_EXCEEDED)

class MissingDataError(ICDError):
    """ An error caused by missing data in the request. """

    def __init__(self):
        ICDError.__init__(self, Result.REQUEST_DATA_MISSING)

class InvalidDataError(ICDError):
    """ An error caused by invalid data in the request. """

    def __init__(self):
        ICDError.__init__(self, Result.REQUEST_DATA_INVALID)
