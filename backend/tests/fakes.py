import time

import numpy as np

from app.ml.predictor import CLASS_INDEX, CLASSES, ModelInfo, Prediction


class FakePredictor:
    """Stands in for Predictor, so tests don't need the checkpoint."""

    def __init__(self, label="fake", confidence=0.9, explain_seconds=0.0):
        self.label = label
        self.confidence = confidence
        # Every tensor passed to predict(), to check what the model would see
        self.received = []
        # Every (tensor, target_class) passed to explain()
        self.explained = []
        # Makes explain() slow, so concurrent requests overlap
        self.explain_seconds = explain_seconds

    def predict(self, video_tensor) -> Prediction:
        self.received.append(video_tensor)
        other = "real" if self.label == "fake" else "fake"

        return Prediction(
            label=self.label,
            predicted_class=CLASS_INDEX[self.label],
            confidence=self.confidence,
            probabilities={self.label: self.confidence, other: 1 - self.confidence},
        )

    def explain(self, video_tensor, target_class) -> np.ndarray:
        self.explained.append((video_tensor, target_class))
        time.sleep(self.explain_seconds)

        # A horizontal ramp per frame, in [0, 1] like real Grad-CAM maps
        frames, _, height, width = video_tensor.shape
        ramp = np.linspace(0, 1, width, dtype=np.float32)
        return np.broadcast_to(ramp, (frames, height, width)).copy()

    def info(self) -> ModelInfo:
        return ModelInfo(
            backbone="fake_backbone",
            sampled_frames=16,
            input_size=224,
            feature_size=1280,
            embedding_size=256,
            classes=CLASSES,
        )
