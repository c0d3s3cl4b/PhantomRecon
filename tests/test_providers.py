import pytest

from core.providers import Provider, ProviderRegistry


def _handler():
    return "ok"


def test_provider_registry_register_get_and_list():
    registry = ProviderRegistry()
    provider = Provider(
        name="demo",
        capability="ip",
        handler=_handler,
        homepage="https://example.com/",
        description="Demo provider",
    )

    registry.register(provider)

    assert registry.get("demo") is provider
    assert registry.list("ip") == [provider]
    assert registry.list("email") == []
    assert provider.ready is True
    assert provider.to_dict()["status"] == "ready"


def test_provider_registry_rejects_duplicates():
    registry = ProviderRegistry()
    provider = Provider(name="demo", capability="ip", handler=_handler)
    registry.register(provider)

    with pytest.raises(ValueError):
        registry.register(provider)
