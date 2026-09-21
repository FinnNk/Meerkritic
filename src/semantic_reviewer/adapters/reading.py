"""Import preserved GitHub receipts and retain immutable human reading context."""

import hashlib
import json
import os
import re
import tempfile
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from semantic_reviewer.adapters.observations import publish
from semantic_reviewer.adapters.state import SQLiteState
from semantic_reviewer.application.jobs import Job
from semantic_reviewer.application.reading import ReadingContext
from semantic_reviewer.domain.datasets import Observation

MAX_RECEIPT_BYTES = 2 * 1024 * 1024


def _difference(original: str, imported: str) -> str:
    if original == imported:
        return "Identical text"
    if " ".join(original.split()) == " ".join(imported.split()):
        return "Whitespace differs only"
    return "Other text differences: assess both versions"


def _verify(body: dict) -> dict:
    """Check locally supplied receipt consistency, not remote authenticity."""
    if body.get("schema_version") != 1:
        raise ValueError("Unsupported preserved source schema.")
    source = Observation(**body["observation"])
    response_raw, receipt_raw = body["response"], body["receipt"]
    if any(
        not isinstance(value, str) or len(value.encode("utf-8")) > MAX_RECEIPT_BYTES
        for value in (response_raw, receipt_raw)
    ):
        raise ValueError("Preserved source exceeds the supported size.")
    response, receipt = json.loads(response_raw), json.loads(receipt_raw)
    expected = (
        f"https://api.github.com/repos/{source.owner}/{source.repository}"
        f"/pulls/comments/{source.comment_id}"
    )
    response_url = response.get("url", "")
    match = re.fullmatch(
        r"https://api\.github\.com/repos/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/pulls/comments/([0-9]+)",
        response_url,
    )
    effective = receipt.get("effective_url", "")
    # GitHub can redirect renamed repositories through a numeric repository URL.
    # Retain that receipt, while checking the same comment ID and returned PR/path.
    effective_matches = effective.casefold() == response_url.casefold() or re.fullmatch(
        rf"https://api\.github\.com/repositories/[0-9]+/pulls/comments/{source.comment_id}",
        effective,
    )
    if (
        not match
        or int(match[2]) != source.comment_id
        or receipt.get("url", "").casefold() != expected.casefold()
        or not effective_matches
        or receipt.get("http_status") != 200
        or receipt.get("response_sha256")
        != hashlib.sha256(response_raw.encode("utf-8")).hexdigest()
        or type(response.get("id")) is not int
        or response["id"] != source.comment_id
        or response.get("path") != source.file_path
    ):
        raise ValueError("Preserved source identity or response hash does not match.")
    repository = match[1]
    if (
        response.get("pull_request_url", "").casefold()
        != f"https://api.github.com/repos/{repository}/pulls/{source.pull_request}".casefold()
        or response.get("html_url", "").casefold()
        != f"https://github.com/{repository}/pull/{source.pull_request}#discussion_r{source.comment_id}".casefold()
        or any(not isinstance(response.get(key), str) for key in ("body", "diff_hunk"))
        or datetime.fromisoformat(receipt["checked_at"]).utcoffset() is None
    ):
        raise ValueError("Preserved source content or retrieval identity does not match.")
    return response


class GitHubReadingSources:
    """Own immutable receipt files, job binding and attachment events; never use the network."""

    def __init__(self, root: Path, database: Path) -> None:
        """Initialise external files and the shared operational catalogue."""
        self.root = root
        self.state = SQLiteState(database)
        root.mkdir(parents=True, exist_ok=True)

    def attach(
        self, job: Job, source: Observation, response: bytes, receipt: bytes
    ) -> ReadingContext:
        """Verify and bind exact UTF-8 receipts before review; identical retries are safe.

        Refuse changed context and already reviewed jobs. Files may survive a failed
        transaction as unreferenced complete evidence. Source records are never edited.
        A redirect is retained only when the requested source URL, effective response
        URL, comment ID, PR number and path agree with the receipt and observation.
        """
        if (
            source.id != job.observation_id
            or source.source_index != job.source_index
            or job.status not in ("succeeded", "failed")
            or not job.artefact_sha256
            or max(len(response), len(receipt)) > MAX_RECEIPT_BYTES
        ):
            raise ValueError("Choose a terminal job with matching source and bounded receipts.")
        body = {
            "schema_version": 1,
            "job_id": job.id,
            "result_sha256": job.artefact_sha256,
            "observation": asdict(source),
            "response": response.decode("utf-8"),
            "receipt": receipt.decode("utf-8"),
        }
        try:
            _verify(body)
        except (KeyError, TypeError, AttributeError) as error:
            raise ValueError("Malformed preserved source receipt.") from error
        data = json.dumps(body, ensure_ascii=False, sort_keys=True).encode("utf-8")
        if len(data) > 6 * MAX_RECEIPT_BYTES:
            raise ValueError("Preserved source attachment is too large.")
        digest = hashlib.sha256(data).hexdigest()
        with tempfile.NamedTemporaryFile(dir=self.root, delete=False) as stream:
            staged = Path(stream.name)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            publish(staged, self.root / f"{digest}.json")
        finally:
            staged.unlink(missing_ok=True)
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute(
                "SELECT sha256 FROM source_context WHERE job_id=?", (job.id,)
            ).fetchone()
            if existing and existing[0] != digest:
                raise ValueError("This job already has different preserved source context.")
            if not existing:
                if db.execute("SELECT 1 FROM annotation WHERE job_id=?", (job.id,)).fetchone():
                    raise ValueError("Cannot attach new context to an existing assessment.")
                db.execute(
                    "INSERT INTO source_context VALUES (?, ?, ?, ?)",
                    (job.id, digest, source.id, job.artefact_sha256),
                )
                db.execute(
                    "INSERT INTO event(kind,subject_id,occurred_at,details_json) "
                    "VALUES (?, ?, strftime('%Y-%m-%dT%H:%M:%fZ','now'), ?)",
                    (
                        "source_context_attached",
                        job.id,
                        json.dumps({"sha256": digest, "schema_version": 1}),
                    ),
                )
        return self.read(job.id)

    def read(self, job_id: str) -> ReadingContext | None:
        """Verify every attachment read; an absent attachment alone returns None."""
        with self.state.connect() as db:
            row = db.execute("SELECT * FROM source_context WHERE job_id=?", (job_id,)).fetchone()
        if row is None:
            return None
        digest = row["sha256"]
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("Invalid preserved source identity.")
        with (self.root / f"{digest}.json").open("rb") as stream:
            data = stream.read(6 * MAX_RECEIPT_BYTES + 1)
        if len(data) > 6 * MAX_RECEIPT_BYTES or hashlib.sha256(data).hexdigest() != digest:
            raise ValueError("Preserved source checksum mismatch.")
        try:
            body = json.loads(data)
            response = _verify(body)
            source = Observation(**body["observation"])
            receipt = json.loads(body["receipt"])
            if (body["job_id"], source.id, body["result_sha256"]) != (
                job_id,
                row["observation_id"],
                row["result_sha256"],
            ):
                raise ValueError("Preserved source belongs to a different result.")
            return ReadingContext(
                digest,
                job_id,
                source.id,
                response["html_url"],
                receipt["checked_at"],
                receipt["response_sha256"],
                response["body"],
                response["diff_hunk"],
                _difference(response["body"], source.comment),
                _difference(response["diff_hunk"], source.code),
            )
        except (KeyError, TypeError, AttributeError) as error:
            raise ValueError("Malformed preserved source attachment.") from error
