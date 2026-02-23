"""
PhantomRecon - Email OSINT Module
Email validation, MX record checking, and reputation analysis.
"""

import re
import requests
import dns.resolver

from core.banner import show_module_banner, print_success, print_error, print_info, print_warning, get_input, console
from core.utils import validate_email, display_results_table, ask_save_report, pause


def check_mx_records(domain: str) -> list:
    """Check MX records for a domain."""
    try:
        mx_records = dns.resolver.resolve(domain, "MX")
        return [str(record.exchange).rstrip(".") for record in mx_records]
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, Exception):
        return []


def check_email_reputation(email: str) -> dict | None:
    """Check email reputation using emailrep.io API."""
    try:
        headers = {"User-Agent": "PhantomRecon OSINT Tool"}
        response = requests.get(
            f"https://emailrep.io/{email}",
            headers=headers,
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException:
        return None


def check_disposable(domain: str) -> bool:
    """Check if the email domain is a disposable email service."""
    disposable_domains = [
        "tempmail.com", "throwaway.email", "guerrillamail.com",
        "mailinator.com", "10minutemail.com", "trashmail.com",
        "yopmail.com", "sharklasers.com", "guerrillamailblock.com",
        "grr.la", "dispostable.com", "maildrop.cc", "temp-mail.org",
        "fakeinbox.com", "tempail.com", "mohmal.com", "burnermail.io",
    ]
    return domain.lower() in disposable_domains


def run():
    """Run the email OSINT module."""
    show_module_banner("Email OSINT", "📧")

    print_info("Enter the email address to analyze")
    target = get_input("Email")

    if not target:
        print_error("No email entered.")
        pause()
        return

    if not validate_email(target):
        print_error("Invalid email format!")
        pause()
        return

    try:
        domain = target.split("@")[1]
        username = target.split("@")[0]

        print_info("Analyzing email...")

        # MX Records
        mx_records = check_mx_records(domain)
        has_mx = len(mx_records) > 0

        # Disposable check
        is_disposable = check_disposable(domain)

        # Basic analysis
        results = {
            "Email": target,
            "Username": username,
            "Domain": domain,
            "Format Valid": "✅ Yes",
            "MX Records": ", ".join(mx_records) if mx_records else "❌ Not found",
            "Mail Server Exists": "✅ Yes" if has_mx else "❌ No",
            "Disposable": "⚠️ Yes" if is_disposable else "✅ No",
        }

        # Domain type detection
        free_providers = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
                          "protonmail.com", "aol.com", "icloud.com", "mail.com",
                          "yandex.com", "zoho.com"]
        if domain.lower() in free_providers:
            results["Provider Type"] = "Free Email Provider"
        else:
            results["Provider Type"] = "Corporate / Custom Domain"

        # Email reputation check
        print_info("Checking email reputation...")
        reputation = check_email_reputation(target)

        if reputation:
            results["Reputation"] = reputation.get("reputation", "N/A")
            results["Suspicious"] = "⚠️ Yes" if reputation.get("suspicious") else "✅ No"
            results["Malicious"] = "🔴 Yes" if reputation.get("malicious") else "✅ No"

            details = reputation.get("details", {})
            if details:
                results["Data Breach"] = "⚠️ Yes" if details.get("data_breach") else "No info"
                results["First Seen"] = details.get("first_seen", "N/A")
                results["Profiles"] = ", ".join(details.get("profiles", [])) or "Not found"
        else:
            print_warning("Email reputation service did not respond (rate limit might be hit).")

        print_success("Email analysis complete!")
        display_results_table("📧 Email OSINT Results", results)

        ask_save_report(results, "email_osint", target)

    except Exception as e:
        print_error(f"Hata oluştu: {e}")

    pause()
