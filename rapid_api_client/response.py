from inspect import isclass
from typing import Optional, Type, cast

from httpx import Response
from pydantic import BaseModel, PrivateAttr, TypeAdapter

from .utils import T, pydantic_xml


class ResponseModel(BaseModel):
    """
    Base class for response models that need access to the original HTTP response.

    ResponseModel extends Pydantic's BaseModel to provide access to the original
    httpx.Response object through the `_response` private attribute. This is useful
    when you need to access HTTP metadata (status codes, headers, etc.) alongside
    the parsed response data.

    The `_response` attribute is automatically populated by the rapid-api-client
    library when processing HTTP responses for methods that return ResponseModel
    subclasses.

    Attributes:
        _response: The original httpx.Response object. This is a private attribute
                  that is automatically set by the library and should not be
                  modified directly.

    Examples:
        >>> from rapid_api_client.response import ResponseModel
        >>> from rapid_api_client import RapidApi, get, Path
        >>> from typing import Annotated
        >>>
        >>> class UserResponse(ResponseModel):
        ...     id: int
        ...     name: str
        ...     email: str
        >>>
        >>> class UserApi(RapidApi):
        ...     @get("/users/{user_id}")
        ...     def get_user(self, user_id: Annotated[int, Path()]) -> UserResponse:
        ...         pass
        >>>
        >>> api = UserApi(base_url="https://api.example.com")
        >>> user = api.get_user(123)
        >>> print(f"User: {user.name}")
        >>> print(f"Status: {user._response.status_code}")
        >>> print(f"Headers: {dict(user._response.headers)}")

    Note:
        - Only classes that inherit from ResponseModel will have the `_response` attribute
        - Regular BaseModel classes do not get access to the HTTP response
        - The `_response` attribute is set automatically by the library's response processing
        - This works with both successful responses and error responses when raise_for_status=False
        - Compatible with both JSON and XML when used with appropriate parsing
    """

    _response: Response = PrivateAttr(init=False)


def process_response(
    response: Response, response_class: Type[T], raise_for_status: Optional[bool] = None
) -> T:
    """
    Process the HTTP response and convert it to the specified type.

    This function handles the conversion of HTTP responses to various types based on
    the specified response_class. It's a core utility used by the decorator module
    to process API responses according to the return type annotation of the API method.

    The conversion logic follows these rules:
    1. If response_class is Response, return the raw response object
    2. If response_class is str, return response.text
    3. If response_class is bytes, return response.content
    4. If response_class is a Pydantic XML model, parse the XML content
    5. If response_class is a Pydantic model, parse the JSON content
    6. For any other type, use Pydantic's TypeAdapter to validate the JSON content

    Args:
        response: The HTTP response object from httpx
        response_class: The class to convert the response to (typically from the return
                       type annotation of the API method)
        raise_for_status: Whether to call response.raise_for_status() before processing
                         the response. If True (default), HTTP errors (4xx, 5xx) will
                         raise an HTTPStatusError. Set to False to skip this check.

    Returns:
        The response converted to the specified type

    Raises:
        HTTPStatusError: If raise_for_status is True and the response status code
                        indicates an error (4xx, 5xx)
        ValidationError: If the response content cannot be parsed into the specified type
        TypeError: If the response_class is not supported

    Examples:
        # Return raw Response object
        >>> process_response(response, Response)
        <Response [200 OK]>

        # Convert to string
        >>> process_response(response, str)
        '{"key": "value"}'

        # Convert to bytes
        >>> process_response(response, bytes)
        b'{"key": "value"}'

        # Convert to Pydantic model
        >>> class MyModel(BaseModel):
        ...     key: str
        >>> process_response(response, MyModel)
        MyModel(key='value')

        # Convert to dataclass or other type
        >>> @dataclass
        ... class MyDataClass:
        ...     key: str
        >>> process_response(response, MyDataClass)
        MyDataClass(key='value')

        # Skip HTTP status check
        >>> process_response(response, str, raise_for_status=False)
        '{"error": "Not found"}'
    """
    if response_class is Response:
        # In case of Response, only check status if explicitly asked
        if raise_for_status is True:
            response.raise_for_status()
        return cast(T, response)

    # For other types than Response, check if the response status code indicates an error
    if raise_for_status is not False:
        response.raise_for_status()

    # In case of a string or bytes, return the response content
    if response_class is str:
        return cast(T, response.text)
    if response_class is bytes:
        return cast(T, response.content)

    out = None
    if (
        pydantic_xml is not None
        and isclass(response_class)
        and issubclass(response_class, pydantic_xml.BaseXmlModel)
    ):
        # Check if pydantic-xml is installed and if the response class is a pydantic-xml model
        out = response_class.from_xml(response.content)
    elif isclass(response_class) and issubclass(response_class, BaseModel):
        # Check if the response class is a pydantic model
        out = response_class.model_validate_json(response.content)
    else:
        # Fallback to TypeAdapter for other types
        out = TypeAdapter(response_class).validate_json(response.content)

    # Check if the response class is a subclass of ResponseModel to set the response private attribute
    if isinstance(out, ResponseModel):
        out._response = response
    return cast(T, out)
