"""Prepare and record the fixed study input sequence in external, immutable JSON files."""

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from semantic_reviewer.bootstrap import runtime_path
from semantic_reviewer.domain.study_preparation import (
    PreparationAttempt,
    content_digest,
    preparation_progress,
    prepare_sample,
)


def read_record(source: bytes, path: Path) -> tuple[dict, str]:
    """Verify a saved record against the original source and recomputed progress.

    This detects inconsistent content, not malicious re-authoring of attestations.
    Keep the predecessor files: their byte hashes link the actual recorded sequence.
    """
    body = _read(path)
    record = json.loads(body)
    fields = {
        "schema_version",
        "plan",
        "plan_sha256",
        "attempts",
        "progress",
        "previous_record_sha256",
    }
    if (
        not isinstance(record, dict)
        or set(record) != fields
        or type(record["schema_version"]) is not int
        or record["schema_version"] != 1
    ):
        raise ValueError("Unsupported preparation record.")
    plan = record["plan"]
    expected = prepare_sample(source, plan["source_sha256"], tuple(plan["prior_exposure"]))
    if content_digest(plan) != content_digest(expected) or record["plan_sha256"] != content_digest(
        plan
    ):
        raise ValueError("Preparation plan differs from its source or fixed sampling procedure.")
    attempts = tuple(PreparationAttempt.model_validate(item) for item in record["attempts"])
    predecessor = record["previous_record_sha256"]
    if (not attempts and predecessor is not None) or (
        attempts
        and (not isinstance(predecessor, str) or not re.fullmatch(r"[0-9a-f]{64}", predecessor))
    ):
        raise ValueError("Attempt records require a predecessor digest; an empty plan forbids it.")
    if preparation_progress(plan, attempts) != record["progress"]:
        raise ValueError("Stored progress disagrees with the preparation attempts.")
    return record, hashlib.sha256(body).hexdigest()


def publish_record(
    output: Path, plan: dict, attempts: tuple[PreparationAttempt, ...], previous=None
) -> dict:
    """Publish a complete external record once; refuse replacement, including identical bytes."""
    output = runtime_path(output)
    if (not attempts and previous is not None) or (
        attempts and (not isinstance(previous, str) or not re.fullmatch(r"[0-9a-f]{64}", previous))
    ):
        raise ValueError("Attempt records require a predecessor digest; an empty plan forbids it.")
    result = {
        "schema_version": 1,
        "plan": plan,
        "plan_sha256": content_digest(plan),
        "attempts": [attempt.model_dump(mode="json") for attempt in attempts],
        "progress": preparation_progress(plan, attempts),
        "previous_record_sha256": previous,
    }
    body = (json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()
    if len(body) > 32 * 1024 * 1024:
        raise ValueError("Preparation record exceeds 32 MB.")
    output.parent.mkdir(parents=True, exist_ok=True)
    # Publish by hard link after flushing: readers never see a partial final record.
    # An occupied destination is an error, never permission to replace evidence.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=output.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(body)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return {"record_sha256": hashlib.sha256(body).hexdigest(), **result["progress"]}


def main() -> int:
    """Create a source plan, append one terminal attempt or inspect verified progress."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan")
    plan.add_argument("--source-sha256", required=True)
    plan.add_argument("--exposed-repository", action="append", default=[])
    plan.add_argument("--output", type=Path, required=True)
    record = commands.add_parser("record")
    record.add_argument("previous", type=Path)
    record.add_argument("attempt", type=Path)
    record.add_argument("--output", type=Path, required=True)
    progress = commands.add_parser("progress")
    progress.add_argument("record", type=Path)
    args = parser.parse_args()
    try:
        source = _read(args.source)
        if args.command == "plan":
            prepared = prepare_sample(source, args.source_sha256, tuple(args.exposed_repository))
            result = publish_record(args.output, prepared, ())
        elif args.command == "record":
            previous, digest = read_record(source, args.previous)
            attempt = PreparationAttempt.model_validate_json(_read(args.attempt))
            attempts = tuple(
                PreparationAttempt.model_validate(item) for item in previous["attempts"]
            )
            result = publish_record(args.output, previous["plan"], (*attempts, attempt), digest)
        else:
            previous, digest = read_record(source, args.record)
            result = {"record_sha256": digest, **previous["progress"]}
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"Study preparation failed: {error}", file=sys.stderr)
        return 1


def _read(path: Path) -> bytes:
    with path.open("rb") as stream:
        body = stream.read(32 * 1024 * 1024 + 1)
    if len(body) > 32 * 1024 * 1024:
        raise ValueError("Preparation input exceeds 32 MB.")
    return body


if __name__ == "__main__":
    raise SystemExit(main())
