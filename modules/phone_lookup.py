"""PhantomRecon phone-number OSINT module."""

from __future__ import annotations

import phonenumbers
from phonenumbers import carrier, geocoder, timezone

from core.banner import (
    get_input,
    print_error,
    print_info,
    print_success,
    show_module_banner,
)
from core.result import ScanResult
from core.utils import ask_save_report, display_results_table, pause

TYPE_MAP = {
    phonenumbers.PhoneNumberType.FIXED_LINE: "Fixed Line",
    phonenumbers.PhoneNumberType.MOBILE: "Mobile",
    phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line / Mobile",
    phonenumbers.PhoneNumberType.TOLL_FREE: "Toll Free",
    phonenumbers.PhoneNumberType.PREMIUM_RATE: "Premium Rate",
    phonenumbers.PhoneNumberType.VOIP: "VoIP",
    phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
    phonenumbers.PhoneNumberType.PAGER: "Pager",
    phonenumbers.PhoneNumberType.UAN: "UAN",
    phonenumbers.PhoneNumberType.UNKNOWN: "Unknown",
}


def lookup_phone(target: str) -> ScanResult:
    """Analyze a phone number and return structured metadata."""
    try:
        parsed = phonenumbers.parse(target.strip(), None)
    except phonenumbers.NumberParseException as exc:
        return ScanResult.failure(
            "phone_lookup",
            target,
            f"Number parse failed: {exc}",
        )

    possible = phonenumbers.is_possible_number(parsed)
    valid = phonenumbers.is_valid_number(parsed)
    if not possible:
        return ScanResult.failure(
            "phone_lookup",
            target,
            "Phone number is not possible",
        )

    data = {
        "valid": valid,
        "possible": possible,
        "country": geocoder.description_for_number(parsed, "en") or None,
        "country_code": parsed.country_code,
        "national_number": str(parsed.national_number),
        "carrier": carrier.name_for_number(parsed, "en") or None,
        "line_type": TYPE_MAP.get(phonenumbers.number_type(parsed), "Unknown"),
        "time_zones": list(timezone.time_zones_for_number(parsed)),
        "international_format": phonenumbers.format_number(
            parsed,
            phonenumbers.PhoneNumberFormat.INTERNATIONAL,
        ),
        "e164_format": phonenumbers.format_number(
            parsed,
            phonenumbers.PhoneNumberFormat.E164,
        ),
    }
    return ScanResult(module="phone_lookup", target=target, data=data)


def _display_data(result: ScanResult) -> dict[str, object]:
    data = result.data
    return {
        "Number": result.target,
        "Valid": "✅ Yes" if data.get("valid") else "❌ No",
        "Possible": "✅ Yes" if data.get("possible") else "❌ No",
        "Country": data.get("country") or "Unknown",
        "Country Code": f"+{data.get('country_code')}",
        "National Number": data.get("national_number") or "N/A",
        "Carrier": data.get("carrier") or "Unknown",
        "Line Type": data.get("line_type") or "Unknown",
        "Time Zone": ", ".join(data.get("time_zones", [])) or "Unknown",
        "International Format": data.get("international_format") or "N/A",
        "E164 Format": data.get("e164_format") or "N/A",
    }


def run() -> None:
    """Run the classic interactive phone lookup interface."""
    show_module_banner("Phone Number OSINT", "📱")
    print_info("Enter the phone number in international format (e.g., +905551234567)")
    target = get_input("Phone Number")
    if not target:
        print_error("No number entered.")
        pause()
        return

    result = lookup_phone(target)
    if result.status != "success":
        print_error(result.errors[0] if result.errors else "Phone lookup failed")
        pause()
        return

    results = _display_data(result)
    print_success("Phone number analysis complete!")
    display_results_table("📱 Phone Number OSINT", results)
    ask_save_report(results, "phone_lookup", target)
    pause()
