from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.api.schemas import HealthResponse

router = APIRouter()


@router.get("/api/health", response_model=HealthResponse)
def health(request: Request):
    model_loaded = request.app.state.predictor is not None

    if model_loaded:
        return HealthResponse(status="ok", model_loaded=True)

    # A status endpoint: its 503 keeps the health body, not the error format
    body = HealthResponse(status="degraded", model_loaded=False)
    return JSONResponse(status_code=503, content=body.model_dump(by_alias=True))
