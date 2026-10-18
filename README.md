<p align="center">
  <img src="docs/assets/banner.svg" alt="STime NOW — Screen time, focus, and shared insights." width="100%">
</p>

# STime NOW

Desktop screen-time management for personal focus, families, and teams.

STime NOW is being developed for Windows and Linux to help people understand application usage, manage distractions, and share relevant insights through role-specific dashboards.

**In development.** The repository currently includes an activity aggregation core and a synthetic CLI demo. Desktop monitoring, app suspension, accounts, and dashboards are planned.

## Product scope

- **Personal focus:** explore usage charts and suspend selected apps during focus sessions.
- **Families:** connect children through a family code, set screen-time limits, and review temporary access requests.
- **Teams:** organize members, categorize applications, and review usage summaries and daily reports.

The planned interface supports **English and Portuguese**, with charts powered by pandas and matplotlib. See the [product specification](docs/product.md) for roles and requirements, and the [roadmap](docs/roadmap.md) for delivery priorities.

## Run the demo

Requires Git and Python 3.11+. The current demo has no third-party runtime dependencies and uses synthetic data only.

```bash
git clone https://github.com/muhh190106/app-monitoramento-linux.git
cd app-monitoramento-linux
```

**Windows · PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m activity_monitor --demo
```

**Linux · Bash**

```bash
python3 -m venv .venv
.venv/bin/python -m activity_monitor --demo
```

The demo reports 120 active seconds for Editor and 60 for Browser. It does not collect desktop activity.

## Documentation

[Product specification](docs/product.md) · [Architecture](docs/architecture.md) · [Development](docs/development.md) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md)

The Python package remains `activity_monitor`, and the installable command is `activity-monitor`. Setup, installation, and test commands are documented in the development guide.

## Acknowledgments

Inspired by [ActivityWatch](https://github.com/ActivityWatch/activitywatch). STime NOW is an independent project; no ActivityWatch source code is included.
