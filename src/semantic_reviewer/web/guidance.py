"""Expose deliberate coherent sends and distinguish advisory responses from applied decisions."""

import json
from uuid import uuid4

from fastapi import HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.concurrency import run_in_threadpool

from semantic_reviewer.application.guidance import GuidanceService
from semantic_reviewer.domain.guidance import GuidanceRequest, GuidanceTarget
from semantic_reviewer.web.discovery import local_form


def add_guidance_routes(app, templates, service: GuidanceService) -> None:
    """Attach bounded submission and verified inspection; model execution belongs to the worker."""

    @app.get("/guidance", response_class=HTMLResponse)
    def compose(request: Request, version: str | None = None):
        """Show at most six targets and twenty notes each for an explicit coherent submission."""
        targets = [version] if version else []
        targets += [
            h.version_id for h in service.rules.store.recent() if h.version_id not in targets
        ]
        try:
            rows = []
            for target in targets[:6]:
                head, body, _, _ = service.rules.store.read(target)
                rows.append(
                    {
                        "version": target,
                        "revision": head.revision,
                        "title": body.definition.statement,
                        "notes": service.workspace.discussion(target)[-20:],
                    }
                )
        except (ValueError, LookupError, OSError) as error:
            raise HTTPException(409, "Guidance source is unavailable or changed.") from error
        return templates.TemplateResponse(
            request=request,
            name="guidance.html",
            context={"rows": rows, "batch_id": str(uuid4()), "batches": service.store.recent()},
        )

    @app.post("/guidance")
    async def submit(request: Request):
        """Freeze checked context after same-origin validation; retain rejected input
        for correction.
        """
        fields = await local_form(request, max_fields=160)
        try:
            targets = tuple(
                GuidanceTarget(
                    version_id=fields[f"version_{i}"],
                    expected_revision=int(fields[f"revision_{i}"]),
                    discussion_ids=tuple(
                        fields[f"note_{i}_{n}"] for n in range(20) if fields.get(f"note_{i}_{n}")
                    ),
                )
                for i in range(6)
                if fields.get(f"target_{i}")
            )
            body = GuidanceRequest(
                id=fields.get("batch_id", ""),
                actor=fields.get("actor", ""),
                instruction=fields.get("instruction", ""),
                targets=targets,
            )
            await run_in_threadpool(service.submit, body)
        except (ValueError, KeyError, LookupError, OSError):
            return templates.TemplateResponse(
                request=request,
                name="rule_conflict.html",
                status_code=409,
                context={"submitted": json.dumps(fields, indent=2)},
            )
        return RedirectResponse("/guidance/" + body.id, status_code=303)

    @app.get("/guidance/{batch_id}", response_class=HTMLResponse)
    def detail(request: Request, batch_id: str):
        """Render verified advisory output and warn if its target context is now historical."""
        try:
            run, snapshot, result = service.inspect(batch_id)
            stale = []
            for target in snapshot["request"]["targets"]:
                head = service.rules.store.read(target["version_id"])[0]
                if (
                    head.version_id != target["version_id"]
                    or head.revision != target["expected_revision"]
                ):
                    stale.append(target["version_id"])
        except LookupError as error:
            raise HTTPException(404, "Guidance or rule version does not exist.") from error
        except (ValueError, OSError, KeyError) as error:
            raise HTTPException(409, "Guidance evidence is unavailable or changed.") from error
        return templates.TemplateResponse(
            request=request,
            name="guidance_result.html",
            context={
                "run": run,
                "snapshot": snapshot,
                "result": result,
                "stale": stale,
                "telemetry": service.telemetry(run),
                "trace": json.dumps(result, indent=2, ensure_ascii=False) if result else None,
            },
        )
