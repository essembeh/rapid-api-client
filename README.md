![Github](https://img.shields.io/github/tag/essembeh/rapid-api-client.svg)
![PyPi](https://img.shields.io/pypi/v/rapid-api-client.svg)
![Python](https://img.shields.io/pypi/pyversions/rapid-api-client.svg)
![CI](https://github.com/essembeh/rapid-api-client/actions/workflows/poetry.yml/badge.svg)

> 🙏 As a Python Backend developer, I've wasted so much time in recent years writing the same API clients over and over using [Requests](https://requests.readthedocs.io/) or [HTTPX](https://www.python-httpx.org/). At the same time, I could be so efficient by using [FastAPI](https://fastapi.tiangolo.com/) for API servers. I just wanted to save time for my upcoming projects, thinking that other developers might find it useful too.

# Rapid API Client

Library to **rapidly** develop *API clients* in Python, based on [Pydantic](https://docs.pydantic.dev/) and [Httpx](https://www.python-httpx.org/), using almost only *decorators* and *annotations*.

✨ Main features:
- ✏️ You don't write any code, you only declare the endpoints using *decorators* and *annotations*.
- 🪄 Pydantic validation for `Header`, `Query`, `Path` or `Body` parameters.
- 📤 Support Pydantic to parse and validate responses content so your method returns a model object if the response is OK.
- 📥 Also support Pydantic serialization for `Body` with `POST`-like operations.
- 🏗️ Does not reimplement any low-level HTTP related logic (like auth, transport...), it simply uses `httpx.Client` like you are used to. *Decorators* simply build the `httpx.Request` for you.
- ⚡️ Support `async` operations, with `httpx.AsyncClient`.


# Quick Start

Here's a complete example to get you started quickly:

First, install `rapid-api-client`:

```sh
# to install the latest version using pip
pip install rapid-api-client

# or add it to your `pyproject.toml` file using poetry
poetry add rapid-api-client
```

Then, declare your API client using *decorators* and *annotations*:


```python
from typing import Annotated, List
from pydantic import BaseModel
from rapid_api_client import RapidApi, get, post, Path, Query, JsonBody, rapid

# Define your data models
class User(BaseModel):
    id: int
    name: str
    email: str
    
class CreateUserRequest(BaseModel):
    name: str
    email: str

# Define your API client
# Note: the @rapid decorator is optional, but it allows you to set default values for your constructor
@rapid(base_url="https://api.example.com")
class UserApi(RapidApi):
    # GET request with path parameter and query parameter
    @get("/users/{user_id}")
    def get_user(self, user_id: Annotated[int, Path()]) -> User:
        """Get a user by ID"""
        ...
    
    # GET request with query parameters
    @get("/users")
    def list_users(self, 
                  page: Annotated[int, Query()] = 1, 
                  limit: Annotated[int, Query()] = 10) -> List[User]:
        """List users with pagination"""
        ...
    
    # POST request with JSON body
    @post("/users")
    def create_user(self, user: Annotated[CreateUserRequest, JsonBody()]) -> User:
        """Create a new user"""
        ...
```

Finally, use your API client to interact with the API:

```python
# Use the API client
if __name__ == "__main__":
    # Initialize the API client
    # Note: you don't need to pass the base URL here if you used the @rapid decorator
    api = UserApi()
    
    # Get a user by ID
    user = api.get_user(123)
    print(f"User: {user.name} ({user.email})")
    
    # List users with pagination
    users = api.list_users(page=1, limit=5)
    for user in users:
        print(f"- {user.name}")
    
    # Create a new user
    new_user = CreateUserRequest(name="John Doe", email="john@example.com")
    created_user = api.create_user(new_user)
    print(f"Created user with ID: {created_user.id}")
```


# Features

## HTTP Methods

Any HTTP method can be used with the `http` decorator:

```python
from rapid_api_client import RapidApi, http 


class MyApi(RapidApi):

    @http("GET", "/anything")
    def get(self): ...

    @http("POST", "/anything")
    def post(self): ...

    @http("DELETE", "/anything")
    def delete(self): ...
```

Convenient decorators are available like `get`, `post`, `delete`, `put`, `patch`:

```python
from rapid_api_client import RapidApi, get, post, delete

class MyApi(RapidApi):

    @get("/anything")
    def get(self): ...

    @post("/anything")
    def post(self): ...

    @delete("/anything")
    def delete(self): ...
```

To use your API, you just need to instantiate it with a `httpx.Client` like:

```python
from httpx import Client

api = MyApi(base_url="https://httpbin.org")
resp = api.get()
resp.raise_for_status()
```


## `async` Support

> ✨ Since version `0.7.0`, the same code works for synchronous and `async` methods.

You can write:
```python
class GithubIssuesApi(RapidApi):

    @get("/repos/{owner}/{repo}/issues")
    def list_issues(self, owner: Annotated[str, Path()], repo: Annotated[str, Path()]) -> List[Issue]: ...

    @get("/repos/{owner}/{repo}/issues")
    async def alist_issues(self, owner: Annotated[str, Path()], repo: Annotated[str, Path()]) -> List[Issue]: ...


api = GithubIssuesApi(base_url="https://api.github.com")
issues_sync = api.list_issues("essembeh", "rapid-api-client", state="closed")
issues_async = await api.alist_issues("essembeh", "rapid-api-client", state="closed")
# both lists are the same
```

*Rapid API Client* supports both `sync` and `async` methods. It will automatically choose `httpx.Client` or `httpx.AsyncClient` to build and send the HTTP request.

By default, all parameters given to the `RapidApi` constructor are used to instantiate a `httpx.Client` or `httpx.AsyncClient`, depending on whether your method is `async` or not. You can provide a custom `client` or `async_client` (or both) to have more control over the clients creation:

```python
from httpx import Client, AsyncClient

# In this example, the sync client has a timeout of 10s and the async client has a timeout of 20s
api = GithubIssuesApi(
    client=Client(base_url="https://api.github.com", timeout=10), 
    async_client=AsyncClient(base_url="https://api.github.com", timeout=20)
)

issues_sync = api.list_issues("essembeh", "rapid-api-client", state="closed")  # this HTTP call has a timeout of 10s
issues_async = await api.alist_issues("essembeh", "rapid-api-client", state="closed")  # this one has a timeout of 20s
```


## Response Parsing

By default, methods return a `httpx.Response` object and the HTTP return code is not tested (you have to call `resp.raise_for_status()` if you need to ensure the response is OK).

But you can also specify a class so that the response is parsed. You can use:
- `httpx.Response` to get the response itself, this is the default behavior
- `str` to get the `response.text` 
- `bytes` to get the `response.content` 
- Any *Pydantic* model class (subclass of `BaseModel`), the *JSON* will be automatically validated
    - If your model extends `rapid_api_client.ResponseModel`, then you'll have access to the `httpx.Response` with the `_response` private attribute (see below for more examples)
- Any *Pydantic-xml* model class (subclass of `BaseXmlModel`), the *XML* will be automatically validated
    - If your XML model also inherits from `rapid_api_client.ResponseModel`, then you'll have access to the `httpx.Response` with the `_response` private attribute
- Any other class will try to use `TypeAdapter` to parse it (see [pydantic doc](https://docs.pydantic.dev/latest/api/type_adapter/))

> Note: When the returned object is not `httpx.Response`, the `raise_for_status()` is called to ensure the HTTP response is OK before parsing the content. You can disable this behavior by setting `raise_for_status=False` in the method decorator. For `httpx.Response` return types, `raise_for_status()` is only called if explicitly set to `raise_for_status=True`.

```python
class User(BaseModel):
    name: str
    email: str

class MyApi(RapidApi):

    # This method returns a httpx.Response, you can omit it, but you should add it for clarity
    @get("/user/me")
    def get_user_raw(self) -> Response: ...

    # This method returns a User class
    @get("/user/me")
    def get_user(self) -> User: ...
```


### `ResponseModel` - Access to HTTP Response Object

When using Pydantic models for response parsing, you may sometimes need access to the raw HTTP response object (for example, to check headers or status codes). The `ResponseModel` class provides this functionality:

```python
from typing import Annotated
from pydantic import ValidationError
from rapid_api_client import RapidApi, get, Path, ResponseModel

class UserResponse(ResponseModel):
    id: int
    name: str
    email: str
    
class MyApi(RapidApi):
    @get("/user/{user_id}")
    def get_user(self, user_id: Annotated[int, Path()]) -> UserResponse: ...
    
# Usage
api = MyApi(base_url="https://api.example.com")

# Get a user - the response object has access to the original HTTP response
user = api.get_user(123)
print(f"User: {user.name}")
print(f"Response status: {user._response.status_code}")
print(f"Response headers: {user._response.headers}")
print(f"Request URL: {user._response.url}")
```

Key benefits of `ResponseModel`:
- **Access to HTTP metadata**: Status codes, headers, URL, etc.
- **Error handling**: Check response status even when `raise_for_status=False`
- **Debugging**: Inspect the raw response for troubleshooting
- **Conditional logic**: Make decisions based on status codes or headers

> **Note**: Only classes that inherit from `ResponseModel` will have the `_response` attribute. Regular `BaseModel` classes do not get access to the HTTP response object.


### Error Handling with `raise_for_status`

The `raise_for_status` parameter provides fine-grained control over HTTP error handling:

```python
from httpx import Response, HTTPStatusError
from rapid_api_client import RapidApi, get

class MyApi(RapidApi):

    # Raw Response: No automatic error checking (default behavior)
    @get("/status/500")
    def get_raw_response(self) -> Response: ...

    # Raw Response: Explicitly enable error checking
    @get("/status/500", raise_for_status=True)
    def get_raw_response_with_errors(self) -> Response: ...

    # Parsed Response: Automatic error checking (default behavior)
    @get("/status/500")
    def get_parsed_response(self) -> str: ...

    # Parsed Response: Disable error checking
    @get("/status/500", raise_for_status=False)
    def get_parsed_response_no_errors(self) -> str: ...

# Usage examples
api = MyApi(base_url="https://httpbin.org")

# This will return a Response object with status 500, no exception raised
response = api.get_raw_response()
print(response.status_code)  # 500

# This will raise HTTPStatusError due to explicit raise_for_status=True
try:
    response = api.get_raw_response_with_errors()
except HTTPStatusError as e:
    print(f"HTTP Error: {e.response.status_code}")

# This will raise HTTPStatusError due to automatic error checking for parsed responses
try:
    content = api.get_parsed_response()
except HTTPStatusError as e:
    print(f"HTTP Error: {e.response.status_code}")

# This will return the error response content as a string, no exception raised
error_content = api.get_parsed_response_no_errors()
print(error_content)  # Error page HTML/JSON content
```


## Path Parameters

Like `fastapi`, you can use your method arguments to build the API path to call:

```python
class MyApi(RapidApi):

    # Path parameter
    @get("/user/{user_id}")
    def get_user(self, user_id: Annotated[int, Path()]): ...

    # Path parameters with value validation
    @get("/user/{user_id}")
    def get_user(self, user_id: Annotated[PositiveInt, Path()]): ...

    # Path parameters with a default value
    @get("/user/{user_id}")
    def get_user(self, user_id: Annotated[int, Path(default=1)]): ...

    # Path parameters with a default value using a factory
    @get("/user/{user_id}")
    def get_user(self, user_id: Annotated[int, Path(default_factory=lambda: 42)]): ...
```

## Query Parameters

You can add `query parameters` to your request using the `Query` annotation:

```python
class MyApi(RapidApi):

    # Query parameter
    @get("/issues")
    def get_issues(self, sort: Annotated[str, Query()]): ...

    # Query parameters with value validation
    @get("/issues")
    def get_issues(self, sort: Annotated[Literal["updated", "id"], Query()]): ...

    # Query parameter with a default value
    @get("/issues")
    def get_issues(self, sort: Annotated[str, Query(default="updated")]): ...

    # Query parameter with a default value using a factory
    @get("/issues")
    def get_issues(self, sort: Annotated[str, Query(default_factory=lambda: "updated")]): ...

    # Query parameter with an alias
    @get("/issues")
    def get_issues(self, my_parameter: Annotated[str, Query(alias="sort")]): ...
```


## Header Parameters

You can add `headers` to your request using the `Header` annotation:

```python
class MyApi(RapidApi):

    # Header parameter
    @get("/issues")
    def get_issues(self, x_version: Annotated[str, Header()]): ...

    # Header parameters with value validation
    @get("/issues")
    def get_issues(self, x_version: Annotated[Literal["2024.06", "2024.01"], Header()]): ...

    # Header parameter with a default value
    @get("/issues")
    def get_issues(self, x_version: Annotated[str, Header(default="2024.06")]): ...

    # Header parameter with a default value using a factory
    @get("/issues")
    def get_issues(self, x_version: Annotated[str, Header(default_factory=lambda: "2024.06")]): ...

    # Header parameter with an alias
    @get("/issues")
    def get_issues(self, my_parameter: Annotated[str, Header(alias="x-version")]): ...

    # You can also add constant headers
    @get("/issues", headers={"x-version": "2024.06", "accept": "application/json"})
    def get_issues(self): ...
```

## Body Parameters

You can send a body with your request using the `Body` annotation. 

This body can be:
 - A *raw* object with `Body`
 - A `dict` object with `JsonBody` 
 - A *Pydantic* object with `PydanticBody`
 - One or more files with `FileBody`

```python
class MyApi(RapidApi):

    # Send a string in request content
    @post("/string")
    def post_string(self, body: Annotated[str, Body()]): ...

    # Send a dict in request content as JSON
    @post("/string")
    def post_json(self, body: Annotated[dict, JsonBody()]): ...

    # Send a Pydantic model serialized as JSON
    @post("/model")
    def post_model(self, body: Annotated[MyPydanticClass, PydanticBody()]): ...

    # Send multiple files
    @post("/files")
    def post_files(self, report: Annotated[bytes, FileBody()], image: Annotated[bytes, FileBody()]): ...

    # Send a form
    @post("/form")
    def post_form(self, my_param: Annotated[str, FormBody(alias="name")], extra_fields: Annotated[Dict[str, str], FormBody()]): ...
```

## XML Support

XML is also supported if you use [Pydantic-Xml](https://pydantic-xml.readthedocs.io/), either for responses (if you type your function to return a `BaseXmlModel` subclass) or for POST/PUT content with `PydanticXmlBody`.

```python
class ResponseXmlRootModel(BaseXmlModel): ...

class MyApi(RapidApi):

    # Parse response XML content
    @get("/get")
    def get_xml(self) -> ResponseXmlRootModel: ...

    # Serialize XML model automatically
    @post("/post")
    def post_xml(self, body: Annotated[ResponseXmlRootModel, PydanticXmlBody()]): ...
```

# Examples

## Authentication and Error Handling

Here's a simple example showing how to handle authentication and errors:

```python
from typing import Annotated, Optional
from pydantic import BaseModel
from httpx import HTTPStatusError
from rapid_api_client import RapidApi, get, post, Header

# Define your data models
class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class UserProfile(BaseModel):
    id: int
    username: str
    email: str

# Define your API client
class AuthenticatedApi(RapidApi):
    # Login endpoint
    @post("/auth/login")
    def login(self, username: str, password: str) -> AuthResponse:
        """Get an authentication token"""
        ...
    
    # Protected endpoint that requires authentication
    @get("/users/me")
    def get_profile(self, authorization: Annotated[str, Header()]) -> UserProfile:
        """Get the current user's profile"""
        ...

# Example usage with error handling
def main():
    # Create API client
    api = AuthenticatedApi(base_url="https://api.example.com")
    
    try:
        # Login to get token
        auth_response = api.login(username="user@example.com", password="password123")
        
        # Use token for authenticated requests
        auth_header = f"{auth_response.token_type} {auth_response.access_token}"
        profile = api.get_profile(authorization=auth_header)
        
        print(f"Logged in as: {profile.username} ({profile.email})")
        
    except HTTPStatusError as e:
        # Handle HTTP errors (4xx, 5xx)
        if e.response.status_code == 401:
            print("Authentication failed: Invalid credentials")
        elif e.response.status_code == 403:
            print("Authorization failed: Insufficient permissions")
        elif e.response.status_code >= 500:
            print(f"Server error: {e}")
        else:
            print(f"Request failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
```

See the [examples directory](./examples/) for more examples.
