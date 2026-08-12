from unittest.mock import patch

from modules.subdomain_finder import find_subdomains
from modules.username_search import search_username


def test_username_rejects_whitespace():
    result = search_username("bad user")
    assert result.status == "error"


@patch("modules.username_search.check_platform")
def test_username_returns_structured_profiles(check):
    check.side_effect = lambda platform, url, timeout: {
        "platform": platform,
        "url": url,
        "found": platform == "GitHub",
        "status_code": 200 if platform == "GitHub" else 404,
        "error": None,
    }
    result = search_username("tester", workers=2)
    assert result.status == "success"
    assert result.data["platforms_scanned"] > 20
    assert result.data["profiles_found"] == 1


@patch("modules.subdomain_finder.crt_sh_lookup")
def test_subdomain_passive_mode(crt):
    crt.return_value = {"www.example.com", "api.example.com"}
    result = find_subdomains("https://example.com/path")
    assert result.status == "success"
    assert result.data["mode"] == "passive"
    assert result.data["total"] == 2
