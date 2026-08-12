"""Built-in public data providers used by PhantomRecon engines."""

from __future__ import annotations

from core.http import get
from core.providers import Provider, registry


def ip_api_lookup(ip: str, *, fields: str, timeout: float | None = None) -> dict:
    response = get(
        f"http://ip-api.com/json/{ip}",
        params={"fields": fields},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def emailrep_lookup(email: str, *, timeout: float | None = None) -> dict | None:
    response = get(f"https://emailrep.io/{email}", timeout=timeout)
    if response.status_code != 200:
        return None
    return response.json()


def crtsh_lookup(domain: str, *, timeout: float | None = None) -> list[dict]:
    response = get(
        "https://crt.sh/",
        params={"q": f"%.{domain}", "output": "json"},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def register_builtin_providers() -> None:
    providers = (
        Provider(
            "ip-api",
            "ip_lookup",
            ip_api_lookup,
            homepage="https://ip-api.com/",
            description="Public IP geolocation and network metadata",
        ),
        Provider(
            "emailrep",
            "email_reputation",
            emailrep_lookup,
            homepage="https://emailrep.io/",
            description="Optional public email reputation data",
        ),
        Provider(
            "crt.sh",
            "subdomain_discovery",
            crtsh_lookup,
            homepage="https://crt.sh/",
            description="Certificate transparency based passive discovery",
        ),
    )
    existing = {provider.name for provider in registry.list()}
    for provider in providers:
        if provider.name not in existing:
            registry.register(provider)


register_builtin_providers()
