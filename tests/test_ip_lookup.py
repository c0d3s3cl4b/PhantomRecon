from unittest.mock import patch

from core.providers import registry
from modules.ip_lookup import lookup_ip


def test_lookup_ip_rejects_invalid_target():
    result = lookup_ip("not a valid target")
    assert result.status == "error"
    assert result.module == "ip_lookup"


@patch("modules.ip_lookup.socket.gethostbyaddr", side_effect=OSError)
def test_lookup_ip_returns_machine_readable_data(_mock_reverse):
    provider = registry.get("ip-api")
    original = provider.handler
    object.__setattr__(
        provider,
        "handler",
        lambda *_args, **_kwargs: {
            "status": "success",
            "query": "8.8.8.8",
            "country": "United States",
            "countryCode": "US",
            "lat": 37.751,
            "lon": -97.822,
            "proxy": False,
            "hosting": True,
            "mobile": False,
        },
    )
    try:
        result = lookup_ip("8.8.8.8")
    finally:
        object.__setattr__(provider, "handler", original)

    assert result.status == "success"
    assert result.data["ip"] == "8.8.8.8"
    assert result.data["provider"] == "ip-api"
    assert result.data["proxy"] is False
    assert result.data["hosting"] is True
