"""Checks that an upload is a video the pipeline can read."""

# torch must be loaded before decord: on Windows, importing torch after
# decord fails with "DLL initialization routine failed" (WinError 1114)
import torch  # noqa: F401
from decord import DECORDError, VideoReader, cpu

from app.errors import UnreadableVideo, UnsupportedMediaType


def check_declared_type(content_type: str | None) -> None:
    # Ignores case and parameters such as "; codecs=..."
    media_type = (content_type or "").split(";")[0].strip().lower()

    if not media_type.startswith("video/"):
        raise UnsupportedMediaType()


def check_readable_video(path) -> None:
    """Opens the file the way preprocess_video does and checks it has frames."""
    try:
        frame_count = len(VideoReader(str(path), ctx=cpu(0)))
    except (DECORDError, RuntimeError) as error:
        # The decord message includes the server path, so it is not passed on
        raise UnreadableVideo() from error

    if frame_count == 0:
        raise UnreadableVideo()
