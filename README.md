![Github](https://img.shields.io/github/tag/essembeh/rapid-api-client.svg)
![PyPi](https://img.shields.io/pypi/v/rapid-api-client.svg)
![Python](https://img.shields.io/pypi/pyversions/rapid-api-client.svg)
![CI](https://github.com/essembeh/python-helloworld/actions/workflows/poetry.yml/badge.svg)


# Rapid Api Client

Library to rapidly develop asynchronous API clients based on [Pydantic](https://docs.pydantic.dev/) and [Httpx](https://www.python-httpx.org/) using *decorators* and *annotations*.

This project is largely inspired by [FastAPI](https://fastapi.tiangolo.com/).


# Usage 

Install the project

```sh
pip install rapid-api-client
```

Declare your API using decorators and annotations (the method does not need any code, it will be generated by the decorator)

```python
class GithubIssuesApi(RapidApi):

    @get("/repos/{owner}/{repo}/issues", response_class=RootModel[List[Issue]])
    async def list_issues(self, owner: Annotated[str, Path()], repo: Annotated[str, Path()]): ...

```

Use it 

```python
    api = GithubIssuesApi(client)
    issues = await api.list_issues("essembeh", "rapid-api-client", state="closed")
    for issue in issues.root:
        print(f"Issue: {issue.title} [{issue.url}]")
```

# Features

## Http method

Any HTTP method can be used with `http` decorator

```python
class MyApi(RapidApi)

    @http("/anything") # default is GET
    async def get(self): ...

    @http("/anything", method="POST")
    async def post(self): ...

    @http("/anything", method="DELETE")
    async def delete(self): ...
```

Convenient decorators are available like `get`, `post`, `delete`, `put`, `patch`

```python
class MyApi(RapidApi)

    @get("/anything")
    async def get(self): ...

    @post("/anything")
    async def post(self): ...

    @delete("/anything")
    async ef delete(self): ...
```


## Response class

By default methods return a `httpx.Response` object and the http return code is not tested (you have to call `resp.raise_for_status()` if you need to ensure the response is OK).

But you can also specify a *Pydantic model class* to automatically parse the response.

> Note: When a `response_class` is given, the `raise_for_status()` is always called to ensure the http response is OK

```python
class User(BaseModel): ...

class MyApi(RapidApi)

    # this method return a httpx.Response
    @get("/user/me")
    async def get_user_resp(self): ...

    # this method returns a User class
    @get("/user/me", response_class=User)
    async def get_user(self): ...
```


## Path parameters

Like `fastapi` you can use your method arguments to build the api path to call.

```python
class MyApi(RapidApi)

    @get("/user/{user_id}")
    async def get_user(self, user_id: Annotated[int, Path()]): ...

    # Path parameters dans have a default value
    @get("/user/{user_id}")
    async def get_user(self, user_id: Annotated[int, Path()] = 1): ...

```

## Query parameters

You can add `query parameters` to your request using the `Query` annotation.

```python
class MyApi(RapidApi)

    @get("/issues")
    async def get_issues(self, sort: Annotated[str, Query()]): ...

    # Query parameters can have a default value
    @get("/issues")
    async def get_issues_default(self, sort: Annotated[str, Query()] = "date"): ...

    # Query parameters can have an alias to change the key in the http request
    @get("/issues")
    async def get_issues_alias(self, sort: Annotated[str, Query(alias="sort-by")] = "date"): ...
```


## Header parameter

You can add `headers` to your request using the `Header` annotation.

```python
class MyApi(RapidApi)

    @get("/issues")
    async def get_issues(self, version: Annotated[str, Header()]): ...

    # Headers can have a default value
    @get("/issues")
    async def get_issues(self, version: Annotated[str, Header()] = "1"): ...

    # Headers can have an alias to change the key in the http request
    @get("/issues")
    async def get_issues(self, version: Annotated[str, Header(alias="X-API-Version")] = "1"): ...
```

## Body parameter

You can send a body with your request using the `Body` annotation. 

This body can be 
 - a *raw* object with `Body`
 - a *Pydantic* object  with `PydanticBody`
 - one or more files with `FileBody`

 ```python
class MyApi(RapidApi)

    # send a string in request content
    @post("/string")
    async def message(self, body: Annotated[str, Body()]): ...

    # send a string in request content
    @post("/model")
    async def model(self, body: Annotated[MyPydanticClass, PydanticBody()]): ...

    # send a multiple files
    @post("/files")
    async def model(self, report: Annotated[bytes, FileBody()], image: Annotated[bytes, FileBody()]): ...

 ```

 ## Xml Support

 Xml is also supported is you use [Pydantic-Xml](https://pydantic-xml.readthedocs.io/), either for responses with `response_class` or for POST/PUT content with `PydanticXmlBody`.

 ```python
class ResponseXmlRootModel(BaseXmlModel): ...

class MyApi(RapidApi)

    # parse response xml content
    @get("/get", response_class=ResponseXmlRootModel)
    async def get_xml(self): ...

    # serialize xml model automatically
    @post("/post")
    async def post_xml(self, body: Annotated[ResponseXmlRootModel, PydanticXmlBody()]): ...

 ```

 # Examples

 See [example directory](./examples/) for some examples