from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_predictor
from app.api.schemas import ModelResponse
from app.ml.predictor import Predictor

router = APIRouter()


@router.get("/api/model", response_model=ModelResponse)
def model_info(predictor: Annotated[Predictor, Depends(get_predictor)]):
    # Read from the loaded model, not a hand-written copy
    info = predictor.info()

    return ModelResponse(
        backbone=info.backbone,
        sampled_frames=info.sampled_frames,
        input_size=info.input_size,
        feature_size=info.feature_size,
        embedding_size=info.embedding_size,
        classes=list(info.classes),
    )
