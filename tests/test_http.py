from core.http import build_session


def test_build_session_sets_user_agent_and_retry_adapters():
    session = build_session()

    assert session.headers["User-Agent"].startswith("PhantomRecon/")
    assert "http://" in session.adapters
    assert "https://" in session.adapters
    assert session.adapters["https://"].max_retries.total >= 0
