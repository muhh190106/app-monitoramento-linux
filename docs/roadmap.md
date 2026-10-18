# Increment plan

## Near-term goal

Deliver a usable visitor experience on Windows: open the desktop app, inspect application usage over time, and control when monitoring starts and stops. Each increment must be executable and independently verifiable before expanding to family or team workflows.

| Increment | Outcome | Completion criteria |
| --- | --- | --- |
| **1 · Demo dashboard** | A working visitor interface using sample data. | Open on Windows/Linux; switch English/Portuguese; filter by application, end date, and 1/7/30-day period; show correct charts, totals, and empty states. |
| **2 · Integrated synthetic flow** | Send synthetic events through an API and database into the dashboard. | Scoped client provisioning; validated/idempotent ingestion; SQLite migrations; calendar/time-zone queries; API-backed dashboard; restart, deletion, retention and isolation tests. |
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

## Integration baseline · specified

The [API contract](api.md), [OpenAPI document](contracts/openapi.json) and
[data model](data-model.md) define the shared boundary for the five workstreams.
This completes the contract/design step only. API endpoints, migrations, clients,
and cross-module tests are not implemented yet. Focus and goal routes are reserved
for subsequent work; family/team modeling remains a separate extension.

## Next increment · integrated synthetic flow

1. Database developer: implement versioned SQLite migrations, constraints, indexes,
   transactional storage, explicit synthetic seeds and local deletion/retention.
2. Backend developer: provision a personal workspace/device and scoped tokens
   locally; implement batch ingestion and usage summaries against that repository.
3. Agent developer: supply a synthetic sender with stable event IDs and retry
   handling; add real platform collection only after this flow passes.
4. Extension/focus developer: supply synthetic domain intervals to the same batch
   endpoint and verify separate source credentials; implement browser permissions
   and enforcement later, behind the reserved focus contract.
5. Dashboard/docs/test developer: add the API provider, calendar filters and error
   states; verify end-to-end operation without reading the database from widgets.

Acceptance: a fresh Windows or Linux setup can provision its isolated local
workspace, submit synthetic app/idle/domain observations, restart the backend and
see the same results in the dashboard. Identical retries never increase totals;
invalid/overlapping batches persist nothing; browser observations never inflate
app time; unauthorized devices are rejected. Tests must cover time-zone/daylight-
saving boundaries, empty coverage, retention and deletion replay prevention.
No real collection, automatic startup, hosts/firewall edits or app suspension is
required or permitted as part of setup/tests.

## Priority alignment

The [Sprint 2 specification](product.md) keeps personal focus and family essentials at high priority. Family insight extensions and team workflows follow at medium priority; automatic reports and child achievements follow at low priority. `GR.05` is grouped with team categorization in the source priority table and still needs a standalone priority decision.

## Definition of done

An increment is complete when its acceptance criteria are met, relevant tests pass, the interface is visually checked, and the README accurately states what works. Add platform-specific checks before claiming collector or suspension support. Update this plan after each delivery rather than marking an entire product area complete from a demo.
