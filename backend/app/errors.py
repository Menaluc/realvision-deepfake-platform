"""Domain errors with the code and message the API returns.

Plain Python, so services can raise them without importing FastAPI. The
error handlers in app.api turn them into the error format.
"""


class AppError(Exception):
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
