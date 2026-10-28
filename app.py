"""Compatibility ASGI entry point: uvicorn app:app.

Canonical application: student_performance.api:app.
"""

from student_performance.api import app

__all__ = ["app"]
