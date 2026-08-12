"""PhantomRecon email OSINT module."""

from __future__ import annotations

import dns.resolver
import requests

from core.banner import get_input, print_error, print_info, print_success, print_warning, show_module_banner
from core.result import ScanResult
from core.utils import ask_save_report, display_results_table, pause, validate_email

DISPOSABLE_DOMAINS = {
    "tempmail.com", "throwaway.email", "guerrillamail.com", "mailinator.com",
    "10minutemail.com", "trashmail.com", "yopmail.com", "sharklasers.com",
    "guerrillamailblock.com", "grr.la", "dispostable.com", "maildrop.cc",
    "temp-mail.org", "fakeinbox.com", "tempail.com", "mohmal.com", "burnermail.io",
}

FREE_PROVIDERS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "protonmail.com",
    "aol.com", "icloud.com", "mail.com", "yandex.com", "zoho.com",
}


def check_mx_records(domain: str) -> list[str]:
    try:
        records = dns.resolver.resolve(domain, "MX")
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.resolver.Timeout):
        return []
    return [str(record.exchange).rstrip(".") for record in records]


def check_email_reputation(email: str, timeout: float = 10.0) -> dict | None:
    try:
        response = requests.get(
            f"https://emailrep.io/{email}",
            headers={"User-Agent": "PhantomRecon OSINT Tool"},
            timeout=timeout,
        )
        if response.status_code == 200:
            return response.json()
    except (requests.RequestException, ValueError):
        return None
    return None


def analyze_email(target: str, *, reputation: bool = True, timeout: float = 10.0) -> ScanResult:
    target = target.strip().lower()
    if not validate_email(target):
        return ScanResult.failure("email_osint", target, "Invalid email format")

    username, domain = target.rsplit("@", 1)
    mx_records = check_mx_records(domain)
    data = {
        "email": target,
        "username": username,
        "domain": domain,
        "format_valid": True,
        "mx_records": mx_records,
        "mail_server_exists": bool(mx_records),
        "disposable": domain in DISPOSABLE_DOMAINS,
        "provider_type": "free" if domain in FREE_PROVIDERS else "custom",
        "reputation_available": False,
    }

    if reputation:
        rep = check_email_reputation(target, timeout=timeout)
        if rep:
            details = rep.get("details") or {}
            data.update(
                {
                    "reputation_available": True,
                    "reputation": rep.get("reputation"),
                    "suspicious": bool(rep.get("suspicious")),
                    "malicious": bool(rep.get("malicious")),
                    "data_breach": bool(details.get("data_breach")),
                    "first_seen": details.get("first_seen"),
                    "profiles": list(details.get("profiles") or []),
                }
            )

    return ScanResult(module="email_osint", target=target, data=data)


def _display_data(result: ScanResult) -> dict[str, object]:
    d = result.data
    values: dict[str, object] = {
        "Email": d.get("email"),
        "Username": d.get("username"),
        "Domain": d.get("domain"),
        "Format Valid": "✅ Yes",
        "MX Records": ", ".join(d.get("mx_records", [])) or "❌ Not found",
        "Mail Server Exists": "✅ Yes" if d.get("mail_server_exists") else "❌ No",
        "Disposable": "⚠️ Yes" if d.get("disposable") else "✅ No",
        "Provider Type": "Free Email Provider" if d.get("provider_type") == "free" else "Corporate / Custom Domain",
    }
    if d.get("reputation_available"):
        values.update(
            {
                "Reputation": d.get("reputation") or "N/A",
                "Suspicious": "⚠️ Yes" if d.get("suspicious") else "✅ No",
                "Malicious": "🔴 Yes" if d.get("malicious") else "✅ No",
                "Data Breach": "⚠️ Yes" if d.get("data_breach") else "No info",
                "First Seen": d.get("first_seen") or "N/A",
                "Profiles": ", ".join(d.get("profiles", [])) or "Not found",
            }
        )
    return values


def run() -> None:
    show_module_banner("Email OSINT", "📧")
    print_info("Enter the email address to analyze")
    target = get_input("Email")
    if not target:
        print_error("No email entered.")
        pause()
        return

    print_info("Analyzing email and checking reputation...")
    result = analyze_email(target)
    if result.status != "success":
        print_error(result.errors[0] if result.errors else "Email analysis failed")
        pause()
        return

    if not result.data.get("reputation_available"):
        print_warning("Email reputation service did not return data; local/DNS analysis is still valid.")

    results = _display_data(result)
    print_success("Email analysis complete!")
    display_results_table("📧 Email OSINT Results", results)
    ask_save_report(results, "email_osint", result.target)
    pause()
