"""Pinned CRC-Py import and immutable Parquet queries; raw bodies never enter SQLite."""

import hashlib
import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import urlopen

import duckdb

from semantic_reviewer.application.datasets import PublicDataset
from semantic_reviewer.domain.datasets import Dataset, DatasetError

MAX_SOURCE_BYTES = 16 * 1024 * 1024


def digest(path: Path) -> str:
    """Compute the file SHA-256 without loading its complete contents into memory."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def publish(staged: Path, target: Path) -> None:
    """Publish complete bytes without replacing an existing artefact.

    An existing target is accepted only when its digest matches the staged file.
    A new target shares the staged file's bytes: do not modify either after
    publication. The staged name remains the caller's responsibility to remove.

    Args:
        staged: Complete file on the same filesystem as the destination.
        target: Destination whose parent directory already exists.

    Raises:
        DatasetError: The target already contains different bytes.
        OSError: Linking or reading files fails, including unsupported hard links.
    """
    try:
        # Staging shares the target filesystem: expose complete bytes without an overwrite race.
        os.link(staged, target)
    except FileExistsError:
        if digest(staged) != digest(target):
            raise DatasetError("An immutable artefact has conflicting content.") from None


class ParquetObservations:
    """Local immutable source files and canonical CRC-Py observations.

    Attributes:
        root: Artefact directory; the composition boundary keeps it outside Git.
    """

    def __init__(self, root: Path) -> None:
        """Create the artefact directory without importing or querying datasets."""
        self.root = root
        root.mkdir(parents=True, exist_ok=True)

    def prepare(self, source: PublicDataset) -> Dataset:
        """Verify pinned source bytes and publish immutable Parquet.

        Accept source files up to MAX_SOURCE_BYTES; download from a pinned GitHub
        URL on a cache miss. Revalidate cached bytes on every call. Download,
        decoding and storage errors propagate; publication may leave complete
        unreferenced files.

        Args:
            source: Catalogue entry identifying the revision, checksum and row count.

        Returns:
            Metadata ready for registration. Preparation does not write the registry.

        Raises:
            DatasetError: Source size, checksum or records violate the import contract,
                or an existing immutable artefact conflicts with the prepared bytes.
        """
        raw = self.root / (source.source_sha256 + ".json")
        with tempfile.TemporaryDirectory(dir=self.root, prefix="import-") as temporary:
            staging = Path(temporary)
            if not raw.exists():
                if not source.source_url.startswith("https://raw.githubusercontent.com/"):
                    raise DatasetError("Only pinned GitHub dataset downloads are supported.")
                with urlopen(source.source_url, timeout=60) as response:
                    body = response.read(MAX_SOURCE_BYTES + 1)
                if len(body) > MAX_SOURCE_BYTES:
                    raise DatasetError("Source exceeds the bounded importer size.")
                downloaded = staging / "source.json"
                downloaded.write_bytes(body)
                if digest(downloaded) != source.source_sha256:
                    raise DatasetError("Source checksum does not match the pinned manifest.")
                publish(downloaded, raw)
            if raw.stat().st_size > MAX_SOURCE_BYTES or digest(raw) != source.source_sha256:
                raise DatasetError("Cached source checksum or size is invalid.")
            rows = self._canonical_rows(json.loads(raw.read_text(encoding="utf-8")), source)
            canonical = staging / "observations.json"
            canonical.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
            parquet = staging / "observations.parquet"
            # Fix nullable column types so missing context cannot change the Parquet schema.
            with duckdb.connect() as connection:
                connection.execute(
                    "COPY (SELECT * FROM read_json($source, "
                    "columns={id:'VARCHAR', source_index:'BIGINT', owner:'VARCHAR', "
                    "repository:'VARCHAR', pull_request:'BIGINT', comment_id:'BIGINT', "
                    "file_path:'VARCHAR', comment:'VARCHAR', code:'VARCHAR', category:'VARCHAR', "
                    "subcategory:'VARCHAR', created_at:'VARCHAR', enriched:'VARCHAR', "
                    "line_number:'BIGINT', source_sha256:'VARCHAR', source_revision:'VARCHAR', "
                    "source_url:'VARCHAR', commit_sha:'VARCHAR'}) ORDER BY source_index) "
                    "TO $destination (FORMAT PARQUET)",
                    {"source": str(canonical), "destination": str(parquet)},
                )
            parquet_sha = digest(parquet)
            publish(parquet, self.root / (parquet_sha + ".parquet"))
        return Dataset(
            id=source.id,
            title=source.title,
            revision=source.revision,
            source_url=source.source_url,
            source_sha256=source.source_sha256,
            parquet_sha256=parquet_sha,
            row_count=len(rows),
            registered_at=datetime.now(UTC).isoformat(),
        )

    @staticmethod
    def _canonical_rows(value: object, source: PublicDataset) -> list[dict]:
        """Validate source records and preserve their order, including repeated comment IDs."""
        if not isinstance(value, list) or len(value) != source.expected_rows or not value:
            raise DatasetError("Source record count does not match the manifest.")
        string_fields = (
            "owner",
            "repo",
            "file_path",
            "comment",
            "code",
            "category",
            "subcategory",
            "comment_created_at",
        )
        rows = []
        for index, item in enumerate(value):
            if not isinstance(item, dict) or any(
                not isinstance(item.get(field), str) for field in string_fields
            ):
                raise DatasetError(f"Record {index} has invalid text fields.")
            if any(type(item.get(field)) is not int for field in ("pr_number", "comment_id")):
                raise DatasetError(f"Record {index} has invalid source identifiers.")
            line = item.get("line_number")
            if line is not None and type(line) is not int:
                raise DatasetError(f"Record {index} has an invalid line number.")
            if item.get("enriched") is not None and not isinstance(item["enriched"], str):
                raise DatasetError(f"Record {index} has invalid optional context.")
            try:
                datetime.fromisoformat(item["comment_created_at"])
            except ValueError as error:
                raise DatasetError(f"Record {index} has an invalid timestamp.") from error
            # A comment can occur in several source records; identify each by its source position.
            rows.append(
                {
                    "id": f"{source.source_sha256}:{index}",
                    "source_index": index,
                    "owner": item["owner"],
                    "repository": item["repo"],
                    "pull_request": item["pr_number"],
                    "comment_id": item["comment_id"],
                    "file_path": item["file_path"],
                    "comment": item["comment"],
                    "code": item["code"],
                    "category": item["category"],
                    "subcategory": item["subcategory"],
                    "created_at": item["comment_created_at"],
                    "enriched": item.get("enriched"),
                    "line_number": line,
                    "source_sha256": source.source_sha256,
                    "source_revision": source.revision,
                    "source_url": source.source_url,
                    # The source does not identify a commit; do not infer one from other fields.
                    "commit_sha": None,
                }
            )
        return rows
