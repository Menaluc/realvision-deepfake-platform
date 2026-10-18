"""V2 must give the same predictions as V1 on the local sample videos.

The expected values were recorded from V1's own code by
scripts/record_baseline.py. The videos stay local (samples/ is gitignored),
so each case is skipped where its video or the checkpoint is missing.
"""

import hashlib
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app

BACKEND_DIR = Path(__file__).resolve().parents[2]
CHECKPOINT = BACKEND_DIR / "models" / "baseline_best.pt"
SAMPLES_DIR = BACKEND_DIR.parent / "samples"
BASELINE = json.loads(
    (BACKEND_DIR / "tests" / "fixtures" / "parity_baseline.json").read_text("utf-8")
)

# Same code, same versions, both on CPU: only the order of floating-point
# operations across threads may differ
TOLERANCE = 1e-5

pytestmark = pytest.mark.skipif(
    not CHECKPOINT.is_file(), reason=f"checkpoint not found at {CHECKPOINT}"
)


@pytest.fixture(scope="module")
def client():
    return TestClient(create_app(Settings(checkpoint_path=CHECKPOINT)))


@pytest.mark.parametrize(
    "expected", BASELINE["samples"], ids=[s["path"] for s in BASELINE["samples"]]
)
def test_v2_matches_v1(client, expected):
    path = SAMPLES_DIR / expected["path"]

    if not path.is_file():
        pytest.skip(f"sample video not found at {path}")

    content = path.read_bytes()
    # Same name but different content would make the comparison meaningless
    assert hashlib.sha256(content).hexdigest() == expected["sha256"], (
        f"{expected['path']} is not the video the baseline was recorded on"
    )

    # Through the whole API: upload, validation, preprocessing, prediction
    response = client.post(
        "/api/analyses", files={"video": (path.name, content, "video/mp4")}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["prediction"] == expected["label"]
    for label, probability in expected["probabilities"].items():
        assert body["probabilities"][label] == pytest.approx(probability, abs=TOLERANCE)
