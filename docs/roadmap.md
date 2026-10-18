# Roadmap

This roadmap describes direction rather than release dates. Features are complete only when their acceptance criteria are met.

## Foundation · implemented

- [x] Validated aggregation of active time by application.
- [x] Idle interval exclusion and synthetic CLI demo.
- [x] English project documentation and contribution workflow.
- [x] Unit tests and Windows/Linux CI.
- [x] Python package metadata and an installable CLI.

## Milestone 1 · reliable local data

- [ ] Define timestamp, time zone, device, and interval semantics.
- [ ] Normalize overlapping events and idle transitions.
- [ ] Add local SQLite storage, migrations, and retention.
- [ ] Support export and permanent deletion through explicit user controls.

Acceptance: deterministic tests cover overlap, time zone boundaries, migrations, retention, and deletion using synthetic fixtures.

## Milestone 2 · desktop collection

- [ ] Implement a Windows active application collector.
- [ ] Identify supported Linux desktop sessions and implement capability detection.
- [ ] Add idle detection with documented semantics.
- [ ] Add explicit start, pause, and stop controls.

Acceptance: collectors are opt-in, fail clearly on unsupported sessions, and pass integration checks on documented systems. No keystroke content is needed for the planned activity metrics.

## Milestone 3 · useful insights

- [ ] Build a local dashboard with daily totals and a timeline.
- [ ] Add user-defined application categories.
- [ ] Explain missing data, collection status, and idle time in the interface.
- [ ] Verify keyboard navigation and readable contrast.

Acceptance: users can inspect their day, pause collection, and manage their data without editing configuration files.

## Future exploration

Optional activity synchronization, browser integration, packaging, and installers. These require separate design discussions and must preserve the local data boundary.
