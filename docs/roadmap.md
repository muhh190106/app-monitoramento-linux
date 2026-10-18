# Increment plan

## Near-term goal

Deliver a usable visitor experience on Windows: open the desktop app, inspect application usage over time, and control when monitoring starts and stops. Each increment must be executable and independently verifiable before expanding to family or team workflows.

| Increment | Outcome | Completion criteria |
| --- | --- | --- |
| **1 · Demo dashboard** | A working visitor interface using sample data. | Open on Windows/Linux; switch English/Portuguese; filter by application, end date, and 1/7/30-day period; show correct charts, totals, and empty states. |
| **2 · Local history** | Store and retrieve normalized usage events. | SQLite repository and migrations; synthetic seed; history survives restart; date filters, deletion, and data location are tested. |
| **3 · Windows collection** | Capture real foreground-app and idle intervals after explicit activation. | Start/pause/stop controls; no collection before activation; persistence; no duplicate/overlapping time; visible status and platform integration checks. |
| **4 · Focus sessions** | Restrict selected apps for a defined period (`V.02`). | Permission checks, explicit confirmation, safe restoration on expiry/failure, and tests on supported Windows sessions. |
| **5 · Accounts and families** | Profile selection, family enrollment, and guardian limits. | Unique accounts, scoped access, valid/revoked codes, policy audit trail, and child restrictions (`U.01`, `U.02`, `PR.01`, `F.01`, `PR.02`). |
| **6 · Family and team insights** | Extended family dashboards, temporary access, teams, and categories. | Authorized views, expiring exceptions, membership rules, report closure model, and subgroup history preservation. |
| **7 · Reports and achievements** | Automatic daily reports and read-only goals. | Immutable confirmed explanations, correct report filters, deterministic streak calculations (`GR.03`, `F.04`). |

## Increment 1 · implemented

- Visitor dashboard built with Tkinter, pandas, and matplotlib.
- Active/idle metrics, application ranking, and an activity timeline.
- Application, date, and 1/7/30-day filters.
- English and Brazilian Portuguese interface messages.
- Empty-data and invalid-date states; readable labels and keyboard-focusable controls.
- Synthetic data only: no collector, database, account, or background service.
- Unit, chart, and desktop smoke checks. Native Linux collector support and a full accessibility audit remain future work.

This is a demonstrable slice of `V.01`, not completion of live usage monitoring. Desktop UI checks do not establish support for Linux collectors or app suspension.

## Next increment · local history

Define a storage contract before adding a collector: timestamp/time zone rules, device and session identity, event boundaries, retention, and a user data directory outside the repository. Implement SQLite access behind that contract so the dashboard can replace its synthetic provider without embedding storage logic in widgets.

## Priority alignment

The [Sprint 2 specification](product.md) keeps personal focus and family essentials at high priority. Family insight extensions and team workflows follow at medium priority; automatic reports and child achievements follow at low priority. `GR.05` is grouped with team categorization in the source priority table and still needs a standalone priority decision.

## Definition of done

An increment is complete when its acceptance criteria are met, relevant tests pass, the interface is visually checked, and the README accurately states what works. Add platform-specific checks before claiming collector or suspension support. Update this plan after each delivery rather than marking an entire product area complete from a demo.
