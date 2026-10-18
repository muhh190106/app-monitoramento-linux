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

It creates `.venv`, installs the desktop extra, runs headless unit/chart tests, and executes the synthetic CLI demo. Tk window checks require a graphical display and are handled separately in CI. It does not need credentials, external services, or desktop permissions. New cloud environments can use this command as their installation step and the test/demo commands as startup checks.

Existing environments using `python -m monitoramento --demo` remain supported by the compatibility package. The English demo output uses `Browser` as its sample application name.

The product name is STime NOW. Technical package and command names remain unchanged. Desktop mode now includes English/Portuguese messages and pandas/matplotlib charts with synthetic data. The installed monitoring agent is still planned.

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

## Desktop development

Install optional dependencies with `python -m pip install -e '.[desktop]'` and launch with `python -m activity_monitor --desktop`. Add `--language pt-BR` for Portuguese. The existing JSON demo stays dependency-free.

`reporting.py` contains typed intervals and pandas aggregation; `charts.py` renders matplotlib figures; `desktop.py` contains Tkinter widgets; `i18n.py` contains interface translations. Synthetic intervals are generated once at launch for the local current date and preceding 29 days. Filters never regenerate the dataset.

Reporting currently accepts naive local wall-clock datetimes from the synthetic provider, rejects overlapping intervals, clips period boundaries, and splits intervals at chart bucket boundaries. It does not yet define multi-device or daylight-saving behavior for real collection.

Run all headless tests with the desktop extra installed. For Tk smoke tests, set `STIME_DESKTOP_TESTS=1` in a graphical session. On headless Linux use `xvfb-run -a env STIME_DESKTOP_TESTS=1 python -m unittest discover -s tests -v`. In Windows PowerShell, set `$env:STIME_DESKTOP_TESTS = '1'` before running the same unittest command. CI exercises both modes. Core-only installations skip optional chart/report tests.

The desktop provider is in memory. It does not request monitoring permissions, inspect running apps, save activity, or run at startup. Date filters show historical sample data; dates outside the sample range demonstrate the empty state.
