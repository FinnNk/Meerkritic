"""Render saved intent and explicit batch application without starting model work."""

import json
from uuid import uuid4

from fastapi import HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.concurrency import run_in_threadpool

from semantic_reviewer.application.interaction import ReviewWorkspace
from semantic_reviewer.application.rules import RuleService
from semantic_reviewer.domain.interaction import DiscussionNote, ReviewDraft, ReviewIntent
from semantic_reviewer.web.discovery import local_form


def add_interaction_routes(app, templates, workspace: ReviewWorkspace, rules: RuleService) -> None:
    """Attach bounded draft editing, explicit application and append-only discussion."""

    def render(request, draft_id=None, version=None, error=None):
        metadata, body = workspace.read(draft_id) if draft_id else (None, None)
        targets = [intent.version_id for intent in body.intents] if body else []
        if version and version not in targets:
            targets.append(version)
        targets += [h.version_id for h in rules.store.recent() if h.version_id not in targets]
        rows = []
        for target in targets[:20]:
            head, rule, _, _ = rules.store.read(target)
            intent = (
                next((i for i in body.intents if i.version_id == target), None) if body else None
            )
            rows.append(
                {
                    "version": target,
                    "title": rule.definition.statement,
                    "revision": intent.expected_revision if intent else head.revision,
                    "current_revision": head.revision,
                    "intent": intent,
                    "task": workspace.task(target),
                }
            )
        return templates.TemplateResponse(
            request=request,
            name="review_workspace.html",
            status_code=409 if error else 200,
            context={
                "drafts": workspace.recent(),
                "metadata": metadata,
                "body": body,
                "rows": rows,
                "draft_id": draft_id or str(uuid4()),
                "error": error,
                "receipt": json.loads(metadata["receipt_json"])
                if metadata and metadata["receipt_json"]
                else None,
            },
        )

    @app.get("/review-workspace", response_class=HTMLResponse)
    def page(request: Request, draft_id: str | None = None, version: str | None = None):
        """Render saved intent and current target state without applying any decision."""
        try:
            return render(request, draft_id, version)
        except LookupError as error:
            raise HTTPException(404, "Draft or rule does not exist.") from error
        except (ValueError, OSError) as error:
            raise HTTPException(409, "Draft or rule evidence is unavailable or changed.") from error

    @app.post("/review-workspace/save")
    async def save(request: Request):
        """Save a bounded draft only; preserve submitted values on a stale or invalid write."""
        fields = await local_form(request, max_fields=85)
        try:
            intents = tuple(
                ReviewIntent(
                    version_id=fields.get(f"version_{i}", ""),
                    expected_revision=int(fields.get(f"revision_{i}", "")),
                    action=fields[f"action_{i}"],
                    rationale=fields.get(f"rationale_{i}", ""),
                )
                for i in range(20)
                if fields.get(f"action_{i}")
            )
            body = ReviewDraft(actor=fields.get("actor", ""), intents=intents)
            revision = int(fields["draft_revision"]) if fields.get("draft_revision") else None
            await run_in_threadpool(workspace.save, fields.get("draft_id", ""), revision, body)
        except (ValueError, LookupError, OSError):
            return templates.TemplateResponse(
                request=request,
                name="rule_conflict.html",
                status_code=409,
                context={"submitted": json.dumps(fields, indent=2)},
            )
        return RedirectResponse("/review-workspace?draft_id=" + fields["draft_id"], status_code=303)

    @app.post("/review-workspace/apply")
    async def apply(request: Request):
        """Apply the exact saved revision atomically; retain the draft and identify
        target conflicts.
        """
        fields = await local_form(request)
        try:
            await run_in_threadpool(
                workspace.apply, fields.get("draft_id", ""), int(fields.get("revision", ""))
            )
        except ValueError as error:
            return await run_in_threadpool(
                render, request, fields.get("draft_id"), None, str(error)
            )
        except (LookupError, OSError) as error:
            raise HTTPException(409, "Saved draft is unavailable; no batch was applied.") from error
        return RedirectResponse("/review-workspace?draft_id=" + fields["draft_id"], status_code=303)

    @app.post("/review-workspace/discuss")
    async def discuss(request: Request):
        """Append an exact-version message once; do not send it to an agent."""
        fields = await local_form(request)
        try:
            note = DiscussionNote(
                id=fields.get("note_id", ""),
                version_id=fields.get("version_id", ""),
                actor=fields.get("actor", ""),
                text=fields.get("text", ""),
            )
            await run_in_threadpool(workspace.discuss, note)
        except (ValueError, LookupError, OSError):
            return templates.TemplateResponse(
                request=request,
                name="rule_conflict.html",
                status_code=409,
                context={"submitted": json.dumps(fields, indent=2)},
            )
        return RedirectResponse("/rules/" + note.version_id, status_code=303)
