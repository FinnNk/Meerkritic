"""Local source browser, job submission and inspectable normalisation results."""

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.trustedhost import TrustedHostMiddleware

from semantic_reviewer.application.datasets import DatasetService
from semantic_reviewer.application.jobs import JobService
from semantic_reviewer.domain.datasets import DatasetError


def create_app(datasets: DatasetService, jobs: JobService | None = None) -> FastAPI:
    """Build local HTML and JSON interfaces, with optional queue access.

    Args:
        datasets: Service supplying registration metadata and verified observations.

    Returns:
        A FastAPI application without starting a server. Observation requests map
        unknown IDs to 404 and dataset-integrity failures to 409; FastAPI rejects
        invalid query bounds with 422 before calling the handler.
    """
    app = FastAPI(title="Meerkritic", version="0.1.0")
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"], www_redirect=False
    )
    templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

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

        @app.get("/jobs/{job_id}", response_class=HTMLResponse)
        def job_result(request: Request, job_id: str):
            """Render verified results and failures without interpreting model text as HTML."""
            try:
                job, result = jobs.inspect(job_id)
            except LookupError as error:
                raise HTTPException(404, str(error)) from error
            except (ValueError, OSError) as error:
                raise HTTPException(
                    409, "Stored result evidence is unavailable or changed."
                ) from error
            return templates.TemplateResponse(
                request=request,
                name="job.html",
                context={"job": job, "result": result, "telemetry": jobs.telemetry(job)},
            )

    return app
