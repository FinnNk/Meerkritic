"""Submit explicit corpus jobs and inspect verified provenance without invoking models."""

import json
from urllib.parse import parse_qs

from fastapi import HTTPException, Request
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
        return templates.TemplateResponse(
            request=request, name="discovery.html", context={"runs": service.store.recent()}
        )

    @app.post("/discovery/embed")
    async def embed(request: Request):
        fields = await local_form(request)
        try:
            run = await run_in_threadpool(service.embed, fields.get("selection_id", ""))
        except (ValueError, LookupError, OSError) as error:
            raise HTTPException(
                409, "Selection is unavailable or has no eligible records."
            ) from error
        return RedirectResponse(f"/discovery/{run.id}", status_code=303)

    @app.get("/discovery/{run_id}", response_class=HTMLResponse)
    def detail(request: Request, run_id: str):
        try:
            run, body = service.inspect(run_id)
            summary, _ = service.selections.read(run.request.selection_id)
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
                "manifest": json.dumps(body, indent=2, ensure_ascii=False),
            },
        )
