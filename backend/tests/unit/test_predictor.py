import threading
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pytest
import torch
from torch import nn

from app.ml import predictor as predictor_module
from app.ml.gradcam import compute_gradcam
from app.ml.model_arch import VideoOnlyBaseline
from app.ml.predictor import CLASS_INDEX, ModelInfo, ModelLoadError, Predictor

# Fewer frames than the real 16 keep the tests fast; the model accepts any count
FRAMES = 4


@pytest.fixture(scope="module")
def model():
    # Random weights are enough to check the maths and the wiring
    torch.manual_seed(0)
    return VideoOnlyBaseline().eval()


@pytest.fixture(scope="module")
def predictor(model):
    return Predictor(model)


@pytest.fixture(scope="module")
def video_tensor():
    torch.manual_seed(1)
    return torch.randn(FRAMES, 3, 224, 224)


def model_with_fixed_logits(real_logit, fake_logit):
    # Zero weights make the logits equal to the classifier bias
    model = VideoOnlyBaseline()
    nn.init.zeros_(model.classifier.weight)

    with torch.no_grad():
        model.classifier.bias.copy_(torch.tensor([real_logit, fake_logit]))

    return model


# --- predict ---


def test_predict_returns_a_consistent_result(predictor, video_tensor):
    result = predictor.predict(video_tensor)

    assert result.label in ("real", "fake")
    assert result.predicted_class == CLASS_INDEX[result.label]
    assert result.confidence == result.probabilities[result.label]
    assert sum(result.probabilities.values()) == pytest.approx(1.0)


def test_predict_matches_the_reference_maths(model, predictor, video_tensor):
    # Reference maths: no_grad forward on a batch of one, then softmax
    with torch.no_grad():
        expected = torch.softmax(model(video_tensor.unsqueeze(0)), dim=1)

    result = predictor.predict(video_tensor)

    assert result.probabilities["real"] == expected[0][0].item()
    assert result.probabilities["fake"] == expected[0][1].item()


def test_predict_is_deterministic(predictor, video_tensor):
    assert predictor.predict(video_tensor) == predictor.predict(video_tensor)


def test_predicts_fake_when_fake_is_more_likely(video_tensor):
    result = Predictor(model_with_fixed_logits(0.0, 1.0)).predict(video_tensor)

    assert result.label == "fake"
    assert result.predicted_class == 1
    assert result.confidence == result.probabilities["fake"]


def test_a_tie_counts_as_real(video_tensor):
    result = Predictor(model_with_fixed_logits(0.0, 0.0)).predict(video_tensor)

    assert result.probabilities == {"real": 0.5, "fake": 0.5}
    assert result.label == "real"
    assert result.predicted_class == 0
    assert result.confidence == 0.5


def test_predict_leaves_no_gradients_and_keeps_eval_mode(
    model, predictor, video_tensor
):
    predictor.predict(video_tensor)

    assert not model.training
    assert all(param.grad is None for param in model.parameters())


def test_puts_the_model_in_eval_mode():
    model = VideoOnlyBaseline().train()

    Predictor(model)

    assert not model.training


# --- explain ---


def test_explain_returns_one_heatmap_per_frame(model, predictor, video_tensor):
    heatmaps = predictor.explain(video_tensor, target_class=1)

    assert heatmaps.shape == (FRAMES, 224, 224)
    assert heatmaps.dtype == np.float32
    assert len(model.cnn._forward_hooks) == 0
    assert all(param.grad is None for param in model.parameters())


def test_explain_is_the_reference_gradcam(model, predictor, video_tensor):
    expected = compute_gradcam(model, video_tensor, 1)

    assert np.array_equal(predictor.explain(video_tensor, 1), expected)


def test_explain_still_gets_gradients_inside_no_grad(predictor, video_tensor):
    # A caller's no_grad() must not break Grad-CAM, which needs gradients
    with torch.no_grad():
        heatmaps = predictor.explain(video_tensor, target_class=1)

    assert heatmaps.max() == pytest.approx(1.0)


# --- info ---


def test_info_is_read_from_the_model(predictor):
    assert predictor.info() == ModelInfo(
        backbone="tf_efficientnet_b0",
        sampled_frames=16,
        input_size=224,
        feature_size=1280,
        embedding_size=256,
        classes=("real", "fake"),
    )


# --- load ---


def test_load_restores_a_saved_checkpoint(model, predictor, video_tensor, tmp_path):
    path = tmp_path / "checkpoint.pt"
    torch.save({"model": model.state_dict()}, path)

    loaded = Predictor.load(path)

    assert loaded.predict(video_tensor) == predictor.predict(video_tensor)


def test_load_fails_clearly_when_the_file_is_missing(tmp_path):
    with pytest.raises(ModelLoadError, match="Checkpoint not found"):
        Predictor.load(tmp_path / "missing.pt")


@pytest.mark.parametrize(
    "write",
    [
        lambda path: path.write_bytes(b"not a checkpoint"),
        lambda path: torch.save(torch.zeros(1), path),
        lambda path: torch.save({}, path),
        lambda path: torch.save({"model": {}}, path),
        lambda path: torch.save({"model": nn.Linear(2, 2).state_dict()}, path),
    ],
    ids=["garbage", "not-a-dict", "no-model-key", "empty-state", "wrong-model"],
)
def test_load_fails_clearly_on_a_bad_checkpoint(write, tmp_path):
    path = tmp_path / "checkpoint.pt"
    write(path)

    with pytest.raises(ModelLoadError, match="Failed to load checkpoint") as error:
        Predictor.load(path)

    # The original reason is kept for the server log
    assert error.value.__cause__ is not None


def test_load_fails_clearly_on_an_unknown_device(model, tmp_path):
    path = tmp_path / "checkpoint.pt"
    torch.save({"model": model.state_dict()}, path)

    with pytest.raises(ModelLoadError):
        Predictor.load(path, device="not-a-device")


@pytest.mark.skipif(torch.cuda.is_available(), reason="needs a machine without CUDA")
def test_load_fails_clearly_when_cuda_is_unavailable(model, tmp_path):
    path = tmp_path / "checkpoint.pt"
    torch.save({"model": model.state_dict()}, path)

    with pytest.raises(ModelLoadError):
        Predictor.load(path, device="cuda")


# --- lock ---


class ConcurrencyTracker:
    def __init__(self):
        self._lock = threading.Lock()
        self.active = 0
        self.max_active = 0

    def run(self):
        with self._lock:
            self.active += 1
            self.max_active = max(self.max_active, self.active)

        # Long enough for an unlocked caller to overlap
        time.sleep(0.02)

        with self._lock:
            self.active -= 1


class TrackedModel(nn.Module):
    def __init__(self, tracker):
        super().__init__()
        self.tracker = tracker

    def forward(self, batch):
        self.tracker.run()
        return torch.zeros(1, 2)


def test_predict_and_explain_never_use_the_model_at_the_same_time(monkeypatch):
    tracker = ConcurrencyTracker()

    def fake_gradcam(model, video_tensor, target_class):
        tracker.run()
        return np.zeros((FRAMES, 224, 224), dtype=np.float32)

    monkeypatch.setattr(predictor_module, "compute_gradcam", fake_gradcam)

    predictor = Predictor(TrackedModel(tracker))
    video_tensor = torch.zeros(FRAMES, 3, 224, 224)

    def call(i):
        if i % 2:
            predictor.predict(video_tensor)
        else:
            predictor.explain(video_tensor, 1)

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(call, range(16)))

    assert tracker.max_active == 1
