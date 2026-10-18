# Development guide

## Local environment

Use Git and Python 3.11+. Create a virtual environment in the repository:

```bash
python -m venv .venv
```

On Linux, use `python3` if `python` is not available. Call `.venv/bin/python` on Linux or `.venv\Scripts\python.exe` on Windows for the commands below:

```bash
python -m unittest discover -s tests -v
python -m activity_monitor --demo
python -m activity_monitor --version
```

For an editable installation and the `activity-monitor` command:

```bash
python -m pip install -e .
activity-monitor --demo
```

No external runtime dependencies are required. Installation uses setuptools as a build dependency.

## Working across devices

Use an independent clone and virtual environment on each operating system, including dual-boot computers. Before starting, inspect `git status`. When the working tree is clean, update with `git pull --ff-only`. Create a branch for your task, commit reviewed changes, and push before switching devices.

```bash
git switch -c codex/describe-your-change
git add path/to/changed-file
git commit -m "Describe the change in English"
git push -u origin HEAD
```

Open a pull request to review and integrate the change. On another device, fetch and switch to the branch. Uncommitted work and local data are not synchronized through GitHub.

## Codex Cloud

The repository contains a reproducible setup command:

```bash
bash scripts/setup-cloud.sh
```

It creates `.venv`, runs unit tests, and executes the synthetic demo. It does not need credentials, external services, or desktop permissions. New cloud environments can use this command as their installation step and the test/demo commands as startup checks.

Existing environments using `python -m monitoramento --demo` remain supported by the compatibility package. The English demo output uses `Browser` as its sample application name.

The product name is STime NOW. Technical package and command names remain unchanged. Product localization in English and Portuguese, pandas/matplotlib charts, and the installed device agent are planned requirements; the synthetic CLI does not implement these features yet.

## Repository layout

```text
activity_monitor/        Portable core and English CLI
monitoramento/          Compatibility entry points
tests/                  Synthetic unit and CLI tests
scripts/                Cloud setup
docs/                   Architecture, roadmap, and development guide
.github/                CI and contribution templates
```

## Data hygiene

Keep databases, exports, logs, and credentials outside version control. The ignore rules provide a starting point; inspect `git diff --cached` before committing. Use synthetic examples in issues, tests, documentation, and cloud tasks.
