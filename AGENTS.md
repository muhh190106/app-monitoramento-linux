# Project instructions

STime NOW is an early-stage desktop screen-time project for individuals, families, and teams. The current core uses Python 3.11+. Read docs/product.md for planned roles and requirements.

- Read the applicable instructions, verify the Git root, and inspect `git status` before editing.
- Preserve user changes. Do not reset, clean, or force push without an explicit request.
- Keep documentation, code, errors, CLI output, and commit messages in English.
- Run tests with `python -m unittest discover -s tests -v`.
- Run the synthetic demo with `python -m activity_monitor --demo`.
- In a cloud/Linux environment, use `.venv/bin/python`; on Windows, use `.venv\Scripts\python.exe`.
- Cloud setup: `bash scripts/setup-cloud.sh` from the repository root.
- The `monitoramento` package is a compatibility entry point for previously configured environments. Keep it functional.
- Never start real collection or configure autostart during setup or tests.
- Use synthetic data in examples, tests, fixtures, and logs.
- Keep platform-specific collectors separate from aggregation and storage.
- Never commit real activity history, local databases, activity exports, or secrets.
- Describe implemented features accurately. The desktop dashboard uses synthetic data. Collection, storage, accounts, and enforcement are not implemented yet.

- Desktop dependencies: `python -m pip install -e ".[desktop]"`. Desktop launch: `python -m activity_monitor --desktop`.
- Use `STIME_DESKTOP_TESTS=1` only in a graphical session or Xvfb when running Tk smoke tests.
