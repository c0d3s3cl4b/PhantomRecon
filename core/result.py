"""Structured result model used by PhantomRecon modules and CLI output."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class ScanResult:
    """Machine-readable result returned by a PhantomRecon operation."""

    module: str
    target: str
    data: dict[str, Any] = field(default_factory=dict)
    status: str = "success"
    errors: list[str] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @classmethod
    def failure(cls, module: str, target: str, message: str) -> ScanResult:
        return cls(module=module, target=target, status="error", errors=[message])

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
