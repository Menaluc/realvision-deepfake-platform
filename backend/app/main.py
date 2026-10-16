"""App factory. Run with: uvicorn app.main:create_app --factory

There is no module-level app, so importing this module never loads the model.
"""

import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.error_handlers import register_error_handlers
from app.api.routes import analyses, health, model
from app.api.upload_limit import UploadLimitMiddleware
from app.config import Settings
from app.ml.predictor import ModelLoadError, Predictor
from app.storage.analysis_cache import AnalysisCache

logger = logging.getLogger(__name__)


def load_predictor(settings: Settings) -> Predictor | None:
    """Returns the loaded predictor, or None to start degraded."""
    try:
        predictor = Predictor.load(settings.checkpoint_path, settings.device)
    except ModelLoadError as error:
        logger.warning("Starting in degraded mode: %s", error)
        return None

    logger.info("Model loaded from %s on %s", settings.checkpoint_path, settings.device)
    return predictor


def mount_frontend(app: FastAPI, settings: Settings) -> None:
    """Serves the built frontend at "/", so one process serves the whole app.

    Mounted after the API routers: routes are matched in order, so /api/*
    still reaches the API, and an unknown /api path falls through to the
    static files, whose 404 the error handlers turn into NOT_FOUND. There is
    no client-side routing, so unknown pages are a plain 404, not index.html.
    """
    if not (settings.frontend_dist / "index.html").is_file():
        # Normal in development, where Vite serves the frontend
        logger.info(
            "No frontend build at %s; serving the API only", settings.frontend_dist
        )
        return

    app.mount(
        "/", StaticFiles(directory=settings.frontend_dist, html=True), name="frontend"
    )


def create_app(settings: Settings | None = None, predictor=None) -> FastAPI:
    """Builds the app. Tests pass a fake predictor to skip loading the checkpoint."""
    if settings is None:
        settings = Settings.from_env()

    if predictor is None:
        predictor = load_predictor(settings)

    app = FastAPI(title="RealVision")

    app.state.settings = settings
    # None means degraded: routes that need the model answer 503
    app.state.predictor = predictor
    # Created in degraded mode too, so the frame routes still work; they
    # answer 404 because nothing can be added to it without the model
    app.state.cache = AnalysisCache(
        max_entries=settings.cache_max_entries,
        ttl_seconds=settings.cache_ttl_seconds,
    )

    register_error_handlers(app)
    app.add_middleware(UploadLimitMiddleware)

    app.include_router(health.router)
    app.include_router(model.router)
    app.include_router(analyses.router)

    # Last: it matches every path the routers above did not
    mount_frontend(app, settings)

    return app
