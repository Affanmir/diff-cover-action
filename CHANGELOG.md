# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2026-04-08

### Added
- Shields.io badges in PR comments — `for-the-badge` hero badge with dynamic color for coverage/quality percentage
- Threshold pass/fail badge (`flat-square` style) in PR comments
- Per-file colored status icons (🟢 ≥90%, 🟡 ≥70%, 🔴 <70%)
- Unicode progress bar (`████░░░░`) alongside the badge
- `badge_color` Jinja2 filter mapping percentage to shields.io color scale
- GitHub Pages documentation site with Schema.org structured data
- `llms.txt` for AI tool discoverability (Claude, ChatGPT, Perplexity)
- GitHub Pages deployment workflow
- GitHub Discussions enabled
- 15 repository topics for discoverability

### Changed
- **Breaking**: PR comment layout completely redesigned — comments now use shields.io badges, compact inline metrics, and a new visual hierarchy
- Action name changed to "Diff Cover — PR Coverage & Quality Reports"
- Action branding changed from check-circle/green to shield/blue
- Compact inline metric layout replaces table-based metrics in PR comments
- Step summary template redesigned to match new PR comment style
- Integration test now dogfoods the action — posts real coverage comments on PRs
- README overhauled with comparison table, badges, "Why This Action?" section, and supported tools table

### Fixed
- Action description trimmed to under 125 characters for GitHub Marketplace compatibility
- Converted from Docker to composite action for faster execution

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
