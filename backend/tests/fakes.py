from app.ml.predictor import CLASS_INDEX, CLASSES, ModelInfo, Prediction


class FakePredictor:
    """Stands in for Predictor, so tests don't need the checkpoint."""

    def __init__(self, label="fake", confidence=0.9):
        self.label = label
        self.confidence = confidence
        # Every tensor passed to predict(), to check what the model would see
        self.received = []

    def predict(self, video_tensor) -> Prediction:
        self.received.append(video_tensor)
        other = "real" if self.label == "fake" else "fake"

        return Prediction(
            label=self.label,
            predicted_class=CLASS_INDEX[self.label],
            confidence=self.confidence,
            probabilities={self.label: self.confidence, other: 1 - self.confidence},
        )

    def info(self) -> ModelInfo:
        return ModelInfo(
            backbone="fake_backbone",
            sampled_frames=16,
            input_size=224,
            feature_size=1280,
            embedding_size=256,
            classes=CLASSES,
        )
