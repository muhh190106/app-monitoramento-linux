CREATE TABLE workspaces (
    id TEXT PRIMARY KEY, name TEXT NOT NULL CHECK(length(trim(name)) > 0),
    timezone TEXT NOT NULL, retention_days INTEGER NOT NULL CHECK(retention_days > 0),
    created_at INTEGER NOT NULL
) STRICT;
CREATE TABLE devices (
    id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL CHECK(length(trim(name)) > 0),
    platform TEXT NOT NULL CHECK(platform IN ('windows','linux')),
    ingestion_not_before INTEGER NOT NULL, created_at INTEGER NOT NULL, revoked_at INTEGER,
    UNIQUE(id, workspace_id)
) STRICT;
CREATE TABLE applications (
    id TEXT PRIMARY KEY, app_key TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL CHECK(length(trim(display_name)) > 0),
    platform TEXT NOT NULL CHECK(platform IN ('windows','linux')),
    CHECK(app_key LIKE platform || ':%')
) STRICT;
CREATE TABLE domains (
    id TEXT PRIMARY KEY, hostname TEXT NOT NULL UNIQUE CHECK(length(hostname) BETWEEN 1 AND 253)
) STRICT;
CREATE TABLE access_tokens (
    id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    device_id TEXT, browser_application_id TEXT REFERENCES applications(id),
    token_hash TEXT NOT NULL UNIQUE, client_kind TEXT NOT NULL,
    created_at INTEGER NOT NULL, expires_at INTEGER NOT NULL CHECK(expires_at > created_at),
    revoked_at INTEGER,
    FOREIGN KEY(device_id, workspace_id) REFERENCES devices(id, workspace_id) ON DELETE CASCADE,
    CHECK((client_kind = 'desktop_ui' AND device_id IS NULL AND browser_application_id IS NULL)
       OR (client_kind = 'desktop' AND device_id IS NOT NULL AND browser_application_id IS NULL)
       OR (client_kind = 'browser' AND device_id IS NOT NULL AND browser_application_id IS NOT NULL))
) STRICT;
CREATE TABLE usage_sessions (
    id TEXT PRIMARY KEY, device_id TEXT NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    event_id TEXT NOT NULL, source TEXT NOT NULL, state TEXT NOT NULL,
    application_id TEXT REFERENCES applications(id), domain_id TEXT REFERENCES domains(id),
    started_at INTEGER NOT NULL, ended_at INTEGER NOT NULL,
    received_at INTEGER NOT NULL, payload_hash TEXT NOT NULL,
    UNIQUE(device_id, event_id),
    CHECK(ended_at > started_at AND ended_at - started_at <= 60000),
    CHECK((source = 'desktop' AND state = 'active' AND application_id IS NOT NULL AND domain_id IS NULL)
       OR (source = 'desktop' AND state = 'idle' AND application_id IS NULL AND domain_id IS NULL)
       OR (source = 'browser' AND state = 'active' AND application_id IS NOT NULL AND domain_id IS NOT NULL))
) STRICT;
CREATE TABLE goals (
    id TEXT PRIMARY KEY, device_id TEXT NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    target_type TEXT NOT NULL, application_id TEXT REFERENCES applications(id),
    domain_id TEXT REFERENCES domains(id), period TEXT NOT NULL CHECK(period IN ('day','week','month')),
    timezone TEXT NOT NULL, limit_seconds INTEGER NOT NULL CHECK(limit_seconds > 0),
    created_at INTEGER NOT NULL,
    CHECK((target_type = 'all' AND application_id IS NULL AND domain_id IS NULL)
       OR (target_type = 'application' AND application_id IS NOT NULL AND domain_id IS NULL)
       OR (target_type = 'domain' AND application_id IS NULL AND domain_id IS NOT NULL))
) STRICT;
CREATE TABLE rules (
    id TEXT PRIMARY KEY, device_id TEXT NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    target_type TEXT NOT NULL, application_id TEXT REFERENCES applications(id),
    domain_id TEXT REFERENCES domains(id), action TEXT NOT NULL CHECK(action IN ('block','allow')),
    created_at INTEGER NOT NULL,
    CHECK((target_type = 'application' AND application_id IS NOT NULL AND domain_id IS NULL)
       OR (target_type = 'domain' AND application_id IS NULL AND domain_id IS NOT NULL))
) STRICT;
CREATE TABLE focus_sessions (
    id TEXT PRIMARY KEY, device_id TEXT NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    status TEXT NOT NULL CHECK(status IN ('active','completed','cancelled')),
    started_at INTEGER NOT NULL, scheduled_end_at INTEGER NOT NULL,
    finished_at INTEGER, created_at INTEGER NOT NULL,
    CHECK(scheduled_end_at - started_at BETWEEN 60000 AND 14400000),
    CHECK((status = 'active' AND finished_at IS NULL)
       OR (status = 'completed' AND finished_at IS NOT NULL AND finished_at = scheduled_end_at)
       OR (status = 'cancelled' AND finished_at IS NOT NULL
           AND finished_at >= started_at AND finished_at <= scheduled_end_at))
) STRICT;
CREATE TABLE focus_session_rules (
    id TEXT PRIMARY KEY, focus_id TEXT NOT NULL REFERENCES focus_sessions(id) ON DELETE CASCADE,
    target_type TEXT NOT NULL CHECK(target_type IN ('application','domain')),
    target_key TEXT NOT NULL, action TEXT NOT NULL CHECK(action IN ('block','allow')),
    UNIQUE(focus_id, target_type, target_key)
) STRICT;
CREATE TABLE idempotency_requests (
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    route TEXT NOT NULL, key TEXT NOT NULL, request_hash TEXT NOT NULL,
    response_status INTEGER NOT NULL CHECK(response_status BETWEEN 200 AND 599),
    response_body TEXT NOT NULL, created_at INTEGER NOT NULL,
    expires_at INTEGER NOT NULL CHECK(expires_at > created_at),
    PRIMARY KEY(workspace_id, route, key)
) STRICT;
