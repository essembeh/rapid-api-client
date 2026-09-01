# `check` and `test` are two distinct gates, mirroring the CI jobs.

default:
    @just --list

# Lint, format and typing — the full static gate
check:
    uv run ruff format --check src tests
    uv run ruff check src tests
    uv run -- mypy src tests

# Format and auto-fix what ruff can
format:
    uv run ruff format src tests
    uv run ruff check --fix src tests

# Unit tests + console coverage — like the CI test job
test pytest_args="":
    uv run -- pytest --cov=rapid_api_client --cov-report=term-missing {{pytest_args}} tests/

# Same, with a browsable HTML coverage report
test-html pytest_args="":
    uv run -- pytest --cov=rapid_api_client --cov-report=html {{pytest_args}} tests/
    xdg-open htmlcov/index.html