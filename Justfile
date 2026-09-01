# `check` and `test` are two distinct gates, mirroring the CI jobs.

export HTTPBIN_URL := env_var_or_default("HTTPBIN_URL", "http://localhost:18080")

default:
    @just --list

# Start the local httpbin used by the test suite (go-httpbin, the httpbingo.org implementation)
httpbin:
    podman inspect --type container httpbin >/dev/null 2>&1 || podman run --rm -d --name httpbin -p 18080:8080 ghcr.io/mccutchen/go-httpbin

# Lint, format and typing — the full static gate
check:
    uv run ruff format --check src tests
    uv run ruff check src tests
    uv run -- mypy src tests

# Format and auto-fix what ruff can
format:
    uv run ruff format src tests
    uv run ruff check --fix src tests

# Unit tests + console coverage — like the CI test job (which uses a httpbin service container)
test pytest_args="": httpbin
    uv run -- pytest --cov=rapid_api_client --cov-report=term-missing {{pytest_args}} tests/

# Known vulnerabilities in the dependencies resolved from uv.lock
audit:
    uv run --no-sync -- pip-audit

# Report outdated direct dependencies, and update GitHub Actions pins (rewrites .github/workflows/)
outdated:
    uv tree --outdated --depth 1
    GITHUB_TOKEN=$(gh auth token) uvx gha-update

# Bump the version, commit and tag — publishing happens in CI when the tag is pushed
release bump="patch":
    echo "{{bump}}" | grep -E "^(major|minor|patch)$"
    uv version --bump "{{bump}}"
    git add pyproject.toml uv.lock
    git commit --message "🔖 New release: `uv version --short`"
    git tag "`uv version --short`"

[confirm('Confirm push --tags ?')]
publish:
    git log -1 --pretty="%B" | grep '^🔖 New release: '
    git push
    git push --tags

# Same, with a browsable HTML coverage report
test-html pytest_args="":
    uv run -- pytest --cov=rapid_api_client --cov-report=html {{pytest_args}} tests/
    xdg-open htmlcov/index.html