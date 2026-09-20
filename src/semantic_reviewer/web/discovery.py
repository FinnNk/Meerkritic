"""Submit explicit corpus jobs and inspect verified provenance without invoking models."""

import json
from urllib.parse import parse_qs

from fastapi import HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.concurrency import run_in_threadpool

from semantic_reviewer.application.discovery import DiscoveryService


async def local_form(request: Request) -> dict[str, str]:
    """Read a bounded same-origin form; reject repeated fields and cross-site writes."""
    if request.headers.get("origin") != f"{request.url.scheme}://{request.url.netloc}":
        raise HTTPException(403, "Use the local harness form.")
    if request.headers.get("content-type", "").split(";")[0] != "application/x-www-form-urlencoded":
        raise HTTPException(415, "Submit the form.")
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > 64000:
            raise HTTPException(413, "Form is too large.")
    try:
        fields = parse_qs(body.decode("utf-8"), keep_blank_values=True, max_num_fields=20)
        if any(len(values) != 1 for values in fields.values()):
            raise ValueError("Repeated field.")
        return {key: values[0] for key, values in fields.items()}
    except (ValueError, UnicodeError) as error:
        raise HTTPException(422, "Invalid form.") from error


def add_discovery_routes(app, templates, service: DiscoveryService):
    """Attach queue and result views to an already configured loopback harness."""

    @app.get("/discovery", response_class=HTMLResponse)
    def runs(request: Request):
        """List recent discovery metadata without invoking a model."""
        return templates.TemplateResponse(
            request=request, name="discovery.html", context={"runs": service.store.recent()}
        )

    @app.post("/discovery/embed")
    async def embed(request: Request):
        """Queue verified frozen inputs after bounded same-origin submission."""
        fields = await local_form(request)
        try:
            run = await run_in_threadpool(service.embed, fields.get("selection_id", ""))
        except (ValueError, LookupError, OSError) as error:
            raise HTTPException(
                409, "Selection is unavailable or has no eligible records."
            ) from error
        return RedirectResponse(f"/discovery/{run.id}", status_code=303)

    @app.post("/discovery/cluster")
    async def cluster(request: Request):
        """Queue an exact embedding result with explicit grouping parameters."""
        fields = await local_form(request)
        try:
            run = await run_in_threadpool(
                service.cluster,
                fields.get("embedding_run", ""),
                float(fields.get("threshold", "")),
                int(fields.get("minimum_size", "2")),
            )
        except (ValueError, LookupError, OSError) as error:
            raise HTTPException(
                409, "Clustering parameters or embedding evidence are invalid."
            ) from error
        return RedirectResponse(f"/discovery/{run.id}", status_code=303)

    @app.get("/discovery/{run_id}", response_class=HTMLResponse)
    def detail(request: Request, run_id: str, page: int = Query(1, ge=1, le=10)):
        """Render verified provenance and a bounded membership page; reject missing evidence."""
        try:
            run, body = service.inspect(run_id)
            trace = (
                service.files.read_json(body["trace_digest"])
                if body and body.get("trace_digest")
                else None
            )
            if trace and trace.get("run_id") != run.id:
                raise ValueError("Synthesis trace belongs to another invocation.")
            summary, snapshot = service.selections.read(run.request.selection_id)
            records = {item.annotation.id: item for item in snapshot.records}
            members = (
                service.files.read_members(body["members_digest"])
                if body and body.get("members_digest")
                else ()
            )
            rows = [(member, records[member["annotation_id"]]) for member in members]
        except LookupError as error:
            raise HTTPException(404, "Discovery run or input does not exist.") from error
        except (ValueError, OSError, KeyError) as error:
            raise HTTPException(409, "Discovery evidence is unavailable or changed.") from error
        return templates.TemplateResponse(
            request=request,
            name="discovery_run.html",
            context={
                "run": run,
                "body": body,
                "summary": summary,
                "rows": rows[(page - 1) * 10 : page * 10],
                "page": page,
                "total": len(rows),
                "manifest": json.dumps(body, indent=2, ensure_ascii=False),
                "trace": json.dumps(trace, indent=2, ensure_ascii=False) if trace else None,
                "telemetry": body.get("telemetry")
                if body and body.get("telemetry")
                else service.telemetry(run),
            },
        )

    @app.post("/discovery/synthesise")
    async def synthesise(request: Request):
        """Queue a pinned cluster group for worker synthesis; return its inspection URL."""
        fields = await local_form(request)
        try:
            run = await run_in_threadpool(
                service.synthesise, fields.get("cluster_run", ""), int(fields.get("cluster", ""))
            )
        except (ValueError, LookupError, OSError) as error:
            raise HTTPException(409, "Synthesis needs a successful cluster and group.") from error
        return RedirectResponse(f"/discovery/{run.id}", status_code=303)
