# Roadmap

Delivery follows the [product specification](product.md) and its Sprint 2 priorities. All milestones below are planned; only the aggregation core, synthetic CLI demo, packaging, and automated checks exist today.

## 1. Desktop foundation

Define the event/session model, device identity, storage, and agent/backend boundary. Add permission-aware collection, synthetic database seeds, and a shared dashboard using pandas and matplotlib. Establish English/Portuguese localization, accessible components, and adaptable layouts from the start.

Supports `V.01`, `RNG-2`–`RNG-4`, and `RNF-1`–`RNF-7`.

## 2. Focus and family essentials · high priority

Implement focus sessions with automatic app restoration (`V.02`), registration and profile selection (`U.01`, `U.02`), family codes and enrollment (`PR.01`, `F.01`), and guardian-defined app limits with an audit trail (`PR.02`).

Acceptance: supported platforms enforce authorized rules, restore access after focus expiry, reject invalid enrollment, and prevent children from changing guardian policies.

## 3. Family and team insights · medium priority

Add guardian/child dashboards and limit notifications (`PR.03`, `F.02`), temporary access decisions (`F.03`), team enrollment (`GR.01`, `CB.01`), personal/team dashboards (`GR.02`, `CB.02`), application categories (`GR.04`), and member explanations (`CB.03`). Keep subgroup work (`GR.05`) beside categories; its individual priority needs confirmation.

Acceptance: role-scoped views expose only authorized records; temporary access expires correctly; team membership and historical usage remain consistent. Define the report closure model needed by explanations before implementing `CB.03`.

## 4. Reports and achievements · low priority

Deliver automatic manager reports and report history (`GR.03`), plus read-only goals and streaks for children (`F.04`).

Acceptance: daily reports include confirmed explanations, enforce closure rules, and support date/member filters. Achievement calculations are reproducible from synthetic fixtures.

## Delivery checks

Each milestone needs behavior tests, role authorization checks, relevant Windows/Linux integration checks, English/Portuguese interface review, and accessibility verification. Planned collector and suspension behavior must be demonstrated on supported desktop sessions before being described as available.
