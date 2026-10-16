"""Records V1's predictions on the local sample videos, for the parity test.

Run once, from backend/:  uv run python scripts/record_baseline.py

The predictions come from V1's own inference code (v1_reference/inference.py),
not from the new Predictor, so the parity test compares V2 against V1 rather
than against itself. Needs the local-only v1_reference/ folder, the real
checkpoint, and samples/{real,fake}/*.mp4 at the repository root.

Writes tests/fixtures/parity_baseline.json. The videos are never committed;
the JSON holds only their names, hashes and the recorded probabilities.
"""

import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

# V1 picks CUDA automatically; hide any GPU so V1 runs on the CPU like V2
os.environ["CUDA_VISIBLE_DEVICES"] = ""

BACKEND_DIR = Path(__file__).resolve().parents[1]
SAMPLES_DIR = BACKEND_DIR.parent / "samples"
V1_INFERENCE = BACKEND_DIR / "v1_reference" / "inference.py"
OUTPUT = BACKEND_DIR / "tests" / "fixtures" / "parity_baseline.json"

sys.path.insert(0, str(BACKEND_DIR))

# torch must be loaded before decord on Windows (see app/services/validation.py)
import torch

import app.ml.model_arch
from app.ml.preprocess import preprocess_video


def load_v1_inference():
    # V1 imports app.model_arch, which now lives at app.ml.model_arch. An
    # alias lets the V1 file run as it is, without editing it.
    sys.modules["app.model_arch"] = app.ml.model_arch

    spec = importlib.util.spec_from_file_location("v1_inference", V1_INFERENCE)
    module = importlib.util.module_from_spec(spec)
    # Loads the checkpoint, as V1 did at import time
    spec.loader.exec_module(module)
    return module


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    v1 = load_v1_inference()
    samples = []

    for path in sorted(SAMPLES_DIR.glob("*/*")):
        # V1's pipeline: the same preprocessing, then V1's predict_tensor
        result = v1.predict_tensor(preprocess_video(str(path)).tensor)

        samples.append(
            {
                "path": path.relative_to(SAMPLES_DIR).as_posix(),
                "sha256": sha256(path),
                # From the folder name; for information only, not asserted
                "true_label": path.parent.name,
                "label": result["prediction"],
                "probabilities": result["probabilities"],
            }
        )
        print(
            f"{samples[-1]['path']:20} {result['prediction']:5} {result['probabilities']}"
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(
            {
                "recorded_with": {
                    "code": "v1_reference/inference.py",
                    "torch": torch.__version__,
                    "device": str(v1.DEVICE),
                },
                "samples": samples,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(samples)} samples to {OUTPUT.relative_to(BACKEND_DIR)}")


if __name__ == "__main__":
    main()
