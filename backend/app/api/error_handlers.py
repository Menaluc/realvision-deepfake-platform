"""Turns every error into the one error format: { error: { code, message } }."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.api.schemas import ErrorDetail, ErrorResponse
from app.errors import AppError

logger = logging.getLogger(__name__)

# HTTP errors raised by FastAPI/Starlette themselves, not by our code
HTTP_ERROR_CODES = {
    400: ("INVALID_REQUEST", "The request is malformed."),
    404: ("NOT_FOUND", "The requested resource does not exist."),
    405: ("METHOD_NOT_ALLOWED", "This method is not allowed on this path."),
}


def error_response(status_code, code, message, headers=None) -> JSONResponse:
    body = ErrorResponse(error=ErrorDetail(code=code, message=message))
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(by_alias=True),
        headers=headers,
    )


async def handle_app_error(request: Request, error: AppError) -> JSONResponse:
    return error_response(error.status_code, error.code, error.message)


async def handle_validation_error(
    request: Request, error: RequestValidationError
) -> JSONResponse:
    # 400 instead of FastAPI's default 422, which is kept for UNREADABLE_VIDEO.
    # Only the first problem is reported, so the message stays one sentence.
    first = error.errors()[0]
    location = ".".join(str(part) for part in first["loc"])
    return error_response(400, "INVALID_REQUEST", f"{location}: {first['msg']}")


async def handle_http_error(request: Request, error: HTTPException) -> JSONResponse:
    if error.status_code not in HTTP_ERROR_CODES:
        logger.error("Unmapped HTTP error %s: %s", error.status_code, error.detail)
        return error_response(500, "INTERNAL_ERROR", AppError.message)

    code, message = HTTP_ERROR_CODES[error.status_code]
    # Keeps headers such as Allow on a 405
    return error_response(error.status_code, code, message, error.headers)


async def handle_unexpected_error(request: Request, error: Exception) -> JSONResponse:
    # Details go to the server log only, never to the client
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return error_response(500, "INTERNAL_ERROR", AppError.message)


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, handle_app_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    # Starlette's HTTPException, not FastAPI's subclass: the router raises the
    # Starlette one for unknown paths (404) and wrong methods (405)
    app.add_exception_handler(HTTPException, handle_http_error)
    # Starlette runs this one outside the other middleware, as the last resort
    # for anything not caught above
    app.add_exception_handler(Exception, handle_unexpected_error)
