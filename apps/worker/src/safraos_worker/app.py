"""Composition root do worker Celery (SPEC-001)."""

from __future__ import annotations

import os

from celery import Celery

broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6383/0")
result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6383/1")

celery_app = Celery(
    "safraos",
    broker=broker_url,
    backend=result_backend,
    include=["safraos_worker.tasks.smoke"],
)
