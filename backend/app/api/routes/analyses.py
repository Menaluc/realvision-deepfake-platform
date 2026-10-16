from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile

from app.api.dependencies import get_cache, get_predictor, get_settings
from app.api.schemas import AnalysisResponse, Probabilities
from app.config import Settings
from app.ml.predictor import Predictor
from app.services.analysis import analyze_upload
from app.storage.analysis_cache import AnalysisCache

router = APIRouter()


# A plain def: preprocessing and inference block, so FastAPI runs this in
# its thread pool instead of on the event loop
@router.post("/api/analyses", status_code=201, response_model=AnalysisResponse)
def create_analysis(
    video: UploadFile,
    predictor: Annotated[Predictor, Depends(get_predictor)],
    settings: Annotated[Settings, Depends(get_settings)],
    cache: Annotated[AnalysisCache, Depends(get_cache)],
):
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
