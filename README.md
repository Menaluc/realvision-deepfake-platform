# RealVision Deepfake Platform

Deepfake video detection: upload a short video and get a real/fake verdict, confidence, the sampled frames and Grad-CAM attention heatmaps.

A single FastAPI app serves the API and the React frontend. The detection model's behavior is fixed and protected by regression tests.

**Status:** in development. Run instructions will be added once the app is complete.

## Layout

- `frontend/`: React + TypeScript + Vite
- `backend/`: FastAPI on Python 3.11, managed with uv

The model weights (`backend/models/baseline_best.pt`) are not included in this repository.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [AIDD development guide](docs/AIDD_DEVELOPMENT_GUIDE.md)
- [AIDD workflow](docs/AIDD_WORKFLOW.md)
