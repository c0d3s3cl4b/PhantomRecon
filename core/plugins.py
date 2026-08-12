"""Plugin discovery for PhantomRecon 2.2.

Third-party packages can register plugins through the
``phantomrecon.plugins`` Python entry-point group.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import metadata
from typing import Any

PLUGIN_GROUP = "phantomrecon.plugins"


@dataclass(frozen=True, slots=True)
class PluginInfo:
    name: str
    value: str
    distribution: str | None
    version: str | None
    loaded: bool = False
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "distribution": self.distribution,
            "version": self.version,
            "loaded": self.loaded,
            "error": self.error,
        }


def _entry_points() -> list[metadata.EntryPoint]:
    points = metadata.entry_points()
    if hasattr(points, "select"):
        return list(points.select(group=PLUGIN_GROUP))
    return list(points.get(PLUGIN_GROUP, []))  # type: ignore[attr-defined]


def discover_plugins(*, load: bool = False) -> list[PluginInfo]:
    """Discover installed PhantomRecon plugins without loading them by default."""
    plugins: list[PluginInfo] = []
    for point in sorted(_entry_points(), key=lambda item: item.name.lower()):
        distribution = getattr(point, "dist", None)
        dist_name = getattr(distribution, "name", None)
        dist_version = getattr(distribution, "version", None)
        loaded = False
        error = None
        if load:
            try:
                point.load()
                loaded = True
            except Exception as exc:  # plugin boundary: third-party code
                error = f"{type(exc).__name__}: {exc}"
        plugins.append(
            PluginInfo(
                name=point.name,
                value=point.value,
                distribution=dist_name,
                version=dist_version,
                loaded=loaded,
                error=error,
            )
        )
    return plugins
