import io
import subprocess
import sys
from pathlib import Path

import pytest

from app.errors import UnreadableVideo, UnsupportedMediaType
from app.services.upload import saved_upload
from app.services.validation import check_declared_type, check_readable_video

BACKEND_DIR = Path(__file__).resolve().parents[2]


# --- check_declared_type ---


@pytest.mark.parametrize(
    "content_type", ["video/mp4", "video/quicktime", "VIDEO/MP4; codecs=avc1"]
)
def test_accepts_any_video_type(content_type):
    check_declared_type(content_type)


@pytest.mark.parametrize(
    "content_type", ["image/png", "application/octet-stream", "", None]
)
def test_rejects_anything_that_is_not_declared_as_video(content_type):
    with pytest.raises(UnsupportedMediaType):
        check_declared_type(content_type)


# --- check_readable_video ---


def test_accepts_a_readable_video(video_file):
    check_readable_video(video_file)


@pytest.mark.parametrize(
    "fixture", ["empty_video_file", "junk_file", "truncated_video_file"]
)
def test_rejects_an_unreadable_video(request, fixture):
    path = request.getfixturevalue(fixture)

    with pytest.raises(UnreadableVideo) as error:
        check_readable_video(path)

    # The server path must not reach the client
    assert str(path) not in error.value.message
    assert path.name not in error.value.message


def test_validated_upload_can_still_be_deleted(tmp_path, video_file):
    # On Windows a file that decord still holds open can't be deleted
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()

    with saved_upload(
        io.BytesIO(video_file.read_bytes()), "video.mp4", 10**6, upload_dir
    ) as path:
        check_readable_video(path)

    assert list(upload_dir.iterdir()) == []


@pytest.mark.parametrize("module", ["app.services.validation", "app.ml.preprocess"])
def test_modules_using_decord_can_be_imported_before_torch(module):
    # Regression: decord loaded before torch breaks torch on Windows
    # (WinError 1114). A fresh process, so no earlier import hides it.
    result = subprocess.run(
        [sys.executable, "-c", f"import {module}; import torch"],
        cwd=BACKEND_DIR,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
