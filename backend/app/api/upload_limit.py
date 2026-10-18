"""Rejects an oversized upload from its Content-Length, before the body is read.

FastAPI parses the whole multipart form before any dependency or route
runs, so a check in the route would only happen after the file was already
spooled to disk. This runs first, as plain ASGI middleware.
"""

from starlette.types import ASGIApp, Receive, Scope, Send

from app.api.error_handlers import error_response
from app.errors import VideoTooLarge
from app.services.upload import check_content_length

# Must match the route in app/api/routes/analyses.py; the 413 API test fails
# if the two drift apart
UPLOAD_PATH = "/api/analyses"


class UploadLimitMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if self.should_reject(scope):
            # Answers without calling receive(), so the body is never read
            error = VideoTooLarge()
            response = error_response(error.status_code, error.code, error.message)
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)

    @staticmethod
    def should_reject(scope: Scope) -> bool:
        if scope["type"] != "http" or scope["method"] != "POST":
            return False

        if scope["path"] != UPLOAD_PATH:
            return False

        # Starlette puts the app in the scope before any middleware runs
        state = scope["app"].state

        # Degraded: let the route answer 503, which comes before 413
        if state.predictor is None:
            return False

        # ASGI headers are (name, value) byte pairs with lowercase names
        headers = dict(scope["headers"])
        content_length = headers.get(b"content-length")

        try:
            check_content_length(
                # HTTP header bytes are latin-1 by definition
                content_length.decode("latin-1") if content_length else None,
                state.settings.max_upload_bytes,
            )
        except VideoTooLarge:
            return True

        return False
