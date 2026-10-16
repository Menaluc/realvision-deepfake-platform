"""App factory. Run with: uvicorn app.main:create_app --factory

There is no module-level app, so importing this module never loads the model.
"""

import logging

from fastapi import FastAPI

from app.api.error_handlers import register_error_handlers
from app.api.routes import health, model
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
    app.state.cache = AnalysisCache(
        max_entries=settings.cache_max_entries,
        ttl_seconds=settings.cache_ttl_seconds,
    )

    register_error_handlers(app)

    app.include_router(health.router)
    app.include_router(model.router)

    return app
