"""Custom exceptions for the rapid-api-client library.

This module defines custom exception classes used throughout the rapid-api-client
library to provide specific error handling for various validation and runtime
scenarios. All custom exceptions inherit from the base RapidError class.
"""


class RapidError(BaseException):
    """Base exception class for all rapid-api-client specific errors.

    This is the parent class for all custom exceptions in the rapid-api-client
    library. It inherits from BaseException to distinguish library-specific
    errors from standard Python exceptions.

    All other custom exceptions in this library should inherit from this class
    to provide a consistent exception hierarchy and enable catching all
    library-specific errors with a single except clause.
    """

    ...


class InvalidBodyError(RapidError):
    """Exception raised when body parameter validation fails.

    This exception is raised during API method parameter processing when
    there are validation issues with body parameters, such as:

    - Multiple body parameters of different types (all must be the same type)
    - Multiple Body annotations when only one is allowed for a specific type
    - Invalid body parameter configuration

    The error message will contain specific details about the validation
    failure to help with debugging.
    """

    ...
