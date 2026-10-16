"""Response bodies. Fields are snake_case in Python and camelCase in JSON."""

from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class HealthResponse(CamelModel):
    status: Literal["ok", "degraded"]
    model_loaded: bool


class ModelResponse(CamelModel):
    backbone: str
    sampled_frames: int
    input_size: int
    feature_size: int
    embedding_size: int
    classes: list[str]


class Probabilities(CamelModel):
    real: float
    fake: float


class AnalysisResponse(CamelModel):
    id: str
    prediction: Literal["real", "fake"]
    confidence: float
    probabilities: Probabilities


class ErrorDetail(CamelModel):
    code: str
    message: str


class ErrorResponse(CamelModel):
    error: ErrorDetail
