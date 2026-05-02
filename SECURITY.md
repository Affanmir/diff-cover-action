# Security Policy

`diff-cover-action` runs inside your GitHub Actions workflow with access to your repository content and a `GITHUB_TOKEN`. We take security reports seriously and ask that you report them privately so we can fix issues before they are publicly disclosed.

## Supported Versions

Only the latest major version receives security updates.

| Version | Supported          |
| ------- | ------------------ |
| `v2.x`  | :white_check_mark: |
| `v1.x`  | :x: (please upgrade) |

The major-version tag (`@v2`) is moved on each compatible release, so pinning to `@v2` automatically receives security patches. Pinning to a SHA is supported and recommended for hardened environments — see the [release notes](https://github.com/Affanmir/diff-cover-action/releases) for the SHA of each version.

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security reports.**

Use one of the following private channels:

1. **GitHub Security Advisory (preferred)** — open a private report at <https://github.com/Affanmir/diff-cover-action/security/advisories/new>. This keeps the discussion private and lets us coordinate a fix and release together.
2. **Email** — `affan.amir.mir@gmail.com` with the subject prefix `[diff-cover-action security]`.

Please include:

- A description of the vulnerability and its impact
- Steps to reproduce (a minimal repo or workflow snippet helps)
- Affected version(s) or commit SHA
- Any suggested mitigation, if you have one

## What to Expect

- **Acknowledgement**: within 5 business days.
- **Initial assessment**: within 10 business days, including whether we consider the report in scope and a rough remediation timeline.
- **Fix and release**: severity-dependent. Critical issues are prioritised; lower-severity issues are bundled into the next regular release.
- **Public disclosure**: typically once a fix has shipped and downstream users have had a reasonable upgrade window (target: 30 days after release for high/critical, sooner for low-impact). We will credit the reporter unless anonymity is requested.

This is a solo-maintained open-source project — response times are best-effort, not contractual.

## Scope

**In scope**

- The action code in this repository (`src/`, `entrypoint.py`, `action.yml`, `Dockerfile`, `templates/`)
- The published Docker image used at runtime
- Direct dependencies declared in `requirements.txt`
- Documentation that could mislead users into an insecure configuration

**Out of scope**

- Vulnerabilities in transitive dependencies that have no exploitable path through this action (please report those upstream)
- Misconfiguration in *consumer* workflows (e.g. a user passing `pull_request_target` with insufficient hardening); we will document safer patterns but cannot patch them centrally
- Issues in [`diff_cover`](https://github.com/Bachmann1234/diff_cover) itself — please report upstream
- Denial-of-service via unbounded user input that only impacts the user's own runner

## Hardening Recommendations for Consumers

If you are using this action in security-sensitive workflows:

- Pin to a commit SHA (`uses: Affanmir/diff-cover-action@<sha>`) rather than a moving tag
- Grant the minimum required permissions (`contents: read`, `pull-requests: write`)
- Avoid `pull_request_target` unless you understand the [security implications](https://securitylab.github.com/research/github-actions-preventing-pwn-requests/)
- Review the [release notes](https://github.com/Affanmir/diff-cover-action/releases) before upgrading the major-version tag

Thank you for helping keep `diff-cover-action` and its users safe.
