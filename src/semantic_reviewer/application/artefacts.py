"""Own explicit artefact publication metadata and maintenance contracts."""

from dataclasses import dataclass
from typing import Literal, Protocol, TypedDict

ArtefactKind = Literal["normalisation", "human_edit", "job_log"]


@dataclass(frozen=True)
class Publication:
    """Identify the owning job and evidence kind independently of JSON body keys.

    Construction rejects blank job identities and unsupported kinds. The store
    checks the job exists; callers own the meaning and version of the JSON body.
    """

    job_id: str
    kind: ArtefactKind

    def __post_init__(self) -> None:
        if not self.job_id.strip() or self.kind not in ("normalisation", "human_edit", "job_log"):
            raise ValueError("Publication requires a job identity and supported artefact kind.")


class ArtefactMetadata(TypedDict):
    """Describe catalogued immutable bytes; path is absolute and size is in bytes."""

    sha256: str
    job_id: str
    type: ArtefactKind
    path: str
    size: int
    created_at: str


class ResultStore(Protocol):
    """Publish verified JSON objects with explicit metadata outside operational SQLite."""

    def publish(self, value: dict[str, object], publication: Publication) -> str:
        """Retain complete bytes and catalogue metadata, returning their SHA-256.

        The body must be a JSON-serialisable object; another shape raises ValueError
        before publication. Its keys do not select storage behaviour.
        The job must exist. Identical body/metadata retries are safe; conflicting
        metadata raises ValueError. Filesystem/database failures propagate and may
        leave a complete unreferenced file, never an accepted partial result.
        """
        ...

    def read(self, digest: str) -> dict[str, object]:
        """Verify and return a JSON object; no writes or schema inference occur.

        Invalid identity, checksum or object shape raises ValueError. Missing or
        unreadable files raise OSError. Payload schema validation belongs to callers.
        """
        ...


class ArtefactIndex(Protocol):
    """Expose explicit maintenance of existing result/edit catalogue references."""

    def index_referenced(self) -> int:
        """Verify and catalogue relational result/edit references; return their count.

        Metadata comes from the referring job/annotation, never inferred body keys.
        Repeated runs are safe. Integrity or metadata conflicts raise ValueError;
        storage failures propagate. Earlier successful entries remain on failure.
        """
        ...
