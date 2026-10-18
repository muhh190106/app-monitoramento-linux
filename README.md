<p align="center">
  <img src="docs/assets/banner.svg" alt="Activity Monitor — Understand your time. Own your data." width="100%">
</p>

<p align="center">
  <a href="https://github.com/muhh190106/app-monitoramento-linux/actions/workflows/tests.yml"><img src="https://github.com/muhh190106/app-monitoramento-linux/actions/workflows/tests.yml/badge.svg" alt="Tests"></a>
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white" alt="Python 3.11 or newer">
  <img src="https://img.shields.io/badge/Platforms-Windows%20%7C%20Linux-64748B" alt="Windows and Linux">
  <img src="https://img.shields.io/badge/Status-Early%20development-F59E0B" alt="Early development">
</p>

# Activity Monitor

**Understand how you spend your time, with control over your own data.**

Activity Monitor is a personal activity tracking project being developed for Windows and Linux. Its architecture takes inspiration from [ActivityWatch](https://github.com/ActivityWatch/activitywatch): small collectors, a local data layer, and a clear view of how time is spent.

> **Project status:** early development. The current version includes a tested activity aggregation core and a synthetic demo. Desktop collection, persistent storage, and a dashboard are planned features.

[Quick start](#quick-start) · [Architecture](docs/architecture.md) · [Roadmap](docs/roadmap.md) · [Contributing](CONTRIBUTING.md)

## What works today

- Summarize active time by application from normalized, non-overlapping intervals.
- Exclude idle intervals and validate event values before aggregation.
- Run a reproducible demo with synthetic data and no desktop permissions.
- Test the same core on Windows and Linux with Python 3.11–3.14 in CI.
- Prepare a development environment locally or in Codex Cloud.

## Quick start

Requirements: Git and Python **3.11 or newer**. The application has no third-party runtime dependencies.

```bash
git clone https://github.com/muhh190106/app-monitoramento-linux.git
cd app-monitoramento-linux
```

### Windows · PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m activity_monitor --demo
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

### Linux · Bash

```bash
python3 -m venv .venv
.venv/bin/python -m activity_monitor --demo
.venv/bin/python -m unittest discover -s tests -v
```

The demo prints:

```json
{
  "demo": true,
  "active_seconds": {
    "Editor": 120,
    "Browser": 60
  }
}
```

All demo events are synthetic. The demo reads no activity history and writes no tracking database.

### Optional command-line installation

Inside your virtual environment, run `python -m pip install -e .`. The `activity-monitor --demo` command then provides the same demo. Use your virtual environment's Python executable when it is not activated.

## Designed around personal control

The intended product keeps activity data on the device by default, provides explicit controls for starting and pausing collection, and separates code synchronization from activity data synchronization. Those collection and storage features are still on the roadmap.

The development workflow uses synthetic fixtures. Local databases, activity exports, logs, and credentials belong outside version control. See [Security and privacy](SECURITY.md) for reporting guidance and [Architecture](docs/architecture.md) for the data boundary.

## Development across devices

Keep a separate clone and virtual environment on each computer and operating system. Commit and push your work before switching devices, then pull it into the other clone. The same workflow applies to dual-boot Windows/Linux systems.

For local setup, branches, checks, and cloud preparation, see the [development guide](docs/development.md).

## Roadmap

1. Define the event model and persist normalized events locally.
2. Build Windows and Linux collectors with explicit user controls.
3. Add a local dashboard with timelines, app totals, and categories.
4. Design optional synchronization with documented privacy guarantees.

See the [full roadmap](docs/roadmap.md) for scope and acceptance criteria.

## Contributing

Bug reports, feature discussions, documentation improvements, and focused pull requests are welcome. Start with [CONTRIBUTING.md](CONTRIBUTING.md) and check the roadmap before proposing a large feature.

## Acknowledgments

[ActivityWatch](https://github.com/ActivityWatch/activitywatch) is the architectural inspiration for this project. Activity Monitor is an independent implementation and is not affiliated with ActivityWatch. No ActivityWatch source code is included in this repository.
