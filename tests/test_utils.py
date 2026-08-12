from core.utils import validate_domain, validate_email, validate_ip, validate_phone


def test_validate_ip_accepts_valid_ipv4():
    assert validate_ip("8.8.8.8")


def test_validate_ip_rejects_out_of_range_octet():
    assert not validate_ip("999.8.8.8")


def test_validate_email_basic_cases():
    assert validate_email("analyst@example.com")
    assert not validate_email("not-an-email")


def test_validate_phone_requires_international_format():
    assert validate_phone("+905551234567")
    assert not validate_phone("05551234567")


def test_validate_domain_basic_cases():
    assert validate_domain("example.com")
    assert not validate_domain("http://example.com")
