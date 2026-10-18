# Architecture

STime NOW is planned as a desktop application with an installed device agent and an application backend. The agent monitors usage and applies authorized suspension policies; the backend owns account, family, team, policy, and reporting workflows.

The aggregation core, CLI demo, and a visitor desktop dashboard with synthetic data are implemented. The following diagram describes the target architecture, not running services.

```mermaid
flowchart LR
    A[Device agent] -->|Usage events| B[Application backend]
    E[Browser extension] -->|Domain events| B
    B -->|Authorized focus and limit policies| A
    B -->|Personal focus snapshot| E
    B <--> D[Data storage]
    U[Desktop interface] <--> B
    B -->|Aggregated reporting data| U
    U --> C[matplotlib charts]
```

## Component boundaries

**Device agent:** Windows/Linux capability detection, permission-aware collection, idle state, and application suspension/restoration. Desktop session support and enforcement semantics must be defined before implementation.

**Application backend:** owns ingestion, validation, aggregation and personal focus lifecycle in the first integration. The baseline is one local backend per personal workspace, with revocable client tokens. Hosted authentication, family/team codes, membership, temporary access and report closure are later extensions. Non-loopback communication requires HTTPS.

**Data storage:** SQLite is selected for the first local integration, outside the repository. The [data model](data-model.md) defines devices, observations, goals and focus rules. Accounts, memberships, guardian policies and team reports need a later model extension.

**Desktop interface:** role-specific dashboards, day/week/month filters, focus controls, family limits, request review, and team reports. Charts use pandas and matplotlib as required by the product specification. Layouts must adapt to screen size, support English/Portuguese, and account for accessibility.

## Current local demo interface

`activity_monitor.summary.summarize` accepts normalized, non-overlapping intervals:

```python
{"app": "Editor", "seconds": 120, "afk": False}
```

| Field | Type | Meaning |
| --- | --- | --- |
| `app` | Non-empty string | Application identifier or display name |
| `seconds` | Finite, non-negative number | Interval duration |
| `afk` | Boolean | Whether the interval represents idle time |

The function returns active seconds grouped by application. Invalid values raise `ValueError`; missing fields raise `KeyError`. This older helper has no timestamp or device validation and is not the ingestion contract. The separate desktop reporting module validates non-overlapping synthetic intervals using naive local timestamps.

## Integration contracts

The [API contract](api.md), [OpenAPI document](contracts/openapi.json), and
[entity model](data-model.md) define the next implementation boundary. They are
specifications, not implemented services. UTC intervals replace naive timestamps
at the future API boundary. Desktop and browser observations remain separate;
browser time is intersected with desktop active time rather than added to it.
Backend reports use calendar periods and IANA time zones. The desktop consumes
those results and renders charts without duplicating aggregation.

## Data and authorization

Visitor access is local to the user's own usage. Guardian access is scoped to linked children; manager access to the managed team. Team members view only their own records. Device trust, data retention, sharing, and revocation must be specified before enabling these workflows.

Use synthetic fixtures in development, CI, and cloud workspaces. Activity data does not belong in Git. Code synchronization through GitHub is independent of the product's future agent/backend data exchange.

## Technical names

The product name is **STime NOW**. The repository URL, `activity_monitor` Python package, and `activity-monitor` CLI retain their existing names. The `monitoramento` package remains a compatibility entry point for existing environments.

## First desktop slice

`desktop.py` depends on a reporting interface rather than platform collection APIs. `reporting.py` clips typed intervals into period buckets and uses pandas to derive totals; `charts.py` turns the report into a matplotlib figure. The current provider generates deterministic sample data. The next increment will implement the API/storage flow and introduce an API adapter at this boundary. It must handle UTC/time-zone semantics explicitly instead of stripping time-zone information to reuse the demo implementation.

Tkinter supplies the initial desktop shell. This is a starting toolkit decision for the visitor slice, not a commitment to the final account/backend topology. Full accessibility and platform coverage require dedicated follow-up checks.
