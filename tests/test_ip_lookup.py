from unittest.mock import Mock, patch

from modules.ip_lookup import lookup_ip


def test_lookup_ip_rejects_invalid_target():
    result = lookup_ip("not a valid target")
    assert result.status == "error"
    assert result.module == "ip_lookup"


@patch("modules.ip_lookup.socket.gethostbyaddr", side_effect=OSError)
@patch("modules.ip_lookup.requests.get")
def test_lookup_ip_returns_machine_readable_data(mock_get, _mock_reverse):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "status": "success",
        "query": "8.8.8.8",
        "country": "United States",
        "countryCode": "US",
        "lat": 37.751,
        "lon": -97.822,
        "proxy": False,
        "hosting": True,
        "mobile": False,
    }
    mock_get.return_value = response

    result = lookup_ip("8.8.8.8")

    assert result.status == "success"
    assert result.data["ip"] == "8.8.8.8"
    assert result.data["proxy"] is False
    assert result.data["hosting"] is True
    mock_get.assert_called_once()
