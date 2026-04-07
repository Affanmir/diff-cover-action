# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-04-08

### Added
- Issue templates (bug report and feature request)
- Pull request template with checklist
- CODEOWNERS file

### Fixed
- Hyphenated action inputs (e.g., `coverage-files`, `compare-branch`) not being read due to env var name mismatch
- Docker Build CI job failing because verify step appended args to ENTRYPOINT instead of overriding it
- Git `safe.directory` error when Docker actions mount the runner workspace
- GHCR image push failing due to uppercase characters in repository name
- Ruff lint violations (import sorting, list concatenation, ambiguous variable names, line length)
- Ruff formatting across 9 source and test files
- Mypy type annotation error in fork PR detection

## [1.0.0] - 2026-04-07

### Added
- Initial release of diff-cover-action
- Coverage mode: run diff-cover on PR changes with full CLI parity
- Quality mode: run diff-quality with all supported violation tools
- Idempotent PR comments (create or update existing)
- Inline annotations on uncovered/violating lines
- Step summary in GitHub Actions UI
- Structured outputs (coverage %, violations, threshold status)
- Shields.io endpoint badge generation
- Automatic shallow clone repair (progressive fetch strategy)
- Full input/output specification in action.yml
- Unit test suite (75 tests)
- CI workflows: lint, test, Docker build, integration test
- Release workflow with pre-built Docker images on GHCR
