"""Keep draft application and review transitions atomic with the canonical rule registry."""

import json
from datetime import UTC, datetime
from pathlib import Path

from semantic_reviewer.adapters.rules import SQLiteRules
from semantic_reviewer.application.discovery import DiscoveryFiles
from semantic_reviewer.domain.interaction import DiscussionNote, ReviewDraft
from semantic_reviewer.domain.rules import RuleDecisionRequest


def _now():
    return datetime.now(UTC).isoformat()


def _event(db, kind, subject, details):
    db.execute(
        "INSERT INTO event(kind,subject_id,occurred_at,details_json) VALUES(?,?,?,?)",
        (kind, subject, _now(), json.dumps(details)),
    )


class SQLiteReviewWorkspace:
    """Own saved intent and review lifecycle without holding transactions across file/model work."""

    def __init__(self, database: Path, files: DiscoveryFiles) -> None:
        """Bind shared registry metadata and immutable payload storage; no decisions apply."""
        self.rules = SQLiteRules(database, files)
        self.state, self.files = self.rules.state, files

    def save(self, draft_id: str, expected_revision: int | None, body: ReviewDraft) -> dict:
        """Save a bounded, verified payload with draft CAS and an event; never apply intent."""
        body = ReviewDraft.model_validate_json(body.model_dump_json())
        if not draft_id or len(draft_id) > 100:
            raise ValueError("Draft identity must contain 1..100 characters.")
        for intent in body.intents:
            self.rules.read(intent.version_id)
        digest = self.files.write_json(body.model_dump(mode="json"))
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM review_draft WHERE id=?", (draft_id,)).fetchone()
            if row:
                if row["status"] != "saved":
                    raise ValueError("Applied drafts are immutable; create a new draft.")
                if row["digest"] == digest:
                    return dict(row)
                if type(expected_revision) is not int or row["revision"] != expected_revision:
                    raise ValueError("Draft changed; reload before saving.")
                db.execute(
                    "UPDATE review_draft SET digest=?,revision=revision+1 WHERE id=?",
                    (digest, draft_id),
                )
            else:
                if expected_revision is not None:
                    raise ValueError("New draft requires no expected revision.")
                db.execute(
                    "INSERT INTO review_draft VALUES(?,1,?,'saved',NULL,?)",
                    (draft_id, digest, _now()),
                )
            _event(db, "review_draft_saved", draft_id, {"digest": digest})
            return dict(db.execute("SELECT * FROM review_draft WHERE id=?", (draft_id,)).fetchone())

    def read(self, draft_id: str) -> tuple[dict, ReviewDraft]:
        """Verify saved content before presenting it as review intent."""
        with self.state.connect() as db:
            row = db.execute("SELECT * FROM review_draft WHERE id=?", (draft_id,)).fetchone()
        if row is None:
            raise LookupError("Draft does not exist.")
        return dict(row), ReviewDraft.model_validate(self.files.read_json(row["digest"]))

    def recent(self) -> tuple[dict, ...]:
        """List up to 100 newest draft pointers, including applied status."""
        with self.state.connect() as db:
            return tuple(
                dict(row)
                for row in db.execute(
                    "SELECT * FROM review_draft ORDER BY created_at DESC,id DESC LIMIT 100"
                )
            )

    def task(self, version_id: str) -> dict:
        """Return the exact-version lifecycle; superseded versions expose a replacement link."""
        with self.state.connect() as db:
            row = db.execute(
                "SELECT * FROM review_task WHERE version_id=?", (version_id,)
            ).fetchone()
        if row is None:
            raise LookupError("Review task does not exist.")
        return dict(row)

    def history(self, version_id: str) -> tuple[dict, ...]:
        """Return the newest 1,000 explicit staged transitions for this version."""
        with self.state.connect() as db:
            return tuple(
                dict(row)
                for row in db.execute(
                    "SELECT * FROM review_interaction WHERE version_id=? "
                    "ORDER BY id DESC LIMIT 1000",
                    (version_id,),
                )
            )

    def apply(self, draft_id: str, expected_revision: int) -> dict:
        """Atomically apply every checked target; stale targets leave draft and decisions intact."""
        metadata, body = self.read(draft_id)
        # Verify immutable bodies before the short write transaction; CAS binds their identities.
        for intent in body.intents:
            self.rules.read(intent.version_id)
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM review_draft WHERE id=?", (draft_id,)).fetchone()
            if type(expected_revision) is not int or row["revision"] != expected_revision:
                raise ValueError("Draft changed; reload before applying.")
            if row["digest"] != metadata["digest"]:
                raise ValueError("Draft content changed before application.")
            if row["status"] == "applied":
                return json.loads(row["receipt_json"])
            results = []
            for intent in body.intents:
                head = db.execute(
                    "SELECT * FROM rule_head WHERE version_id=?", (intent.version_id,)
                ).fetchone()
                task = db.execute(
                    "SELECT * FROM review_task WHERE version_id=?", (intent.version_id,)
                ).fetchone()
                if head is None or head["revision"] != intent.expected_revision:
                    raise ValueError(
                        f"Rule version {intent.version_id} changed; saved draft retained."
                    )
                if intent.action in ("promote", "reject"):
                    if task["state"] not in ("pending", "reopened"):
                        raise ValueError(
                            f"Rule version {intent.version_id} must be reopened first."
                        )
                    self.rules.decide_in_transaction(
                        db,
                        RuleDecisionRequest(
                            operation_id=draft_id + ":" + intent.version_id,
                            version_id=intent.version_id,
                            expected_revision=intent.expected_revision,
                            action=intent.action,
                            actor=body.actor,
                            rationale=intent.rationale,
                        ),
                    )
                else:
                    allowed = (
                        ("pending", "reopened")
                        if intent.action == "defer"
                        else ("answered", "deferred")
                    )
                    if task["state"] not in allowed:
                        raise ValueError(
                            f"Cannot {intent.action} version {intent.version_id} "
                            f"from {task['state']}."
                        )
                    state = "deferred" if intent.action == "defer" else "reopened"
                    db.execute(
                        "UPDATE review_task SET state=? WHERE version_id=?",
                        (state, intent.version_id),
                    )
                    db.execute(
                        "UPDATE rule_head SET status='candidate',revision=revision+1 "
                        "WHERE version_id=?",
                        (intent.version_id,),
                    )
                db.execute(
                    "INSERT INTO review_interaction"
                    "(version_id,kind,actor,rationale,occurred_at,draft_id) VALUES(?,?,?,?,?,?)",
                    (
                        intent.version_id,
                        intent.action,
                        body.actor,
                        intent.rationale,
                        _now(),
                        draft_id,
                    ),
                )
                results.append(
                    {
                        "version_id": intent.version_id,
                        "action": intent.action,
                        "resulting_revision": intent.expected_revision + 1,
                    }
                )
            receipt = {
                "draft_id": draft_id,
                "draft_revision": expected_revision,
                "applied_at": _now(),
                "results": results,
            }
            db.execute(
                "UPDATE review_draft SET status='applied',receipt_json=? WHERE id=?",
                (json.dumps(receipt), draft_id),
            )
            _event(db, "review_draft_applied", draft_id, receipt)
            return receipt

    def discuss(self, note: DiscussionNote) -> None:
        """Append a replay-safe named message; historical-version discussion stays historical."""
        note = DiscussionNote.model_validate_json(note.model_dump_json())
        self.rules.read(note.version_id)
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute(
                "SELECT payload_json FROM rule_discussion WHERE id=?", (note.id,)
            ).fetchone()
            if existing:
                if DiscussionNote.model_validate_json(existing[0]) != note:
                    raise ValueError("Discussion identity refers to different content.")
                return
            if (
                db.execute(
                    "SELECT count(*) FROM rule_discussion WHERE version_id=?", (note.version_id,)
                ).fetchone()[0]
                >= 1000
            ):
                raise ValueError("Version has reached its 1,000-note discussion bound.")
            db.execute(
                "INSERT INTO rule_discussion VALUES(?,?,?,?)",
                (note.id, note.version_id, note.model_dump_json(), _now()),
            )
            _event(db, "rule_discussed", note.version_id, {"note_id": note.id})

    def discussion(self, version_id: str) -> tuple[DiscussionNote, ...]:
        """Return all immutable notes within the enforced bound, in creation order."""
        with self.state.connect() as db:
            return tuple(
                DiscussionNote.model_validate_json(row[0])
                for row in db.execute(
                    "SELECT payload_json FROM rule_discussion WHERE version_id=? "
                    "ORDER BY occurred_at,id",
                    (version_id,),
                )
            )
