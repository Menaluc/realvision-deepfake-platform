"""Owns the loaded model: loading, prediction, Grad-CAM and model facts.

The prediction maths is part of the behavioral baseline and must not change.
Around it:

- The checkpoint is loaded when load() is called, not when the module is
  imported, and a failure raises ModelLoadError instead of crashing.
- The device is a parameter. The default is "cpu"; CUDA is used only when it
  is configured explicitly.
- One lock serializes every use of the shared model, so a prediction can't
  run while Grad-CAM has its forward hook on model.cnn.
"""

import threading
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

from app.ml.gradcam import compute_gradcam
from app.ml.model_arch import VideoOnlyBaseline
from app.ml.preprocess import IMG_SIZE, K_FRAMES

# Output order of the classifier
CLASS_INDEX = {"real": 0, "fake": 1}
CLASSES = tuple(CLASS_INDEX)


class ModelLoadError(Exception):
    """The checkpoint could not be turned into a ready model."""


@dataclass(frozen=True)
class Prediction:
    label: str
    # Index of the label in the classifier output; Grad-CAM explains this class
    predicted_class: int
    confidence: float
    probabilities: dict[str, float]


@dataclass(frozen=True)
class ModelInfo:
    backbone: str
    sampled_frames: int
    input_size: int
    feature_size: int
    embedding_size: int
    classes: tuple[str, ...]


class Predictor:
    def __init__(self, model: VideoOnlyBaseline, device="cpu"):
        self._device = torch.device(device)
        self._model = model.to(self._device).eval()
        self._lock = threading.Lock()

    @classmethod
    def load(cls, checkpoint_path, device="cpu") -> "Predictor":
        path = Path(checkpoint_path)

        if not path.is_file():
            raise ModelLoadError(f"Checkpoint not found: {path}")

        try:
            checkpoint = torch.load(path, map_location=device, weights_only=True)
            if not isinstance(checkpoint, dict) or "model" not in checkpoint:
                raise ValueError("expected a dict with a 'model' state dict")

            model = VideoOnlyBaseline()
            model.load_state_dict(checkpoint["model"], strict=True)

            return cls(model, device)

        except Exception as error:
            raise ModelLoadError(
                f"Failed to load checkpoint {path}: {error}"
            ) from error

    def predict(self, video_tensor: torch.Tensor) -> Prediction:
        # Add batch dimension: (T, 3, H, W) → (1, T, 3, H, W)
        batch = video_tensor.unsqueeze(0).to(self._device)

        with self._lock, torch.no_grad():
            logits = self._model(batch)
            probabilities = torch.softmax(logits, dim=1)

        real_probability = probabilities[0][CLASS_INDEX["real"]].item()
        fake_probability = probabilities[0][CLASS_INDEX["fake"]].item()

        # Baseline decision rule: a tie counts as real
        if fake_probability > real_probability:
            label, confidence = "fake", fake_probability
        else:
            label, confidence = "real", real_probability

        return Prediction(
            label=label,
            predicted_class=CLASS_INDEX[label],
            confidence=confidence,
            probabilities={"real": real_probability, "fake": fake_probability},
        )

    def explain(self, video_tensor: torch.Tensor, target_class: int) -> np.ndarray:
        # compute_gradcam turns gradients on itself, so this must not be
        # wrapped in no_grad() or inference_mode()
        with self._lock:
            return compute_gradcam(self._model, video_tensor, target_class)

    def info(self) -> ModelInfo:
        # Read from the loaded model, so it can't drift from the checkpoint
        return ModelInfo(
            backbone=self._model.cnn.pretrained_cfg["architecture"],
            sampled_frames=K_FRAMES,
            input_size=IMG_SIZE,
            feature_size=self._model.cnn.num_features,
            embedding_size=self._model.proj.out_features,
            classes=CLASSES,
        )
