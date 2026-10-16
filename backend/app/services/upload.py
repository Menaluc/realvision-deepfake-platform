"""Writes an upload to one temp file, enforcing the size limit.

The size is checked twice: from the Content-Length header before anything
is read, and again while copying, in case the header is missing or wrong.
"""

import os
import re
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import BinaryIO

from app.errors import VideoTooLarge

CHUNK_SIZE = 1024 * 1024

# Content-Length covers the whole multipart body, not just the file, so the
# precheck leaves room for the form overhead. The copy enforces the exact limit.
CONTENT_LENGTH_MARGIN = 1024 * 1024

DEFAULT_SUFFIX = ".mp4"
SAFE_SUFFIX = re.compile(r"^\.[A-Za-z0-9]{1,8}$")


def check_content_length(header: str | None, max_bytes: int) -> None:
    """Rejects a request that declares a body clearly over the limit."""
    try:
        declared = int(header)
    except (TypeError, ValueError):
        # Missing or malformed: the copy still enforces the limit
        return

    if declared > max_bytes + CONTENT_LENGTH_MARGIN:
        raise VideoTooLarge()


def safe_suffix(filename: str | None) -> str:
    # Only the extension is kept from the client's name; the file name is random
    suffix = Path(filename or "").suffix
    return suffix if SAFE_SUFFIX.match(suffix) else DEFAULT_SUFFIX


@contextmanager
def saved_upload(
    source: BinaryIO,
    filename: str | None,
    max_bytes: int,
    temp_dir: Path | None = None,
) -> Iterator[Path]:
    """Copies source to a temp file and yields its path.

    The file is closed before it is yielded, because on Windows it can't be
    opened again (by decord) while it is open for writing. It is deleted
    when the block exits, whether it succeeds or raises.
    """
    handle, name = tempfile.mkstemp(suffix=safe_suffix(filename), dir=temp_dir)
    path = Path(name)

    try:
        with os.fdopen(handle, "wb") as target:
            copy_with_limit(source, target, max_bytes)

        yield path

    finally:
        path.unlink(missing_ok=True)


def copy_with_limit(source: BinaryIO, target: BinaryIO, max_bytes: int) -> None:
    written = 0

    while chunk := source.read(CHUNK_SIZE):
        written += len(chunk)

        if written > max_bytes:
            raise VideoTooLarge()

        target.write(chunk)
