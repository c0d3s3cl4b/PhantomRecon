from unittest.mock import patch

import pytest

from modules.port_scanner import MAX_PORTS_PER_SCAN, parse_ports, scan_ports


def test_parse_ports_supports_lists_and_ranges():
    assert parse_ports("22,80,443,8000-8002") == [22, 80, 443, 8000, 8001, 8002]


def test_parse_ports_rejects_invalid_range():
    with pytest.raises(ValueError):
        parse_ports("100-1")


def test_parse_ports_enforces_scan_limit():
    with pytest.raises(ValueError):
        parse_ports(f"1-{MAX_PORTS_PER_SCAN + 1}")


@patch("modules.port_scanner.normalize_target", return_value=("127.0.0.1", "localhost"))
@patch("modules.port_scanner.scan_port")
def test_scan_ports_returns_structured_open_ports(mock_scan, _mock_target):
    mock_scan.side_effect = lambda _ip, port, _timeout: (
        {"port": port, "state": "open", "service": "HTTP"}
        if port == 80
        else None
    )

    result = scan_ports("localhost", [22, 80], workers=2)

    assert result.status == "success"
    assert result.data["ports_scanned"] == 2
    assert result.data["open_count"] == 1
    assert result.data["open_ports"][0]["port"] == 80
