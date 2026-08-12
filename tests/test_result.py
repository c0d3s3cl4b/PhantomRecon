from core.result import ScanResult


def test_scan_result_is_machine_readable():
    result = ScanResult(module="ip_lookup", target="8.8.8.8", data={"proxy": False})
    payload = result.to_dict()

    assert payload["module"] == "ip_lookup"
    assert payload["target"] == "8.8.8.8"
    assert payload["status"] == "success"
    assert payload["data"]["proxy"] is False
    assert payload["errors"] == []


def test_failure_result_contains_error():
    result = ScanResult.failure("whois", "invalid", "Invalid domain")

    assert result.status == "error"
    assert result.errors == ["Invalid domain"]
