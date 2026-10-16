import cv2
import numpy as np
import pytest


def write_video(path, frame_count, size=(64, 48), fps=10):
    """Writes a tiny MPEG-4 video; frame_count=0 gives a file with no frames."""
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, size)

    for i in range(frame_count):
        writer.write(np.full((size[1], size[0], 3), i * 10 % 256, np.uint8))

    writer.release()
    return path


@pytest.fixture
def video_file(tmp_path):
    return write_video(tmp_path / "video.mp4", frame_count=5)


@pytest.fixture
def empty_video_file(tmp_path):
    return write_video(tmp_path / "empty.mp4", frame_count=0)


@pytest.fixture
def junk_file(tmp_path):
    path = tmp_path / "junk.mp4"
    path.write_bytes(b"not a video" * 10)
    return path


@pytest.fixture
def truncated_video_file(tmp_path, video_file):
    path = tmp_path / "truncated.mp4"
    path.write_bytes(video_file.read_bytes()[:300])
    return path
