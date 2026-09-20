"""Register immutable rule bodies and atomic research decisions with explicit version fencing."""

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from semantic_reviewer.adapters.state import SQLiteState
from semantic_reviewer.application.discovery import DiscoveryFiles
from semantic_reviewer.application.rules import RuleHead
from semantic_reviewer.domain.rules import RuleDecisionRequest, RuleEvidence, RuleVersionBody


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _event(db, rule_id, kind, details):
    db.execute(
        "INSERT INTO event(kind,subject_id,occurred_at,details_json) VALUES(?,?,?,?)",
        ("rule_" + kind, rule_id, _now(), json.dumps(details)),
    )


class SQLiteRules:
    """Own the current pointer and append-only versions/evidence/decisions in short transactions."""

    def __init__(self, database: Path, files: DiscoveryFiles) -> None:
        """Migrate metadata and bind immutable files without generating or reviewing a rule."""
        self.state, self.files = SQLiteState(database), files

    @staticmethod
    def _head(db, rule_id):
        row = db.execute("SELECT * FROM rule_head WHERE rule_id=?", (rule_id,)).fetchone()
        if row is None:
            raise LookupError("Rule does not exist.")
        return RuleHead(**dict(row))

    @staticmethod
    def _current(db, version_id, revision):
        if type(revision) is not int or revision < 1:
            raise ValueError("Expected revision must be a positive integer.")
        row = db.execute(
            "SELECT * FROM rule_head WHERE version_id=? AND revision=?", (version_id, revision)
        ).fetchone()
        if row is None:
            raise ValueError(
                "Rule changed; inspect the current version and revision before applying."
            )
        return RuleHead(**dict(row))

    @staticmethod
    def _insert_evidence(db, evidence):
        db.execute(
            "INSERT INTO rule_evidence VALUES(?,?,?)",
            (evidence.id, evidence.version_id, evidence.model_dump_json()),
        )

    def publish(self, body: RuleVersionBody, expected_revision: int | None) -> str:
        """Publish complete content, then atomically move the pointer and inherit evidence.

        A definition change demotes inherited verification to weak: earlier verification
        applies to the earlier rule version. Original evidence remains unchanged.
        """
        body = RuleVersionBody.model_validate_json(body.model_dump_json())
        digest = self.files.write_json(body.model_dump(mode="json"))
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM rule_version WHERE id=?", (digest,)).fetchone():
                return digest
            now = _now()
            inherited = []
            if body.parent_version:
                head = self._current(db, body.parent_version, expected_revision)
                if head.rule_id != body.rule_id:
                    raise ValueError("Parent belongs to another rule.")
                inherited = [
                    RuleEvidence.model_validate_json(row[0])
                    for row in db.execute(
                        "SELECT payload_json FROM rule_evidence WHERE version_id=?",
                        (body.parent_version,),
                    )
                ]
            elif (
                expected_revision is not None
                or db.execute("SELECT 1 FROM rule_head WHERE rule_id=?", (body.rule_id,)).fetchone()
            ):
                raise ValueError("New rules require a new identity and no expected revision.")
            supported = {item.annotation_id for item in inherited if item.kind == "positive"}
            additional = set(body.definition.supporting_annotations) - supported
            if len(inherited) + len(additional) > 1000:
                raise ValueError(
                    "Revision would exceed the 1000-link evidence bound; nothing changed."
                )
            db.execute(
                "INSERT INTO rule_version VALUES(?,?,?,?,?)",
                (digest, body.rule_id, body.parent_version, body.cluster_run, now),
            )
            if body.parent_version:
                db.execute(
                    "UPDATE rule_head SET version_id=?,revision=revision+1,status='candidate' "
                    "WHERE rule_id=?",
                    (digest, body.rule_id),
                )
            else:
                db.execute(
                    "INSERT INTO rule_head VALUES(?,?,1,'candidate',?)", (body.rule_id, digest, now)
                )
            for previous in inherited:
                self._insert_evidence(
                    db,
                    RuleEvidence(
                        **{
                            **previous.model_dump(),
                            "id": str(uuid4()),
                            "version_id": digest,
                            "inherited_from": previous.id,
                            "verification": "weak",
                            "actor": "registry:inheritance",
                            "rationale": "Retained from the parent; earlier verification "
                            "applies only to that version.",
                        }
                    ),
                )
            for annotation in body.definition.supporting_annotations:
                if annotation not in supported:
                    self._insert_evidence(
                        db,
                        RuleEvidence(
                            id=str(uuid4()),
                            version_id=digest,
                            annotation_id=annotation,
                            kind="positive",
                            verification="weak",
                            actor=body.origin.actor,
                            rationale="Proposed support; source linkage is not validation.",
                        ),
                    )
            _event(
                db,
                body.rule_id,
                "revised" if body.parent_version else "created",
                {"version_id": digest, "parent_version": body.parent_version},
            )
        return digest

    def read(self, version_id: str) -> tuple:
        """Verify the immutable body and relational identity before exposing bounded history."""
        with self.state.connect() as db:
            row = db.execute("SELECT * FROM rule_version WHERE id=?", (version_id,)).fetchone()
            if row is None:
                raise LookupError("Rule version does not exist.")
            head = self._head(db, row["rule_id"])
            evidence = tuple(
                RuleEvidence.model_validate_json(item[0])
                for item in db.execute(
                    "SELECT payload_json FROM rule_evidence WHERE version_id=? "
                    "ORDER BY rowid LIMIT 1000",
                    (version_id,),
                )
            )
            decisions = tuple(
                self._decision(row)
                for row in db.execute(
                    "SELECT * FROM rule_decision WHERE version_id=? "
                    "ORDER BY occurred_at,id LIMIT 1000",
                    (version_id,),
                )
            )
        body = RuleVersionBody.model_validate(self.files.read_json(version_id))
        if (
            body.rule_id != row["rule_id"]
            or body.parent_version != row["parent_version"]
            or body.cluster_run != row["cluster_run"]
        ):
            raise ValueError("Rule body disagrees with its registered identity.")
        return head, body, evidence, decisions

    def recent(self) -> tuple[RuleHead, ...]:
        """Return up to 100 current heads; opening a version verifies its body."""
        with self.state.connect() as db:
            return tuple(
                RuleHead(**dict(row))
                for row in db.execute(
                    "SELECT * FROM rule_head ORDER BY created_at DESC,rule_id DESC LIMIT 100"
                )
            )

    def add_evidence(self, evidence: RuleEvidence, expected_revision: int) -> None:
        """Append a typed evidence claim once; stale versions/revisions preserve existing state."""
        evidence = RuleEvidence.model_validate_json(evidence.model_dump_json())
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute(
                "SELECT payload_json FROM rule_evidence WHERE id=?", (evidence.id,)
            ).fetchone()
            if existing:
                if RuleEvidence.model_validate_json(existing[0]) != evidence:
                    raise ValueError("Evidence identity already refers to different content.")
                return
            head = self._current(db, evidence.version_id, expected_revision)
            if (
                db.execute(
                    "SELECT count(*) FROM rule_evidence WHERE version_id=?", (evidence.version_id,)
                ).fetchone()[0]
                >= 1000
            ):
                raise ValueError("Rule version has reached its 1000-link evidence bound.")
            self._insert_evidence(db, evidence)
            db.execute("UPDATE rule_head SET revision=revision+1 WHERE rule_id=?", (head.rule_id,))
            _event(
                db,
                head.rule_id,
                "evidence_added",
                {"evidence_id": evidence.id, "version_id": evidence.version_id},
            )

    @staticmethod
    def _decision(row):
        return {
            "request": json.loads(row["request_json"]),
            "occurred_at": row["occurred_at"],
            "resulting_revision": row["resulting_revision"],
        }

    def decide(self, request: RuleDecisionRequest) -> dict:
        """Apply an explicit research decision with a replay-safe operation identity and event."""
        request = RuleDecisionRequest.model_validate_json(request.model_dump_json())
        self.read(request.version_id)
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            return self.decide_in_transaction(db, request)

    def decide_in_transaction(self, db, request: RuleDecisionRequest) -> dict:
        """Apply the canonical decision contract inside an already owned write transaction.

        Adapter collaborators may compose atomic batches using the same database.
        The caller owns commit/rollback; this operation never opens another connection.
        Verify each immutable rule body before acquiring the transaction.
        """
        if not db.in_transaction:
            raise ValueError("Decision requires an owned write transaction.")
        request = RuleDecisionRequest.model_validate_json(request.model_dump_json())
        existing = db.execute(
            "SELECT * FROM rule_decision WHERE id=?", (request.operation_id,)
        ).fetchone()
        if existing:
            if RuleDecisionRequest.model_validate_json(existing["request_json"]) != request:
                raise ValueError("Decision operation identity already refers to different intent.")
            return self._decision(existing)
        head = self._current(db, request.version_id, request.expected_revision)
        task = db.execute(
            "SELECT state FROM review_task WHERE version_id=?", (request.version_id,)
        ).fetchone()
        if task[0] not in ("pending", "reopened"):
            raise ValueError("This review task must be reopened before a new decision.")
        if head.status != "candidate":
            raise ValueError("This version already has a decision; revise it explicitly.")
        now = _now()
        db.execute(
            "INSERT INTO rule_decision VALUES(?,?,?,?,?)",
            (
                request.operation_id,
                request.version_id,
                request.model_dump_json(),
                now,
                head.revision + 1,
            ),
        )
        db.execute(
            "UPDATE rule_head SET status=?,revision=revision+1 WHERE rule_id=?",
            ("promoted" if request.action == "promote" else "rejected", head.rule_id),
        )
        _event(
            db,
            head.rule_id,
            "decided",
            {
                "operation_id": request.operation_id,
                "version_id": request.version_id,
                "action": request.action,
            },
        )
        return {
            "request": request.model_dump(mode="json"),
            "occurred_at": now,
            "resulting_revision": head.revision + 1,
        }
