# diff-cover-action

[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-Diff%20Cover%20Action-blue?logo=github)](https://github.com/marketplace/actions/diff-cover-pr-coverage-quality-reports)
[![GitHub Stars](https://img.shields.io/github/stars/Affanmir/diff-cover-action?style=social)](https://github.com/Affanmir/diff-cover-action)
[![GitHub Release](https://img.shields.io/github/v/release/Affanmir/diff-cover-action)](https://github.com/Affanmir/diff-cover-action/releases)
[![License: MIT](https://img.shields.io/github/license/Affanmir/diff-cover-action)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/Affanmir/diff-cover-action/integration-test.yml?label=tests)](https://github.com/Affanmir/diff-cover-action/actions)

A GitHub Action that wraps [diff-cover](https://github.com/Bachmann1234/diff_cover) to report test coverage and code quality **only on changed lines**. Native GitHub integration with PR comments, inline annotations, step summaries, and badge generation.

**Zero vendor lock-in** -- everything runs locally in the GitHub Actions runner. No external services, no accounts, no data leaving your CI.

---

## Why This Action?

| | diff-cover-action | Codecov | Coveralls | coverage-diff |
|---|:---:|:---:|:---:|:---:|
| **Free & self-hosted** | Yes | Freemium | Freemium | Yes |
| **No external account** | Yes | No | No | Yes |
| **Coverage + quality in one** | Yes | No | No | No |
| **13+ lint tools** (ruff, eslint, mypy...) | Yes | No | No | No |
| **PR comments** | Yes | Yes | Yes | Yes |
| **Inline annotations** | Yes | Yes | Yes | No |
| **Step summaries** | Yes | No | No | No |
| **Badge generation** | Yes | Yes | Yes | Yes |
| **JaCoCo / lcov / XML** | Yes | Yes | Yes | JSON only |
| **Shallow clone handling** | Auto | Manual | Manual | N/A |
| **Fork PR safe** | Yes | Yes | Yes | Limited |
| **Data stays in your CI** | Yes | No | No | Yes |

**In short**: This is the only action that does **both** diff coverage and diff quality analysis in a single step, with full GitHub integration, across any language and linter -- with zero vendor dependencies.

---

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

### Supported Languages & Tools

| Category | Tools |
|----------|-------|
| **Coverage formats** | Cobertura XML, lcov, JaCoCo XML, Clover XML |
| **Python linters** | ruff, flake8, pylint, pycodestyle, pyflakes, mypy, pydocstyle |
| **JavaScript linters** | eslint, jshint |
| **Other** | checkstyle, checkstylexml, clang, cppcheck, shellcheck |

Works with **any language** that can produce Cobertura XML, lcov, or JaCoCo coverage reports (Python, JavaScript, TypeScript, Java, Go, Rust, C#, Ruby, PHP, and more).

---

## What You Get

### PR Comment (auto-posted, updates on re-run)

> ## :white_check_mark: Diff Coverage: 82.0%
>
> > :heavy_check_mark: Meets threshold of 80%
>
> | Metric | Value |
> |--------|------:|
> | **Coverage on diff lines** | **82.0%** |
> | Lines changed | 50 |
> | Lines uncovered | 9 |
> | Files changed | 3 |
>
> <details>
> <summary>File breakdown (3 files)</summary>
>
> | File | Coverage | Uncovered Lines |
> |------|:--------:|:---------------:|
> | `src/bar.py` | 60.0% | 5, 6, 7, 8, 15, 22 |
> | `src/foo.py` | 85.0% | 13, 27, 42 |
> | `src/baz.py` | 100.0% | |
>
> </details>
>
> ---
> <sub>Posted by <a href="https://github.com/Affanmir/diff-cover-action">diff-cover-action</a></sub>

### PR Comment -- Below Threshold

> ## :red_circle: Diff Coverage: 45.0%
>
> > :x: Below threshold of 80% -- needs 35.0% more coverage
>
> | Metric | Value |
> |--------|------:|
> | **Coverage on diff lines** | **45.0%** |
> | Lines changed | 120 |
> | Lines uncovered | 66 |
> | Files changed | 8 |
>
> <details>
> <summary>File breakdown (8 files)</summary>
>
> | File | Coverage | Uncovered Lines |
> |------|:--------:|:---------------:|
> | `src/payments/stripe.py` | 0.0% | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 (+12 more) |
> | `src/auth/login.py` | 25.0% | 15, 16, 17, 30, 31, 32 |
> | `src/api/routes.py` | 40.0% | 22, 23, 55, 56, 57 |
> | `src/models/user.py` | 50.0% | 8, 9, 44 |
> | `src/utils/cache.py` | 60.0% | 18, 19 |
> | `src/services/email.py` | 70.0% | 33 |
> | `src/config.py` | 80.0% | 5 |
> | `src/middleware.py` | 100.0% | |
>
> </details>
>
> ---
> <sub>Posted by <a href="https://github.com/Affanmir/diff-cover-action">diff-cover-action</a></sub>

### Diff Quality PR Comment

> ## :large_orange_diamond: Diff Quality: 75.0%
>
> > :x: Below threshold of 90%
>
> | Metric | Value |
> |--------|------:|
> | **Quality on diff lines** | **75.0%** |
> | Lines changed | 20 |
> | Lines with violations | 4 |
> | Files changed | 1 |
>
> <details>
> <summary>File breakdown (1 file)</summary>
>
> | File | Quality | Violation Lines |
> |------|:-------:|:---------------:|
> | `src/module.py` | 75.0% | 10, 11, 12, 30 |
>
> </details>
>
> ---
> <sub>Posted by <a href="https://github.com/Affanmir/diff-cover-action">diff-cover-action</a></sub>

### Inline Annotations (appear directly on the PR diff)

```
warning: src/bar.py#5-8 — Lines 5-8 are not covered by tests
warning: src/bar.py#15 — Line 15 is not covered by tests
warning: src/bar.py#22 — Line 22 is not covered by tests
warning: src/foo.py#13 — Line 13 is not covered by tests
```

### Step Summary (in Actions run UI)

The same coverage table also appears in the **Actions > Job Summary** tab so you can see results without opening the PR.

---

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
        uses: Affanmir/diff-cover-action@v1
        with:
          coverage-files: coverage.xml
          fail-under: '80'
```

### Quality Mode

```yaml
      - name: Diff Quality
        uses: Affanmir/diff-cover-action@v1
        with:
          mode: quality
          violations: ruff.check
          fail-under: '90'
```

### Both Coverage and Quality

```yaml
      - name: Diff Coverage
        uses: Affanmir/diff-cover-action@v1
        with:
          coverage-files: coverage.xml
          fail-under: '80'

      - name: Diff Quality
        uses: Affanmir/diff-cover-action@v1
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
        uses: Affanmir/diff-cover-action@v1
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
        uses: Affanmir/diff-cover-action@v1
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
      - uses: Affanmir/diff-cover-action@v1
        with:
          coverage-files: 'unit-coverage.xml integration-coverage.xml'
```

### Glob Patterns

```yaml
      - uses: Affanmir/diff-cover-action@v1
        with:
          coverage-files: '**/coverage*.xml'
```

### Exclude Patterns

```yaml
      - uses: Affanmir/diff-cover-action@v1
        with:
          coverage-files: coverage.xml
          exclude: |
            tests/*
            setup.py
            **/migrations/*
```

### JaCoCo (Java)

```yaml
      - uses: Affanmir/diff-cover-action@v1
        with:
          coverage-files: target/site/jacoco/jacoco.xml
          src-roots: 'src/main/java'
```

### TOML Configuration

```yaml
      - uses: Affanmir/diff-cover-action@v1
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
        uses: Affanmir/diff-cover-action@v1
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
