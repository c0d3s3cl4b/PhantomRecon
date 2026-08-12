"""Provider registry for pluggable PhantomRecon data sources."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

ProviderCallable = Callable[..., object]


@dataclass(frozen=True, slots=True)
class Provider:
    name: str
    capability: str
    handler: ProviderCallable
    homepage: str = ""
    description: str = ""

    @property
    def ready(self) -> bool:
        return callable(self.handler)

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "capability": self.capability,
            "homepage": self.homepage,
            "description": self.description,
            "status": "ready" if self.ready else "unavailable",
        }


class ProviderRegistry:
    """Small explicit registry for discoverable provider implementations."""

    def __init__(self) -> None:
        self._providers: dict[str, Provider] = {}

    def register(self, provider: Provider) -> None:
        if provider.name in self._providers:
            raise ValueError(f"Provider already registered: {provider.name}")
        self._providers[provider.name] = provider

    def get(self, name: str) -> Provider:
        try:
            return self._providers[name]
        except KeyError as exc:
            raise KeyError(f"Unknown provider: {name}") from exc

    def list(self, capability: str | None = None) -> list[Provider]:
        providers = self._providers.values()
        if capability is not None:
            providers = (p for p in providers if p.capability == capability)
        return sorted(providers, key=lambda provider: provider.name)


registry = ProviderRegistry()
