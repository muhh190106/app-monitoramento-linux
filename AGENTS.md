# Project instructions

Activity Monitor is an early-stage personal activity tracking project for Python 3.11+.

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
- Describe implemented features accurately. Collection, storage, and the dashboard are not implemented yet.
