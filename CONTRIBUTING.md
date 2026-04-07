# Contributing to diff-cover-action

## Development Setup

```bash
# Clone the repo
git clone https://github.com/your-org/diff-cover-action.git
cd diff-cover-action

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Lint
ruff check src/ tests/ entrypoint.py

# Format
ruff format src/ tests/ entrypoint.py

# Type check
mypy src/ entrypoint.py --ignore-missing-imports
```

## Project Structure

```
src/
  cli_builder.py     # Maps action inputs to diff-cover CLI args
  runner.py          # Subprocess execution with streaming output
  report_parser.py   # Parses diff-cover JSON output
  comment.py         # PR comment create/update logic
  annotations.py     # GitHub workflow command annotations
  badge.py           # Shields.io badge JSON generation
  outputs.py         # GITHUB_OUTPUT + GITHUB_STEP_SUMMARY
  git_setup.py       # Shallow clone repair

templates/           # Jinja2 templates for PR comments and step summaries
tests/               # Unit tests (pytest)
entrypoint.py        # Main orchestrator
```

## Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src --cov-report=term-missing

# Single test file
pytest tests/test_cli_builder.py -v
```

## Docker Build

```bash
# Build
docker build -t diff-cover-action:test .

# Test the entrypoint
docker run --rm diff-cover-action:test python -c "import src; print('OK')"
```

## Adding a Feature

1. Create a branch from `main`
2. Write tests first (in `tests/`)
3. Implement the feature
4. Ensure all tests pass and linting is clean
5. Open a PR

## Release Process

1. Merge to `main` -- CI builds and pushes Docker image to GHCR
2. Create a GitHub Release with a semver tag (e.g., `v1.2.0`)
3. Release workflow rewrites Dockerfile to pre-built image and updates major version tag
