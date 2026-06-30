"""Application exception hierarchy and FastAPI handlers.

All domain errors derive from ``AppException`` and serialize to a consistent
``{"error": {"code": ..., "message": ...}}`` envelope.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("app.error")


class AppException(Exception):
    status_code: int = 400
    code: str = "bad_request"

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        status_code: int | None = None,
    ) -> None:
        self.message = message
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    status_code = 404
    code = "not_found"


class ValidationError(AppException):
    status_code = 422
    code = "validation_error"


class AuthError(AppException):
    status_code = 401
    code = "auth_error"


class RuleBlockError(AppException):
    status_code = 409
    code = "rule_block"


def _error_body(code: str, message: str) -> dict[str, dict[str, str]]:
    return {"error": {"code": code, "message": message}}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def _handle_app_exception(_: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.code, exc.message),
        )

    @app.exception_handler(RequestValidationError)
    async def _handle_validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=_error_body("validation_error", "Request validation failed")
            | {"detail": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def _handle_unexpected(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content=_error_body("internal_error", "An unexpected error occurred"),
        )
