![Github](https://img.shields.io/github/tag/essembeh/rapid-api-client.svg)
![PyPi](https://img.shields.io/pypi/v/rapid-api-client.svg)
![Python](https://img.shields.io/pypi/pyversions/rapid-api-client.svg)
![CI](https://github.com/essembeh/python-helloworld/actions/workflows/poetry.yml/badge.svg)

> 🙏 As a Python Backend developer, I've wasted so much time in recent years writing the same API clients over and over using [Requests](https://requests.readthedocs.io/) or [HTTPX](https://www.python-httpx.org/); At the same time, I could be so efficient by using [FastAPI](https://fastapi.tiangolo.com/) for API servers; I just wanted to save time for my upcoming projects, thinking that other developers might find it useful too.




# Rapid Api Client

Library to **rapidly** develop *API clients* in Python, based on [Pydantic](https://docs.pydantic.dev/) and [Httpx](https://www.python-httpx.org/), using almost only *decorators* and *annotations*.

✨ Main features:
- ✏️ You don't write any code, you only declare the endpoints using *decorators* and *annotations*.
- 🪄 Pydantic validation for `Header`, `Query`, `Path` or `Body` parameters.
- 📤 Support Pydantic to parse and validate reponses content so your method returns a model object if the response is OK.
- 📥 Also support Pydantic serialization for `Body` with `POST`-like opeations.
- 🏗️ Does not reimplement any low-level http related logic (like auth, transport ...), it simply uses `httpx.Client` like you are used to, *decorators* simply build the `httpx.Request` for you.
- ⚡️ Support `async` operations, because `httpx` and `asyncio` are just amazingly fast.


# Usage 

Install the library

```sh
pip install rapid-api-client
```

Declare your API endpoints using decorators and annotations, **the method does not need any code, it will be generated by the decorator**, just write `...` or `pass` or whatever, it won't be called anyway 🙈.

```python
class GithubIssuesApi(RapidApi):

    @get("/repos/{owner}/{repo}/issues", response_class=TypeAdapter(List[Issue]))
    def list_issues(self, owner: Annotated[str, Path()], repo: Annotated[str, Path()]): ...

    @get("/repos/{owner}/{repo}/releases", response_class=TypeAdapter(List[Release]))
    def list_releases(self, owner: Annotated[str, Path()], repo: Annotated[str, Path()]): ...

```

Use it 

```python
    from httpx import Client

    api = GithubIssuesApi(Client(base_url="https://api.github.com"))
    issues = api.list_issues("essembeh", "rapid-api-client", state="closed")
    for issue in issues:
        print(f"Issue: {issue.title} [{issue.url}]")
```

# Features

## Http method

Any HTTP method can be used with `http` decorator

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

Convenient decorators are available like `get`, `post`, `delete`, `put`, `patch`

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

To use you API, you just need to instanciate it with a `httpx.Client` like:

```python
from httpx import Client

api = MyApi(Client(base_url="https://httpbin.org"))
resp = api.get()
resp.raise_for_status()
```


## `async` support

> Since version `0.5.0`, the default *client* and *annotations* are synchronous, `async` decorators and clients are in `rapid_api_client.async_` package.

RapidApiClient support both `sync` and `async` methods, based on `httpx.Client` and `httpx.AsyncClient`.

To build an asynchronous client:
* use common `RapidApi` class with an `AsyncClient` or use `AsyncRapidApi` class
* use annotations like `get` or `post` from `rapid_api_client.async_` package

Example:

```python
from rapid_api_client import RapidApi
from rapid_api_client.async_ import get, post, delete
from httpx import AsyncClient

class MyApi(RapidApi):

    @get("/anything")
    async def get(self): ...

    @post("/anything")
    async def post(self): ...

    @delete("/anything")
    async def delete(self): ...

# Usage
api = MyApi(AsyncClient(base_url="https://httpbin.org"))
resp = await api.get()
```

You can also use the dedicated `AsyncRapidApi` class which provides a default factory for an `AsyncClient`:

```python
from rapid_api_client.async_ import get, post, delete, AsyncRapidApi

class MyApi(AsyncRapidApi):

    @get("https://httpbin.org/anything")
    async def get(self): ...

    @post("https://httpbin.org/anything")
    async def post(self): ...

    @delete("https://httpbin.org/anything")
    async def delete(self): ...

# Usage
api = MyApi()
resp = await api.get()
```


## Response class

By default methods return a `httpx.Response` object and the http return code is not tested (you have to call `resp.raise_for_status()` if you need to ensure the response is OK).

But you can also specify a class so that the response is parsed, you can use:
- `httpx.Response` to get the response itself, this is the default behavior
- `str` to get the `response.text` 
- `bytes` to get the `response.content` 
- Any *Pydantic* model class (subclass of `BaseModel`), the *json* will be automatically validated
- Any *Pydantic-xml* model class (subclass of `BaseXmlModel`), the *xml* will be automatically validated
- Any `TypeAdapter` to parse the *json*, see [pydantic doc](https://docs.pydantic.dev/latest/api/type_adapter/)

> Note: When `response_class` is given (and is not `httpx.Response`), the `raise_for_status()` is always called to ensure the http response is OK

```python
class User(BaseModel): ...

class MyApi(RapidApi):

    # this method return a httpx.Response
    @get("/user/me")
    def get_user_raw(self): ...

    # this method returns a User class
    @get("/user/me", response_class=User)
    def get_user(self): ...
```


## Path parameters

Like `fastapi` you can use your method arguments to build the api path to call.

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

## Query parameters

You can add `query parameters` to your request using the `Query` annotation.

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

    # Query parameter with a default value
    @get("/issues")
    def get_issues(self, my_parameter: Annotated[str, Query(alias="sort")]): ...
```


## Header parameter

You can add `headers` to your request using the `Header` annotation.

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

    # Header parameter with a default value
    @get("/issues")
    def get_issues(self, my_parameter: Annotated[str, Header(alias="x-version")]): ...
```

## Body parameter

You can send a body with your request using the `Body` annotation. 

This body can be 
 - a *raw* object with `Body`
 - a `dict` object with `JsonBody` 
 - a *Pydantic* object  with `PydanticBody`
 - one or more files with `FileBody`

 ```python
class MyApi(RapidApi):

    # send a string in request content
    @post("/string")
    def post_string(self, body: Annotated[str, Body()]): ...

    # send a dict in request content as json
    @post("/string")
    def post_json(self, body: Annotated[dict, JsonBody()]): ...

    # send a Pydantic model in serialized as json
    @post("/model")
    def post_model(self, body: Annotated[MyPydanticClass, PydanticBody()]): ...

    # send a multiple files
    @post("/files")
    def post_files(self, report: Annotated[bytes, FileBody()], image: Annotated[bytes, FileBody()]): ...

    # send a form
    @post("/form")
    def post_form(self, my_param: Annotated[str, FormBody(alias="name")], extra_fields: Annotated[Dict[str, str], FormBody()]): ...

 ```

 ## Xml Support

 Xml is also supported is you use [Pydantic-Xml](https://pydantic-xml.readthedocs.io/), either for responses with `response_class` or for POST/PUT content with `PydanticXmlBody`.

 ```python
class ResponseXmlRootModel(BaseXmlModel): ...

class MyApi(RapidApi):

    # parse response xml content
    @get("/get", response_class=ResponseXmlRootModel)
    def get_xml(self): ...

    # serialize xml model automatically
    @post("/post")
    def post_xml(self, body: Annotated[ResponseXmlRootModel, PydanticXmlBody()]): ...

 ```


 # Examples

 See [example directory](./examples/) for some examples
