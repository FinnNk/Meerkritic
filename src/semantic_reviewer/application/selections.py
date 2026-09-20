"""Freeze explicit annotation versions without turning test decisions into research labels."""

import json
from dataclasses import dataclass
from typing import Literal, Protocol, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from semantic_reviewer.application.annotations import Annotation, AnnotationStore, JobReader
from semantic_reviewer.application.artefacts import ResultStore
from semantic_reviewer.application.datasets import DatasetService
from semantic_reviewer.domain.datasets import Dataset, Observation
from semantic_reviewer.domain.normalisation import IssueInterpretation, ground


class SelectionRequest(BaseModel):
    """Declare ordered versions, purpose and holdouts; never infer the latest result.

    Research requires a curator's explicit claim that the included decisions were
    human-reviewed. This records attestation, not authentication or sampling validity.
    Fixture requests cannot carry that claim. Repository names use owner/name,
    case-insensitive for exclusion; an empty holdout list must be explicit.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)
    dataset_id: str = Field(min_length=1, max_length=200)
    annotation_ids: tuple[str, ...] = Field(min_length=1, max_length=100)
    purpose: Literal["fixture", "research"]
    holdout_repositories: tuple[str, ...] = Field(max_length=1000)
    curator: str | None = Field(default=None, min_length=1, max_length=200)
    human_review_attested: bool = Field(default=False, strict=True)

    @model_validator(mode="after")
    def validate_choices(self) -> Self:
        """Reject ambiguous versions and contradictory provenance before any reads."""
        if len(set(self.annotation_ids)) != len(self.annotation_ids) or any(
            not item.strip() or len(item) > 200 for item in self.annotation_ids
        ):
            raise ValueError("Choose distinct, non-empty annotation IDs of at most 200 characters.")
        if any(
            len(repo) > 200
            or len(repo.split("/")) != 2
            or any(not part or part.strip() != part for part in repo.split("/"))
            for repo in self.holdout_repositories
        ):
            raise ValueError("Holdout repositories must use owner/name.")
        if len({repo.casefold() for repo in self.holdout_repositories}) != len(
            self.holdout_repositories
        ):
            raise ValueError("Holdout repositories must be distinct.")
        if self.purpose == "research":
            if not self.curator or not self.curator.strip() or not self.human_review_attested:
                raise ValueError(
                    "Research requires a named curator and explicit human-review attestation."
                )
        elif self.curator is not None or self.human_review_attested:
            raise ValueError("Fixture selections cannot claim human-review attestation.")
        return self


class SelectedAnnotation(BaseModel):
    """Retain source, chosen decision and effective interpretation, including uncertainty."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    annotation: Annotation
    source: Observation
    interpretation: IssueInterpretation
    exclusion: Literal["rejected_interpretation", "holdout_repository"] | None


class SelectionSnapshot(BaseModel):
    """A bounded immutable input body; registration time is outside its content identity."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: Literal[1] = 1
    eligibility_policy: Literal["explicit-accept-edit-v1"] = "explicit-accept-edit-v1"
    request: SelectionRequest
    dataset: Dataset
    records: tuple[SelectedAnnotation, ...] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def validate_identity(self) -> Self:
        """Enforce version uniqueness, grounding and the declared exclusion policy."""
        if (
            self.dataset.id != self.request.dataset_id
            or tuple(item.annotation.id for item in self.records) != self.request.annotation_ids
        ):
            raise ValueError("Selection records must match the ordered request and dataset.")
        source_ids = [item.source.id for item in self.records]
        if len(set(source_ids)) != len(source_ids):
            raise ValueError("Choose exactly one annotation version per source record.")
        for item in self.records:
            source, annotation = item.source, item.annotation
            if (
                source.id != f"{self.dataset.source_sha256}:{source.source_index}"
                or not 0 <= source.source_index < self.dataset.row_count
                or annotation.observation_id != source.id
            ):
                raise ValueError("Selection source identity disagrees with dataset or annotation.")
            expected = _exclusion(self.request, annotation, source)
            if item.exclusion != expected:
                raise ValueError("Selection exclusion disagrees with the frozen policy.")
            ground(item.interpretation, source)
        return self


def _exclusion(
    request: SelectionRequest, annotation: Annotation, source: Observation
) -> Literal["rejected_interpretation", "holdout_repository"] | None:
    # Holdout wins when both apply; the original Reject decision remains in the record.
    if f"{source.owner}/{source.repository}".casefold() in {
        repo.casefold() for repo in request.holdout_repositories
    }:
        return "holdout_repository"
    return "rejected_interpretation" if annotation.decision == "reject" else None


@dataclass(frozen=True)
class SelectionSummary:
    """Small persisted metadata; counts describe this snapshot, not dataset coverage."""

    id: str
    dataset_id: str
    purpose: Literal["fixture", "research"]
    included: int
    excluded: int
    created_at: str


class SelectionStore(Protocol):
    """Own immutable body publication, atomic metadata/events and verified inspection."""

    def publish(self, snapshot: SelectionSnapshot) -> SelectionSummary:
        """Publish at most 32 MB canonical JSON, then atomically register metadata/event.

        Identical content returns the original ID/time without another event. Never
        replace an existing file; damaged content raises ValueError. I/O and database
        failures propagate and may leave a complete, unreferenced file, never a
        registered partial snapshot. The request order is part of content identity.
        """
        ...

    def read(self, selection_id: str) -> tuple[SelectionSummary, SelectionSnapshot]:
        """Verify stored bytes, schema and metadata before returning the bounded snapshot.

        Unknown IDs raise LookupError; invalid IDs/corruption raise ValueError;
        filesystem errors propagate. This self-contained body does not re-read live
        annotations or claim that its original source/result files remain available.
        """
        ...

    def recent(self, page: int = 1) -> tuple[SelectionSummary, ...]:
        """List at most 20 metadata rows newest first; page is 1..1,000,000.

        Invalid bounds raise ValueError. This catalogue query does not verify bodies.
        """
        ...


class SelectionService:
    """Hide eligibility, source/edit resolution and provenance checks behind one operation."""

    def __init__(
        self,
        annotations: AnnotationStore,
        jobs: JobReader,
        datasets: DatasetService,
        results: ResultStore,
        store: SelectionStore,
    ) -> None:
        """Bind ports for the same runtime; expose the store's read-only inspection operations."""
        self._annotations = annotations
        self._jobs = jobs
        self._datasets = datasets
        self._results = results
        self.store = store

    def freeze(self, request: SelectionRequest) -> SelectionSummary:
        """Verify explicit choices and publish an immutable selection outside HTTP.

        Accept uses the original body; Edit uses its verified replacement and keeps
        the original hash. Reject/holdout records remain explicit exclusions. No
        existing annotation is changed, and later decisions cannot enter this body.
        Unknown records raise LookupError; identity/schema/grounding conflicts raise
        ValueError; storage errors propagate. Nothing registers before all inputs
        pass. Caller-declared holdouts/attestation are retained claims, not inferred facts.
        """
        records = []
        dataset = None
        for annotation_id in request.annotation_ids:
            annotation = self._annotations.by_id(annotation_id)
            if annotation is None:
                raise LookupError("Annotation does not exist.")
            job, original = self._jobs.inspect(annotation.job_id)
            if (
                job.dataset_id != request.dataset_id
                or job.status != "succeeded"
                or job.artefact_sha256 != annotation.result_sha256
                or job.observation_id != annotation.observation_id
                or original is None
                or original.get("job_id") != job.id
            ):
                raise ValueError("Annotation does not identify the exact successful result.")
            dataset, source = self._datasets.observation(job.dataset_id, job.source_index)
            body = original
            if annotation.decision == "edit":
                body = self._results.read(annotation.interpretation_sha256)
                if (
                    body.get("job_id") != job.id
                    or body.get("original_result_sha256") != annotation.result_sha256
                    or body.get("observation_id") != source.id
                ):
                    raise ValueError("Edited interpretation has conflicting provenance.")
            interpretation = IssueInterpretation.model_validate_json(
                json.dumps(body.get("interpretation"))
            )
            records.append(
                SelectedAnnotation(
                    annotation=annotation,
                    source=source,
                    interpretation=interpretation,
                    exclusion=_exclusion(request, annotation, source),
                )
            )
        return self.store.publish(
            SelectionSnapshot(
                request=request,
                dataset=dataset,
                records=tuple(records),
            )
        )
