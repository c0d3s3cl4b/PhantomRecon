"""Shared HTTP client primitives for PhantomRecon providers."""

from __future__ import annotations

import threading
import time
from urllib.parse import urlsplit

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from core.config import settings

_last_request_at: dict[str, float] = {}
_rate_limit_lock = threading.Lock()


def build_session() -> requests.Session:
    """Create a reusable HTTP session with bounded retries and backoff."""
    retry = Retry(
        total=settings.http_retries,
        connect=settings.http_retries,
        read=settings.http_retries,
        backoff_factor=settings.http_backoff,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "HEAD"}),
        raise_on_status=False,
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.headers.update({"User-Agent": settings.user_agent})
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def _throttle(url: str) -> None:
    """Apply a small per-host delay to reduce accidental request bursts."""
    interval = settings.http_min_interval
    if interval <= 0:
        return
    host = urlsplit(url).netloc.lower()
    if not host:
        return
    with _rate_limit_lock:
        now = time.monotonic()
        previous = _last_request_at.get(host)
        if previous is not None:
            delay = interval - (now - previous)
            if delay > 0:
                time.sleep(delay)
                now = time.monotonic()
        _last_request_at[host] = now


session = build_session()


def get(url: str, **kwargs) -> requests.Response:
    """Perform a rate-limited GET using shared defaults."""
    kwargs.setdefault("timeout", settings.http_timeout)
    _throttle(url)
    return session.get(url, **kwargs)
