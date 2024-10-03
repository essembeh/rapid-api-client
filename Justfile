test pytest_args="":
    poetry run -- pytest --cov=rapid_api_client {{pytest_args}} tests/
    poetry run -- coverage html
    xdg-open htmlcov/index.html

pylint:
    poetry run -- pylint rapid_api_client

mypy:
    poetry run -- mypy rapid_api_client

release bump="patch":
    echo "{{bump}}" | grep -E "^(major|minor|patch)$"
    poetry version "{{bump}}"
    git add pyproject.toml
    git commit --message "🔖 New release: `poetry version -s`"
    git tag "`poetry version -s`"

[confirm('Confirm push --tags ?')]
publish:
    git log -1 --pretty="%B" | grep '^🔖 New release: '
    git push
    git push --tags
