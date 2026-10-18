from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Response, UploadFile

from app.api.dependencies import get_cache, get_predictor, get_settings
from app.api.schemas import AnalysisResponse, FrameInfo, FramesResponse, Probabilities
from app.config import Settings
from app.ml.predictor import Predictor
from app.services.analysis import (
    analyze_upload,
    attention_png,
    frame_jpeg,
    list_frames,
)
from app.storage.analysis_cache import AnalysisCache

router = APIRouter()

# Typed path parameters: a malformed id or a negative index is a 400.
# Routes pass str(id) to the services: UUID normalizes the text (lowercase),
# so it matches the keys the cache created with str(uuid4()).
AnalysisId = Annotated[UUID, Path()]
FrameIndex = Annotated[int, Path(ge=0)]
CacheDep = Annotated[AnalysisCache, Depends(get_cache)]
# Raises MODEL_UNAVAILABLE in degraded mode. Dependencies run before path
# parameters are validated, so that 503 comes before any 400 or 404.
PredictorDep = Annotated[Predictor, Depends(get_predictor)]


# Plain defs: preprocessing, inference and encoding block, so FastAPI runs
# these in its thread pool instead of on the event loop
@router.post("/api/analyses", status_code=201, response_model=AnalysisResponse)
def create_analysis(
    # Required multipart field; a missing one is a 400 INVALID_REQUEST
    video: UploadFile,
    predictor: PredictorDep,
    settings: Annotated[Settings, Depends(get_settings)],
    cache: CacheDep,
):
    # video.file is the spooled upload Starlette already wrote; the service
    # reads it like any binary file, without knowing about FastAPI
    analysis_id, prediction = analyze_upload(
        video.file,
        video.filename,
        video.content_type,
        settings,
        predictor,
        cache,
    )

    return AnalysisResponse(
        id=analysis_id,
        prediction=prediction.label,
        confidence=prediction.confidence,
        probabilities=Probabilities(**prediction.probabilities),
    )


@router.get("/api/analyses/{id}/frames", response_model=FramesResponse)
def get_frames(id: AnalysisId, cache: CacheDep):
    frames = list_frames(cache, str(id))

    return FramesResponse(
        frames=[
            FrameInfo(
                index=frame.index,
                frame_number=frame.frame_number,
                timestamp=frame.timestamp,
            )
            for frame in frames
        ]
    )


@router.get(
    "/api/analyses/{id}/frames/{index}",
    response_class=Response,
    responses={200: {"content": {"image/jpeg": {}}}},
)
def get_frame_image(id: AnalysisId, index: FrameIndex, cache: CacheDep):
    return Response(frame_jpeg(cache, str(id), index), media_type="image/jpeg")


@router.get(
    "/api/analyses/{id}/frames/{index}/attention",
    response_class=Response,
    responses={200: {"content": {"image/png": {}}}},
)
def get_frame_attention(
    id: AnalysisId, index: FrameIndex, predictor: PredictorDep, cache: CacheDep
):
    png = attention_png(cache, predictor, str(id), index)
    return Response(png, media_type="image/png")
