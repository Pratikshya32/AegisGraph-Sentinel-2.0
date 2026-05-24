"""Shared background task loops."""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Optional

from ..observability import get_logger


async def honeypot_auto_release_loop(
    get_honeypot_manager: Callable[[], Optional[Any]],
    *,
    interval_seconds: int = 60,
    logger: Any = None,
) -> None:
    """Periodically check honeypot auto-release state until cancelled."""
    task_logger = logger or get_logger("runtime.background_tasks")
    try:
        while True:
            await asyncio.sleep(interval_seconds)
            manager = get_honeypot_manager()
            if manager is None:
                continue
            try:
                manager.check_auto_release()
            except Exception as exc:
                task_logger.warning(
                    f"Honeypot auto-release check failed: {exc}",
                    event_type="honeypot_auto_release_error",
                )
    except asyncio.CancelledError:
        task_logger.info(
            "Honeypot auto-release loop stopped",
            event_type="honeypot_auto_release_stopped",
        )
        raise
