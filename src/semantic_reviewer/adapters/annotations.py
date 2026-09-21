"""Store immutable human decisions and their events in short SQLite transactions."""

import json
from dataclasses import asdict
from pathlib import Path

from semantic_reviewer.adapters.state import SQLiteState
from semantic_reviewer.application.annotations import Annotation, AnnotationProgress


class SQLiteAnnotations:
    """Serialise competing submissions without overwriting prior human judgement."""

    def __init__(self, database: Path) -> None:
        """Migrate the shared operational database."""
        self.state = SQLiteState(database)

    def record(self, annotation: Annotation) -> Annotation:
        """Commit decision and event together; identical retries create no additional event."""
        values = asdict(annotation)
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT * FROM annotation WHERE job_id=?", (annotation.job_id,)
            ).fetchone()
            if row:
                existing = Annotation(**dict(row))
                if any(
                    getattr(existing, key) != value
                    for key, value in values.items()
                    if key not in ("id", "created_at")
                ):
                    raise ValueError(
                        "This result already has a different decision; it was not changed."
                    )
                return existing
            context = db.execute(
                "SELECT sha256 FROM source_context WHERE job_id=?", (annotation.job_id,)
            ).fetchone()
            if annotation.context_sha256 != (context[0] if context else None):
                raise ValueError(
                    "Source context changed; retain your edits and reload before saving."
                )
            db.execute(
                "INSERT INTO annotation VALUES (" + ",".join("?" for _ in values) + ")",
                tuple(values.values()),
            )
            db.execute(
                "INSERT INTO event(kind, subject_id, occurred_at, details_json) "
                "VALUES (?, ?, ?, ?)",
                (
                    "annotation_recorded",
                    annotation.id,
                    annotation.created_at,
                    json.dumps(
                        {
                            "job_id": annotation.job_id,
                            "decision": annotation.decision,
                            "schema_version": 1,
                            "context_sha256": annotation.context_sha256,
                        }
                    ),
                ),
            )
        return annotation

    def get(self, job_id: str) -> Annotation | None:
        """Read a result's decision without loading artefact bodies."""
        with self.state.connect() as db:
            row = db.execute("SELECT * FROM annotation WHERE job_id=?", (job_id,)).fetchone()
            return Annotation(**dict(row)) if row else None

    def history(self, observation_id: str) -> tuple[Annotation, ...]:
        """Return the latest 100 decisions for this immutable source identity."""
        with self.state.connect() as db:
            return tuple(
                Annotation(**dict(row))
                for row in db.execute(
                    "SELECT * FROM annotation WHERE observation_id=? "
                    "ORDER BY created_at DESC, id DESC LIMIT 100",
                    (observation_id,),
                )
            )

    def by_id(self, annotation_id: str) -> Annotation | None:
        """Resolve an explicit version without guessing the latest result for its source."""
        with self.state.connect() as db:
            row = db.execute("SELECT * FROM annotation WHERE id=?", (annotation_id,)).fetchone()
            return Annotation(**dict(row)) if row else None

    def progress(self, dataset_id: str) -> AnnotationProgress:
        """Count all results and distinct source coverage, not just the recent job page."""
        with self.state.connect() as db:
            # SELECT alone does not open a persistent SQLite snapshot. Keep the
            # denominators and decision/source counts on the same committed view.
            db.execute("BEGIN")
            row = db.execute("SELECT row_count FROM dataset WHERE id=?", (dataset_id,)).fetchone()
            if row is None:
                raise LookupError("Dataset is not registered.")
            counts = dict(
                db.execute(
                    "SELECT status, count(*) FROM job WHERE dataset_id=? GROUP BY status",
                    (dataset_id,),
                )
            )
            decisions = dict(
                db.execute(
                    "SELECT a.decision, count(*) FROM annotation a JOIN job j ON j.id=a.job_id "
                    "WHERE j.dataset_id=? GROUP BY a.decision",
                    (dataset_id,),
                )
            )
            reviewed = dict(
                db.execute(
                    "SELECT j.status, count(*) FROM annotation a JOIN job j ON j.id=a.job_id "
                    "WHERE j.dataset_id=? GROUP BY j.status",
                    (dataset_id,),
                )
            )
            sources = db.execute(
                "SELECT count(DISTINCT a.observation_id) FROM annotation a "
                "JOIN job j ON j.id=a.job_id "
                "WHERE j.dataset_id=?",
                (dataset_id,),
            ).fetchone()[0]
            return {
                "source_total": row[0],
                "reviewed_sources": sources,
                "successful_results": counts.get("succeeded", 0),
                "reviewed_results": sum(decisions.values()),
                "reviewed_successful_results": reviewed.get("succeeded", 0),
                "reviewed_failed_results": reviewed.get("failed", 0),
                "accept": decisions.get("accept", 0),
                "edit": decisions.get("edit", 0),
                "reject": decisions.get("reject", 0),
                "failed": counts.get("failed", 0),
                "queued": counts.get("queued", 0),
                "running": counts.get("running", 0),
            }

    def pending(self, dataset_id: str, page: int) -> tuple[str, ...]:
        """Page through unreviewed successes and published failures for inspection."""
        if not 1 <= page <= 1_000_000:
            raise ValueError("Page is outside the supported range.")
        with self.state.connect() as db:
            return tuple(
                row[0]
                for row in db.execute(
                    "SELECT j.id FROM job j LEFT JOIN annotation a ON a.job_id=j.id "
                    "WHERE j.dataset_id=? AND a.id IS NULL AND "
                    "(j.status='succeeded' OR "
                    "(j.status='failed' AND j.artefact_sha256 IS NOT NULL)) "
                    "ORDER BY j.completed_at, j.id LIMIT 20 OFFSET ?",
                    (dataset_id, (page - 1) * 20),
                )
            )
