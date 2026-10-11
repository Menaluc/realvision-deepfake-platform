# RealVision Deepfake Platform

Deepfake video detection: upload a short video and get a real/fake verdict, confidence, the sampled frames and Grad-CAM attention heatmaps.

EfficientNet-B0 processes 16 sampled frames, the frame representations are averaged, and the resulting video representation is classified as real or fake.

The target architecture is a single FastAPI app that serves both the API and the React frontend. The detection model's behavior is kept fixed: its core modules have unit tests, and regression/parity validation against a recorded baseline is planned.

**Status:** in development. Run instructions will be added once the app is complete.

## Tech stack

- **Frontend:** React 19, TypeScript, Vite, Vitest
- **Backend:** Python 3.11, FastAPI, uv, pytest, ruff
- **ML:** PyTorch, timm (EfficientNet-B0), decord, OpenCV

## Layout

- `frontend/`: React + TypeScript + Vite
- `backend/`: FastAPI on Python 3.11, managed with uv

The model weights (`backend/models/baseline_best.pt`) are not included in this repository.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [AIDD development guide](docs/AIDD_DEVELOPMENT_GUIDE.md)
- [AIDD workflow](docs/AIDD_WORKFLOW.md)
