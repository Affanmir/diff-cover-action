# diff-cover-action

A GitHub Action that wraps [diff-cover](https://github.com/Bachmann1234/diff_cover) to report test coverage and code quality **only on changed lines**. Native GitHub integration with PR comments, inline annotations, step summaries, and badge generation.

**Zero vendor lock-in** -- everything runs locally in the GitHub Actions runner. No external services, no accounts, no data leaving your CI.

## Features

- **Diff coverage** -- find lines in your PR that aren't covered by tests
- **Diff quality** -- find lint/style violations only in changed code (flake8, pylint, ruff, mypy, eslint, and more)
- **PR comments** -- auto-posted, idempotent (updates on re-run instead of spamming)
- **Inline annotations** -- uncovered lines appear directly in the PR diff view
- **Step summaries** -- coverage summary in the Actions run UI
- **Structured outputs** -- coverage %, violation count, threshold status for downstream steps
- **Badge generation** -- shields.io endpoint JSON for README badges
- **Shallow clone handling** -- automatically fetches enough history for diff-cover
- **Full CLI parity** -- every diff-cover/diff-quality flag is exposed as an input

## Quick Start

### Coverage Mode

```yaml
name: Coverage
on: [pull_request]

permissions:
  contents: read
  pull-requests: write

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run tests with coverage
        run: |
          pip install pytest pytest-cov
          pytest --cov --cov-report=xml

      - name: Diff Coverage
        uses: your-org/diff-cover-action@v1
        with:
          coverage-files: coverage.xml
          fail-under: '80'
```

### Quality Mode

```yaml
      - name: Diff Quality
        uses: your-org/diff-cover-action@v1
        with:
          mode: quality
          violations: ruff.check
          fail-under: '90'
```

### Both Coverage and Quality

```yaml
      - name: Diff Coverage
        uses: your-org/diff-cover-action@v1
        with:
          coverage-files: coverage.xml
          fail-under: '80'

      - name: Diff Quality
        uses: your-org/diff-cover-action@v1
        with:
          mode: quality
          violations: flake8
          fail-under: '90'
          comment-identifier: diff-quality  # separate comment from coverage
```

## Inputs

### Mode

| Input | Description | Default |
|-------|-------------|---------|
| `mode` | `"coverage"` or `"quality"` | `coverage` |

### Coverage Mode

| Input | Description | Default |
|-------|-------------|---------|
| `coverage-files` | Space-separated coverage report paths (XML/lcov). Globs supported. | *required* |

### Quality Mode

| Input | Description | Default |
|-------|-------------|---------|
| `violations` | Tool: `pycodestyle`, `pyflakes`, `flake8`, `pylint`, `ruff.check`, `mypy`, `checkstyle`, `checkstylexml`, `clang`, `cppcheck`, `eslint`, `jshint`, `pydocstyle`, `shellcheck` | *required* |
| `quality-input-reports` | Pre-generated violation report files (space-separated) | |
| `quality-options` | Pass-through arguments to the violations tool | |

### Git Diff

| Input | Description | Default |
|-------|-------------|---------|
| `compare-branch` | Branch to diff against | `origin/main` |
| `diff-range-notation` | `"..."` or `".."` | `...` |
| `diff-file` | Pre-generated diff file path | |
| `ignore-staged` | Exclude staged changes | `false` |
| `ignore-unstaged` | Exclude unstaged changes | `false` |
| `include-untracked` | Include untracked files | `false` |
| `ignore-whitespace` | Ignore whitespace in diff | `false` |

### Filtering

| Input | Description | Default |
|-------|-------------|---------|
| `exclude` | Newline-separated fnmatch exclude patterns | |
| `include` | Newline-separated glob include patterns | |
| `src-roots` | Space-separated source roots (for JaCoCo reports) | |

### Report Options

| Input | Description | Default |
|-------|-------------|---------|
| `expand-coverage-report` | Extend coverage for multi-line statements (XML only) | `false` |
| `show-uncovered` | Show uncovered lines in console output | `false` |
| `quiet` | Suppress non-error output | `false` |
| `config-file` | TOML configuration file path | |

### Threshold

| Input | Description | Default |
|-------|-------------|---------|
| `fail-under` | Minimum acceptable percentage (0-100) | `0` |
| `fail-on-threshold` | Fail the step when below threshold | `true` |

### GitHub Integration

| Input | Description | Default |
|-------|-------------|---------|
| `github-token` | Token for PR comments and annotations | `${{ github.token }}` |
| `post-comment` | Post/update PR comment with results | `true` |
| `comment-identifier` | Unique marker for idempotent comment updates | `diff-cover-action` |
| `create-annotations` | Create inline annotations on uncovered lines | `true` |
| `annotation-type` | `"warning"`, `"error"`, or `"notice"` | `warning` |
| `annotation-limit` | Max annotations (GitHub caps at 50/job) | `50` |
| `create-badge` | Generate shields.io endpoint JSON | `false` |
| `badge-filename` | Badge JSON output filename | `diff-cover-badge.json` |

## Outputs

| Output | Description |
|--------|-------------|
| `total-percent` | Coverage/quality percentage (integer) |
| `total-percent-float` | Percentage with 2 decimal places |
| `total-lines` | Total lines in the diff |
| `total-violations` | Uncovered or violating lines |
| `files-changed` | Number of files with changes |
| `threshold-met` | `"true"` or `"false"` |
| `comment-id` | PR comment ID |
| `report-json` | Path to JSON report file |
| `badge-json` | Path to badge JSON file |
| `exit-code` | Raw diff-cover CLI exit code |

### Using Outputs

```yaml
      - name: Diff Coverage
        id: coverage
        uses: your-org/diff-cover-action@v1
        with:
          coverage-files: coverage.xml

      - name: Check result
        if: steps.coverage.outputs.threshold-met == 'false'
        run: echo "Coverage is ${{ steps.coverage.outputs.total-percent }}%"
```

## Permissions

The action needs these permissions for full functionality:

```yaml
permissions:
  contents: read        # Read repository content
  pull-requests: write  # Post PR comments
  checks: write         # Create check annotations (optional, for >10 annotations)
```

### Fork PRs

When a PR comes from a fork, `GITHUB_TOKEN` has read-only permissions. The action detects this and:
- Skips PR comment posting (with a `::notice` message)
- Annotations via workflow commands still work

To enable comments on fork PRs, use `pull_request_target`:

```yaml
on:
  pull_request_target:
    types: [opened, synchronize]
```

## Shallow Clones

The action automatically handles shallow clones (the default for `actions/checkout`). It progressively fetches history until the merge-base is available. For fastest operation on large repos, set:

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0  # Full history, fastest for diff-cover
```

## Badge

Enable badge generation and use with shields.io:

```yaml
      - name: Diff Coverage
        uses: your-org/diff-cover-action@v1
        with:
          coverage-files: coverage.xml
          create-badge: 'true'

      - name: Upload badge
        uses: actions/upload-artifact@v4
        with:
          name: coverage-badge
          path: diff-cover-badge.json
```

Then use with a [shields.io endpoint badge](https://shields.io/badges/endpoint-badge).

## Advanced Examples

### Multiple Coverage Files

```yaml
      - uses: your-org/diff-cover-action@v1
        with:
          coverage-files: 'unit-coverage.xml integration-coverage.xml'
```

### Glob Patterns

```yaml
      - uses: your-org/diff-cover-action@v1
        with:
          coverage-files: '**/coverage*.xml'
```

### Exclude Patterns

```yaml
      - uses: your-org/diff-cover-action@v1
        with:
          coverage-files: coverage.xml
          exclude: |
            tests/*
            setup.py
            **/migrations/*
```

### JaCoCo (Java)

```yaml
      - uses: your-org/diff-cover-action@v1
        with:
          coverage-files: target/site/jacoco/jacoco.xml
          src-roots: 'src/main/java'
```

### TOML Configuration

```yaml
      - uses: your-org/diff-cover-action@v1
        with:
          coverage-files: coverage.xml
          config-file: pyproject.toml
```

Where `pyproject.toml` contains:

```toml
[tool.diff_cover]
compare_branch = "origin/develop"
fail_under = 80
exclude = ["tests/*", "setup.py"]
```

### Conditional Failure

Report coverage without failing the step:

```yaml
      - name: Coverage Report
        id: coverage
        uses: your-org/diff-cover-action@v1
        with:
          coverage-files: coverage.xml
          fail-under: '80'
          fail-on-threshold: 'false'  # Don't fail, just report

      - name: Warn if low
        if: steps.coverage.outputs.threshold-met == 'false'
        run: echo "::warning::Coverage is below 80%"
```

## How It Works

1. **Git setup** -- detects shallow clones and progressively fetches history
2. **CLI execution** -- builds and runs `diff-cover` or `diff-quality` with your options
3. **Report parsing** -- parses the JSON output into structured data
4. **PR comment** -- renders a markdown comment and creates/updates it on the PR
5. **Annotations** -- emits `::warning` workflow commands for uncovered lines
6. **Outputs** -- writes `GITHUB_OUTPUT` values and `GITHUB_STEP_SUMMARY`

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

[MIT](LICENSE)
