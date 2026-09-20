-- depends: 009_discovery
CREATE TABLE rule_version (
    id TEXT PRIMARY KEY CHECK(length(id)=64 AND id NOT GLOB '*[^0-9a-f]*'),
    rule_id TEXT NOT NULL,
    parent_version TEXT REFERENCES rule_version(id),
    cluster_run TEXT NOT NULL REFERENCES discovery_run(id),
    created_at TEXT NOT NULL
);
CREATE TABLE rule_head (
    rule_id TEXT PRIMARY KEY,
    version_id TEXT NOT NULL REFERENCES rule_version(id),
    revision INTEGER NOT NULL CHECK(revision>=1),
    status TEXT NOT NULL CHECK(status IN ('candidate','promoted','rejected')),
    created_at TEXT NOT NULL
);
CREATE TABLE rule_evidence (
    id TEXT PRIMARY KEY,
    version_id TEXT NOT NULL REFERENCES rule_version(id),
    payload_json TEXT NOT NULL CHECK(length(payload_json)<16000)
);
CREATE TABLE rule_decision (
    id TEXT PRIMARY KEY,
    version_id TEXT NOT NULL REFERENCES rule_version(id),
    request_json TEXT NOT NULL CHECK(length(request_json)<16000),
    occurred_at TEXT NOT NULL,
    resulting_revision INTEGER NOT NULL
);
CREATE TRIGGER rule_version_no_update BEFORE UPDATE ON rule_version
BEGIN SELECT RAISE(ABORT,'Rule versions are immutable'); END;
CREATE TRIGGER rule_version_no_delete BEFORE DELETE ON rule_version
BEGIN SELECT RAISE(ABORT,'Rule versions retain their history'); END;
CREATE TRIGGER rule_evidence_no_update BEFORE UPDATE ON rule_evidence
BEGIN SELECT RAISE(ABORT,'Rule evidence is append-only'); END;
CREATE TRIGGER rule_evidence_no_delete BEFORE DELETE ON rule_evidence
BEGIN SELECT RAISE(ABORT,'Rule evidence is append-only'); END;
CREATE TRIGGER rule_decision_no_update BEFORE UPDATE ON rule_decision
BEGIN SELECT RAISE(ABORT,'Rule decisions are append-only'); END;
CREATE TRIGGER rule_decision_no_delete BEFORE DELETE ON rule_decision
BEGIN SELECT RAISE(ABORT,'Rule decisions are append-only'); END;
CREATE TRIGGER rule_head_no_delete BEFORE DELETE ON rule_head
BEGIN SELECT RAISE(ABORT,'Rules retain their history'); END;
