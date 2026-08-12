from core.config import Settings


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("PHANTOMRECON_HTTP_TIMEOUT", "3.5")
    monkeypatch.setenv("PHANTOMRECON_HTTP_RETRIES", "4")
    monkeypatch.setenv("PHANTOMRECON_HTTP_MIN_INTERVAL", "0.3")
    monkeypatch.setenv("PHANTOMRECON_MAX_WORKERS", "99")

    settings = Settings.from_env()

    assert settings.http_timeout == 3.5
    assert settings.http_retries == 4
    assert settings.http_min_interval == 0.3
    assert settings.max_workers == 64


def test_invalid_env_values_fall_back(monkeypatch):
    monkeypatch.setenv("PHANTOMRECON_HTTP_TIMEOUT", "invalid")
    monkeypatch.setenv("PHANTOMRECON_HTTP_RETRIES", "invalid")
    monkeypatch.setenv("PHANTOMRECON_HTTP_MIN_INTERVAL", "invalid")

    settings = Settings.from_env()

    assert settings.http_timeout == 10.0
    assert settings.http_retries == 2
    assert settings.http_min_interval == 0.15
