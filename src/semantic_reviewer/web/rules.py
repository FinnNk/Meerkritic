"""Inspect immutable rule versions and record explicit, version-fenced research judgements."""

import json
from uuid import uuid4

from fastapi import HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.concurrency import run_in_threadpool

from semantic_reviewer.application.rules import RuleService
from semantic_reviewer.domain.rules import RuleDecisionRequest, RuleDefinition, RuleEvidence
from semantic_reviewer.web.discovery import local_form


def add_rule_routes(app, templates, service: RuleService) -> None:
    """Attach rule inspection and bounded same-origin mutations to the local harness."""

    def conflict(request, fields):
        return templates.TemplateResponse(
            request=request,
            name="rule_conflict.html",
            status_code=409,
            context={"submitted": json.dumps(fields, indent=2, ensure_ascii=False)},
        )

    @app.get("/rules", response_class=HTMLResponse)
    def rules(request: Request):
        """List current candidate heads; opening a version verifies its immutable body."""
        return templates.TemplateResponse(
            request=request, name="rules.html", context={"heads": service.store.recent()}
        )

    @app.get("/rules/{version_id}", response_class=HTMLResponse)
    def detail(request: Request, version_id: str):
        """Render a verified version, exact source evidence and historical decisions."""
        try:
            head, body, evidence, decisions = service.store.read(version_id)
            _, snapshot = service.discovery.selections.read(body.selection_id)
            records = {item.annotation.id: item for item in snapshot.records}
            examples = [(item, records[item.annotation_id]) for item in evidence]
            trace = (
                service.files.read_json(body.origin.trace_digest)
                if body.origin.trace_digest
                else None
            )
        except LookupError as error:
            raise HTTPException(404, "Rule or source selection does not exist.") from error
        except (ValueError, OSError, KeyError) as error:
            raise HTTPException(
                409, "Rule or source evidence is unavailable or changed."
            ) from error
        return templates.TemplateResponse(
            request=request,
            name="rule.html",
            context={
                "head": head,
                "trace": json.dumps(trace, indent=2, ensure_ascii=False) if trace else None,
                "body": body,
                "version_id": version_id,
                "examples": examples,
                "decisions": decisions,
                "sources": [
                    item for item in snapshot.records if item.exclusion != "holdout_repository"
                ],
                "evidence_id": str(uuid4()),
                "operation_id": str(uuid4()),
                "definition": body.definition,
                "support": "\n".join(body.definition.supporting_annotations),
                "exclusions": "\n".join(body.definition.exclusions),
            },
        )

    @app.post("/rules/{version_id}/decide")
    async def decide(request: Request, version_id: str):
        """Record an explicit fenced research decision; preserve submitted values on conflict."""
        fields = await local_form(request)
        try:
            decision = RuleDecisionRequest(
                operation_id=fields.get("operation_id", ""),
                version_id=version_id,
                expected_revision=int(fields.get("revision", "")),
                action=fields.get("action", ""),
                actor=fields.get("actor", ""),
                rationale=fields.get("rationale", ""),
            )
            await run_in_threadpool(service.store.decide, decision)
        except (ValueError, LookupError, OSError):
            return conflict(request, fields)
        return RedirectResponse("/rules/" + version_id, status_code=303)

    @app.post("/rules/{version_id}/evidence")
    async def evidence(request: Request, version_id: str):
        """Validate a typed source claim and append it against the expected current revision."""
        fields = await local_form(request)
        try:
            item = RuleEvidence(
                id=fields.get("evidence_id", ""),
                version_id=version_id,
                annotation_id=fields.get("annotation_id", ""),
                kind=fields.get("kind", ""),
                verification=fields.get("verification", ""),
                actor=fields.get("actor", ""),
                rationale=fields.get("rationale", ""),
            )
            await run_in_threadpool(service.add_evidence, item, int(fields.get("revision", "")))
        except (ValueError, LookupError, OSError):
            return conflict(request, fields)
        return RedirectResponse("/rules/" + version_id, status_code=303)

    @app.post("/rules/{version_id}/revise")
    async def revise(request: Request, version_id: str):
        """Publish a child definition with retained evidence; preserve input on conflict."""
        fields = await local_form(request)
        try:
            definition = RuleDefinition(
                statement=fields.get("statement", ""),
                scope=fields.get("scope", ""),
                applicability=fields.get("applicability", ""),
                violation=fields.get("violation", ""),
                exclusions=tuple(
                    line.strip()
                    for line in fields.get("exclusions", "").splitlines()
                    if line.strip()
                ),
                supporting_annotations=tuple(
                    line.strip() for line in fields.get("support", "").splitlines() if line.strip()
                ),
            )
            replacement = await run_in_threadpool(
                service.revise,
                version_id,
                definition,
                fields.get("actor", ""),
                fields.get("rationale", ""),
                int(fields.get("revision", "")),
            )
        except (ValueError, LookupError, OSError):
            return conflict(request, fields)
        return RedirectResponse("/rules/" + replacement, status_code=303)
