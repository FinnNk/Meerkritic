"""Local source browser, job submission and inspectable normalisation results."""

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.concurrency import run_in_threadpool
from starlette.middleware.trustedhost import TrustedHostMiddleware

from semantic_reviewer.application.annotations import AnnotationService, review_actions
from semantic_reviewer.application.architecture import ArchitectureView
from semantic_reviewer.application.datasets import DatasetService
from semantic_reviewer.application.discovery import DiscoveryService
from semantic_reviewer.application.guidance import GuidanceService
from semantic_reviewer.application.interaction import ReviewWorkspace
from semantic_reviewer.application.jobs import JobService
from semantic_reviewer.application.reviews import ReviewIndex
from semantic_reviewer.application.rules import RuleService
from semantic_reviewer.application.selections import SelectionStore
from semantic_reviewer.domain.datasets import DatasetError
from semantic_reviewer.web.assessment import (
    OPTIONS,
    AssessmentForm,
    assessment_error,
    parse_assessment,
)
from semantic_reviewer.web.discovery import add_discovery_routes
from semantic_reviewer.web.guidance import add_guidance_routes
from semantic_reviewer.web.interaction import add_interaction_routes
from semantic_reviewer.web.rules import add_rule_routes


def create_app(
    datasets: DatasetService,
    jobs: JobService | None = None,
    annotations: AnnotationService | None = None,
    reviews: ReviewIndex | None = None,
    selections: SelectionStore | None = None,
    discovery: DiscoveryService | None = None,
    rules: RuleService | None = None,
    workspace: ReviewWorkspace | None = None,
    guidance: GuidanceService | None = None,
    architecture: ArchitectureView | None = None,
) -> FastAPI:
    """Build local HTML and JSON interfaces, with optional queue access.

    Args:
        datasets: Service supplying registration metadata and verified observations.
        jobs: Queue/result access. When absent, job routes are not registered.
        annotations: Human review access, enabled only together with jobs. Supplied
            services must refer to the same runtime data as datasets and jobs.
        reviews: Optional external DER reference index; enables the reviews page.
        selections: Optional frozen-input catalogue for the same runtime. Enables
            read-only browsing; freezing remains an explicit command-line operation.

    Returns:
        A FastAPI application without starting a server. Observation requests map
        unknown IDs to 404 and dataset-integrity failures to 409; FastAPI rejects
        invalid query bounds with 422 before calling the handler.
        Construction does not enqueue or execute inference. HTTP mutation routes
        persist explicit submissions; human decisions include their events.
    """
    app = FastAPI(title="Meerkritic", version="0.1.0")
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"], www_redirect=False
    )
    templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
    templates.env.globals["has_reviews"] = reviews is not None
    templates.env.globals["has_selections"] = selections is not None
    templates.env.globals["has_discovery"] = discovery is not None
    templates.env.globals["has_rules"] = rules is not None
    templates.env.globals["has_workspace"] = workspace is not None
    templates.env.globals["has_guidance"] = guidance is not None
    templates.env.globals["has_architecture"] = architecture is not None
    if architecture is not None:

        @app.get("/architecture", response_class=HTMLResponse)
        def architecture_page(request: Request):
            """Render verified architecture evidence and stale-source status; never
            refresh it implicitly.
            """
            try:
                view = architecture.read()
            except (ValueError, OSError) as error:
                raise HTTPException(
                    409, "Architecture evidence is unavailable or changed."
                ) from error
            return templates.TemplateResponse(
                request=request,
                name="architecture.html",
                context={
                    "view": view,
                    **{
                        name: json.dumps(view["body"][name], indent=2) if view else None
                        for name in ("before", "after", "delta")
                    },
                },
            )

    if guidance is not None:
        add_guidance_routes(app, templates, guidance)
    if workspace is not None and rules is not None:
        add_interaction_routes(app, templates, workspace, rules)
    if rules is not None:
        add_rule_routes(app, templates, rules, workspace)
    if discovery is not None:
        add_discovery_routes(app, templates, discovery)

    if selections is not None:

        @app.get("/selections", response_class=HTMLResponse)
        def selection_list(request: Request, page: int = Query(1, ge=1, le=1_000_000)):
            """List bounded metadata without claiming its bodies have been verified."""
            return templates.TemplateResponse(
                request=request,
                name="selections.html",
                context={"items": selections.recent(page), "page": page},
            )

        @app.get("/selections/{selection_id}", response_class=HTMLResponse)
        def selection_detail(
            request: Request,
            selection_id: str,
            page: int = Query(1, ge=1, le=10),
        ):
            """Verify the frozen body and display ten records, including labelled exclusions."""
            try:
                summary, snapshot = selections.read(selection_id)
            except LookupError as error:
                raise HTTPException(404, "Selection does not exist.") from error
            except (ValueError, OSError) as error:
                raise HTTPException(
                    409, "Frozen selection evidence is unavailable or changed."
                ) from error
            return templates.TemplateResponse(
                request=request,
                name="selection.html",
                context={
                    "summary": summary,
                    "snapshot": snapshot,
                    "page": page,
                    "items": snapshot.records[(page - 1) * 10 : page * 10],
                },
            )

    if reviews is not None:

        @app.get("/reviews", response_class=HTMLResponse)
        def review_references(request: Request):
            """Display indexed readiness separately from slice status and owner approval."""
            return templates.TemplateResponse(
                request=request, name="reviews.html", context={"references": reviews.references()}
            )

    @app.exception_handler(DatasetError)
    async def dataset_error(request: Request, error: DatasetError):
        """Report invalid or conflicting dataset evidence as HTTP 409."""
        return JSONResponse(status_code=409, content={"detail": str(error)})

    def observations(dataset_id: str, page: int, page_size: int):
        """Translate missing dataset identities into HTTP 404 for both browser and API callers."""
        try:
            return datasets.browse(dataset_id, page, page_size)
        except LookupError as error:
            raise HTTPException(404, "Dataset is not registered.") from error

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request):
        """Render the registered dataset catalogue."""
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"datasets": datasets.datasets(), "can_normalise": jobs is not None},
        )

    @app.get("/datasets/{dataset_id}", response_class=HTMLResponse)
    def browse(
        request: Request,
        dataset_id: str,
        page: int = Query(1, ge=1, le=1_000_000),
        page_size: int = Query(20, ge=1, le=100),
    ):
        """Render a bounded observation page with its dataset provenance."""
        return templates.TemplateResponse(
            request=request,
            name="observations.html",
            context={
                "result": observations(dataset_id, page, page_size),
                "can_normalise": jobs is not None,
                "can_annotate": annotations is not None,
            },
        )

    @app.get("/api/datasets")
    def list_datasets():
        """Return registered dataset metadata as JSON."""
        return datasets.datasets()

    @app.get("/api/datasets/{dataset_id}/observations")
    def api_observations(
        dataset_id: str,
        page: int = Query(1, ge=1, le=1_000_000),
        page_size: int = Query(20, ge=1, le=100),
    ):
        """Return a bounded observation page and its dataset provenance as JSON."""
        return observations(dataset_id, page, page_size)

    if jobs is not None:

        @app.post("/datasets/{dataset_id}/observations/{source_index}/normalise")
        def normalise(request: Request, dataset_id: str, source_index: int):
            """Enqueue only; reject browser cross-origin and non-loopback mutation requests."""
            origin = request.headers.get("origin")
            if request.url.hostname not in ("127.0.0.1", "::1", "localhost") or (
                origin != f"{request.url.scheme}://{request.url.netloc}"
            ):
                raise HTTPException(403, "Submit jobs from this local harness.")
            try:
                job = jobs.enqueue(dataset_id, source_index)
            except LookupError as error:
                raise HTTPException(404, str(error)) from error
            return RedirectResponse(f"/jobs/{job.id}", status_code=303)

        @app.get("/jobs", response_class=HTMLResponse)
        def job_list(request: Request):
            """Show recent queued, completed and failed jobs."""
            return templates.TemplateResponse(
                request=request, name="jobs.html", context={"jobs": jobs.jobs.recent()}
            )

        def render_job(
            request: Request, job_id: str, error=None, draft=None, status=200, form=None
        ):
            """Render verified results and failures without interpreting model text as HTML."""
            try:
                job, result = jobs.inspect(job_id)
                annotation, edited = annotations.review(job_id) if annotations else (None, None)
                reading = annotations.reading_context(job_id) if annotations else None
                history = annotations.store.history(job.observation_id) if annotations else ()
                actions = review_actions(job, result) if annotations else ()
                _, source = datasets.observation(job.dataset_id, job.source_index)
                initial_draft = ""
                if actions:
                    initial_draft = (
                        result["model_output"]
                        if job.status == "failed"
                        else json.dumps(result["interpretation"], ensure_ascii=False, indent=2)
                    )
                if form is None:
                    form = AssessmentForm.from_output(
                        draft.get("edited_json", initial_draft) if draft else initial_draft
                    )
            except LookupError as error:
                raise HTTPException(404, str(error)) from error
            except (ValueError, OSError) as error:
                raise HTTPException(
                    409, "Stored result evidence is unavailable or changed."
                ) from error
            return templates.TemplateResponse(
                request=request,
                name="job.html",
                status_code=status,
                context={
                    "job": job,
                    "result": result,
                    "telemetry": jobs.telemetry(job),
                    "can_annotate": annotations is not None,
                    "actions": actions,
                    "source": source,
                    "reading": reading,
                    "presented_context": (
                        draft.get("context_sha256", "")
                        if draft is not None
                        else reading.sha256
                        if reading
                        else ""
                    ),
                    "initial_draft": initial_draft,
                    "annotation": annotation,
                    "edited": edited,
                    "history": history,
                    "error": error,
                    "draft": draft,
                    "form": form,
                    "assessment_options": OPTIONS,
                },
            )

        @app.get("/jobs/{job_id}", response_class=HTMLResponse)
        def job_result(request: Request, job_id: str):
            """Show the proposed result, human decision and immutable history."""
            return render_job(request, job_id)

        if annotations is not None:

            @app.post("/jobs/{job_id}/annotation", response_class=HTMLResponse)
            async def annotate(request: Request, job_id: str):
                """Validate bounded same-origin input; preserve invalid edits for correction."""
                if request.headers.get("origin") != f"{request.url.scheme}://{request.url.netloc}":
                    raise HTTPException(403, "Submit decisions from this local harness.")
                if (
                    request.headers.get("content-type", "").split(";")[0]
                    != "application/x-www-form-urlencoded"
                ):
                    raise HTTPException(415, "Submit the annotation form.")
                body = bytearray()
                async for chunk in request.stream():
                    body.extend(chunk)
                    if len(body) > 1_000_000:
                        raise HTTPException(413, "Annotation form is too large.")
                try:
                    draft, form = parse_assessment(bytes(body))
                except (ValueError, UnicodeError) as error:
                    raise HTTPException(422, "Invalid annotation form.") from error
                try:
                    if form is not None and "form_action" in draft:
                        form.change_rows(draft["form_action"])
                        return await run_in_threadpool(
                            render_job, request, job_id, None, draft, 200, form
                        )

                    def save_assessment():
                        replacement = None
                        if draft.get("decision") == "edit":
                            replacement = draft.get("edited_json")
                            if form is not None:
                                job, _ = jobs.inspect(job_id)
                                _, source = datasets.observation(job.dataset_id, job.source_index)
                                replacement = form.interpretation_json(source)
                        return annotations.decide(
                            job_id,
                            draft.get("decision", ""),
                            draft.get("notes", ""),
                            replacement,
                            context_sha256=draft.get("context_sha256") or None,
                        )

                    await run_in_threadpool(save_assessment)
                except LookupError as error:
                    raise HTTPException(404, str(error)) from error
                except (ValueError, OSError) as error:
                    return await run_in_threadpool(
                        render_job, request, job_id, assessment_error(error), draft, 409, form
                    )
                return RedirectResponse(f"/jobs/{job_id}", status_code=303)

            @app.get("/datasets/{dataset_id}/progress", response_class=HTMLResponse)
            def progress(
                request: Request, dataset_id: str, page: int = Query(1, ge=1, le=1_000_000)
            ):
                """Expose honest source and result denominators with a paged review queue."""
                try:
                    counts = annotations.store.progress(dataset_id)
                except LookupError as error:
                    raise HTTPException(404, str(error)) from error
                return templates.TemplateResponse(
                    request=request,
                    name="progress.html",
                    context={
                        "dataset_id": dataset_id,
                        "counts": counts,
                        "page": page,
                        "pending": annotations.store.pending(dataset_id, page),
                    },
                )

    return app
