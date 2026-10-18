# Product specification

STime NOW is a desktop screen-time management application for personal use, families, and work teams. It combines usage insights with focus sessions and role-specific access to activity data.

This specification summarizes the Sprint 2 requirements. Story identifiers are retained for traceability. The requirements below describe the full planned product. The current increment implements a visitor desktop dashboard, English/Portuguese messages, and pandas/matplotlib charts using synthetic data. Live monitoring, suspension, persistence, accounts, and family/team workflows remain planned.

## User roles

| Role | Access | Intended capabilities |
| --- | --- | --- |
| Visitor (`V`) | No account required | View personal usage and configure focus sessions. |
| Parent or guardian (`PR`) | Username and password | Manage a family, set child limits, review usage, and decide access requests. |
| Child (`F`) | Join a family using a code; no username/password login | View personal usage, remaining time, restrictions, and achievements; request temporary access. |
| Manager (`GR`) | Username and password | Manage a team, inspect individual and aggregate usage, classify apps, and review reports. |
| Team member (`CB`) | Authenticated account and team code | View personal usage and provide context for activity included in daily reports. |

A person with multiple roles must be able to select the appropriate profile. Team members must only see their own activity; manager access is scoped to the managed team, and guardian access to the linked family. A child cannot change the guardian's limits or restriction policies.

## Functional requirements

### Personal usage and focus

`V.01` provides interactive usage charts, application icons and totals, and period filters such as day, week, and month. Missing data and missing monitoring permission must have clear states. A usage chart is generated at the end of each session (`RNG-4`).

`V.02` lets a user choose applications and a focus period. After the necessary permission and confirmation, selected applications are suspended or restricted for that period and restored automatically when it ends. Denied permission and an empty selection must be handled explicitly.

### Accounts and access

`U.01` collects full name, email, username, password, and the parent/guardian or manager profile. Email and username must be unique; successful registration leads to login. `U.02` authenticates credentials, handles invalid attempts, and routes the user to the selected authorized profile.

### Families

- `PR.01` / `F.01`: generate and rotate a unique family code; validate it before linking a child. A child can belong to only one family at a time. The guardian sees updated membership immediately and confirms member removal. Invalid, expired, or revoked codes must not create a link.
- `PR.02`: define per-child daily usage limits, selected apps to limit or suspend, and optional schedules. Apply restrictions when the limit is reached. Record the actor and timestamp of every policy change.
- `PR.03` / `F.02`: show the appropriate usage dashboard, period filters, active rules, remaining daily time, and a warning as the limit approaches. Child access is read-only for policies.
- `F.03`: allow one pending temporary access request per restricted app, with a reason and requested duration. The app stays blocked pending a decision. Approval grants temporary access; expiry restores the restriction. Approved exception time does not consume the global daily allowance.
- `F.04`: show read-only streaks, completed focus hours, and comparisons between configured limits and actual usage. Children cannot manually edit or reset these metrics.

### Teams

- `GR.01` / `CB.01`: create named teams and rotatable join codes. An authenticated member can join only one active team and must appear immediately in the manager's member list. Invalid codes are rejected. Member removal and voluntary departure require confirmation.
- `GR.02` / `CB.02`: managers can switch between individual and team totals and filter periods. Members see their own application usage and manager-defined categories. Empty results have a clear explanation.
- `GR.04`: provide editable default categories such as Productive, Communication, and Leisure/Distraction. Apply the current classification across team charts and reports, including historical views as described in `UC-11`.
- `GR.05`: create subgroups or projects, associate team members, and filter dashboards by subgroup. Deleting a subgroup preserves team membership and individual usage history.
- `GR.03` / `CB.03`: make daily reports available to the manager at the end of a member's shift or session, with active time, category breakdowns, and submitted explanations. Explanations can be submitted before report closure and become immutable once confirmed. Reports support date and member filters.

## Quality and platform requirements

| ID | Requirement |
| --- | --- |
| `RNF-1` | Desktop application. Windows and Linux are the repository's target platforms. |
| `RNF-2` | Python charts using pandas and matplotlib. These dependencies are used by the optional desktop dashboard; the lightweight CLI demo does not require them. |
| `RNF-3` | HTTPS for network communication. |
| `RNF-4` | Layouts that adapt to different screen sizes. |
| `RNF-5` | Accessibility guided by WCAG; the target version and conformance level remain to be defined. |
| `RNF-6` | At least English and Portuguese in the product interface. |
| `RNF-7` | An installed device agent for monitoring and app suspension, integrated with the application backend. |

`RNG-1` requires role-specific screens and authorization. `RNG-2` requires friendly handling of registration conflicts, denied access, and technical failures, with diagnostic logging. Logs must not expose passwords or raw private activity. `RNG-3` requires example database data for implemented stories; development fixtures must remain synthetic.

## Delivery priorities

| Priority | Stories |
| --- | --- |
| High | `V.01`, `V.02`, `U.01`, `U.02`, `PR.01`, `F.01`, `PR.02` |
| Medium | `PR.03`, `F.02`, `F.03`, `GR.01`, `CB.01`, `GR.02`, `GR.04`, `CB.02`, `CB.03` |
| Low | `GR.03`, `F.04` |

The source priority table groups subgroup organization under `GR.04`; the detailed story is `GR.05`. The roadmap keeps subgroup work beside team categorization, with its standalone priority awaiting confirmation. Member explanations (`CB.03`) depend on a report lifecycle even though automatic report delivery (`GR.03`) has lower priority.

## Decisions to resolve before implementation

- **Team member enrollment:** members must authenticate, but the registration story currently offers only guardian and manager profiles. Define invitation and account creation for members.
- **Account and device identity:** define multi-role account assignment and persistent identification for children who join without credentials, including unlinking and device replacement.
- **Policy enforcement:** specify supported Windows/Linux sessions, required permissions, safe suspension/restoration behavior, and how family policies coexist with personal focus sessions.
- **Service boundaries:** the first integration now selects Tkinter, a local backend, SQLite and scoped local client tokens; see [API](api.md) and [data model](data-model.md). These implementation decisions do not come from Sprint 2 itself. Hosted deployment, multi-user trust and family/team sharing remain unresolved.

## Use-case map

`UC-01` usage dashboard; `UC-02` focus suspension; `UC-03` registration; `UC-04` login; `UC-05` family management; `UC-06` limits and policies; `UC-07` child usage; `UC-08` family enrollment; `UC-09` team management; `UC-10` team insights; `UC-11` categories and subgroups; `UC-12` daily reports; `UC-13` temporary access; `UC-14` team enrollment.
