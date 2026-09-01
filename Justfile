# `check` and `test` are two distinct gates, mirroring the CI jobs.

default:
    @just --list

# Lint and format — mypy will join once strict typing is enforced
check:
    uv run ruff format --check src tests
    uv run ruff check src tests

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

# Strict typing gate — will join `check` once the codebase passes
mypy:
    uv run -- mypy src tests
