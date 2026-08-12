"""Central configuration for PhantomRecon V2.1."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime defaults shared by CLI modules and providers."""

    http_timeout: float = 10.0
    http_retries: int = 2
    http_backoff: float = 0.4
    user_agent: str = "PhantomRecon/2.1 (+authorized OSINT)"
    max_workers: int = 20

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            http_timeout=max(0.1, _env_float("PHANTOMRECON_HTTP_TIMEOUT", 10.0)),
            http_retries=max(0, min(_env_int("PHANTOMRECON_HTTP_RETRIES", 2), 5)),
            http_backoff=max(0.0, _env_float("PHANTOMRECON_HTTP_BACKOFF", 0.4)),
            user_agent=os.getenv(
                "PHANTOMRECON_USER_AGENT",
                "PhantomRecon/2.1 (+authorized OSINT)",
            ),
            max_workers=max(1, min(_env_int("PHANTOMRECON_MAX_WORKERS", 20), 64)),
        )


settings = Settings.from_env()
