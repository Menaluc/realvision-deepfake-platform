"""Response bodies. Fields are snake_case in Python and camelCase in JSON."""

from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    # alias_generator: JSON uses camelCase aliases (FastAPI responds by alias).
    # populate_by_name: Python code can still build models with snake_case.
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


class FrameInfo(CamelModel):
    index: int
    frame_number: int
    timestamp: float | None


class FramesResponse(CamelModel):
    frames: list[FrameInfo]


class ErrorDetail(CamelModel):
    code: str
    message: str


class ErrorResponse(CamelModel):
    error: ErrorDetail
