CREATE INDEX devices_workspace ON devices(workspace_id, id);
CREATE INDEX usage_period ON usage_sessions(device_id, source, started_at, ended_at);
CREATE INDEX usage_retention ON usage_sessions(started_at);
CREATE INDEX goals_page ON goals(device_id, created_at, id);
CREATE INDEX rules_page ON rules(device_id, created_at, id);
CREATE UNIQUE INDEX rules_application ON rules(device_id, application_id) WHERE target_type = 'application';
CREATE UNIQUE INDEX rules_domain ON rules(device_id, domain_id) WHERE target_type = 'domain';
CREATE INDEX focus_page ON focus_sessions(device_id, created_at, id);
CREATE UNIQUE INDEX focus_active ON focus_sessions(device_id) WHERE status = 'active';
CREATE INDEX focus_expiry ON focus_sessions(status, scheduled_end_at);
CREATE INDEX focus_rules_parent ON focus_session_rules(focus_id);
CREATE INDEX idempotency_expiry ON idempotency_requests(expires_at);
CREATE TRIGGER usage_insert_guard BEFORE INSERT ON usage_sessions BEGIN
    SELECT RAISE(ABORT, 'Device is revoked or event predates the ingestion cutoff')
    WHERE EXISTS (SELECT 1 FROM devices d WHERE d.id = NEW.device_id
        AND (d.revoked_at IS NOT NULL OR NEW.started_at < d.ingestion_not_before));
    SELECT RAISE(ABORT, 'Application platform does not match device')
    WHERE EXISTS (SELECT 1 FROM devices d, applications a
        WHERE d.id = NEW.device_id AND a.id = NEW.application_id AND d.platform != a.platform);
    SELECT RAISE(ABORT, 'Activity intervals overlap') WHERE EXISTS (
        SELECT 1 FROM usage_sessions u WHERE u.device_id = NEW.device_id AND u.source = NEW.source
        AND u.started_at < NEW.ended_at AND u.ended_at > NEW.started_at);
END;
CREATE TRIGGER usage_immutable BEFORE UPDATE ON usage_sessions BEGIN
    SELECT RAISE(ABORT, 'Usage observations are immutable');
END;
CREATE TRIGGER cutoff_monotonic BEFORE UPDATE OF ingestion_not_before ON devices
WHEN NEW.ingestion_not_before < OLD.ingestion_not_before BEGIN
    SELECT RAISE(ABORT, 'Ingestion cutoff cannot move backwards');
END;
CREATE TRIGGER device_identity_immutable BEFORE UPDATE OF id, workspace_id, platform ON devices BEGIN
    SELECT RAISE(ABORT, 'Device identity is immutable');
END;
CREATE TRIGGER application_identity_immutable BEFORE UPDATE OF id, app_key, platform ON applications BEGIN
    SELECT RAISE(ABORT, 'Application identity is immutable');
END;
CREATE TRIGGER focus_terminal BEFORE UPDATE ON focus_sessions
WHEN OLD.status != 'active' OR NEW.device_id != OLD.device_id OR NEW.id != OLD.id
    OR NEW.started_at != OLD.started_at OR NEW.scheduled_end_at != OLD.scheduled_end_at BEGIN
    SELECT RAISE(ABORT, 'Focus identity and terminal state are immutable');
END;
CREATE TRIGGER focus_snapshot_immutable BEFORE UPDATE ON focus_session_rules BEGIN
    SELECT RAISE(ABORT, 'Focus rule snapshots are immutable');
END;
CREATE TRIGGER goal_platform_insert BEFORE INSERT ON goals BEGIN
    SELECT RAISE(ABORT, 'Application platform does not match device') WHERE EXISTS (
        SELECT 1 FROM devices d, applications a WHERE d.id = NEW.device_id
        AND a.id = NEW.application_id AND d.platform != a.platform);
END;
CREATE TRIGGER goal_platform_update BEFORE UPDATE ON goals BEGIN
    SELECT RAISE(ABORT, 'Application platform does not match device') WHERE EXISTS (
        SELECT 1 FROM devices d, applications a WHERE d.id = NEW.device_id
        AND a.id = NEW.application_id AND d.platform != a.platform);
END;
CREATE TRIGGER rule_platform_insert BEFORE INSERT ON rules BEGIN
    SELECT RAISE(ABORT, 'Application platform does not match device') WHERE EXISTS (
        SELECT 1 FROM devices d, applications a WHERE d.id = NEW.device_id
        AND a.id = NEW.application_id AND d.platform != a.platform);
END;
CREATE TRIGGER rule_platform_update BEFORE UPDATE ON rules BEGIN
    SELECT RAISE(ABORT, 'Application platform does not match device') WHERE EXISTS (
        SELECT 1 FROM devices d, applications a WHERE d.id = NEW.device_id
        AND a.id = NEW.application_id AND d.platform != a.platform);
END;
CREATE TRIGGER token_platform_insert BEFORE INSERT ON access_tokens BEGIN
    SELECT RAISE(ABORT, 'Browser platform does not match device') WHERE EXISTS (
        SELECT 1 FROM devices d, applications a WHERE d.id = NEW.device_id
        AND a.id = NEW.browser_application_id AND d.platform != a.platform);
END;
CREATE TRIGGER token_platform_update BEFORE UPDATE ON access_tokens BEGIN
    SELECT RAISE(ABORT, 'Browser platform does not match device') WHERE EXISTS (
        SELECT 1 FROM devices d, applications a WHERE d.id = NEW.device_id
        AND a.id = NEW.browser_application_id AND d.platform != a.platform);
END;
