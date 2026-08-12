from types import SimpleNamespace
from unittest.mock import patch

from modules.email_osint import analyze_email
from modules.phone_lookup import lookup_phone
from modules.whois_lookup import lookup_whois


def test_phone_lookup_returns_structured_result():
    result = lookup_phone("+14155552671")
    assert result.status == "success"
    assert result.module == "phone_lookup"
    assert result.data["possible"] is True
    assert result.data["e164_format"] == "+14155552671"


def test_phone_lookup_rejects_invalid_number():
    result = lookup_phone("abc")
    assert result.status == "error"


@patch("modules.whois_lookup.whois.whois")
def test_whois_lookup_normalizes_record(mock_whois):
    mock_whois.return_value = SimpleNamespace(
        domain_name=["EXAMPLE.COM"],
        registrar="Example Registrar",
        whois_server="whois.example.test",
        creation_date=None,
        updated_date=None,
        expiration_date=None,
        name_servers=["NS1.EXAMPLE.COM", "NS2.EXAMPLE.COM"],
        status=["clientTransferProhibited"],
        org="Example Org",
        country="US",
        state=None,
        city=None,
        address=None,
        emails=["admin@example.com"],
        dnssec="unsigned",
    )

    result = lookup_whois("https://example.com/path")

    assert result.status == "success"
    assert result.target == "example.com"
    assert result.data["domain"] == "EXAMPLE.COM"
    assert result.data["name_servers"] == ["NS1.EXAMPLE.COM", "NS2.EXAMPLE.COM"]


@patch("modules.email_osint.check_email_reputation", return_value=None)
@patch("modules.email_osint.check_mx_records", return_value=["mx.example.com"])
def test_email_analysis_survives_missing_reputation(_mock_mx, _mock_rep):
    result = analyze_email("user@example.com")

    assert result.status == "success"
    assert result.data["format_valid"] is True
    assert result.data["mail_server_exists"] is True
    assert result.data["reputation_available"] is False


def test_email_analysis_rejects_invalid_address():
    result = analyze_email("not-an-email", reputation=False)
    assert result.status == "error"
