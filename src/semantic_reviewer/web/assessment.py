"""Translate editable browser fields without owning research validation or storage."""

import json
import re
from dataclasses import dataclass, field
from urllib.parse import parse_qs

from pydantic import ValidationError

from semantic_reviewer.domain.datasets import Observation
from semantic_reviewer.domain.normalisation import IssueInterpretation

SCALARS = (
    "issue_statement",
    "actionable_engineering_concern",
    "generalisable",
    "scope",
    "proposed_invariant",
)
LIST_LIMITS = {"category": 8, "evidence_source": 16, "evidence_quote": 16, "exclusion": 16}
OPTIONS = {
    name: IssueInterpretation.model_json_schema()["properties"][name]["enum"]
    for name in ("actionable_engineering_concern", "generalisable", "scope")
}


@dataclass
class AssessmentForm:
    """Keep unsaved browser values, including invalid entries, across form responses.

    Domain validation and exact source grounding still run in AnnotationService.
    Row operations only return another page; they never publish an annotation.
    """

    values: dict[str, list[str]] = field(default_factory=dict)
    unmapped_json: str = ""

    def one(self, name: str) -> str:
        """Return a scalar field, leaving absent choices visibly unselected."""
        return self.values.get(name, [""])[0]

    def rows(self, name: str) -> list[str]:
        """Return rows in their displayed order, including unsaved blank entries."""
        return self.values.get(name, [])

    @classmethod
    def from_output(cls, raw: str) -> "AssessmentForm":
        """Populate representable draft fields; retain unsupported output for inspection.

        Invalid values are not guessed or replaced with affirmative judgements.
        A malformed structure starts a blank editor and displays its original text.
        """
        form = cls()
        try:
            data = json.loads(raw)
            if not isinstance(data, dict):
                raise ValueError("Expected an object.")
            for name in SCALARS:
                value = data.get(name, "")
                if name == "proposed_invariant" and value is None:
                    value = ""
                if not isinstance(value, str):
                    raise ValueError("Expected text.")
                form.values[name] = [value]
            for name, key in (("category", "coarse_categories"), ("exclusion", "exclusions")):
                values = data.get(key, [])
                if (
                    not isinstance(values, list)
                    or len(values) > LIST_LIMITS[name]
                    or any(not isinstance(value, str) for value in values)
                ):
                    raise ValueError("Expected a bounded text list.")
                form.values[name] = values
            evidence = data.get("evidence_quotes", [])
            if not isinstance(evidence, list) or len(evidence) > 16:
                raise ValueError("Expected bounded evidence.")
            for item in evidence:
                if (
                    not isinstance(item, dict)
                    or set(item) != {"source", "quote"}
                    or any(not isinstance(value, str) for value in item.values())
                ):
                    raise ValueError("Expected an evidence source and quote.")
            form.values["evidence_source"] = [item["source"] for item in evidence]
            form.values["evidence_quote"] = [item["quote"] for item in evidence]
            if set(data) - set(SCALARS) - {"coarse_categories", "exclusions", "evidence_quotes"}:
                form.unmapped_json = raw
        except (ValueError, TypeError):
            form = cls(unmapped_json=raw)
        return form

    def change_rows(self, action: str) -> None:
        """Add or remove one named row without recording a research decision."""
        parts = action.split(":")
        if len(parts) not in (2, 3) or parts[1] not in ("category", "evidence", "exclusion"):
            raise ValueError("Choose a valid row action.")
        names = ("evidence_source", "evidence_quote") if parts[1] == "evidence" else (parts[1],)
        count = len(self.rows(names[0]))
        if parts[0] == "add" and len(parts) == 2:
            if count >= LIST_LIMITS[names[0]]:
                raise ValueError(f"This list allows at most {LIST_LIMITS[names[0]]} entries.")
            for name in names:
                self.values.setdefault(name, []).append(
                    "comment" if name == "evidence_source" else ""
                )
        elif parts[0] == "remove" and len(parts) == 3 and parts[2].isdigit():
            index = int(parts[2])
            if index >= count:
                raise ValueError("That row does not exist.")
            for name in names:
                self.values[name].pop(index)
        else:
            raise ValueError("Choose a valid row action.")

    def interpretation_json(self, source: Observation) -> str:
        """Encode user fields for the existing service; keep exact source line endings.

        HTML textareas normalise line endings. Resolve each displayed quote back
        to one literal source substring; do not trim text or relax its grounding.
        Empty list rows are omitted and an empty candidate rule means no rule.
        """
        evidence = []
        for origin, quote in zip(
            self.rows("evidence_source"), self.rows("evidence_quote"), strict=True
        ):
            if not quote:
                continue
            if origin not in ("comment", "code"):
                raise ValueError("Choose Comment or Code for each evidence quote.")
            source_text = source.comment if origin == "comment" else source.code
            # Other whitespace remains literal. Ambiguous normalised matches must
            # not select a convenient occurrence and invent a source location.
            pattern = re.escape(quote.replace("\r\n", "\n").replace("\r", "\n")).replace(
                "\\\n", r"(?:\r\n|\r(?!\n)|(?<!\r)\n)"
            )
            matches = list(re.finditer(f"(?=({pattern}))", source_text))
            if len(matches) != 1:
                raise ValueError("Evidence quote is missing or ambiguous in the source.")
            evidence.append({"source": origin, "quote": matches[0].group(1)})
        return json.dumps(
            {name: self.one(name) for name in SCALARS}
            | {
                "proposed_invariant": self.one("proposed_invariant") or None,
                "coarse_categories": [value for value in self.rows("category") if value],
                "exclusions": [value for value in self.rows("exclusion") if value],
                "evidence_quotes": evidence,
            },
            ensure_ascii=False,
        )


def parse_assessment(body: bytes) -> tuple[dict[str, str], AssessmentForm | None]:
    """Decode bounded fields or a legacy JSON submission; reject ambiguous mixtures."""
    fields = parse_qs(
        body.decode("utf-8"),
        keep_blank_values=True,
        max_num_fields=72,
        encoding="utf-8",
        errors="strict",
    )
    scalars = {"decision", "notes", "edited_json", "editor", "form_action", "context_sha256"} | set(
        SCALARS
    )
    if set(fields) - scalars - set(LIST_LIMITS):
        raise ValueError("Invalid annotation fields.")
    if any(len(values) != 1 for name, values in fields.items() if name in scalars):
        raise ValueError("Duplicate annotation fields.")
    draft = {key: values[0] for key, values in fields.items() if key in scalars}
    if "editor" not in fields:
        if set(fields) - {"decision", "notes", "edited_json", "context_sha256"}:
            raise ValueError("Invalid legacy annotation fields.")
        return draft, None
    if draft["editor"] != "fields" or "edited_json" in fields:
        raise ValueError("Choose one annotation editor.")
    if "decision" in fields and "form_action" in fields:
        raise ValueError("Choose a decision or a row action, not both.")
    if any(len(fields.get(name, [])) > limit for name, limit in LIST_LIMITS.items()):
        raise ValueError("Too many annotation rows.")
    if len(fields.get("evidence_source", [])) != len(fields.get("evidence_quote", [])):
        raise ValueError("Each evidence quote needs a matching source field.")
    return draft, AssessmentForm(fields)


def assessment_error(error: ValueError | OSError) -> str:
    """Describe failed fields without exposing a schema traceback or repeating inputs."""
    if not isinstance(error, ValidationError):
        return str(error)
    labels = {
        "issue_statement": "Issue statement",
        "scope": "Impact scope",
        "actionable_engineering_concern": "Actionable concern",
        "generalisable": "Generalisable",
        "coarse_categories": "Categories",
        "proposed_invariant": "Candidate rule",
        "evidence_quotes": "Evidence quotes",
        "exclusions": "Applicability limits",
    }
    messages = []
    for item in error.errors(include_url=False, include_input=False):
        name = labels.get(item["loc"][0], "Assessment") if item["loc"] else "Assessment"
        messages.append(f"{name}: {item['msg'].removeprefix('Value error, ')}")
    return "; ".join(messages)
