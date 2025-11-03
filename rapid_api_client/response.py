from httpx import Response
from pydantic import BaseModel, PrivateAttr


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
