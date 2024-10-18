from datetime import datetime
from os import environ
from typing import Annotated, List

from httpx import Client
from pydantic import BaseModel, HttpUrl, TypeAdapter

from rapid_api_client import Header, Path, Query, RapidApi, get


class Issue(BaseModel):
    """
    Github model for issues
    """

    title: str
    created_at: datetime
    updated_at: datetime
    url: HttpUrl


class GithubIssuesApi(RapidApi):
    @get("/repos/{owner}/{repo}/issues", response_class=TypeAdapter(List[Issue]))
    def list_issues(
        self,
        owner: Annotated[str, Path()],
        repo: Annotated[str, Path()],
        state: Annotated[str | None, Query()] = None,
        sort: Annotated[str | None, Query()] = "updated",
        github_version: Annotated[
            str, Header(alias="X-GitHub-Api-Version")
        ] = "2022-11-28",
    ): ...


if __name__ == "__main__":
    """
    Ensure you have an environment variable GITHUB_TOKEN with a valid token
    """
    client = Client(
        base_url="https://api.github.com",
        headers={"Authorization": f"Bearer {environ['GITHUB_TOKEN']}"},
    )

    api = GithubIssuesApi(client)
    issues = api.list_issues("fastapi", "fastapi", state="closed")
    for issue in issues:
        print(f"Issue: {issue.title} [{issue.url}]")
