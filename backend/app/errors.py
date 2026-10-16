"""Domain errors with the code and message the API returns.

Plain Python, so services can raise them without importing FastAPI. The
error handlers in app.api turn them into the error format.
"""


class AppError(Exception):
    # Each subclass sets these three. Keeping the HTTP status here puts every
    # error's code, status and message in one place, at the cost of the
    # domain layer knowing about HTTP status numbers.
    status_code = 500
    code = "INTERNAL_ERROR"
    message = "An unexpected error occurred."

    def __init__(self, message: str | None = None):
        if message is not None:
            self.message = message
        super().__init__(self.message)


class ModelUnavailable(AppError):
    status_code = 503
    code = "MODEL_UNAVAILABLE"
    message = "The detection model is not loaded. Try again later."


class VideoTooLarge(AppError):
    status_code = 413
    code = "VIDEO_TOO_LARGE"
    # Matches the default Settings.max_upload_bytes
    message = "The video is larger than the 20 MB limit."


class UnsupportedMediaType(AppError):
    status_code = 415
    code = "UNSUPPORTED_MEDIA_TYPE"
    message = "The file is not a video."


class AnalysisNotFound(AppError):
    status_code = 404
    code = "ANALYSIS_NOT_FOUND"
    message = "The analysis does not exist or has expired."


class FrameNotFound(AppError):
    status_code = 404
    code = "FRAME_NOT_FOUND"
    message = "The analysis has no frame with this index."


class UnreadableVideo(AppError):
    status_code = 422
    code = "UNREADABLE_VIDEO"
    message = "The video could not be read, or it has no frames."
