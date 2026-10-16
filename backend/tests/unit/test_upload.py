import io

import pytest

from app.errors import VideoTooLarge
from app.services.upload import (
    CHUNK_SIZE,
    CONTENT_LENGTH_MARGIN,
    check_content_length,
    saved_upload,
)

LIMIT = 1000


def temp_files(directory):
    return list(directory.iterdir())


# --- saved_upload ---


def test_copies_the_upload_unchanged(tmp_path):
    # More than one chunk, so the loop runs several times
    content = bytes(range(256)) * (CHUNK_SIZE // 256 + 10)

    with saved_upload(io.BytesIO(content), "clip.mp4", len(content), tmp_path) as path:
        assert path.read_bytes() == content


def test_accepts_exactly_the_limit(tmp_path):
    with saved_upload(io.BytesIO(b"x" * LIMIT), "clip.mp4", LIMIT, tmp_path) as path:
        assert path.stat().st_size == LIMIT


def test_rejects_one_byte_over_the_limit_and_cleans_up(tmp_path):
    source = io.BytesIO(b"x" * (LIMIT + 1))

    with (
        pytest.raises(VideoTooLarge),
        saved_upload(source, "clip.mp4", LIMIT, tmp_path),
    ):
        pytest.fail("the block must not run")

    assert temp_files(tmp_path) == []


def test_deletes_the_file_after_the_block(tmp_path):
    with saved_upload(io.BytesIO(b"data"), "clip.mp4", LIMIT, tmp_path) as path:
        assert path.is_file()

    assert not path.exists()


def test_deletes_the_file_when_the_block_raises(tmp_path):
    with (
        pytest.raises(RuntimeError),
        saved_upload(io.BytesIO(b"data"), "clip.mp4", LIMIT, tmp_path) as path,
    ):
        raise RuntimeError("processing failed")

    assert not path.exists()
    assert temp_files(tmp_path) == []


@pytest.mark.parametrize(
    ("filename", "suffix"),
    [
        ("clip.mov", ".mov"),
        ("clip.MP4", ".MP4"),
        ("no-extension", ".mp4"),
        (None, ".mp4"),
        ("clip.mp4/../../evil", ".mp4"),
        ("clip.mp4 ; rm -rf", ".mp4"),
        ("clip.waytoolongext", ".mp4"),
    ],
)
def test_keeps_only_a_safe_suffix(tmp_path, filename, suffix):
    with saved_upload(io.BytesIO(b"data"), filename, LIMIT, tmp_path) as path:
        assert path.suffix == suffix
        # The client's name never becomes part of the path
        assert path.parent == tmp_path


# --- check_content_length ---


@pytest.mark.parametrize("header", [None, "", "abc", "-5", str(LIMIT)])
def test_content_length_precheck_lets_these_through(header):
    check_content_length(header, LIMIT)


def test_content_length_allows_the_multipart_margin():
    check_content_length(str(LIMIT + CONTENT_LENGTH_MARGIN), LIMIT)


def test_content_length_rejects_a_body_clearly_over_the_limit():
    with pytest.raises(VideoTooLarge):
        check_content_length(str(LIMIT + CONTENT_LENGTH_MARGIN + 1), LIMIT)
