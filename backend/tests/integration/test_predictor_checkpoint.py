from pathlib import Path

import pytest
import torch

from app.ml.predictor import CLASS_INDEX, ModelInfo, Predictor
from app.ml.preprocess import IMG_SIZE, K_FRAMES

# The real checkpoint is copied in by hand and never committed
CHECKPOINT = Path(__file__).resolve().parents[2] / "models" / "baseline_best.pt"

pytestmark = pytest.mark.skipif(
    not CHECKPOINT.is_file(), reason=f"checkpoint not found at {CHECKPOINT}"
)


@pytest.fixture(scope="module")
def predictor():
    return Predictor.load(CHECKPOINT)


@pytest.fixture(scope="module")
def video_tensor():
    torch.manual_seed(0)
    return torch.randn(K_FRAMES, 3, IMG_SIZE, IMG_SIZE)


def test_loads_the_real_checkpoint(predictor):
    assert predictor.info() == ModelInfo(
        backbone="tf_efficientnet_b0",
        sampled_frames=16,
        input_size=224,
        feature_size=1280,
        embedding_size=256,
        classes=("real", "fake"),
    )


def test_predicts_with_the_real_weights(predictor, video_tensor):
    result = predictor.predict(video_tensor)

    assert result.predicted_class == CLASS_INDEX[result.label]
    assert sum(result.probabilities.values()) == pytest.approx(1.0)


def test_explains_with_the_real_weights(predictor, video_tensor):
    heatmaps = predictor.explain(video_tensor, target_class=1)

    assert heatmaps.shape == (K_FRAMES, IMG_SIZE, IMG_SIZE)
    assert 0.0 <= heatmaps.min() and heatmaps.max() <= 1.0
