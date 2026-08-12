"""Shared HTTP client primitives for PhantomRecon providers."""

from __future__ import annotations

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from core.config import settings


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
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.headers.update({"User-Agent": settings.user_agent})
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


session = build_session()


def get(url: str, **kwargs) -> requests.Response:
    """Perform a GET request using shared defaults unless explicitly overridden."""
    kwargs.setdefault("timeout", settings.http_timeout)
    return session.get(url, **kwargs)
