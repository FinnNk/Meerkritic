"""Read-only, local observation browser and bounded JSON endpoints."""

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from semantic_reviewer.application.datasets import DatasetService
from semantic_reviewer.domain.datasets import DatasetError


def create_app(datasets: DatasetService) -> FastAPI:
    """Build the read-only HTML and JSON interface for a dataset service.

    Args:
        datasets: Service supplying registration metadata and verified observations.

    Returns:
        A FastAPI application without starting a server. Observation requests map
        unknown IDs to 404 and dataset-integrity failures to 409; FastAPI rejects
        invalid query bounds with 422 before calling the handler.
    """
    app = FastAPI(title="Meerkritic", version="0.1.0")
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
            request=request, name="index.html", context={"datasets": datasets.datasets()}
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
            context={"result": observations(dataset_id, page, page_size)},
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

    return app
