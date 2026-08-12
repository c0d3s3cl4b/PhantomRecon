from unittest.mock import patch

from modules.subdomain_finder import find_subdomains
from modules.username_search import classify_response, search_username


def test_username_rejects_whitespace():
    result = search_username("bad user")
    assert result.status == "error"


def test_username_classifier_only_confirms_reliable_status_platforms():
    assert classify_response("GitHub", 200) == ("confirmed", "high")
    assert classify_response("Instagram", 200) == ("candidate", "low")
    assert classify_response("Instagram", 404) == ("not_found", "high")
    assert classify_response("GitLab", 302) == ("unknown", "low")


@patch("modules.username_search.check_platform")
def test_username_returns_confirmed_and_candidate_profiles(check):
    def fake_check(platform, url, timeout):
        if platform == "GitHub":
            return {
                "platform": platform,
                "url": url,
                "found": True,
                "state": "confirmed",
                "confidence": "high",
                "status_code": 200,
                "error": None,
            }
        if platform == "Instagram":
            return {
                "platform": platform,
                "url": url,
                "found": False,
                "state": "candidate",
                "confidence": "low",
                "status_code": 200,
                "error": None,
            }
        return {
            "platform": platform,
            "url": url,
            "found": False,
            "state": "not_found",
            "confidence": "high",
            "status_code": 404,
            "error": None,
        }

    check.side_effect = fake_check
    result = search_username("tester", workers=2)
    assert result.status == "success"
    assert result.data["platforms_scanned"] > 20
    assert result.data["profiles_found"] == 1
    assert result.data["candidate_profiles"] == 1
    assert result.data["profiles"][0]["platform"] == "GitHub"
    assert result.data["candidates"][0]["platform"] == "Instagram"


@patch("modules.subdomain_finder.crt_sh_lookup")
def test_subdomain_passive_mode(crt):
    crt.return_value = {"www.example.com", "api.example.com"}
    result = find_subdomains("https://example.com/path")
    assert result.status == "success"
    assert result.data["mode"] == "passive"
    assert result.data["total"] == 2
