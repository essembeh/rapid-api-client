test pytest_args="":
    uv run -- pytest --cov=rapid_api_client {{pytest_args}} tests/
    uv run -- coverage html
    xdg-open htmlcov/index.html

pylint:
    uv run -- pylint rapid_api_client

mypy:
    uv run -- mypy src/
