# Contributing to STime NOW

Thanks for helping improve STime NOW. The project is in early development; focused changes are easier to review and build on.

## Before you start

Read the [product specification](docs/product.md), [roadmap](docs/roadmap.md), and [architecture](docs/architecture.md). Open an issue to discuss a substantial feature or a new dependency before implementation. Keep public discussions and contributions in English so contributors from different countries can participate.

## Development workflow

1. Fork the repository if you do not have write access, then clone your fork.
2. Create a virtual environment using the [development guide](docs/development.md).
3. Create a branch, for example `git switch -c codex/improve-summary`.
4. Keep the change focused and add tests for behavior changes.
5. Run `python -m unittest discover -s tests -v` and `python -m activity_monitor --demo` with your virtual environment's Python.
6. Open a pull request describing the problem, the change, and how you verified it.

Use clear English names, messages, and documentation. Preserve existing work and avoid unrelated rewrites. Do not rewrite shared Git history.

## Test data and privacy

Use synthetic events only. Never upload activity exports, real window titles, browsing history, credentials, or personal databases. Redact sensitive information from issue reports and screenshots.

## Reporting a bug

Include the operating system, Python version, command, expected result, actual result, and a minimal synthetic example. Use the bug report template. Security reports belong in the private process described in [SECURITY.md](SECURITY.md).

## Working together

Be respectful, give actionable feedback, and explain technical tradeoffs. Critique the work rather than the person. Keep discussions relevant to the project and its users.
