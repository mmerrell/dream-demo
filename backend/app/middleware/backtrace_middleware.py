# backend/app/middleware/backtrace_middleware.py
import os
import logging
import traceback
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from typing import Optional

logger = logging.getLogger(__name__)


class BacktraceMiddleware:
    def __init__(self, app):
        self.app = app
        self.backtrace_enabled = os.getenv("BACKTRACE_ENABLED", "false").lower() == "true"
        self.backtrace_token = os.getenv("BACKTRACE_TOKEN")

    async def __call__(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            await self.handle_exception(exc, request)
            # Return error response
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error", "error_id": self.get_error_id(exc)}
            )

    async def handle_exception(self, exc: Exception, request: Request):
        error_data = {
            "error": str(exc),
            "type": type(exc).__name__,
            "traceback": traceback.format_exc(),
            "request_path": str(request.url.path),
            "method": request.method,
            "user_agent": request.headers.get("user-agent"),
            "sprint_version": os.getenv("SPRINT_VERSION", "unknown")
        }

        if self.backtrace_enabled and self.backtrace_token:
            await self.send_to_backtrace(error_data)
        else:
            # Log locally if Backtrace not configured
            logger.error(f"Error occurred: {error_data}")

    def get_error_id(self, exc: Exception) -> str:
        return f"err_{abs(hash(str(exc)))}"

    async def send_to_backtrace(self, error_data: dict):
        # TODO: Implement actual Backtrace API call
        logger.info(f"Would send to Backtrace: {error_data}")