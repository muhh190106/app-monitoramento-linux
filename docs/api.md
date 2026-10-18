# API contract

Status: design baseline v1. No HTTP server or client is implemented yet. The
machine-readable contract is [OpenAPI](contracts/openapi.json); storage and
relationships are defined in the [data model](data-model.md).

## Scope and ownership

The first integration runs one local backend per user workspace, with SQLite
outside the repository. The desktop, collector, and extension use the same API;
none accesses the database directly. This is a development topology, not a
hosted family/team service. Hosted access, account enrollment, and role-based
sharing require a later contract revision before deployment.

All routes use `/api/v1`. JSON field names and error messages are English.
The contract uses [OpenAPI 3.1](https://spec.openapis.org/oas/v3.1.0.html).

| Owner | Boundary |
| --- | --- |
| Desktop agent | Observe permitted foreground/idle intervals; queue and retry stable event IDs; report unsupported capabilities. |
| Browser extension and focus | Observe active domains; send separate browser intervals; apply supported focus rules with visible permission/status handling. |
| Backend | Authenticate clients, validate events, resolve conflicts, aggregate usage, own focus lifecycle and authorization. |
| Database | Enforce identities, references and uniqueness; persist transactions; supply indexed queries and migrations. |
| Dashboard and quality | Consume API responses, render charts, handle errors/empty states, maintain cross-module acceptance checks. |

## Identity and transport

- Each local installation has a workspace UUID and registered device UUIDs.
  A workspace belongs to one local user; it is not a family or team.
- Devices must be explicitly paired in the local setup before ingestion. Device
  IDs are server-issued. Reinstalling or revoking a device invalidates its tokens.
- Every request requires a bearer token. Store only token hashes on the backend.
  Agent/extension tokens are restricted to their device, source, event submission,
  and reading its effective focus policy. Desktop tokens can query the workspace
  and manage its own goals/focus/rules. The server derives workspace access from
  the token, never from a submitted owner ID.
- Pairing/token issuance is not an exposed endpoint in this contract. The next
  increment must provide an explicit local provisioning command before running
  the flow; never ship a shared token or put credentials in examples/Git.
- Bind development services to loopback. HTTP is permitted only on loopback for
  isolated local development; non-loopback traffic requires HTTPS. Production
  must meet `RNF-3`. CORS permits explicit extension origins only, never `*` with
  credentials. Neither CORS nor a loopback address replaces token validation.

## Usage events

`POST /api/v1/events/batch` accepts 1–500 closed intervals from one device and
one source (`desktop` or `browser`). A maximum request body of 1 MiB applies.
These are raw observations, not aggregate totals. Events contain:

| Field | Meaning |
| --- | --- |
| `event_id` | Client-generated UUID, stable across retries. |
| `started_at`, `ended_at` | UTC RFC 3339 timestamps ending in `Z`, millisecond precision or whole seconds; half-open interval `[start, end)`. |
| `state` | `active` or `idle`. Browser events must be `active`; desktop owns idle detection. |
| `app_id`, `app_name` | Stable platform application key and display label, required for active desktop events. Omit both for idle. |
| `domain` | Required only for browser events: lowercase ASCII hostname without scheme, port, path, query, fragment or trailing dot. |

Application keys are platform-qualified, for example `windows:sample-editor.exe`
or `linux:org.example.SampleEditor`. Do not submit executable paths, command
lines, window titles, page titles, URLs, keystrokes, or browser content. Normalize
internationalized hostnames to their ASCII form before submission. Domains match
exactly; subdomains are different values in v1.

```json
{
  "device_id": "00000000-0000-4000-8000-000000000001",
  "source": "desktop",
  "events": [{
    "event_id": "00000000-0000-4000-8000-000000000002",
    "started_at": "2026-10-01T12:00:00Z",
    "ended_at": "2026-10-01T12:01:00Z",
    "state": "active",
    "app_id": "windows:sample-editor.exe",
    "app_name": "Sample Editor"
  }]
}
```

Validation and retry rules:

- Require `start < end`, duration at most 60 seconds, and end no more than five
  minutes ahead of server UTC. Long observations must be split. Reject naive
  timestamps, unknown fields, unknown/revoked devices and mismatched source tokens.
- Use a configurable 90-day history retention window initially. Reject older
  events with `outside_retention`; queued data is not allowed to recreate deleted
  history. Record reception time separately from observation time.
- Intervals cannot overlap within `(device_id, source)`, including inside a batch.
  Touching boundaries are allowed. Compare persisted intervals transactionally.
  Reject conflicts; do not silently trim, sum or resolve them by arrival order.
- `event_id` is unique within a device. An identical retry is a duplicate success;
  the same ID with changed normalized content is `409 event_conflict`.
- Within one batch, reject repeated event IDs with `422 duplicate_batch_id`,
  even if identical. Receipt arrays contain unique IDs and are disjoint.
- A batch is atomic: validate everything before inserting anything. A `200`
  response contains `accepted_event_ids` and `duplicate_event_ids`. A failed batch
  stores nothing, including new events beside a conflict. Serialize conflicting
  writes so simultaneous requests cannot bypass the overlap checks.
- Retry the same IDs after network failures and `429`/`503`, using bounded
  exponential backoff and `Retry-After`. Do not blindly retry validation failures.
  Offline queues stay local, outside Git, and are bounded by retention.

## Dashboard queries

`GET /api/v1/usage/summary` returns totals, timeline buckets and ranking in one
response. Required query parameters are `device_id`, `date` (`YYYY-MM-DD`),
`period` (`day`, `week`, `month`) and `timezone` (IANA identifier). Optional
`dimension=application|domain` defaults to `application`.

- A day is the selected calendar day; a week is Monday through Sunday containing
  it; a month is its calendar month. These are not rolling 7/30-day windows.
- Resolve calendar boundaries in the requested time zone, then convert to UTC.
  Clip intervals to `[start, end)` and split at bucket boundaries. Daylight-saving
  days can contain 23 or 25 hours. Emit zero-valued empty buckets.
- Daily reports use hourly buckets; weeks/months use daily buckets. Each bucket
  exposes UTC `started_at` and `ended_at`; the dashboard localizes labels, including
  repeated clock hours. Totals and durations are seconds, never rounded minutes.
- Application totals and idle time come only from desktop events. Domain totals
  intersect browser intervals with desktop active intervals on the same device.
  Missing desktop context contributes no domain time. Browser time is a breakdown
  of desktop time, never added to it. Do not infer browser/app correlation beyond
  this intersection in v1; browser capability/visibility gaps remain gaps.
- Domain reports expose `idle_seconds=0`; their active total equals observed,
  intersected domain time. Ranking `share` is a fraction of the selected
  dimension's active total; zero total produces an empty ranking.
- Rank by seconds descending, then resource key ascending for ties. No cross-device
  summation in v1: simultaneous devices require a separate future policy.
- Reports include `coverage.desktop_seconds` (observed active plus idle) and
  `coverage.browser_seconds` (intersected domain time). Zero coverage means no
  observations, not zero real usage. Coverage can legitimately differ by source.
- Empty results return `200`, zero totals, an empty ranking and zero buckets for
  the entire period. Invalid time zones/dates return `422`.

The existing demo uses naive local datetimes and rolling 1/7/30-day filters.
It remains unchanged until an API adapter replaces its provider. Never strip
time-zone information to feed live events into the old reporting implementation.
The backend must own the new aggregation semantics; the UI must not recompute them.

## Goals, focus, and rules

These endpoints reserve the shared interface for later increments. They are not
part of the first ingestion/reporting implementation's completion criteria.

| Method and route | Contract |
| --- | --- |
| `GET /goals?device_id=…` | List goals with server-calculated progress for the current period in each goal's time zone. |
| `POST /goals` | Create an active-time maximum for a day/week/month, for all apps or one exact app/domain. Goals inform; they do not enforce restrictions. |
| `DELETE /goals/{goal_id}` | Delete a workspace-owned goal; return `204`. |
| `GET /focus-sessions?device_id=…` | Desktop UI lists active and historical sessions, newest first. Device tokens can read only their own active session and its immutable rule snapshot. |
| `POST /focus-sessions` | Start one device-scoped session now, with duration 60–14400 seconds and selected rule IDs. Snapshot rules and return `201`. |
| `POST /focus-sessions/{focus_id}/cancel` | Cancel and return the session; repeating cancellation is safe. |
| `GET /rules?device_id=…` | Desktop UI lists device rules; unavailable to agent/extension tokens. |
| `POST /rules` | Create an exact app/domain rule: `block` or `allow`. |
| `DELETE /rules/{rule_id}` | Delete a rule; existing focus snapshots remain unchanged. |

All routes above are relative to `/api/v1`. List routes use `limit` (1–100,
default 50) and an opaque `cursor`; responses contain `items` and `next_cursor`
(`null` when finished). Cursor and ordering are stable under concurrent inserts;
an invalid cursor returns `422`. Goal/rule lists order by creation time and ID
descending, as do focus lists.

Only one running focus session is allowed per device (`409 focus_conflict`).
Every selected rule must belong to that same authorized device; missing or
out-of-scope rule IDs return `404`, and duplicate IDs return `422`.
States are `active -> completed` on expiry or `active -> cancelled` explicitly;
terminal states never become active again. Expiry must be evaluated on reads and
background reconciliation, including after backend restart. Cancellation of an
already completed session returns it unchanged. The backend supplies UTC start/end
times; clients must restore permitted restrictions locally on expiry even when
offline. A backend session does not prove enforcement succeeded.

Rules are exact matches with no wildcards. An explicit allow rule overrides a
block rule for the same target within this personal focus snapshot. Absence of a
rule allows usage. App blocking and domain blocking are different capabilities:
an extension cannot enforce app rules, and an allowed domain cannot override a
blocked browser application. Unsupported targets must be disclosed before start.
Guardian/team policy precedence is outside v1 and must not inherit this personal
allow-over-block rule implicitly. No hosts/firewall changes or process suspension
are performed by the current prototype.

Creation endpoints for goals/rules/focus require `Idempotency-Key` (UUID) scoped to
workspace and route. Save request hash plus response atomically for 24 hours;
identical retries return the original result, changed payload returns `409`.
Clients must reconcile resource state after key expiry instead of automatic retry.

## Errors and acceptance

Errors use `{"error":{"code":"invalid_event","message":"…","field":"events[0].ended_at"}}`.
`field` may be null. Never echo tokens or activity payloads in logs/errors.
Use `401` for missing/invalid tokens, `403` for source/capability restrictions,
`404` for absent or out-of-workspace resources, `409` for conflicts, `413` for
oversize bodies, `422` for invalid fields, `429` for throttling, and `503` for
temporary unavailability. Client messages may be localized using stable codes.

The first integrated increment must demonstrate synthetic event submission,
duplicate replay, atomic overlap rejection, restart persistence, timezone-aware
reports, empty results, and dashboard consumption of the API. It must also test
source/device isolation, browser/desktop overlap without double counting, UTC
midnight and daylight-saving boundaries, and deletion/retention behavior.
