"""Hands routes what create_app stored on app.state."""

from fastapi import Request

from app.config import Settings
from app.errors import ModelUnavailable
from app.ml.predictor import Predictor
from app.storage.analysis_cache import AnalysisCache


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_cache(request: Request) -> AnalysisCache:
    return request.app.state.cache


def get_predictor(request: Request) -> Predictor:
    predictor = request.app.state.predictor

    # Degraded mode: every route that needs the model answers 503
    if predictor is None:
        raise ModelUnavailable()

    return predictor
