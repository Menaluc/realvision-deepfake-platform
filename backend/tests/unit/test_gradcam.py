import cv2
import numpy as np
import pytest
import torch

from app.ml.gradcam import compute_gradcam, heatmap_to_png
from app.ml.model_arch import VideoOnlyBaseline


@pytest.fixture(scope="module")
def model():
    # Random weights are enough to check shapes and normalization
    torch.manual_seed(0)
    return VideoOnlyBaseline().eval()


@pytest.fixture(scope="module")
def heatmaps(model):
    torch.manual_seed(1)
    video_tensor = torch.randn(4, 3, 224, 224)
    return compute_gradcam(model, video_tensor, target_class=1)


def test_returns_one_map_per_frame_at_frame_size(heatmaps):
    assert heatmaps.shape == (4, 224, 224)
    assert heatmaps.dtype == np.float32


def test_normalizes_jointly_across_frames(heatmaps):
    assert heatmaps.min() >= 0
    assert heatmaps.max() == pytest.approx(1.0)

    # Only the strongest frame reaches 1; the others keep their relative strength
    per_frame_max = heatmaps.reshape(4, -1).max(axis=1)
    assert np.sum(np.isclose(per_frame_max, 1.0)) == 1


def test_leaves_the_model_unchanged(model, heatmaps):
    assert len(model.cnn._forward_hooks) == 0
    assert all(param.grad is None for param in model.parameters())


def test_heatmap_png_is_transparent_where_there_is_no_heat():
    heatmap = np.zeros((224, 224), dtype=np.float32)
    heatmap[100:120, 100:120] = 1.0

    png = heatmap_to_png(heatmap)
    image = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_UNCHANGED)

    assert image.shape == (224, 224, 4)
    assert image[0, 0, 3] == 0
    assert image[110, 110, 3] == 255
