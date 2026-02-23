"""
PhantomRecon - Phone Number OSINT Module
Analyzes phone numbers for carrier, location, and type information.
"""

import phonenumbers
from phonenumbers import carrier, geocoder, timezone

from core.banner import show_module_banner, print_success, print_error, print_info, get_input, console
from core.utils import display_results_table, ask_save_report, pause


def run():
    """Run the phone number lookup module."""
    show_module_banner("Phone Number OSINT", "📱")

    print_info("Enter the phone number in international format (e.g., +905551234567)")
    target = get_input("Phone Number")

    if not target:
        print_error("No number entered.")
        pause()
        return

    try:
        # Parse the phone number
        parsed = phonenumbers.parse(target)

        # Validate
        is_valid = phonenumbers.is_valid_number(parsed)
        is_possible = phonenumbers.is_possible_number(parsed)

        if not is_valid and not is_possible:
            print_error("Invalid phone number!")
            pause()
            return

        # Gather information
        country = geocoder.description_for_number(parsed, "en")
        carrier_name = carrier.name_for_number(parsed, "en")
        time_zones = timezone.time_zones_for_number(parsed)
        number_type = phonenumbers.number_type(parsed)

        type_map = {
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

        results = {
            "Number": target,
            "Valid": "✅ Yes" if is_valid else "❌ No",
            "Country": country or "Unknown",
            "Country Code": f"+{parsed.country_code}",
            "National Number": str(parsed.national_number),
            "Carrier": carrier_name or "Unknown",
            "Line Type": type_map.get(number_type, "Unknown"),
            "Time Zone": ", ".join(time_zones) if time_zones else "Unknown",
            "International Format": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "E164 Format": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
        }

        print_success("Phone number analysis complete!")
        display_results_table("📱 Phone Number OSINT", results)

        ask_save_report(results, "phone_lookup", target)

    except phonenumbers.NumberParseException as e:
        print_error(f"Numara ayrıştırılamadı: {e}")
    except Exception as e:
        print_error(f"Hata oluştu: {e}")

    pause()
