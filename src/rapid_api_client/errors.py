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


class FieldError(RapidError):
    """Exception raised when a required field value is missing.

    This exception is raised when a parameter that is required for an API
    call does not have a value provided. This typically occurs when:

    - A required parameter is not provided in the method call
    - A parameter value evaluates to PydanticUndefined
    - Missing values for required fields during parameter processing

    The error message will specify which parameter is missing to help
    with debugging.
    """

    ...


class AnnotationError(RapidError):
    """Exception raised when an invalid parameter annotation is encountered.

    This exception is raised during parameter processing when an annotation
    cannot be properly handled or processed. This occurs when:

    - An annotation type is not supported by the library
    - Invalid annotation configuration is detected
    - Malformed or incompatible annotation structure

    The error message will contain details about the invalid annotation
    to help identify the issue.
    """

    ...
