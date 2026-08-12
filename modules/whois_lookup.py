"""PhantomRecon WHOIS lookup module."""

from __future__ import annotations

from typing import Any

import whois

from core.banner import get_input, print_error, print_info, print_success, show_module_banner
from core.result import ScanResult
from core.utils import ask_save_report, display_results_table, pause, validate_domain


def normalize_domain(target: str) -> str:
    domain = target.strip().lower().replace("http://", "").replace("https://", "").split("/")[0]
    if not validate_domain(domain):
        raise ValueError("Invalid domain name")
    return domain


def _first(value: Any) -> Any:
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _list(value: Any, limit: int | None = None) -> list[str]:
    if value is None:
        return []
    items = value if isinstance(value, list) else [value]
    if limit is not None:
        items = items[:limit]
    return [str(item) for item in items if item]


def lookup_whois(target: str) -> ScanResult:
    try:
        domain = normalize_domain(target)
    except ValueError as exc:
        return ScanResult.failure("whois_lookup", target, str(exc))

    try:
        record = whois.whois(domain)
    except Exception as exc:
        return ScanResult.failure("whois_lookup", target, f"WHOIS lookup failed: {exc}")

    domain_name = _first(getattr(record, "domain_name", None))
    if not domain_name:
        return ScanResult.failure("whois_lookup", target, "WHOIS information not found")

    data = {
        "domain": str(domain_name),
        "registrar": getattr(record, "registrar", None),
        "whois_server": getattr(record, "whois_server", None),
        "creation_date": str(_first(getattr(record, "creation_date", None)) or ""),
        "updated_date": str(_first(getattr(record, "updated_date", None)) or ""),
        "expiration_date": str(_first(getattr(record, "expiration_date", None)) or ""),
        "name_servers": _list(getattr(record, "name_servers", None), limit=5),
        "status": _list(getattr(record, "status", None), limit=3),
        "organization": getattr(record, "org", None),
        "country": getattr(record, "country", None),
        "state": getattr(record, "state", None),
        "city": getattr(record, "city", None),
        "address": getattr(record, "address", None),
        "emails": _list(getattr(record, "emails", None)),
        "dnssec": getattr(record, "dnssec", None),
    }
    return ScanResult(module="whois_lookup", target=domain, data=data)


def _display_data(result: ScanResult) -> dict[str, object]:
    d = result.data
    return {
        "Domain": d.get("domain") or "N/A",
        "Registrar": d.get("registrar") or "N/A",
        "WHOIS Server": d.get("whois_server") or "N/A",
        "Creation Date": d.get("creation_date") or "N/A",
        "Last Update": d.get("updated_date") or "N/A",
        "Expiration Date": d.get("expiration_date") or "N/A",
        "Name Servers": ", ".join(d.get("name_servers", [])) or "N/A",
        "Status": ", ".join(d.get("status", [])) or "N/A",
        "Organization": d.get("organization") or "N/A",
        "Country": d.get("country") or "N/A",
        "State": d.get("state") or "N/A",
        "City": d.get("city") or "N/A",
        "Address": d.get("address") or "N/A",
        "Email": ", ".join(d.get("emails", [])) or "N/A",
        "DNSSEC": d.get("dnssec") or "N/A",
    }


def run() -> None:
    show_module_banner("WHOIS Lookup", "🔍")
    print_info("Enter the domain name for WHOIS lookup (e.g., example.com)")
    target = get_input("Domain")
    if not target:
        print_error("No domain entered.")
        pause()
        return

    print_info(f"Querying WHOIS for {target}...")
    result = lookup_whois(target)
    if result.status != "success":
        print_error(result.errors[0] if result.errors else "WHOIS lookup failed")
        pause()
        return

    results = _display_data(result)
    print_success("WHOIS lookup complete!")
    display_results_table("🔍 WHOIS Lookup Results", results)
    ask_save_report(results, "whois_lookup", result.target)
    pause()
