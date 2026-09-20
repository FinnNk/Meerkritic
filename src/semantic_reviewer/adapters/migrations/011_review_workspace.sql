-- depends: 010_rules
CREATE TABLE review_task (
    version_id TEXT PRIMARY KEY REFERENCES rule_version(id),
    state TEXT NOT NULL CHECK(state IN ('pending','answered','deferred','reopened','superseded')),
    replacement TEXT REFERENCES rule_version(id),
    CHECK((state='superseded')=(replacement IS NOT NULL))
);
INSERT INTO review_task
SELECT v.id, CASE WHEN h.version_id=v.id THEN
    CASE WHEN h.status='candidate' THEN 'pending' ELSE 'answered' END
    ELSE 'superseded' END,
    CASE WHEN h.version_id=v.id THEN NULL ELSE h.version_id END
FROM rule_version v JOIN rule_head h ON h.rule_id=v.rule_id;
CREATE TRIGGER review_new_version AFTER INSERT ON rule_version
BEGIN INSERT INTO review_task VALUES(NEW.id,'pending',NULL); END;
CREATE TRIGGER review_replaced_version AFTER UPDATE OF version_id ON rule_head
WHEN NEW.version_id<>OLD.version_id
BEGIN UPDATE review_task SET state='superseded',replacement=NEW.version_id
      WHERE version_id=OLD.version_id; END;
CREATE TRIGGER review_answered AFTER UPDATE OF status ON rule_head
WHEN NEW.status IN ('promoted','rejected')
BEGIN UPDATE review_task SET state='answered' WHERE version_id=NEW.version_id; END;
CREATE TABLE review_draft (
    id TEXT PRIMARY KEY,
    revision INTEGER NOT NULL CHECK(revision>=1),
    digest TEXT NOT NULL CHECK(length(digest)=64),
    status TEXT NOT NULL CHECK(status IN ('saved','applied')),
    receipt_json TEXT,
    created_at TEXT NOT NULL,
    CHECK((status='applied')=(receipt_json IS NOT NULL))
);
CREATE TABLE review_interaction (
    id INTEGER PRIMARY KEY,
    version_id TEXT NOT NULL REFERENCES rule_version(id),
    kind TEXT NOT NULL,
    actor TEXT NOT NULL,
    rationale TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    draft_id TEXT REFERENCES review_draft(id)
);
CREATE TABLE rule_discussion (
    id TEXT PRIMARY KEY,
    version_id TEXT NOT NULL REFERENCES rule_version(id),
    payload_json TEXT NOT NULL CHECK(length(payload_json)<16000),
    occurred_at TEXT NOT NULL
);
CREATE TRIGGER review_interaction_no_update BEFORE UPDATE ON review_interaction
BEGIN SELECT RAISE(ABORT,'Review history is append-only'); END;
CREATE TRIGGER review_interaction_no_delete BEFORE DELETE ON review_interaction
BEGIN SELECT RAISE(ABORT,'Review history is append-only'); END;
CREATE TRIGGER rule_discussion_no_update BEFORE UPDATE ON rule_discussion
BEGIN SELECT RAISE(ABORT,'Discussion is append-only'); END;
CREATE TRIGGER rule_discussion_no_delete BEFORE DELETE ON rule_discussion
BEGIN SELECT RAISE(ABORT,'Discussion is append-only'); END;
